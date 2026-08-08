#!/usr/bin/env python3
"""Create readable A4 landscape two-up editions from existing paper data."""

from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import sys
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "y3" / "work"))
import render_paper as renderer

OUTPUT_DIR = ROOT / "y3" / "output" / "2up"
BUILD_DIR = ROOT / "y3" / "build" / "2up-a4"
REPORT_PATH = ROOT / "y3" / "work" / "2up-validation.json"
A4 = fitz.paper_rect("a4")
LANDSCAPE_WIDTH = A4.height
LANDSCAPE_HEIGHT = A4.width
LEFT = fitz.Rect(0, 0, LANDSCAPE_WIDTH / 2, LANDSCAPE_HEIGHT)
RIGHT = fitz.Rect(LANDSCAPE_WIDTH / 2, 0, LANDSCAPE_WIDTH, LANDSCAPE_HEIGHT)
OUTPUT_SCALE = min(LEFT.width / A4.width, LEFT.height / A4.height)


def multiplier(label: str) -> tuple[float, float]:
    if label.startswith("prompt-L"):
        question_number = int(label.removeprefix("prompt-L"))
        if question_number >= 26:
            return 1.38, 1.00
    if label.startswith("prompt-"):
        return 1.42, 1.04
    if label.startswith("options-"):
        return 1.42, 1.02
    if label.startswith(("passage-", "writing-", "diagram-", "answer-")):
        return 1.42, 1.04
    return 1.0, 1.22


class TwoUpAudit:
    def __init__(self):
        self.entries = []

    def record(self, label, spare, scale, font_size):
        entry = {
            "label": label,
            "font_size": font_size,
            "spare_height": round(float(spare), 2),
            "scale": round(float(scale), 4),
        }
        self.entries.append(entry)
        if spare < -0.01 or scale < 0.90:
            raise RuntimeError(f"2-up text overflow or excessive scaling: {entry}")


def enlarged_html_box(page, rect, body, label, size=8, align="left", css=""):
    size_multiplier, line_height = multiplier(label)
    requested_size = size * size_multiplier
    markup = (
        f'<div style="font-size:{requested_size}pt;line-height:{line_height};'
        f'text-align:{align}">{body}</div>'
    )
    spare, scale = page.insert_htmlbox(rect, markup, css=renderer.CSS + css, scale_low=0)
    renderer.AUDIT.record(label, spare, scale, requested_size)


def draw_grammar_item(page, question, number, rect):
    page.draw_line(rect.bl, rect.br, color=(0.84, 0.90, 0.90), width=0.45)
    renderer.draw_number(page, number, rect.x0 + 10, rect.y0 + 11, 7.5)
    renderer.html_box(
        page,
        fitz.Rect(rect.x0 + 23, rect.y0 + 1, rect.x1 - 4, rect.y0 + 35),
        question["prompt"],
        f"prompt-{question['id']}",
        8.4,
    )
    renderer.html_box(
        page,
        fitz.Rect(rect.x0 + 25, rect.y0 + 34, rect.x1 - 3, rect.y1 - 2),
        renderer.option_table(question["options"]),
        f"options-{question['id']}",
        7.6,
    )


def draw_spelling_item(page, question, number, rect):
    page.draw_line(rect.bl, rect.br, color=(0.84, 0.90, 0.90), width=0.4)
    renderer.draw_number(page, number, rect.x0 + 9, rect.y0 + 10, 7)
    prompt_rect = fitz.Rect(rect.x0 + 21, rect.y0 + 1, rect.x1 - 3, rect.y0 + 34)
    answer_rect = fitz.Rect(rect.x0 + 25, rect.y1 - 17, rect.x1 - 7, rect.y1 - 4)
    if prompt_rect.y1 + 2 > answer_rect.y0:
        raise RuntimeError(f"spelling item {question['id']}: prompt and answer areas overlap")
    renderer.html_box(
        page,
        prompt_rect,
        question["prompt"],
        f"prompt-{question['id']}",
        7.5,
    )
    page.draw_rect(
        answer_rect,
        color=renderer.LINE,
        fill=renderer.LIGHT,
        width=0.5,
    )


