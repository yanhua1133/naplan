#!/usr/bin/env python3
"""Impose the existing Year 3 PDFs two-up on landscape A4 pages."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "y3" / "output"
OUTPUT_DIR = SOURCE_DIR / "a4-landscape-2up"
BUILD_DIR = ROOT / "y3" / "build" / "a4-landscape-2up"
REPORT_PATH = ROOT / "y3" / "work" / "a4-landscape-2up-validation.json"
SOURCE_PATTERN = "year3-naplan-style-practice-paper-[0-9][0-9].pdf"
EXPECTED_PAPERS = 20
EXPECTED_SOURCE_PAGES = 26
EXPECTED_OUTPUT_PAGES = 13


def normalized_text(text: str) -> str:
    return re.sub(r"[^\w]+", "", text, flags=re.UNICODE).casefold()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    sources = sorted(SOURCE_DIR.glob(SOURCE_PATTERN))
    if len(sources) != EXPECTED_PAPERS:
        raise RuntimeError(f"Expected {EXPECTED_PAPERS} source PDFs, found {len(sources)}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    a4 = fitz.paper_rect("a4")
    landscape_width = a4.height
    landscape_height = a4.width
    left_rect = fitz.Rect(0, 0, landscape_width / 2, landscape_height)
    right_rect = fitz.Rect(landscape_width / 2, 0, landscape_width, landscape_height)

    results = []
    output_hashes = set()
    rendered_hashes = set()

    for source_path in sources:
        paper_number = source_path.stem.rsplit("-", 1)[-1]
        output_path = OUTPUT_DIR / f"{source_path.stem}-a4-landscape-2up.pdf"
        render_dir = BUILD_DIR / f"paper-{paper_number}"
        render_dir.mkdir(parents=True, exist_ok=True)
        for old_render in render_dir.glob("page-*.png"):
            old_render.unlink()

        source = fitz.open(source_path)
        if source.page_count != EXPECTED_SOURCE_PAGES:
            raise RuntimeError(
                f"{source_path.name}: expected {EXPECTED_SOURCE_PAGES} pages, "
                f"found {source.page_count}"
            )

        output = fitz.open()
        output.set_metadata({
            "title": f"{source.metadata.get('title') or source_path.stem} — A4 landscape 2-up",
            "subject": "Existing practice paper imposed two portrait pages per landscape A4 sheet",
            "creator": "PyMuPDF deterministic 2-up imposition",
        })

        for source_index in range(0, source.page_count, 2):
            sheet = output.new_page(width=landscape_width, height=landscape_height)
            sheet.show_pdf_page(left_rect, source, source_index, keep_proportion=True)
            sheet.show_pdf_page(right_rect, source, source_index + 1, keep_proportion=True)

        output.save(output_path, garbage=4, deflate=True, clean=True)
        output.close()

        imposed = fitz.open(output_path)
        if imposed.page_count != EXPECTED_OUTPUT_PAGES:
            raise RuntimeError(
                f"{output_path.name}: expected {EXPECTED_OUTPUT_PAGES} pages, "
                f"found {imposed.page_count}"
            )

        page_checks = []
        for sheet_index, sheet in enumerate(imposed):
            rect = sheet.rect
            size_ok = (
                abs(rect.width - landscape_width) < 0.1
                and abs(rect.height - landscape_height) < 0.1
            )
            if not size_ok:
                raise RuntimeError(f"{output_path.name} page {sheet_index + 1}: not A4 landscape")

            output_text = normalized_text(sheet.get_text("text"))
            source_indices = (sheet_index * 2, sheet_index * 2 + 1)
            text_matches = []
            for source_page_index in source_indices:
                source_text = normalized_text(source[source_page_index].get_text("text"))
                matches = bool(source_text) and source_text in output_text
                text_matches.append(matches)
                if not matches:
                    raise RuntimeError(
                        f"{output_path.name} sheet {sheet_index + 1}: "
                        f"source page {source_page_index + 1} text mismatch"
                    )

            pixmap = sheet.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            render_path = render_dir / f"page-{sheet_index + 1:02d}.png"
            pixmap.save(render_path)
            render_hash = hashlib.sha256(render_path.read_bytes()).hexdigest()
            if render_hash in rendered_hashes:
                raise RuntimeError(f"Duplicate rendered sheet detected: {render_path}")
            rendered_hashes.add(render_hash)

            page_checks.append({
                "sheet": sheet_index + 1,
                "source_pages": [source_indices[0] + 1, source_indices[1] + 1],
                "a4_landscape": size_ok,
                "source_text_preserved": all(text_matches),
                "render": str(render_path.relative_to(ROOT)),
                "render_sha256": render_hash,
            })

        output_digest = sha256(output_path)
        if output_digest in output_hashes:
            raise RuntimeError(f"Duplicate output PDF detected: {output_path}")
        output_hashes.add(output_digest)

        results.append({
            "paper": int(paper_number),
            "source": str(source_path.relative_to(ROOT)),
            "source_sha256": sha256(source_path),
            "source_pages": source.page_count,
            "output": str(output_path.relative_to(ROOT)),
            "output_sha256": output_digest,
            "output_pages": imposed.page_count,
            "page_size_points": [round(landscape_width, 2), round(landscape_height, 2)],
            "imposition": "source pages 1+2, 3+4, …, 25+26; left-to-right",
            "page_checks": page_checks,
        })
        imposed.close()
        source.close()

    report = {
        "status": "passed",
        "operation": "2-up imposition of existing PDFs only; no question generation and no OCR",
        "source_papers": len(sources),
        "source_pages_per_paper": EXPECTED_SOURCE_PAGES,
        "output_pages_per_paper": EXPECTED_OUTPUT_PAGES,
        "total_output_pages": len(sources) * EXPECTED_OUTPUT_PAGES,
        "output_directory": str(OUTPUT_DIR.relative_to(ROOT)),
        "a4_landscape_points": [round(landscape_width, 2), round(landscape_height, 2)],
        "papers": results,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "papers": report["source_papers"],
        "pages_per_output": report["output_pages_per_paper"],
        "total_pages": report["total_output_pages"],
        "output_directory": report["output_directory"],
        "report": str(REPORT_PATH.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
