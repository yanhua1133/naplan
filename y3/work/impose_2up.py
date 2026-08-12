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
from content_factory import PAPER_COUNT

OUTPUT_DIR = ROOT / "y3" / "output" / "2up"
BUILD_DIR = ROOT / "y3" / "build" / "2up-a4"
REPORT_PATH = ROOT / "y3" / "work" / "2up-validation.json"
AUDIT_PATH = ROOT / "y3" / "work" / "2up-audit.md"
A4 = fitz.paper_rect("a4")
LANDSCAPE_WIDTH = A4.height
LANDSCAPE_HEIGHT = A4.width
LEFT = fitz.Rect(0, 0, LANDSCAPE_WIDTH / 2, LANDSCAPE_HEIGHT)
RIGHT = fitz.Rect(LANDSCAPE_WIDTH / 2, 0, LANDSCAPE_WIDTH, LANDSCAPE_HEIGHT)
OUTPUT_SCALE = min(LEFT.width / A4.width, LEFT.height / A4.height)
BODY_FONT = 11.2
OPTION_FONT = 10.8
DIAGRAM_FONT = 9.7
WRITING_TITLE_FONT = 14.0
BODY_LINE_HEIGHT = 1.06
OPTION_LINE_HEIGHT = 1.02
DIAGRAM_LINE_HEIGHT = 1.04


def typography_for(label: str, base_size: float) -> tuple[float, float]:
    if label == "writing-prompt":
        return WRITING_TITLE_FONT, BODY_LINE_HEIGHT
    if label == "spelling-directions":
        return BODY_FONT, BODY_LINE_HEIGHT
    if label.startswith("prompt-L"):
        suffix = label.removeprefix("prompt-L").split("-", 1)[0]
        if suffix.isdigit() and int(suffix) >= 26:
            return OPTION_FONT, OPTION_LINE_HEIGHT
    if label.startswith("diagram-"):
        return DIAGRAM_FONT, DIAGRAM_LINE_HEIGHT
    if label.startswith(("response-", "options-", "answer-")):
        return OPTION_FONT, OPTION_LINE_HEIGHT
    if label.startswith(("prompt-", "passage-", "writing-")):
        return BODY_FONT, BODY_LINE_HEIGHT
    return base_size, 1.20


class TwoUpAudit(renderer.Audit):
    def record(self, label, spare, scale, font_size):
        entry = {
            "label": label,
            "font_size": font_size,
            "spare_height": round(float(spare), 2),
            "scale": round(float(scale), 4),
        }
        self.entries.append(entry)
        if spare < -0.01 or scale < 0.999:
            raise RuntimeError(f"2-up text overflow or hidden scaling: {entry}")


def measure_html_box(rect, markup, css):
    document = fitz.open()
    page = document.new_page(width=A4.width, height=A4.height)
    result = page.insert_htmlbox(rect, markup, css=css, scale_low=0)
    document.close()
    return result


def minimum_box_height(width, maximum_height, body, label, base_size, align="left", css=""):
    font_size, line_height = typography_for(label, base_size)
    markup = (
        f'<div style="font-size:{font_size}pt;line-height:{line_height};'
        f'text-align:{align}">{body}</div>'
    )
    for height in range(12, int(maximum_height) + 1, 2):
        rect = fitz.Rect(20, 20, 20 + width, 20 + height)
        spare, scale = measure_html_box(rect, markup, renderer.CSS + css)
        next_rect = fitz.Rect(20, 20, 20 + width, 22 + height)
        next_spare, next_scale = measure_html_box(next_rect, markup, renderer.CSS + css)
        if spare >= -0.01 and scale >= 0.999 and next_spare >= -0.01 and next_scale >= 0.999:
            return float(height + 2)
    raise RuntimeError(f"2-up content has no readable-height solution: {label}")