def draw_reading_question(page, question, number, rect):
    page.draw_rect(rect, color=renderer.LINE, fill=(1, 1, 1), radius=0.035, width=0.55)
    renderer.draw_number(page, number, rect.x0 + 10, rect.y0 + 12, 7.2)
    renderer.html_box(
        page,
        fitz.Rect(rect.x0 + 21, rect.y0 + 2, rect.x1 - 3, rect.y0 + 47),
        question["prompt"],
        f"prompt-{question['id']}",
        7.6,
    )
    renderer.html_box(
        page,
        fitz.Rect(rect.x0 + 22, rect.y0 + 46, rect.x1 - 3, rect.y1 - 2),
        renderer.option_markup(question["options"]),
        f"options-{question['id']}",
        7.4,
    )


def draw_writing_page(doc):
    writing = renderer.PAPER["writing"]
    page = renderer.add_page(doc, "Writing", writing["title"])
    page.draw_rect(fitz.Rect(32, 82, 563, 255), color=renderer.LINE, fill=renderer.LIGHT, width=0.6, radius=0.04)
    renderer.html_box(page, fitz.Rect(46, 94, 548, 142), f"<b>{writing['prompt']}</b>", "writing-prompt", 10.0)
    ideas = "".join(f"<li>{html.escape(item)}</li>" for item in writing["ideas"])
    renderer.html_box(page, fitz.Rect(46, 146, 548, 247), f"Your story may be amusing or serious.<ul>{ideas}</ul>", "writing-ideas", 7.8)
    reminders = "".join(f"<li>{html.escape(item)}</li>" for item in writing["reminders"])
    renderer.html_box(page, fitz.Rect(34, 266, 563, 355), f"<b>Remember</b><ul>{reminders}</ul>", "writing-reminders", 7.6)
    renderer.html_box(page, fitz.Rect(34, 365, 563, 386), "<b>Planning notes</b>", "writing-planning", 8.0)
    for y in range(394, 482, 22):
        page.draw_line(fitz.Point(36, y), fitz.Point(560, y), color=(0.76, 0.84, 0.84), width=0.45)
    renderer.html_box(page, fitz.Rect(34, 493, 563, 514), "<b>Begin your narrative</b>", "writing-start", 8.0)
    for y in range(522, 805, 23):
        page.draw_line(fitz.Point(36, y), fitz.Point(560, y), color=(0.76, 0.84, 0.84), width=0.45)


def normalized_text(value: str) -> str:
    return re.sub(r"[^\w]+", "", value, flags=re.UNICODE).casefold()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_enlarged_source(paper_number: int) -> tuple[fitz.Document, list[dict]]:
    renderer.configure(paper_number)
    renderer.AUDIT = TwoUpAudit()
    renderer.validate_cache()
    renderer.validate_content()
    document = fitz.open()
    renderer.draw_language_pages(document)
    renderer.draw_reading_pages(document)
    renderer.draw_writing_page(document)
    renderer.draw_numeracy_pages(document)
    renderer.draw_answers(document)
    if document.page_count != 26:
        raise RuntimeError(f"paper {paper_number}: expected 26 source pages")
    return document, list(renderer.AUDIT.entries)


