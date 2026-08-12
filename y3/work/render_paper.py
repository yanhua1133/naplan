from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import sys
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content_factory import PAPER_COUNT, build_paper


ROOT = Path(__file__).resolve().parents[2]
SOURCE_HASHES = ROOT / "y3" / "source-cache" / "source-hashes.json"
A4 = fitz.paper_rect("a4")
INK = (0.06, 0.18, 0.21)
TEAL = (0.03, 0.42, 0.47)
PALE = (0.84, 0.95, 0.94)
LIGHT = (0.96, 0.99, 0.99)
LINE = (0.52, 0.72, 0.72)
MIN_BODY_FONT = 7.4
MIN_DIAGRAM_FONT = 6.8
MIN_APPENDIX_FONT = 7.4
CSS = """
* { font-family: Arial, Helvetica, sans-serif; color: #16343a; }
p { margin: 0 0 3pt 0; line-height: 1.22; }
strong { color: #103f46; }
em { color: #244f55; }
table { border-collapse: collapse; width: 100%; }
td, th { vertical-align: top; }
ul, ol { margin: 1pt 0 2pt 13pt; padding: 0; }
li { margin-bottom: 1.5pt; line-height: 1.18; }
"""

PAPER = None
PAPER_NUMBER = None
OUTPUT = None
RENDER_DIR = None
LAYOUT_REPORT = None
INVENTORY = None


class Audit:
    def __init__(self):
        self.entries = []
        self.geometry_entries = []
        self.visual_entries = []

    def record(self, label, spare, scale, font_size):
        entry = {
            "label": label,
            "font_size": font_size,
            "spare_height": round(float(spare), 2),
            "scale": round(float(scale), 4),
        }
        self.entries.append(entry)
        if spare < -0.01 or scale < 0.999:
            raise RuntimeError(f"Text overflow or scaling: {entry}")

    def record_visual(self, label, kind, page_number, rect):
        self.visual_entries.append({
            "label": label,
            "kind": kind,
            "page": page_number,
            "rect": [round(value, 2) for value in fitz.Rect(rect)],
        })

    def record_geometry_gap(self, label, shape_rect, text_rect, minimum_gap=1.0):
        shape_rect = fitz.Rect(shape_rect)
        text_rect = fitz.Rect(text_rect)
        intersection = shape_rect & text_rect
        horizontal_overlap = min(shape_rect.x1, text_rect.x1) - max(shape_rect.x0, text_rect.x0)
        vertical_overlap = min(shape_rect.y1, text_rect.y1) - max(shape_rect.y0, text_rect.y0)
        if not intersection.is_empty:
            gap = -min(intersection.width, intersection.height)
        elif horizontal_overlap > 0:
            gap = max(text_rect.y0 - shape_rect.y1, shape_rect.y0 - text_rect.y1)
        elif vertical_overlap > 0:
            gap = max(text_rect.x0 - shape_rect.x1, shape_rect.x0 - text_rect.x1)
        else:
            horizontal_gap = max(shape_rect.x0 - text_rect.x1, text_rect.x0 - shape_rect.x1, 0)
            vertical_gap = max(shape_rect.y0 - text_rect.y1, text_rect.y0 - shape_rect.y1, 0)
            gap = math.hypot(horizontal_gap, vertical_gap)
        entry = {
            "label": label,
            "shape_rect": [round(value, 2) for value in shape_rect],
            "text_rect": [round(value, 2) for value in text_rect],
            "minimum_gap": round(float(minimum_gap), 2),
            "actual_gap": round(float(gap), 2),
        }
        self.geometry_entries.append(entry)
        if gap < minimum_gap:
            raise RuntimeError(f"Diagram label overlaps or crowds geometry: {entry}")


AUDIT = Audit()


def configure(paper_number):
    global PAPER, PAPER_NUMBER, OUTPUT, RENDER_DIR, LAYOUT_REPORT, INVENTORY, AUDIT
    PAPER_NUMBER = paper_number
    PAPER = build_paper(paper_number)
    OUTPUT = ROOT / "y3" / "output" / f"year3-naplan-style-practice-paper-{paper_number:02d}.pdf"
    RENDER_DIR = ROOT / "y3" / "build" / f"paper-{paper_number:02d}" / "rendered"
    work_dir = ROOT / "y3" / "work" / "generated" / f"paper-{paper_number:02d}"
    work_dir.mkdir(parents=True, exist_ok=True)
    LAYOUT_REPORT = work_dir / "layout-report.json"
    INVENTORY = work_dir / "question-inventory.json"
    AUDIT = Audit()


def html_box(page, rect, body, label, size=8.0, align="left", css=""):
    markup = f'<div style="font-size:{size}pt;line-height:1.20;text-align:{align}">{body}</div>'
    spare, scale = page.insert_htmlbox(rect, markup, css=CSS + css, scale_low=1)
    AUDIT.record(label, spare, scale, size)


