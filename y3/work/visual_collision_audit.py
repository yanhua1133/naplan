#!/usr/bin/env python3
"""Build complete diagram contact sheets and verify recorded geometry gates."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "y3" / "work"
BUILD = ROOT / "y3" / "build"
OUTPUT = ROOT / "y3" / "output"
AUDIT_BUILD = BUILD / "visual-collision-audit"
REPORT_PATH = WORK / "visual-collision-audit.json"
A4_WIDTH = 595.276
A4_HEIGHT = 841.89
TWO_UP_LOGICAL_SCALE = 0.5 ** 0.5
TWO_UP_HALF_WIDTH = A4_HEIGHT / 2
EXPECTED_KINDS = {
    "backward_line", "bar_chart", "circle_pattern", "clock", "coins",
    "composite_solid", "cubes", "equal_area", "fractions", "l_grid",
    "letters", "money_table", "number_line", "pictograph", "room_map",
    "scales", "spinners", "thermometers", "top_view", "total_table",
}


def fit_crop(image: Image.Image, rect: list[float], scale_x: float, scale_y: float, margin: float = 5) -> Image.Image:
    x0, y0, x1, y1 = rect
    crop = (
        max(0, int((x0 - margin) * scale_x)),
        max(0, int((y0 - margin) * scale_y)),
        min(image.width, int((x1 + margin) * scale_x + 0.999)),
        min(image.height, int((y1 + margin) * scale_y + 0.999)),
    )
    return image.crop(crop)


def fit_two_up_crop(image: Image.Image, page_number: int, rect: list[float], margin: float = 5) -> Image.Image:
    half_offset = 0 if page_number % 2 else TWO_UP_HALF_WIDTH
    x0, y0, x1, y1 = rect
    points = (
        half_offset + (x0 - margin) * TWO_UP_LOGICAL_SCALE,
        (y0 - margin) * TWO_UP_LOGICAL_SCALE,
        half_offset + (x1 + margin) * TWO_UP_LOGICAL_SCALE,
        (y1 + margin) * TWO_UP_LOGICAL_SCALE,
    )
    scale_x = image.width / A4_HEIGHT
    scale_y = image.height / A4_WIDTH
    crop = (
        max(0, int(points[0] * scale_x)),
        max(0, int(points[1] * scale_y)),
        min(image.width, int(points[2] * scale_x + 0.999)),
        min(image.height, int(points[3] * scale_y + 0.999)),
    )
    return image.crop(crop)


def make_sheet(entries: list[tuple[str, Image.Image]], output: Path) -> None:
    columns, rows = 5, 10
    tile_width, tile_height = 310, 225
    sheet = Image.new("RGB", (columns * tile_width, rows * tile_height), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, (caption, crop) in enumerate(entries):
        column, row = index % columns, index // columns
        left, top = column * tile_width, row * tile_height
        draw.text((left + 6, top + 5), caption, fill="black", font=font)
        available = (tile_width - 12, tile_height - 26)
        crop.thumbnail(available, Image.Resampling.LANCZOS)
        x = left + (tile_width - crop.width) // 2
        y = top + 22 + (available[1] - crop.height) // 2
        sheet.paste(crop, (x, y))
        draw.rectangle((left, top, left + tile_width - 1, top + tile_height - 1), outline="#b8cccc")
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, quality=92, subsampling=0)


def load_layouts() -> tuple[dict[str, list[dict]], int, float]:
    by_kind: dict[str, list[dict]] = defaultdict(list)
    geometry_count = 0
    boundary_crossing_count = 0
    minimum_gap = float("inf")
    for paper in range(1, 51):
        path = WORK / "generated" / f"paper-{paper:02d}" / "layout-report.json"
        layout = json.loads(path.read_text(encoding="utf-8"))
        visuals = layout["diagram_visuals"]
        geometry = layout["diagram_geometry_checks"]
        if len(visuals) != 20 or len(geometry) != 29:
            raise RuntimeError(f"paper {paper}: incomplete diagram audit")
        if any(entry["actual_gap"] < entry["minimum_gap"] for entry in geometry):
            raise RuntimeError(f"paper {paper}: diagram label geometry failure")
        crossings = layout.get("diagram_boundary_crossings", [])
        if crossings:
            raise RuntimeError(f"paper {paper}: diagram boundary failure: {crossings[:3]}")
        geometry_count += len(geometry)
        boundary_crossing_count += len(crossings)
        minimum_gap = min(minimum_gap, *(entry["actual_gap"] for entry in geometry))
        for entry in visuals:
            by_kind[entry["kind"]].append({"paper": paper, **entry})
    if set(by_kind) != EXPECTED_KINDS:
        raise RuntimeError(f"diagram-kind mismatch: {sorted(by_kind)}")
    if any(len(entries) != 50 for entries in by_kind.values()):
        raise RuntimeError("each diagram kind must occur exactly 50 times")
    return by_kind, geometry_count, boundary_crossing_count, minimum_gap


def build_standard(by_kind: dict[str, list[dict]]) -> list[str]:
    directory = AUDIT_BUILD / "standard"
    outputs = []
    for kind, visuals in sorted(by_kind.items()):
        entries = []
        for visual in sorted(visuals, key=lambda item: item["paper"]):
            image_path = BUILD / f"paper-{visual['paper']:02d}" / "rendered" / f"page-{visual['page']:02d}.png"
            image = Image.open(image_path).convert("RGB")
            crop = fit_crop(image, visual["rect"], image.width / A4_WIDTH, image.height / A4_HEIGHT)
            entries.append((f"p{visual['paper']:02d} {visual['label']}", crop))
        output = directory / f"{kind}.jpg"
        make_sheet(entries, output)
        outputs.append(str(output.relative_to(ROOT)))
    return outputs


def build_two_up(by_kind: dict[str, list[dict]]) -> list[str]:
    directory = AUDIT_BUILD / "two-up"
    outputs = []
    for kind, visuals in sorted(by_kind.items()):
        entries = []
        for visual in sorted(visuals, key=lambda item: item["paper"]):
            sheet_number = (visual["page"] + 1) // 2
            image_path = BUILD / "2up-a4" / f"p{visual['paper']:02d}" / f"s{sheet_number:02d}.png"
            image = Image.open(image_path).convert("RGB")
            crop = fit_two_up_crop(image, visual["page"], visual["rect"])
            entries.append((f"p{visual['paper']:02d} {visual['label']}", crop))
        output = directory / f"{kind}.jpg"
        make_sheet(entries, output)
        outputs.append(str(output.relative_to(ROOT)))
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["standard", "two-up", "all"], default="all")
    args = parser.parse_args()
    by_kind, geometry_count, boundary_crossing_count, minimum_gap = load_layouts()
    standard_outputs = build_standard(by_kind) if args.mode in {"standard", "all"} else []
    two_up_outputs = build_two_up(by_kind) if args.mode in {"two-up", "all"} else []
    two_up_boundary_crossings = 0
    if args.mode in {"two-up", "all"}:
        two_up_report = json.loads((WORK / "2up-validation.json").read_text(encoding="utf-8"))
        two_up_boundary_crossings = sum(entry["diagram_boundary_crossings"] for entry in two_up_report["papers"])
        if two_up_boundary_crossings:
            raise RuntimeError(f"two-up diagram boundary failures: {two_up_boundary_crossings}")
    report = {
        "status": "passed",
        "papers": 50,
        "diagram_kinds": len(by_kind),
        "standard_diagram_regions": sum(len(entries) for entries in by_kind.values()),
        "two_up_diagram_regions": sum(len(entries) for entries in by_kind.values()) if two_up_outputs else 0,
        "diagram_geometry_checks": geometry_count,
        "standard_boundary_crossings": boundary_crossing_count,
        "two_up_boundary_crossings": two_up_boundary_crossings,
        "minimum_diagram_geometry_gap": minimum_gap,
        "standard_contact_sheets": standard_outputs,
        "two_up_contact_sheets": two_up_outputs,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