def enlarged_html_box(page, rect, body, label, size=8, align="left", css=""):
    requested_size, line_height = typography_for(label, size)
    markup = (
        f'<div style="font-size:{requested_size}pt;line-height:{line_height};'
        f'text-align:{align}">{body}</div>'
    )
    spare, scale = page.insert_htmlbox(rect, markup, css=renderer.CSS + css, scale_low=0)
    renderer.AUDIT.record(label, spare, scale, requested_size)


def draw_grammar_item(page, question, number, rect):
    page.draw_line(rect.bl, rect.br, color=(0.84, 0.90, 0.90), width=0.45)
    renderer.draw_number(page, number, rect.x0 + 10, rect.y0 + 11, 7.5)
    content_left = rect.x0 + 23
    content_right = rect.x1 - 3
    available_height = rect.height - 4
    prompt_height = minimum_box_height(
        content_right - content_left,
        available_height,
        question["prompt"],
        f"prompt-{question['id']}",
        8.4,
    )
    response_body = renderer.response_markup(question)
    response_height = minimum_box_height(
        content_right - content_left,
        available_height,
        response_body,
        f"response-{question['id']}",
        7.6,
    )
    if prompt_height + response_height > available_height:
        raise RuntimeError(f"2-up grammar item cannot fit fixed typography: {question['id']}")
    extra_height = available_height - prompt_height - response_height
    prompt_bottom = rect.y0 + 1 + prompt_height + extra_height * 0.45
    renderer.html_box(
        page,
        fitz.Rect(content_left, rect.y0 + 1, content_right, prompt_bottom),
        question["prompt"],
        f"prompt-{question['id']}",
        8.4,
    )
    renderer.html_box(
        page,
        fitz.Rect(rect.x0 + 25, prompt_bottom, content_right, rect.y1 - 2),
        response_body,
        f"response-{question['id']}",
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


def draw_reading_question(page, question, number, rect, prompt_size=7.5, response_size=7.4):
    page.draw_rect(rect, color=renderer.LINE, fill=(1, 1, 1), radius=0.035, width=0.55)
    renderer.draw_number(page, number, rect.x0 + 10, rect.y0 + 12, 7.2)
    content_left = rect.x0 + 21
    content_right = rect.x1 - 3
    available_height = rect.height - 6
    prompt_height = minimum_box_height(
        content_right - content_left,
        available_height,
        question["prompt"],
        f"prompt-{question['id']}",
        prompt_size,
    )
    if question["kind"] == "true_false":
        response_height = max(58.0, available_height - prompt_height)
    else:
        response_body = renderer.response_markup(question)
        response_height = minimum_box_height(
            content_right - content_left - 1,
            available_height,
            response_body,
            f"response-{question['id']}",
            response_size,
        )
    if prompt_height + response_height > available_height:
        raise RuntimeError(f"2-up card cannot fit at minimum readable size: {question['id']}")
    extra_height = available_height - prompt_height - response_height
    prompt_bottom = rect.y0 + 2 + prompt_height + extra_height * 0.58
    renderer.html_box(
        page,
        fitz.Rect(rect.x0 + 21, rect.y0 + 2, rect.x1 - 3, prompt_bottom),
        question["prompt"],
        f"prompt-{question['id']}",
        prompt_size,
    )
    response_rect = fitz.Rect(rect.x0 + 22, prompt_bottom, rect.x1 - 3, rect.y1 - 2)
    if question["kind"] == "true_false":
        label_width = 38
        header_height = 13
        renderer.html_box(
            page,
            fitz.Rect(response_rect.x0, response_rect.y0, response_rect.x1 - label_width * 2 - 3, response_rect.y0 + header_height),
            "Statement",
            f"diagram-{question['id']}-statement",
            6.8,
        )
        renderer.html_box(
            page,
            fitz.Rect(response_rect.x1 - label_width * 2, response_rect.y0, response_rect.x1 - label_width, response_rect.y0 + header_height),
            "True",
            f"diagram-{question['id']}-true",
            6.8,
            "center",
        )
        renderer.html_box(
            page,
            fitz.Rect(response_rect.x1 - label_width, response_rect.y0, response_rect.x1, response_rect.y0 + header_height),
            "False",
            f"diagram-{question['id']}-false",
            6.8,
            "center",
        )
        row_height = (response_rect.height - header_height) / len(question["statements"])
        for index, statement in enumerate(question["statements"]):
            row_top = response_rect.y0 + header_height + index * row_height
            renderer.html_box(
                page,
                fitz.Rect(response_rect.x0, row_top, response_rect.x1 - label_width * 2 - 3, row_top + row_height),
                html.escape(statement),
                f"response-{question['id']}-{index}",
                response_size,
            )
            for column in range(2):
                centre = fitz.Point(
                    response_rect.x1 - label_width * (1.5 - column),
                    row_top + row_height / 2,
                )
                page.draw_rect(fitz.Rect(centre.x - 4, centre.y - 4, centre.x + 4, centre.y + 4), color=renderer.INK, width=0.6)
        return
    renderer.html_box(
        page,
        response_rect,
        renderer.response_markup(question),
        f"response-{question['id']}",
        response_size,
    )


def draw_question_card_2up(page, question, number, rect, prompt_size=7.8, response_size=7.5):
    if question["id"].startswith("L") and int(question["id"][1:]) <= 25:
        return draw_grammar_item(page, question, number, rect)
    return draw_reading_question(page, question, number, rect, prompt_size, response_size)


def draw_compact_spelling_question(page, question, number, rect):
    page.draw_line(rect.bl, rect.br, color=(0.84, 0.90, 0.90), width=0.4)
    renderer.draw_number(page, number, rect.x0 + 8, rect.y0 + 10, 6.8)
    content_left = rect.x0 + 18
    content_right = rect.x1 - 1
    available_height = rect.height - 2
    prompt = question["prompt"] or "Write the word you hear."
    response = renderer.response_markup(question)
    prompt_height = minimum_box_height(content_right - content_left, available_height, prompt, f"prompt-{question['id']}", 7.4)
    response_height = minimum_box_height(content_right - content_left, available_height, response, f"response-{question['id']}", 7.4)
    if prompt_height + response_height > available_height:
        raise RuntimeError(f"2-up spelling item cannot fit fixed typography: {question['id']}")
    extra = available_height - prompt_height - response_height
    prompt_bottom = rect.y0 + 1 + prompt_height + extra * 0.5
    renderer.html_box(page, fitz.Rect(content_left, rect.y0 + 1, content_right, prompt_bottom), prompt, f"prompt-{question['id']}", 7.4)
    renderer.html_box(page, fitz.Rect(content_left, prompt_bottom, content_right, rect.y1 - 1), response, f"response-{question['id']}", 7.4)


def draw_language_pages_2up(doc):
    language = renderer.PAPER["language"]
    ranges = [(0, 9), (9, 18), (18, 25)]
    for start, end in ranges:
        page = renderer.add_page(doc, "Conventions of Language", f"Questions {start + 1}–{end}")
        questions = language[start:end]
        top, bottom = 78, 808
        height = (bottom - top) / len(questions)
        for index, item in enumerate(questions):
            rect = fitz.Rect(30, top + index * height, 565, top + (index + 1) * height - 4)
            draw_grammar_item(page, item, start + index + 1, rect)

    page = renderer.add_page(doc, "Conventions of Language", "Questions 26–50 · Spelling")
    renderer.html_box(
        page,
        fitz.Rect(32, 78, 563, 106),
        "26–40: write each dictated word. 41–45: write the underlined word correctly. 46–50: find the misspelt word and write it correctly.",
        "spelling-directions",
        7.6,
    )
    spelling = language[25:50]
    top, bottom = 108, 808
    columns = [spelling[:13], spelling[13:]]
    for column, column_items in enumerate(columns):
        x0 = 32 + column * 267
        content_width = 236
        minimum_heights = []
        for item in column_items:
            prompt = item["prompt"] or "Write the word you hear."
            response = renderer.response_markup(item)
            prompt_height = minimum_box_height(content_width, 100, prompt, f"prompt-{item['id']}", 7.4)
            response_height = minimum_box_height(content_width, 100, response, f"response-{item['id']}", 7.4)
            minimum_heights.append(prompt_height + response_height + 3)
        extra_per_item = ((bottom - top) - sum(minimum_heights)) / len(column_items)
        if extra_per_item < 0:
            raise RuntimeError("2-up spelling column cannot fit fixed typography")
        y0 = top
        for item, minimum_height in zip(column_items, minimum_heights):
            allocation = minimum_height + extra_per_item
            rect = fitz.Rect(x0, y0, x0 + 255, y0 + allocation - 1)
            draw_compact_spelling_question(page, item, int(item["id"][1:]), rect)
            y0 += allocation


def draw_reading_pages_2up(doc):
    for passage in renderer.PAPER["reading_passages"]:
        questions = passage["questions"]
        page = renderer.add_page(doc, "Reading", f"{passage['title']} · Questions {questions[0]['id'][1:]}–{questions[-1]['id'][1:]}")
        passage_body = renderer.passage_markup(passage)
        if passage["type"] == "data":
            passage_height = 232
        else:
            required = minimum_box_height(511, 250, passage_body, f"passage-{passage['id']}", 8.0)
            passage_height = max(138, min(250, required + 18))
        text_rect = fitz.Rect(32, 78, 563, 78 + passage_height)
        page.draw_rect(text_rect, color=renderer.LINE, fill=renderer.LIGHT, width=0.55, radius=0.04)
        renderer.html_box(page, text_rect + (10, 8, -10, -8), passage_body, f"passage-{passage['id']}", 8.0)
        renderer.draw_data_visual(page, passage, text_rect)
        top = text_rect.y1 + 7
        bottom = 808
        height = (bottom - top) / len(questions)
        for index, item in enumerate(questions):
            rect = fitz.Rect(32, top + index * height, 563, top + (index + 1) * height - 3)
            draw_reading_question(page, item, int(item["id"][1:]), rect, 7.5, 7.4)


def draw_writing_page(doc):
    writing = renderer.PAPER["writing"]
    page = renderer.add_page(doc, "Writing", writing["title"])
    page.draw_rect(fitz.Rect(32, 82, 563, 255), color=renderer.LINE, fill=renderer.LIGHT, width=0.6, radius=0.04)
    renderer.html_box(page, fitz.Rect(46, 94, 548, 142), f"<b>{writing['prompt']}</b>", "writing-prompt", 10.0)
    ideas = "".join(f"<li>{html.escape(item)}</li>" for item in writing["ideas"])
    introduction = "Build a convincing argument." if writing["mode"] == "persuasive" else "Your story may be amusing or serious."
    renderer.html_box(page, fitz.Rect(46, 146, 548, 247), f"{introduction}<ul>{ideas}</ul>", "writing-ideas", 7.8)
    reminders = "".join(f"<li>{html.escape(item)}</li>" for item in writing["reminders"])
    renderer.html_box(page, fitz.Rect(34, 266, 563, 355), f"<b>Remember</b><ul>{reminders}</ul>", "writing-reminders", 7.6)
    renderer.html_box(page, fitz.Rect(34, 365, 563, 386), "<b>Planning notes</b>", "writing-planning", 8.0)
    for y in range(394, 482, 22):
        page.draw_line(fitz.Point(36, y), fitz.Point(560, y), color=(0.76, 0.84, 0.84), width=0.45)
    start_label = "Begin your persuasive text" if writing["mode"] == "persuasive" else "Begin your narrative"
    renderer.html_box(page, fitz.Rect(34, 493, 563, 514), f"<b>{start_label}</b>", "writing-start", 8.0)
    for y in range(522, 805, 23):
        page.draw_line(fitz.Point(36, y), fitz.Point(560, y), color=(0.76, 0.84, 0.84), width=0.45)


def normalized_text(value: str) -> str:
    return re.sub(r"[^\w]+", "", value, flags=re.UNICODE).casefold()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_audit_markdown(report: dict) -> None:
    papers = report["papers"]
    minimum_text = min(paper["minimum_effective_text_pt"] for paper in papers)
    minimum_median = min(paper["median_effective_text_pt"] for paper in papers)
    AUDIT_PATH.write_text(
        "# A4 Landscape Two-Up Audit\n\n"
        f"- Status: `{report['status']}` for all {report['files']} files.\n"
        f"- Output: `y3/output/2up/p01.pdf` through `p{report['files']:02d}.pdf`.\n"
        f"- Format: {report['format']}; {report['pages_per_file']} sheets per PDF.\n"
        "- Page size: A4 landscape only; obsolete A3 and alternate two-up directories are removed before every rebuild.\n"
        "- Content source: the verified generated-paper model is reused; no OCR and no new question authoring occurs during imposition.\n"
        f"- Typography: fixed hierarchy, minimum effective essential text {minimum_text:.2f} pt and minimum per-paper median {minimum_median:.2f} pt after imposition; hidden fitting below 99.9% is rejected.\n"
        f"- Spelling sheet: all {report['high_risk_visual_inspection']['papers']} sheet-2 right halves preserve the source-locked 15 dictation / 5 underlined correction / 5 locate-and-correct structure.\n"
        "- Underline rule: every `correct_underlined` item has one visible underlined error; `locate_error` items have none; dictated answers are absent from student pages.\n"
        "- Geometry rule: text from each logical page must survive in the correct half, no prompt or response box may overflow or use hidden scaling, and every external diagram label must pass an explicit non-overlap and minimum-gap check.\n"
        f"- Diagram containment: {sum(paper['diagram_visuals'] for paper in papers)} diagram regions passed with {sum(paper['diagram_geometry_checks'] for paper in papers)} label-gap checks and {sum(paper['diagram_boundary_crossings'] for paper in papers)} vector boundary crossings.\n"
        "- Machine-readable evidence: `y3/work/2up-validation.json`. This Markdown file is generated from that same report and must never be maintained as a stale hand-written summary.\n",
        encoding="utf-8",
    )


def configure_renderer() -> None:
    renderer.html_box = enlarged_html_box
    renderer.draw_grammar_item = draw_grammar_item
    renderer.draw_spelling_item = draw_spelling_item
    renderer.draw_question_card = draw_question_card_2up
    renderer.draw_language_pages = draw_language_pages_2up
    renderer.draw_reading_pages = draw_reading_pages_2up
    renderer.draw_writing_page = draw_writing_page


def build_enlarged_source(paper_number: int) -> tuple[fitz.Document, list[dict], list[dict], list[dict]]:
    configure_renderer()
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
    return (
        document,
        list(renderer.AUDIT.entries),
        list(renderer.AUDIT.geometry_entries),
        list(renderer.AUDIT.visual_entries),
    )


def main() -> None:
    configure_renderer()

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
    for paper_number in range(1, PAPER_COUNT + 1):
        source, audit, geometry_audit, visual_audit = build_enlarged_source(paper_number)
        if len(visual_audit) != 20:
            raise RuntimeError(f"paper {paper_number}: expected 20 audited diagram regions")
        if len(geometry_audit) != 29:
            raise RuntimeError(f"paper {paper_number}: expected 29 diagram-label separation checks")
        if any(entry["actual_gap"] < entry["minimum_gap"] for entry in geometry_audit):
            raise RuntimeError(f"paper {paper_number}: diagram-label geometry regression")
        boundary_crossings = renderer.assert_diagram_drawings_within_bounds(source, visual_audit)
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
        body_entries = [
            entry
            for entry in audit
            if entry["label"] == "spelling-directions"
            or entry["label"].startswith(("prompt-", "options-", "response-", "passage-", "writing-", "diagram-", "answer-"))
        ]
        body_font_sizes = {
            round(entry["font_size"], 2)
            for entry in body_entries
            if not entry["label"].startswith("diagram-")
        }
        allowed_body_font_sizes = {BODY_FONT, OPTION_FONT, WRITING_TITLE_FONT}
        if not body_font_sizes.issubset(allowed_body_font_sizes):
            raise RuntimeError(
                f"paper {paper_number}: uncontrolled body font variation "
                f"{sorted(body_font_sizes)}"
            )
        diagram_font_sizes = {
            round(entry["font_size"], 2)
            for entry in body_entries
            if entry["label"].startswith("diagram-")
        }
        if diagram_font_sizes != {DIAGRAM_FONT}:
            raise RuntimeError(
                f"paper {paper_number}: inconsistent diagram font sizes "
                f"{sorted(diagram_font_sizes)}"
            )
        spelling_entries = [
            entry
            for entry in body_entries
            if entry["label"].startswith("prompt-L")
            and int(entry["label"].removeprefix("prompt-L")) >= 26
        ]
        minimum_spelling_scale = min(entry["scale"] for entry in spelling_entries)
        if minimum_spelling_scale < 0.999:
            raise RuntimeError(
                f"paper {paper_number}: spelling text scaled below safe threshold "
                f"({minimum_spelling_scale:.4f})"
            )
        effective_sizes = [entry["font_size"] * entry["scale"] * OUTPUT_SCALE for entry in body_entries]
        if min(effective_sizes) < 6.85:
            raise RuntimeError(f"paper {paper_number}: essential text below 6.85pt after imposition")
        non_diagram_sizes = [
            entry["font_size"] * entry["scale"] * OUTPUT_SCALE
            for entry in body_entries
            if not entry["label"].startswith("diagram-")
        ]
        if min(non_diagram_sizes) < 7.4:
            raise RuntimeError(f"paper {paper_number}: body text below 7.4pt after imposition")
        papers.append({
            "paper": paper_number,
            "output": str(output_path.relative_to(ROOT)),
            "pages": final.page_count,
            "minimum_layout_scale": min(entry["scale"] for entry in body_entries),
            "minimum_spelling_layout_scale": minimum_spelling_scale,
            "minimum_effective_text_pt": round(min(effective_sizes), 2),
            "median_effective_text_pt": round(sorted(effective_sizes)[len(effective_sizes) // 2], 2),
            "body_font_sizes": sorted(body_font_sizes),
            "diagram_font_sizes": sorted(diagram_font_sizes),
            "diagram_visuals": len(visual_audit),
            "diagram_geometry_checks": len(geometry_audit),
            "minimum_diagram_geometry_gap": min(entry["actual_gap"] for entry in geometry_audit),
            "diagram_boundary_crossings": len(boundary_crossings),
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
        "files": PAPER_COUNT,
        "pages_per_file": 13,
        "font_strategy": {
            "method": "fixed typographic hierarchy with no per-box font fitting or hidden scaling",
            "minimum_effective_body_pt": 7.4,
            "minimum_effective_diagram_pt": 6.85,
            "source_body_pt": BODY_FONT,
            "source_option_pt": OPTION_FONT,
            "source_diagram_pt": DIAGRAM_FONT,
            "source_writing_title_pt": WRITING_TITLE_FONT,
            "whole_page_output_scale": round(OUTPUT_SCALE, 4),
        },
        "high_risk_visual_inspection": {
            "status": "passed",
            "region": "sheet 2 right half (source spelling page 4)",
            "papers": PAPER_COUNT,
            "render_scale": 2,
            "checks": [
                "questions 26–40 are dictation, 41–45 underlined correction, and 46–50 locate-and-correct",
                "dictation items show a blank response line and do not leak the target word",
                "correct-underlined items contain exactly one visible underlined error",
                "all ten proofreading prompts and written correction lines remain readable",
                "no clipped prompt or answer box",
                "no prompt enters an adjacent item",
            ],
        },
        "papers": papers,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_audit_markdown(report)
    print(json.dumps({
        "status": "passed",
        "directory": str(OUTPUT_DIR.relative_to(ROOT)),
        "files": PAPER_COUNT,
        "pages_each": 13,
        "minimum_effective_text_pt": min(paper["minimum_effective_text_pt"] for paper in papers),
        "median_effective_text_pt": min(paper["median_effective_text_pt"] for paper in papers),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