def add_page(doc, section, title):
    page = doc.new_page(width=A4.width, height=A4.height)
    page_number = len(doc)
    page.draw_rect(fitz.Rect(26, 20, 569, 48), color=None, fill=PALE, radius=0.12)
    page.draw_rect(fitz.Rect(32, 27, 76, 43), color=None, fill=TEAL, radius=0.45)
    html_box(page, fitz.Rect(35, 29, 73, 41), '<b style="color:white">Year 3</b>', f"year-{page_number}", 7.1, "center")
    html_box(page, fitz.Rect(84, 27, 360, 43), f"<b>{section}</b>", f"section-{page_number}", 8.6)
    html_box(page, fitz.Rect(420, 27, 562, 43), f"Practice Paper {PAPER_NUMBER:02d}", f"paper-{page_number}", 7.5, "right")
    html_box(page, fitz.Rect(30, 51, 565, 70), f"<b>{title}</b>", f"title-{page_number}", 10.2)
    page.draw_line(fitz.Point(27, 816), fitz.Point(568, 816), color=LINE, width=0.55)
    html_box(page, fitz.Rect(30, 820, 430, 833), "Independent NAPLAN-style practice material", f"footer-{page_number}", 6.8)
    html_box(page, fitz.Rect(530, 820, 563, 833), str(page_number), f"page-{page_number}", 6.8, "right")
    return page


def draw_number(page, number, x, y, radius=7.5):
    page.draw_circle(fitz.Point(x, y), radius, color=None, fill=TEAL)
    html_box(page, fitz.Rect(x - radius, y - 4.7, x + radius, y + 5), f'<b style="color:white">{number}</b>', f"qnum-{number}-{x}-{y}", 6.3, "center")


def option_markup(options, columns=2, checkboxes=False):
    cells = []
    for index, option in enumerate(options):
        marker = "□" if checkboxes else f"<b>{chr(65 + index)}</b>"
        cells.append(f'<td style="width:{100/columns:.1f}%;padding:1pt 4pt 1pt 0">{marker}&nbsp;{html.escape(str(option))}</td>')
    rows = []
    for start in range(0, len(cells), columns):
        row = cells[start:start + columns]
        row += ["<td></td>"] * (columns - len(row))
        rows.append("<tr>" + "".join(row) + "</tr>")
    return "<table>" + "".join(rows) + "</table>"


def response_markup(question):
    kind = question["kind"]
    if kind == "mcq":
        columns = 2 if len(question["options"]) <= 4 else 3
        return option_markup(question["options"], columns)
    if kind in {"circle", "open", "spelling", "dictation"}:
        return '<div style="margin-top:4pt;border-bottom:1px solid #87aaaa;height:13pt"></div>'
    if kind == "cloze":
        words = " &nbsp; • &nbsp; ".join(html.escape(str(word)) for word in question["word_bank"])
        return f'<div style="border:1px solid #87aaaa;padding:3pt"><b>Word box:</b> {words}</div>'
    if kind == "true_false":
        rows = ["<tr><th>Statement</th><th>True</th><th>False</th></tr>"]
        for statement in question["statements"]:
            rows.append(f"<tr><td>{html.escape(statement)}</td><td>□</td><td>□</td></tr>")
        return '<table border="1" cellpadding="2">' + "".join(rows) + "</table>"
    if kind == "order":
        return "<table>" + "".join(f'<tr><td style="width:10%">___</td><td>{html.escape(choice)}</td></tr>' for choice in question["choices"]) + "</table>"
    if kind == "match":
        left = " &nbsp; ".join(f"{html.escape(value)} ___" for value in question["left"])
        right = " &nbsp; ".join(f"<b>{chr(65 + index)}</b> {html.escape(value)}" for index, value in enumerate(question["right"]))
        return f"<p>{left}</p><p>{right}</p>"
    if kind == "select_two":
        return option_markup(question["options"], 2 if len(question["options"]) <= 4 else 3, checkboxes=True)
    raise ValueError(f"Unknown question kind: {kind}")


def draw_question_card(page, question, number, rect, prompt_size=7.8, response_size=7.5):
    page.draw_rect(rect, color=(0.84, 0.90, 0.90), fill=LIGHT, width=0.45, radius=0.04)
    draw_number(page, number, rect.x0 + 10, rect.y0 + 12)
    body = (question["prompt"] or "Write the word you hear.") + '<div style="margin-top:3pt">' + response_markup(question) + "</div>"
    html_box(page, fitz.Rect(rect.x0 + 23, rect.y0 + 4, rect.x1 - 4, rect.y1 - 4), body, f"prompt-{question['id']}", min(prompt_size, response_size))


def draw_language_pages(doc):
    language = PAPER["language"]
    ranges = [(0, 9), (9, 18), (18, 25)]
    for start, end in ranges:
        page = add_page(doc, "Conventions of Language", f"Questions {start + 1}–{end}")
        questions = language[start:end]
        top, bottom = 78, 808
        height = (bottom - top) / len(questions)
        for index, item in enumerate(questions):
            rect = fitz.Rect(30, top + index * height, 565, top + (index + 1) * height - 4)
            draw_question_card(page, item, start + index + 1, rect, 7.8, 7.4)

    page = add_page(doc, "Conventions of Language", "Questions 26–50 · Spelling")
    html_box(
        page,
        fitz.Rect(32, 78, 563, 106),
        "26–40: write each dictated word. 41–45: write the underlined word correctly. 46–50: find the misspelt word and write it correctly.",
        "spelling-directions",
        7.6,
    )
    spelling = language[25:50]
    rows = 13
    top, bottom = 108, 808
    row_height = (bottom - top) / rows
    for index, item in enumerate(spelling):
        column = index // rows
        row = index % rows
        x0 = 32 + column * 267
        rect = fitz.Rect(x0, top + row * row_height, x0 + 255, top + (row + 1) * row_height - 3)
        draw_question_card(page, item, index + 26, rect, 7.4, 7.4)