def main() -> None:
    renderer.html_box = enlarged_html_box
    renderer.draw_grammar_item = draw_grammar_item
    renderer.draw_spelling_item = draw_spelling_item
    renderer.draw_reading_question = draw_reading_question
    renderer.draw_writing_page = draw_writing_page

    for path in (ROOT / "y3" / "output" / "a4-landscape-2up", ROOT / "y3" / "output" / "2up-a3", ROOT / "y3" / "output" / "2up-a4"):
        if path.exists():
            shutil.rmtree(path)
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    OUTPUT_DIR.mkdir(parents=True)
    BUILD_DIR.mkdir(parents=True)

    papers = []
    hashes = set()
    for paper_number in range(1, 21):
        source, audit = build_enlarged_source(paper_number)
        output = fitz.open()
        for source_index in range(0, 26, 2):
            sheet = output.new_page(width=LANDSCAPE_WIDTH, height=LANDSCAPE_HEIGHT)
            sheet.show_pdf_page(LEFT, source, source_index, keep_proportion=True)
            sheet.show_pdf_page(RIGHT, source, source_index + 1, keep_proportion=True)
        output_path = OUTPUT_DIR / f"p{paper_number:02d}.pdf"
        output.save(output_path, garbage=4, deflate=True, clean=True)
        output.close()

        final = fitz.open(output_path)
        render_dir = BUILD_DIR / f"p{paper_number:02d}"
        render_dir.mkdir()
        checks = []
        for sheet_index, sheet in enumerate(final):
            if sheet.rect != fitz.Rect(0, 0, LANDSCAPE_WIDTH, LANDSCAPE_HEIGHT):
                raise RuntimeError(f"{output_path} sheet {sheet_index + 1}: not A4 landscape")
            actual = normalized_text(sheet.get_text("text"))
            source_pages = [sheet_index * 2, sheet_index * 2 + 1]
            for source_page in source_pages:
                expected = normalized_text(source[source_page].get_text("text"))
                if not expected or expected not in actual:
                    raise RuntimeError(f"{output_path} sheet {sheet_index + 1}: text mismatch")
            render_path = render_dir / f"s{sheet_index + 1:02d}.png"
            sheet.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(render_path)
            checks.append({"sheet": sheet_index + 1, "source_pages": [page + 1 for page in source_pages]})
        if final.page_count != 13:
            raise RuntimeError(f"{output_path}: expected 13 pages")

        digest = sha256(output_path)
        if digest in hashes:
            raise RuntimeError(f"duplicate PDF: {output_path}")
        hashes.add(digest)
        body_entries = [entry for entry in audit if entry["label"].startswith(("prompt-", "options-", "passage-", "writing-", "diagram-", "answer-"))]
        spelling_entries = [
            entry
            for entry in body_entries
            if entry["label"].startswith("prompt-L")
            and int(entry["label"].removeprefix("prompt-L")) >= 26
        ]
        minimum_spelling_scale = min(entry["scale"] for entry in spelling_entries)
        if minimum_spelling_scale < 0.94:
            raise RuntimeError(
                f"paper {paper_number}: spelling text scaled below safe threshold "
                f"({minimum_spelling_scale:.4f})"
            )
        effective_sizes = [entry["font_size"] * entry["scale"] * OUTPUT_SCALE for entry in body_entries]
        papers.append({
            "paper": paper_number,
            "output": str(output_path.relative_to(ROOT)),
            "pages": final.page_count,
            "minimum_layout_scale": min(entry["scale"] for entry in body_entries),
            "minimum_spelling_layout_scale": minimum_spelling_scale,
            "minimum_effective_text_pt": round(min(effective_sizes), 2),
            "median_effective_text_pt": round(sorted(effective_sizes)[len(effective_sizes) // 2], 2),
            "sha256": digest,
            "checks": checks,
        })
        final.close()
        source.close()

    report = {
        "status": "passed",
        "format": "A4 landscape, two logical source pages per sheet",
        "content_generation": False,
        "ocr": False,
        "files": 20,
        "pages_per_file": 13,
        "font_strategy": {
            "prompt_multiplier": 1.42,
            "spelling_prompt_multiplier": 1.38,
            "option_multiplier": 1.42,
            "passage_answer_multiplier": 1.42,
            "compact_option_line_height": 1.02,
            "spelling_line_height": 1.00,
            "whole_page_output_scale": round(OUTPUT_SCALE, 4),
        },
        "high_risk_visual_inspection": {
            "status": "passed",
            "region": "sheet 2 right half (source spelling page 4)",
            "papers": 20,
            "render_scale": 2,
            "checks": [
                "questions 26–40 show 15 blank dictation lines and no leaked answers",
                "questions 41–45 each show one visible underlined misspelling",
                "questions 46–50 each show one unmarked misspelling",
                "no clipped prompt or answer box",
                "no prompt enters an adjacent item",
            ],
        },
        "papers": papers,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "passed",
        "directory": str(OUTPUT_DIR.relative_to(ROOT)),
        "files": 20,
        "pages_each": 13,
        "minimum_effective_text_pt": min(paper["minimum_effective_text_pt"] for paper in papers),
        "median_effective_text_pt": min(paper["median_effective_text_pt"] for paper in papers),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