def passage_markup(passage):
    if passage["type"] == "procedure":
        steps = "".join(f"<li>{html.escape(step)}</li>" for step in passage["steps"])
        return f"<p>{html.escape(passage['intro'])}</p><ol>{steps}</ol>"
    if passage["type"] == "poem":
        return "<p>" + "<br>".join(html.escape(line) for line in passage["lines"]) + "</p>"
    return passage.get("text", "")


def draw_data_visual(page, passage, rect):
    if passage["type"] != "data":
        return
    labels = passage["data"]["labels"]
    values = passage["data"]["values"]
    max_value = max(values)
    table_rect = fitz.Rect(rect.x0 + 8, rect.y1 - 96, rect.x0 + 238, rect.y1 - 8)
    tally_rows = []
    for label, value in zip(labels, values):
        groups, remainder = divmod(value, 5)
        tally = " ".join(["||||/"] * groups + (["|" * remainder] if remainder else []))
        tally_rows.append(f"<tr><td>{html.escape(label)}</td><td>{tally}</td></tr>")
    category_heading = html.escape(passage["data"].get("category_heading", "Choice"))
    value_heading = html.escape(passage["data"].get("value_heading", "Tally"))
    html_box(page, table_rect, f"<table border='1' cellpadding='2'><tr><th>{category_heading}</th><th>{value_heading}</th></tr>" + "".join(tally_rows) + "</table>", "diagram-tally", 6.8)
    x0, y0 = rect.x0 + 250, rect.y1 - 96
    page.draw_line(fitz.Point(x0 + 30, y0), fitz.Point(x0 + 30, y0 + 72), color=INK, width=0.7)
    page.draw_line(fitz.Point(x0 + 30, y0 + 72), fitz.Point(rect.x1 - 8, y0 + 72), color=INK, width=0.7)
    bar_width = 34
    for index, (label, value) in enumerate(zip(labels, values)):
        height = 56 * value / max_value
        bx = x0 + 42 + index * 56
        page.draw_rect(fitz.Rect(bx, y0 + 72 - height, bx + bar_width, y0 + 72), color=TEAL, fill=PALE)
        html_box(page, fitz.Rect(bx - 11, y0 + 73, bx + 45, y0 + 91), html.escape(label), f"diagram-label-data-{index}", 6.8, "center")


def draw_reading_pages(doc):
    for passage_index, passage in enumerate(PAPER["reading_passages"]):
        questions = passage["questions"]
        page = add_page(doc, "Reading", f"{passage['title']} · Questions {questions[0]['id'][1:]}–{questions[-1]['id'][1:]}")
        passage_bottoms = {
            "timetable": 228,
            "notice": 242,
            "poem": 238,
            "directions": 246,
            "letter": 252,
            "form": 276,
            "procedure": 286,
            "data": 310,
            "review": 286,
            "narrative": 286,
            "information": 286,
            "paired": 286,
            "opinion": 286,
            "explanation": 286,
        }
        text_rect = fitz.Rect(32, 78, 563, passage_bottoms.get(passage["genre"], 286))
        page.draw_rect(text_rect, color=LINE, fill=LIGHT, width=0.55, radius=0.04)
        html_box(page, text_rect + (10, 8, -10, -8), passage_markup(passage), f"passage-{passage['id']}", 8.0)
        draw_data_visual(page, passage, text_rect)
        top = text_rect.y1 + 7
        bottom = 808
        height = (bottom - top) / len(questions)
        for index, item in enumerate(questions):
            rect = fitz.Rect(32, top + index * height, 563, top + (index + 1) * height - 3)
            draw_question_card(page, item, int(item["id"][1:]), rect, 7.5, 7.4)


def draw_writing_page(doc):
    writing = PAPER["writing"]
    page = add_page(doc, "Writing", writing["title"])
    page.draw_rect(fitz.Rect(32, 82, 563, 195), color=LINE, fill=LIGHT, width=0.6, radius=0.04)
    html_box(page, fitz.Rect(46, 94, 548, 130), f"<b>{writing['prompt']}</b>", "writing-prompt", 10.0)
    ideas = "".join(f"<li>{html.escape(item)}</li>" for item in writing["ideas"])
    introduction = "Build a convincing argument." if writing["mode"] == "persuasive" else "Your story may be amusing or serious."
    html_box(page, fitz.Rect(46, 133, 548, 190), f"{introduction}<ul>{ideas}</ul>", "writing-ideas", 7.8)
    reminders = "".join(f"<li>{html.escape(item)}</li>" for item in writing["reminders"])
    html_box(page, fitz.Rect(34, 207, 563, 278), f"<b>Remember</b><ul>{reminders}</ul>", "writing-reminders", 7.6)
    html_box(page, fitz.Rect(34, 286, 563, 305), "<b>Planning notes</b>", "writing-planning", 8.0)
    for y in range(312, 420, 22):
        page.draw_line(fitz.Point(36, y), fitz.Point(560, y), color=(0.76, 0.84, 0.84), width=0.45)
    start_label = "Begin your persuasive text" if writing["mode"] == "persuasive" else "Begin your narrative"
    html_box(page, fitz.Rect(34, 430, 563, 449), f"<b>{start_label}</b>", "writing-start", 8.0)
    for y in range(458, 805, 23):
        page.draw_line(fitz.Point(36, y), fitz.Point(560, y), color=(0.76, 0.84, 0.84), width=0.45)


def draw_small_visual(page, visual, rect, label):
    kind = visual["kind"]
    AUDIT.record_visual(label, kind, page.number + 1, rect)
    page.draw_rect(rect, color=LINE, fill=(1, 1, 1), width=0.45)
    if kind == "l_grid":
        rows, cols, cut = visual["rows"], visual["cols"], visual["cut"]
        size = min(13, rect.height / rows, rect.width / cols)
        for row in range(rows):
            for col in range(cols):
                if row == rows - 1 and col >= cols - cut:
                    continue
                page.draw_rect(fitz.Rect(rect.x0 + 5 + col * size, rect.y0 + 5 + row * size, rect.x0 + 5 + (col + 1) * size, rect.y0 + 5 + (row + 1) * size), color=INK, fill=PALE, width=0.35)
    elif kind == "circle_pattern":
        values = visual["values"]
        for group, value in enumerate(values):
            group_rect = fitz.Rect(rect.x0 + group * rect.width / 4, rect.y0, rect.x0 + (group + 1) * rect.width / 4, rect.y1)
            if value is None:
                html_box(page, group_rect + (3, 12, -3, -3), "?", f"diagram-{label}-{group}", 10, "center")
            else:
                columns = 4
                radius = min(2.2, (group_rect.width - 8) / (columns * 2.5))
                for index in range(value):
                    row, column = divmod(index, columns)
                    centre = fitz.Point(group_rect.x0 + 7 + column * 7, group_rect.y0 + 8 + row * 7)
                    page.draw_circle(centre, radius, color=INK, fill=PALE)
    elif kind == "pictograph":
        html_box(page, rect + (6, 8, -6, -6), "● " * visual["icons"], f"diagram-{label}", 9.0, "center")
    elif kind == "top_view":
        page.draw_circle(rect.tl + (rect.width / 2, rect.height / 2), min(rect.width, rect.height) * .25, color=INK, fill=PALE)
    elif kind == "fractions":
        patterns = [("A", 1, 4), ("B", 2, 6), ("C", 3, 6), ("D", 2, 5), ("E", 3, 8)]
        cell = min(8.5, (rect.width - 46) / 8, (rect.height - 18) / 5)
        start_y = rect.y0 + (rect.height - len(patterns) * (cell + 2)) / 2
        for row, (name, shaded, total) in enumerate(patterns):
            y0 = start_y + row * (cell + 2)
            label_rect = fitz.Rect(rect.x0 + 7, y0 - 1, rect.x0 + 22, y0 + cell + 2)
            html_box(page, label_rect, name, f"diagram-{label}-{name}", 6.8, "center")
            start_x = rect.x0 + 25
            grid_rect = fitz.Rect(start_x, y0, start_x + total * cell, y0 + cell)
            AUDIT.record_geometry_gap(f"diagram-gap-{label}-{name}", grid_rect, label_rect, 2.0)
            for index in range(total):
                page.draw_rect(
                    fitz.Rect(start_x + index * cell, y0, start_x + (index + 1) * cell, y0 + cell),
                    color=INK,
                    fill=TEAL if index < shaded else (1, 1, 1),
                    width=0.55,
                )
    elif kind == "money_table":
        values = visual["values"]
        html_box(page, rect + (5, 5, -5, -5), "<table border='1' cellpadding='2'>" + "".join(f"<tr><td>{chr(65+i)}</td><td>${value:.2f}</td></tr>" for i, value in enumerate(values)) + "</table>", f"diagram-{label}", 6.8)
    elif kind == "clock":
        centre = fitz.Point(rect.x0 + rect.width / 2, rect.y0 + rect.height / 2)
        radius = min(rect.width, rect.height) * .38
        page.draw_circle(centre, radius, color=INK, fill=None)
        minute_angle = math.radians(visual["minute"] * 6 - 90)
        hour_angle = math.radians((visual["hour"] % 12 + visual["minute"] / 60) * 30 - 90)
        page.draw_line(centre, centre + (math.cos(minute_angle) * radius * .75, math.sin(minute_angle) * radius * .75), color=INK, width=1)
        page.draw_line(centre, centre + (math.cos(hour_angle) * radius * .5, math.sin(hour_angle) * radius * .5), color=INK, width=1.4)
    elif kind == "room_map":
        rooms = ["entry", "office", visual["target"], "store"]
        if len(set(rooms)) != len(rooms):
            raise RuntimeError(f"Room-map labels must be unique: {rooms}")
        width = rect.width / len(rooms)
        for index, room in enumerate(rooms):
            cell = fitz.Rect(rect.x0 + index * width, rect.y0, rect.x0 + (index + 1) * width, rect.y1)
            page.draw_rect(cell, color=INK, fill=PALE if room == "office" else None, width=0.5)
            html_box(page, cell + (2, 8, -2, -2), html.escape(room), f"diagram-{label}-{index}", 6.8, "center")
    elif kind == "letters":
        html_box(page, rect + (5, 7, -5, -5), f"{visual['answer']} &nbsp; F &nbsp; G &nbsp; J", f"diagram-{label}", 12, "center")
    elif kind == "equal_area":
        patterns = [("A", 4), ("B", 3), ("C", 4), ("D", 5)]
        cell = min(10.5, (rect.width - 46) / 5)
        row_gap = max(5, (rect.height - 2 * cell) / 3)
        for index, (name, count) in enumerate(patterns):
            row, column = divmod(index, 2)
            area_width = rect.width / 2
            x0 = rect.x0 + column * area_width + 8
            y0 = rect.y0 + row_gap + row * (cell + row_gap)
            label_rect = fitz.Rect(x0, y0 - 1, x0 + 14, y0 + cell + 2)
            html_box(page, label_rect, name, f"diagram-{label}-{name}", 6.8, "center")
            square_area = fitz.Rect(x0 + 16, y0, x0 + 16 + count * cell, y0 + cell)
            AUDIT.record_geometry_gap(f"diagram-gap-{label}-{name}", square_area, label_rect, 2.0)
            for square in range(count):
                square_x = x0 + 16 + square * cell
                page.draw_rect(
                    fitz.Rect(square_x, y0, square_x + cell, y0 + cell),
                    color=INK,
                    fill=TEAL,
                    width=0.55,
                )
    elif kind == "cubes":
        count = visual["count"]
        for index in range(count):
            row, column = divmod(index, 4)
            x0 = rect.x0 + 18 + column * 23 + row * 5
            y0 = rect.y1 - 28 - row * 18
            page.draw_rect(fitz.Rect(x0, y0, x0 + 16, y0 + 16), color=INK, fill=PALE, width=0.6)
            page.draw_line(fitz.Point(x0, y0), fitz.Point(x0 + 5, y0 - 5), color=INK, width=0.5)
            page.draw_line(fitz.Point(x0 + 16, y0), fitz.Point(x0 + 21, y0 - 5), color=INK, width=0.5)
            page.draw_line(fitz.Point(x0 + 5, y0 - 5), fitz.Point(x0 + 21, y0 - 5), color=INK, width=0.5)
    elif kind == "composite_solid":
        left, right = rect.x0 + 35, rect.x1 - 35
        join_y, bottom = rect.y0 + 38, rect.y1 - 13
        page.draw_rect(fitz.Rect(left, join_y, right, bottom), color=INK, fill=PALE)
        page.draw_oval(fitz.Rect(left, bottom - 8, right, bottom + 8), color=INK, fill=PALE)
        centre_x = (left + right) / 2
        page.draw_bezier(fitz.Point(left, join_y), fitz.Point(left + 8, rect.y0 + 5), fitz.Point(right - 8, rect.y0 + 5), fitz.Point(right, join_y), color=INK, fill=PALE, width=1)
        page.draw_line(fitz.Point(left, join_y), fitz.Point(right, join_y), color=INK, width=0.6)
    elif kind == "thermometers":
        values = [("Before", visual["high"]), ("After", visual["low"])]
        for index, (caption, value) in enumerate(values):
            cx = rect.x0 + rect.width * (.28 if index == 0 else .72)
            top, bottom = rect.y0 + 14, rect.y1 - 36
            tube_rect = fitz.Rect(cx - 4, top, cx + 4, bottom)
            bulb_rect = fitz.Rect(cx - 8, bottom - 3, cx + 8, bottom + 13)
            tick_rect = fitz.Rect(cx + 5, top, cx + 10, bottom)
            geometry_rect = tube_rect | bulb_rect | tick_rect
            caption_rect = fitz.Rect(cx - 30, rect.y1 - 17, cx + 30, rect.y1 - 2)
            AUDIT.record_geometry_gap(f"diagram-gap-{label}-{index}", geometry_rect, caption_rect, 4.0)
            page.draw_rect(tube_rect, color=INK, fill=None, width=0.7)
            page.draw_circle(fitz.Point(cx, bottom + 5), 8, color=INK, fill=PALE)
            fill_top = bottom - (bottom - top) * value / 35
            page.draw_rect(fitz.Rect(cx - 2, fill_top, cx + 2, bottom + 5), color=TEAL, fill=TEAL, width=0.4)
            for tick in range(0, 36, 5):
                y = bottom - (bottom - top) * tick / 35
                page.draw_line(fitz.Point(cx + 5, y), fitz.Point(cx + 10, y), color=INK, width=0.4)
            html_box(page, caption_rect, f"{caption} {value}°C", f"diagram-{label}-{index}", 6.8, "center")
    elif kind == "number_line":
        values = visual["values"]
        plot_rect = fitz.Rect(rect.x0 + 15, rect.y0 + 19, rect.x1 - 15, rect.y0 + 31)
        page.draw_line(fitz.Point(rect.x0 + 15, rect.y0 + 25), fitz.Point(rect.x1 - 15, rect.y0 + 25), color=INK, width=0.7)
        for index, value in enumerate(values):
            x = rect.x0 + 20 + index * (rect.width - 40) / 3
            page.draw_line(fitz.Point(x, rect.y0 + 19), fitz.Point(x, rect.y0 + 31), color=INK, width=0.7)
            label_rect = fitz.Rect(x - 15, rect.y0 + 34, x + 15, rect.y1 - 2)
            AUDIT.record_geometry_gap(f"diagram-gap-{label}-{index}", plot_rect, label_rect, 3.0)
            html_box(page, label_rect, str(value), f"diagram-{label}-{index}", 6.8, "center")
    elif kind in {"scales", "backward_line", "total_table"}:
        if kind == "scales":
            for index, value in enumerate(visual["values"]):
                x0 = rect.x0 + 18 + index * rect.width / 2
                x1 = rect.x0 + (index + 1) * rect.width / 2 - 10
                bottom, top = rect.y1 - 22, rect.y0 + 12
                plot_rect = fitz.Rect(x0 + 16, top, x1 - 8, bottom)
                label_rect = fitz.Rect(x0, rect.y1 - 17, x1, rect.y1 - 2)
                AUDIT.record_geometry_gap(f"diagram-gap-{label}-{index}", plot_rect, label_rect, 5.0)
                page.draw_line(fitz.Point(x0 + 20, bottom), fitz.Point(x0 + 20, top), color=INK, width=0.8)
                for tick in range(0, 61, 10):
                    y = bottom - (bottom - top) * tick / 60
                    page.draw_line(fitz.Point(x0 + 16, y), fitz.Point(x0 + 25, y), color=INK, width=0.45)
                pointer_y = bottom - (bottom - top) * value / 60
                page.draw_line(fitz.Point(x0 + 20, pointer_y), fitz.Point(x1 - 8, pointer_y), color=TEAL, width=1.4)
                html_box(page, label_rect, f"{'AB'[index]} {value} kg", f"diagram-{label}-{index}", 6.8, "center")
            return
        elif kind == "backward_line":
            y = rect.y0 + rect.height / 2
            left, right = rect.x0 + 22, rect.x1 - 22
            page.draw_line(fitz.Point(left, y), fitz.Point(right, y), color=INK, width=0.7)
            for index in range(4):
                x = left + index * (right - left) / 3
                page.draw_circle(fitz.Point(x, y), 5.2, color=INK, fill=(1, 1, 1), width=0.7)
            return
        else:
            text = f"Known: {', '.join(map(str, visual['known']))} &nbsp; Total: {visual['total']}"
        html_box(page, rect + (5, 8, -5, -5), text, f"diagram-{label}", 7.0, "center")
    elif kind == "bar_chart":
        labels, values = visual["labels"], visual["values"]
        max_value = max(values)
        for index, (bar_label, value) in enumerate(zip(labels, values)):
            width = (rect.width - 30) / len(labels)
            x0 = rect.x0 + 15 + index * width
            plot_bottom = rect.y1 - 18
            plot_top = rect.y0 + 15
            height = (plot_bottom - plot_top) * value / max_value
            bar_top = plot_bottom - height
            bar_rect = fitz.Rect(x0 + 4, bar_top, x0 + width - 4, plot_bottom)
            value_rect = fitz.Rect(x0, max(rect.y0, bar_top - 15), x0 + width, bar_top - 2)
            category_rect = fitz.Rect(x0, rect.y1 - 14, x0 + width, rect.y1 - 1)
            AUDIT.record_geometry_gap(f"diagram-gap-{label}-value-{index}", bar_rect, value_rect, 2.0)
            AUDIT.record_geometry_gap(f"diagram-gap-{label}-category-{index}", bar_rect, category_rect, 4.0)
            page.draw_rect(bar_rect, color=TEAL, fill=PALE)
            html_box(page, value_rect, html.escape(str(value)), f"diagram-{label}-value-{index}", 6.8, "center")
            html_box(page, category_rect, html.escape(str(bar_label)), f"diagram-{label}-{index}", 6.8, "center")
    elif kind == "spinners":
        blue_angles = [150, 90, 45, 120]
        for index, angle in enumerate(blue_angles):
            centre = fitz.Point(rect.x0 + 25 + index * (rect.width - 50) / 3, rect.y0 + rect.height / 2 - 3)
            radius = min(17, rect.height * .28)
            circle_rect = fitz.Rect(centre.x - radius, centre.y - radius, centre.x + radius, centre.y + radius)
            label_rect = fitz.Rect(centre.x - 12, centre.y + radius + 3, centre.x + 12, centre.y + radius + 15)
            AUDIT.record_geometry_gap(f"diagram-gap-{label}-{index}", circle_rect, label_rect, 3.0)
            page.draw_circle(centre, radius, color=INK, fill=None, width=0.7)
            start = fitz.Point(centre.x, centre.y - radius)
            page.draw_sector(centre, start, angle, color=TEAL, fill=PALE, width=0.7)
            html_box(page, label_rect, f"{'ABCD'[index]}", f"diagram-{label}-{index}", 6.8, "center")
    elif kind == "coins":
        max_per_row = 5
        rows = []
        for value, count in [("$2", visual["twos"]), ("$1", visual["ones"])]:
            while count:
                row_count = min(max_per_row, count)
                rows.append((value, row_count))
                count -= row_count
        radius = min(
            10.5,
            (rect.width - 16) / (max_per_row * 2.35),
            (rect.height - 14) / (len(rows) * 2.55),
        )
        row_spacing = rect.height / (len(rows) + 1)
        for row_index, (value, count) in enumerate(rows):
            group_y = rect.y0 + (row_index + 1) * row_spacing
            total_width = (count - 1) * radius * 2.35 + radius * 2
            start_x = rect.x0 + (rect.width - total_width) / 2 + radius
            for coin_index in range(count):
                centre = fitz.Point(start_x + coin_index * radius * 2.35, group_y)
                coin_rect = fitz.Rect(centre.x - radius, centre.y - radius, centre.x + radius, centre.y + radius)
                if not rect.contains(coin_rect):
                    raise RuntimeError(f"Coin diagram exceeds its visual region: {label} {coin_rect} not in {rect}")
                page.draw_circle(centre, radius, color=INK, fill=PALE, width=0.65)
                html_box(page, fitz.Rect(centre.x - radius, centre.y - 8, centre.x + radius, centre.y + 8), value, f"diagram-{label}-{row_index}-{coin_index}", 6.8, "center")
    else:
        html_box(page, rect + (5, 5, -5, -5), "Diagram", f"diagram-{label}", 6.8, "center")


def draw_numeracy_item(page, item, number, rect):
    page.draw_rect(rect, color=(0.84, 0.90, 0.90), fill=LIGHT, width=0.45, radius=0.04)
    draw_number(page, number, rect.x0 + 10, rect.y0 + 12)
    visual = item.get("visual")
    prompt_right = rect.x1 - 4
    if visual:
        visual_rect = fitz.Rect(rect.x1 - 160, rect.y0 + 5, rect.x1 - 5, rect.y1 - 5)
        draw_small_visual(page, visual, visual_rect, item["id"])
        prompt_right = visual_rect.x0 - 5
    body = item["prompt"] + '<div style="margin-top:3pt">' + response_markup(item) + "</div>"
    html_box(page, fitz.Rect(rect.x0 + 23, rect.y0 + 4, prompt_right, rect.y1 - 4), body, f"prompt-{item['id']}", 7.4)


def draw_numeracy_pages(doc):
    ranges = [(0, 5), (5, 9), (9, 15), (15, 19), (19, 23), (23, 27), (27, 33), (33, 36)]
    for start, end in ranges:
        page = add_page(doc, "Numeracy", f"Questions {start + 1}–{end}")
        questions = PAPER["numeracy"][start:end]
        top, bottom = 78, 808
        height = (bottom - top) / len(questions)
        for index, item in enumerate(questions):
            rect = fitz.Rect(30, top + index * height, 565, top + (index + 1) * height - 4)
            draw_numeracy_item(page, item, start + index + 1, rect)


def answer_text(item):
    answer = item["answer"]
    if isinstance(answer, list):
        answer = "; ".join(str(value) for value in answer)
    elif isinstance(answer, bool):
        answer = "True" if answer else "False"
    if item["kind"] == "mcq":
        answer = f"{chr(65 + item['answer_index'])}. {answer}"
    return str(answer)


def draw_answer_page(doc, title, items, extra=None):
    page = add_page(doc, "Answers and Explanations", title)
    columns = 2
    rows = math.ceil(len(items) / columns)
    top, bottom = 78, 806 if extra is None else 744
    row_height = (bottom - top) / rows
    for index, item in enumerate(items):
        column = index // rows
        row = index % rows
        rect = fitz.Rect(30 + column * 270, top + row * row_height, 294 + column * 270, top + (row + 1) * row_height - 2)
        page.draw_line(rect.bl, rect.br, color=(0.83, 0.89, 0.89), width=0.35)
        body = f"<b>{item['id']} · {html.escape(answer_text(item))}</b><br>{item['explanation']}"
        html_box(page, rect + (2, 2, -2, -1), body, f"answer-{item['id']}", 7.4)
    if extra:
        page.draw_rect(fitz.Rect(32, 750, 563, 805), color=None, fill=PALE, radius=0.04)
        html_box(page, fitz.Rect(43, 758, 552, 798), extra, f"answer-extra-{title}", 7.4)


def draw_answers(doc):
    language = PAPER["language"]
    reading = [item for passage in PAPER["reading_passages"] for item in passage["questions"]]
    numeracy = PAPER["numeracy"]
    draw_answer_page(doc, "Conventions of Language · L1–L25", language[:25])
    draw_answer_page(doc, "Conventions of Language · L26–L50", language[25:])
    draw_answer_page(doc, "Reading · R1–R20", reading[:20])
    draw_answer_page(doc, "Reading · R21–R39", reading[20:])
    draw_answer_page(doc, "Numeracy · N1–N18", numeracy[:18])
    if PAPER["writing"]["mode"] == "persuasive":
        extra = "<b>Writing review:</b> Check for a clear position, organised reasons, relevant examples, linking words and a strong conclusion; then check sentence structure, punctuation and spelling."
    else:
        extra = "<b>Writing review:</b> Check for a clear setting, characters, complication and ending; organised paragraphs; precise vocabulary; complete sentences; controlled punctuation; and carefully checked spelling."
    draw_answer_page(doc, "Numeracy · N19–N36", numeracy[18:], extra)


def validate_cache():
    cached = json.loads(SOURCE_HASHES.read_text(encoding="utf-8"))
    for item in cached["files"]:
        path = ROOT / "y3" / "orig" / item["file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise RuntimeError(f"Source cache invalid: {item['file']}")


def validate_content():
    language = PAPER["language"]
    reading = [item for passage in PAPER["reading_passages"] for item in passage["questions"]]
    numeracy = PAPER["numeracy"]
    assert [item["id"] for item in language] == [f"L{number}" for number in range(1, 51)]
    assert [item["id"] for item in reading] == [f"R{number}" for number in range(1, 40)]
    assert [item["id"] for item in numeracy] == [f"N{number}" for number in range(1, 37)]
    for item in language + reading + numeracy:
        assert item["answer"] not in (None, "") and item["explanation"]
        if item["kind"] == "mcq":
            assert 4 <= len(item["options"]) <= 5
            assert item["options"][item["answer_index"]] == str(item["answer"])
            assert len(set(item["options"])) == len(item["options"])
        if item["kind"] == "select_two":
            assert len(item["answer"]) == 2 and all(answer in item["options"] for answer in item["answer"])
    assert [item.get("spelling_mode") for item in language[25:]] == ["dictation"] * 15 + ["correct_underlined"] * 5 + ["locate_error"] * 5
    return language, reading, numeracy


def diagram_drawing_boundary_crossings(document, visual_entries, padding=1.0):
    crossings = []
    drawings_by_page = {}
    for visual in visual_entries:
        page_number = visual["page"]
        page_drawings = drawings_by_page.setdefault(page_number, document[page_number - 1].get_drawings())
        rect = fitz.Rect(visual["rect"])
        outer = fitz.Rect(rect.x0 - padding, rect.y0 - padding, rect.x1 + padding, rect.y1 + padding)
        for drawing in page_drawings:
            drawing_rect = fitz.Rect(drawing["rect"])
            if drawing_rect.is_empty or (drawing_rect & outer).is_empty:
                continue
            if outer.contains(drawing_rect) or drawing_rect.contains(outer):
                continue
            crossings.append({
                "label": visual["label"],
                "kind": visual["kind"],
                "page": page_number,
                "visual_rect": [round(value, 2) for value in rect],
                "drawing_rect": [round(value, 2) for value in drawing_rect],
            })
    return crossings


def assert_diagram_drawings_within_bounds(document, visual_entries):
    crossings = diagram_drawing_boundary_crossings(document, visual_entries)
    if crossings:
        raise RuntimeError(f"Diagram drawing crosses its visual boundary: {crossings[:3]}")
    return crossings


def render_pages(pdf):
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    for path in RENDER_DIR.glob("page-*.png"):
        path.unlink()
    document = fitz.open(pdf)
    for index, page in enumerate(document, start=1):
        page.get_pixmap(matrix=fitz.Matrix(1.65, 1.65), alpha=False).save(RENDER_DIR / f"page-{index:02d}.png")


def render_one(paper_number, render_images=True):
    configure(paper_number)
    validate_cache()
    language, reading, numeracy = validate_content()
    document = fitz.open()
    draw_language_pages(document)
    draw_reading_pages(document)
    draw_writing_page(document)
    draw_numeracy_pages(document)
    assert len(document) == 20
    draw_answers(document)
    assert len(document) == 26
    boundary_crossings = assert_diagram_drawings_within_bounds(document, AUDIT.visual_entries)
    document.set_metadata({"title": PAPER["title"], "author": "Independent practice material", "subject": "Year 3 NAPLAN-style practice"})
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.exists():
        OUTPUT.unlink()
    document.save(OUTPUT, garbage=4, deflate=True)
    document.close()
    if render_images:
        render_pages(OUTPUT)
    question_ids = [item["id"] for item in language + reading + numeracy]
    body_entries = [entry for entry in AUDIT.entries if entry["label"].startswith(("prompt-", "response-", "passage-", "writing-"))]
    diagram_entries = [entry for entry in AUDIT.entries if entry["label"].startswith("diagram-")]
    answer_entries = [entry for entry in AUDIT.entries if entry["label"].startswith("answer-") and not entry["label"].startswith("answer-extra-")]
    assert min(entry["font_size"] for entry in body_entries) >= MIN_BODY_FONT
    assert min(entry["font_size"] for entry in diagram_entries) >= MIN_DIAGRAM_FONT
    assert min(entry["font_size"] for entry in answer_entries) >= MIN_APPENDIX_FONT
    inventory = {
        "paper": PAPER["title"],
        "reference_student_pages": 20,
        "student_pages": 20,
        "appendix_pages": 6,
        "total_pages": 26,
        "scored_question_counts": {"language": 50, "reading": 39, "numeracy": 36},
        "writing_tasks": 1,
        "question_ids": question_ids,
        "answer_ids": question_ids,
    }
    INVENTORY.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    report = {
        "pdf": str(OUTPUT.relative_to(ROOT)),
        "student_pages": 20,
        "appendix_pages": 6,
        "pages": 26,
        "minimum_body_font": min(entry["font_size"] for entry in body_entries),
        "minimum_diagram_font": min(entry["font_size"] for entry in diagram_entries),
        "minimum_appendix_font": min(entry["font_size"] for entry in answer_entries),
        "layout_entries": AUDIT.entries,
        "minimum_scale": min(entry["scale"] for entry in AUDIT.entries),
        "negative_spare_entries": [entry for entry in AUDIT.entries if entry["spare_height"] < 0],
        "diagram_visuals": AUDIT.visual_entries,
        "diagram_geometry_checks": AUDIT.geometry_entries,
        "minimum_diagram_geometry_gap": min(entry["actual_gap"] for entry in AUDIT.geometry_entries),
        "diagram_boundary_crossings": boundary_crossings,
    }
    LAYOUT_REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT} · minimum scale {report['minimum_scale']:.4f}")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", type=int)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--no-render", action="store_true")
    args = parser.parse_args()
    numbers = range(1, PAPER_COUNT + 1) if args.all else [args.paper or 1]
    for number in numbers:
        render_one(number, render_images=not args.no_render)


if __name__ == "__main__":
    main()
