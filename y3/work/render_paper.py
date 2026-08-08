from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
import sys
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content_factory import build_paper


ROOT = Path(__file__).resolve().parents[2]
SOURCE_HASHES = ROOT / "y3" / "source-cache" / "source-hashes.json"
PAPER = None
PAPER_NUMBER = None
OUTPUT = None
RENDER_DIR = None
LAYOUT_REPORT = None
INVENTORY = None

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
p { margin: 0 0 4pt 0; line-height: 1.28; }
strong { color: #103f46; }
em { color: #244f55; }
table { border-collapse: collapse; width: 100%; }
td, th { vertical-align: top; }
ul, ol { margin: 1pt 0 3pt 13pt; padding: 0; }
li { margin-bottom: 2pt; line-height: 1.25; }
"""


class Audit:
    def __init__(self):
        self.entries = []

    def record(self, label, spare, scale, font_size):
        entry = {"label": label, "font_size": font_size, "spare_height": round(float(spare), 2), "scale": round(float(scale), 4)}
        self.entries.append(entry)
        if spare < -0.01:
            raise RuntimeError(f"Overflow: {entry}")
        if scale < 0.89:
            raise RuntimeError(f"Text too compressed: {entry}")


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


def html_box(page, rect, body, label, size=8, align="left", css=""):
    markup = f'<div style="font-size:{size}pt;line-height:1.22;text-align:{align}">{body}</div>'
    spare, scale = page.insert_htmlbox(rect, markup, css=CSS + css, scale_low=0)
    AUDIT.record(label, spare, scale, size)


def add_page(doc, section, title):
    page = doc.new_page(width=A4.width, height=A4.height)
    number = len(doc)
    page.draw_rect(fitz.Rect(26, 20, 569, 48), color=None, fill=PALE, radius=0.12)
    page.draw_rect(fitz.Rect(32, 27, 76, 43), color=None, fill=TEAL, radius=0.45)
    html_box(page, fitz.Rect(35, 29, 73, 41), '<b style="color:white">Year 3</b>', f"year-{number}", 7.1, "center")
    html_box(page, fitz.Rect(84, 27, 360, 43), f"<b>{section}</b>", f"section-{number}", 8.6)
    html_box(page, fitz.Rect(440, 27, 562, 43), f"Practice Paper {PAPER_NUMBER:02d}", f"paper-{number}", 7.5, "right")
    html_box(page, fitz.Rect(30, 51, 565, 70), f"<b>{title}</b>", f"title-{number}", 10.5)
    page.draw_line(fitz.Point(27, 816), fitz.Point(568, 816), color=LINE, width=0.55)
    html_box(page, fitz.Rect(30, 820, 430, 833), "Independent NAPLAN-style practice material", f"footer-{number}", 6.8)
    html_box(page, fitz.Rect(530, 820, 563, 833), str(number), f"page-{number}", 6.8, "right")
    return page


def option_table(options):
    letters = "ABCD"
    cells = [f'<td style="width:50%;padding:1pt 4pt 1pt 0"><b>{letters[index]}</b>&nbsp;{html.escape(str(option))}</td>' for index, option in enumerate(options)]
    return f"<table><tr>{cells[0]}{cells[1]}</tr><tr>{cells[2]}{cells[3]}</tr></table>"


def draw_number(page, number, x, y, radius=8):
    page.draw_circle(fitz.Point(x, y), radius, color=None, fill=TEAL)
    html_box(page, fitz.Rect(x - radius, y - 5, x + radius, y + 5), f'<b style="color:white">{number}</b>', f"qnum-{number}-{x}-{y}", 6.5, "center")


def draw_grammar_item(page, question, number, rect):
    page.draw_line(rect.bl, rect.br, color=(0.84, 0.90, 0.90), width=0.45)
    draw_number(page, number, rect.x0 + 10, rect.y0 + 11, 7.5)
    html_box(page, fitz.Rect(rect.x0 + 23, rect.y0 + 2, rect.x1 - 4, rect.y0 + 38), question["prompt"], f"prompt-{question['id']}", 8.4)
    html_box(page, fitz.Rect(rect.x0 + 25, rect.y0 + 38, rect.x1 - 3, rect.y1 - 3), option_table(question["options"]), f"options-{question['id']}", 7.6)


def draw_spelling_item(page, question, number, rect):
    page.draw_line(rect.bl, rect.br, color=(0.84, 0.90, 0.90), width=0.4)
    draw_number(page, number, rect.x0 + 9, rect.y0 + 10, 7)
    html_box(page, fitz.Rect(rect.x0 + 21, rect.y0 + 1, rect.x1 - 3, rect.y0 + 34), question["prompt"], f"prompt-{question['id']}", 7.5)
    page.draw_rect(fitz.Rect(rect.x0 + 25, rect.y1 - 17, rect.x1 - 7, rect.y1 - 4), color=LINE, fill=LIGHT, width=0.5)


def draw_language_pages(doc):
    groups = [(0, 9), (9, 18), (18, 25)]
    for start, end in groups:
        page = add_page(doc, "Conventions of Language", f"Questions {start + 1}–{end}")
        page.draw_rect(fitz.Rect(31, 75, 564, 806), color=LINE, fill=(1, 1, 1), radius=0.025, width=0.7)
        questions = PAPER["language"][start:end]
        item_height = 714 / len(questions)
        y = 82
        for question in questions:
            draw_grammar_item(page, question, int(question["id"][1:]), fitz.Rect(40, y, 555, y + item_height - 2))
            y += item_height

    page = add_page(doc, "Conventions of Language", "Spelling · Questions 26–50")
    page.draw_rect(fitz.Rect(31, 75, 564, 806), color=LINE, fill=(1, 1, 1), radius=0.025, width=0.7)
    questions = PAPER["language"][25:]
    columns = [questions[:13], questions[13:]]
    for column, column_questions in enumerate(columns):
        x0, x1 = (39, 295) if column == 0 else (302, 556)
        item_height = 712 / len(column_questions)
        y = 83
        for question in column_questions:
            draw_spelling_item(page, question, int(question["id"][1:]), fitz.Rect(x0, y, x1, y + item_height - 1))
            y += item_height


def passage_markup(passage):
    if passage["type"] in {"information", "narrative"}:
        return "".join(f"<p>{paragraph}</p>" for paragraph in passage["text"])
    if passage["type"] == "procedure":
        materials = "".join(f"<li>{item}</li>" for item in passage["materials"])
        steps = "".join(f"<li>{item}</li>" for item in passage["steps"])
        return f"<p>{passage['intro']}</p><b>Materials</b><ul>{materials}</ul><b>Steps</b><ol>{steps}</ol>"
    if passage["type"] == "table":
        rows = []
        for row_index, row in enumerate(passage["table"]):
            tag = "th" if row_index == 0 else "td"
            cells = "".join(f"<{tag} style='border:0.6pt solid #527f82;padding:4pt'>{cell}</{tag}>" for cell in row)
            rows.append(f"<tr>{cells}</tr>")
        return f"<p>{passage['intro']}</p><table>{''.join(rows)}</table>"
    if passage["type"] == "poem":
        return "<div style='font-family:Georgia,serif;font-size:9pt;line-height:1.45;padding-left:12pt;border-left:3pt solid #6aaca8'>" + "<br>".join(passage["lines"]) + "</div>"
    raise ValueError(passage["type"])


def draw_reading_question(page, question, number, rect):
    page.draw_rect(rect, color=LINE, fill=(1, 1, 1), radius=0.035, width=0.55)
    draw_number(page, number, rect.x0 + 10, rect.y0 + 11, 7)
    html_box(page, fitz.Rect(rect.x0 + 22, rect.y0 + 3, rect.x1 - 3, rect.y0 + 35), question["prompt"], f"prompt-{question['id']}", 7.6)
    html_box(page, fitz.Rect(rect.x0 + 23, rect.y0 + 35, rect.x1 - 3, rect.y1 - 3), option_table(question["options"]), f"options-{question['id']}", 7.4)


def draw_reading_pages(doc):
    for passage in PAPER["reading_passages"]:
        first = int(passage["questions"][0]["id"][1:])
        last = int(passage["questions"][-1]["id"][1:])
        page = add_page(doc, "Reading", f"{passage['title']} · Questions {first}–{last}")
        page.draw_rect(fitz.Rect(31, 75, 564, 430), color=LINE, fill=LIGHT, radius=0.035, width=0.65)
        html_box(page, fitz.Rect(47, 88, 548, 418), f"<h2 style='text-align:center;margin:0 0 7pt 0'>{passage['title']}</h2>{passage_markup(passage)}", f"passage-{passage['id']}", 9.2)
        questions = passage["questions"]
        for index, question in enumerate(questions):
            column, row = index // 3, index % 3
            x0, x1 = (32, 295) if column == 0 else (301, 564)
            y0 = 440 + row * 119
            draw_reading_question(page, question, int(question["id"][1:]), fitz.Rect(x0, y0, x1, y0 + 111))


def draw_writing_illustration(page, rect, kind):
    page.draw_rect(rect, color=LINE, fill=LIGHT, radius=0.04, width=0.6)
    sky = fitz.Rect(rect.x0 + 1, rect.y0 + 1, rect.x1 - 1, rect.y0 + rect.height * 0.68)
    ground_y = rect.y0 + rect.height * 0.76
    page.draw_rect(sky, color=None, fill=(0.91, 0.97, 0.98))
    page.draw_line(fitz.Point(rect.x0, ground_y), fitz.Point(rect.x1, ground_y - 7), color=(0.55, 0.75, 0.58), width=9)
    cx = (rect.x0 + rect.x1) / 2
    if kind == "door_tree":
        trunk = fitz.Rect(cx - 24, rect.y0 + 62, cx + 27, ground_y)
        page.draw_rect(trunk, color=(0.28, 0.18, 0.12), fill=(0.55, 0.40, 0.28), width=1.2)
        for dx, dy, radius in [(-42, 44, 27), (-15, 31, 31), (18, 35, 30), (47, 45, 26)]:
            page.draw_circle(fitz.Point(cx + dx, rect.y0 + dy), radius, color=None, fill=(0.34, 0.59, 0.39))
        door = fitz.Rect(cx - 10, ground_y - 55, cx + 15, ground_y)
        page.draw_rect(door, color=INK, fill=(0.05, 0.30, 0.34), radius=0.45, width=1)
        page.draw_circle(fitz.Point(door.x1 - 6, door.y0 + 29), 2, color=None, fill=(0.95, 0.78, 0.25))
    elif kind in {"lighthouse", "tower"}:
        tower = fitz.Rect(cx - 24, rect.y0 + 55, cx + 24, ground_y)
        page.draw_rect(tower, color=INK, fill=(0.94, 0.84, 0.70), width=1.1)
        page.draw_rect(fitz.Rect(cx - 31, rect.y0 + 43, cx + 31, rect.y0 + 66), color=INK, fill=TEAL, width=1)
        roof_left = fitz.Point(cx - 35, rect.y0 + 43)
        roof_right = fitz.Point(cx + 35, rect.y0 + 43)
        roof_top = fitz.Point(cx, rect.y0 + 18)
        page.draw_line(roof_left, roof_right, color=INK, width=1)
        page.draw_line(roof_right, roof_top, color=INK, width=1)
        page.draw_line(roof_top, roof_left, color=INK, width=1)
        page.draw_line(fitz.Point(cx + 31, rect.y0 + 52), fitz.Point(rect.x1 - 15, rect.y0 + 33), color=(0.95, 0.78, 0.25), width=7)
    elif kind in {"attic", "book", "museum"}:
        box = fitz.Rect(cx - 58, rect.y0 + 80, cx + 58, ground_y - 10)
        page.draw_rect(box, color=INK, fill=(0.72, 0.53, 0.30), width=1.1)
        page.draw_line(box.tl, fitz.Point(cx, rect.y0 + 52), color=INK, width=1)
        page.draw_line(box.tr, fitz.Point(cx, rect.y0 + 52), color=INK, width=1)
        page.draw_circle(fitz.Point(cx, box.y0 + 28), 5, color=None, fill=(0.95, 0.78, 0.25))
        if kind == "book":
            page.draw_line(fitz.Point(cx, box.y0 + 8), fitz.Point(cx, box.y1 - 8), color=(1, 1, 1), width=1)
    elif kind in {"beach", "island"}:
        for offset, colour in [(0, (0.18, 0.58, 0.72)), (13, (0.25, 0.68, 0.78)), (26, (0.38, 0.75, 0.82))]:
            page.draw_line(fitz.Point(rect.x0 + 8, ground_y - 30 + offset), fitz.Point(rect.x1 - 8, ground_y - 25 + offset), color=colour, width=8)
        page.draw_rect(fitz.Rect(cx - 35, ground_y - 55, cx + 35, ground_y - 18), color=INK, fill=(0.65, 0.43, 0.22), width=1)
        page.draw_line(fitz.Point(cx - 35, ground_y - 55), fitz.Point(cx, ground_y - 75), color=INK, width=1)
        page.draw_line(fitz.Point(cx + 35, ground_y - 55), fitz.Point(cx, ground_y - 75), color=INK, width=1)
    elif kind in {"bridge", "cave", "tunnel"}:
        page.draw_rect(fitz.Rect(rect.x0 + 32, ground_y - 72, rect.x1 - 32, ground_y - 17), color=INK, fill=(0.55, 0.48, 0.40), width=1)
        opening = fitz.Rect(cx - 35, ground_y - 66, cx + 35, ground_y - 17)
        page.draw_rect(opening, color=INK, fill=(0.10, 0.24, 0.28), radius=0.45, width=1)
        page.draw_line(fitz.Point(rect.x0 + 20, ground_y + 4), fitz.Point(rect.x1 - 20, ground_y - 4), color=(0.16, 0.58, 0.72), width=10)
    elif kind == "clock":
        page.draw_circle(fitz.Point(cx, rect.y0 + 103), 55, color=INK, fill=(0.94, 0.96, 0.91), width=1.2)
        page.draw_line(fitz.Point(cx, rect.y0 + 103), fitz.Point(cx, rect.y0 + 67), color=TEAL, width=2)
        page.draw_line(fitz.Point(cx, rect.y0 + 103), fitz.Point(cx + 28, rect.y0 + 119), color=TEAL, width=2)
        page.draw_rect(fitz.Rect(cx - 12, rect.y0 + 158, cx + 12, ground_y), color=INK, fill=(0.55, 0.40, 0.28), width=1)
    elif kind == "globe":
        page.draw_circle(fitz.Point(cx, rect.y0 + 100), 58, color=INK, fill=(0.92, 0.97, 1.0), width=1.2)
        for dx, dy in [(-25, -18), (20, -10), (-5, 12), (29, 23), (-32, 28)]:
            page.draw_circle(fitz.Point(cx + dx, rect.y0 + 100 + dy), 3, color=None, fill=(1, 1, 1))
        page.draw_rect(fitz.Rect(cx - 48, rect.y0 + 157, cx + 48, rect.y0 + 177), color=INK, fill=(0.55, 0.40, 0.28), width=1)
    elif kind == "moon":
        page.draw_circle(fitz.Point(cx + 18, rect.y0 + 65), 37, color=INK, fill=(0.96, 0.92, 0.65), width=1)
        for step in range(4):
            page.draw_oval(fitz.Rect(cx - 55 + step * 24, ground_y - 30 - step * 7, cx - 42 + step * 24, ground_y - 20 - step * 7), color=INK, fill=PALE, width=0.7)
    elif kind == "garden":
        page.draw_line(fitz.Point(cx - 70, ground_y), fitz.Point(cx - 70, rect.y0 + 72), color=(0.40, 0.28, 0.16), width=5)
        page.draw_line(fitz.Point(cx + 70, ground_y), fitz.Point(cx + 70, rect.y0 + 72), color=(0.40, 0.28, 0.16), width=5)
        gate = fitz.Rect(cx - 55, rect.y0 + 92, cx + 55, ground_y)
        page.draw_rect(gate, color=INK, fill=(0.76, 0.90, 0.78), width=1.2)
        for offset in (-35, 0, 35):
            page.draw_line(fitz.Point(cx + offset, gate.y0), fitz.Point(cx + offset, gate.y1), color=INK, width=1)
        page.draw_circle(fitz.Point(cx + 42, rect.y0 + 132), 3, color=None, fill=(0.95, 0.78, 0.25))
    elif kind == "telescope":
        page.draw_line(fitz.Point(cx - 48, rect.y0 + 85), fitz.Point(cx + 45, rect.y0 + 62), color=INK, width=15)
        page.draw_circle(fitz.Point(cx + 49, rect.y0 + 61), 13, color=INK, fill=PALE, width=1)
        page.draw_line(fitz.Point(cx, rect.y0 + 91), fitz.Point(cx - 32, ground_y), color=INK, width=2)
        page.draw_line(fitz.Point(cx, rect.y0 + 91), fitz.Point(cx + 32, ground_y), color=INK, width=2)
    elif kind in {"train", "robot"}:
        body = fitz.Rect(cx - 70, rect.y0 + 75, cx + 70, ground_y - 22)
        page.draw_rect(body, color=INK, fill=PALE, radius=0.1, width=1.2)
        page.draw_rect(fitz.Rect(cx - 43, rect.y0 + 48, cx + 43, rect.y0 + 86), color=INK, fill=TEAL, width=1)
        for dx in (-45, 45):
            page.draw_circle(fitz.Point(cx + dx, ground_y - 18), 15, color=INK, fill=(0.18, 0.27, 0.29), width=1)
        if kind == "robot":
            page.draw_circle(fitz.Point(cx - 16, rect.y0 + 65), 3, color=None, fill=(1, 1, 1))
            page.draw_circle(fitz.Point(cx + 16, rect.y0 + 65), 3, color=None, fill=(1, 1, 1))
    else:
        page.draw_circle(fitz.Point(cx, rect.y0 + 73), 38, color=INK, fill=(0.95, 0.78, 0.25), width=1)
        page.draw_line(fitz.Point(cx, rect.y0 + 111), fitz.Point(cx, ground_y - 15), color=INK, width=1.5)
        kite_top = fitz.Point(cx, rect.y0 + 73)
        kite_right = fitz.Point(cx + 50, rect.y0 + 95)
        kite_bottom = fitz.Point(cx + 15, rect.y0 + 120)
        page.draw_line(kite_top, kite_right, color=INK, width=1)
        page.draw_line(kite_right, kite_bottom, color=INK, width=1)
        page.draw_line(kite_bottom, kite_top, color=INK, width=1)


def draw_writing_page(doc):
    writing = PAPER["writing"]
    page = add_page(doc, "Writing", "Narrative Writing Task")
    draw_writing_illustration(page, fitz.Rect(35, 80, 292, 310), writing["illustration"])
    html_box(page, fitz.Rect(45, 317, 285, 367), f"<b>{writing['title']}</b><br>{writing['prompt']}", "writing-prompt", 8.7, "center")
    ideas = "".join(f"<li>{item}</li>" for item in writing["ideas"])
    reminders = "".join(f"<li>{item}</li>" for item in writing["reminders"])
    page.draw_rect(fitz.Rect(35, 380, 292, 792), color=LINE, fill=(1, 1, 1), radius=0.03, width=0.6)
    html_box(page, fitz.Rect(48, 392, 280, 550), f"<b>Plan your story</b><ul>{ideas}</ul>", "writing-ideas", 8.0)
    html_box(page, fitz.Rect(48, 560, 280, 682), f"<b>Remember</b><ul>{reminders}</ul>", "writing-reminders", 8.0)
    html_box(page, fitz.Rect(48, 700, 280, 770), "<b>Check:</b> characters, setting, complication, ending, paragraphs, spelling and punctuation.", "writing-check", 7.6)
    page.draw_rect(fitz.Rect(307, 80, 560, 792), color=LINE, fill=(1, 1, 1), radius=0.03, width=0.6)
    html_box(page, fitz.Rect(320, 91, 548, 116), "<b>Writing space</b>", "writing-space", 8.5)
    y = 132
    while y < 777:
        page.draw_line(fitz.Point(320, y), fitz.Point(548, y), color=(0.66, 0.78, 0.78), width=0.45)
        y += 21


def draw_visual(page, visual, rect):
    if isinstance(visual, str):
        visual = {"kind": visual}
    kind = visual["kind"]
    cx, cy = (rect.x0 + rect.x1) / 2, (rect.y0 + rect.y1) / 2
    if kind == "area_grid":
        rows, cols = visual["rows"], visual["cols"]
        size = min(14, rect.height / max(rows + 0.5, 1), rect.width / max(cols + 1, 1))
        x0, y0 = cx - size * cols / 2, cy - size * rows / 2
        for row in range(rows):
            for col in range(cols):
                page.draw_rect(fitz.Rect(x0 + col * size, y0 + row * size, x0 + (col + 1) * size, y0 + (row + 1) * size), color=INK, fill=PALE, width=0.55)
    elif kind == "fraction_bar":
        total, shaded = visual["total"], visual["shaded"]
        width, height = min(22, 180 / total), 15
        x0, y0 = cx - width * total / 2, cy - height / 2
        for index in range(total):
            page.draw_rect(fitz.Rect(x0 + index * width, y0, x0 + (index + 1) * width, y0 + height), color=INK, fill=TEAL if index < shaded else (1, 1, 1), width=0.55)
    elif kind == "symmetry_shape":
        shape = visual["shape"]
        width, height = (54, 54) if shape == "square" else (78, 44)
        page.draw_rect(fitz.Rect(cx - width / 2, cy - height / 2, cx + width / 2, cy + height / 2), color=INK, fill=LIGHT, width=1.2)
    elif kind == "cube":
        front = fitz.Rect(cx - 33, cy - 22, cx + 12, cy + 24)
        shift = fitz.Point(19, -14)
        page.draw_rect(front, color=INK, fill=LIGHT, width=1)
        for p1, p2 in [(front.tl, front.tl + shift), (front.tr, front.tr + shift), (front.br, front.br + shift), (front.tl + shift, front.tr + shift), (front.tr + shift, front.br + shift)]:
            page.draw_line(p1, p2, color=INK, width=1)
    elif kind == "map_grid":
        tree_corner = visual.get("tree_corner", "A1")
        labels = [["", "A", "B", "C", "D"], ["1", "", "", "pond", ""], ["2", "", "gate", "bench", ""], ["3", "", "", "", ""]]
        col = ord(tree_corner[0]) - ord("A") + 1
        row = int(tree_corner[1])
        labels[row][col] = "tree"
        cell_w, cell_h = 31, 14
        x0, y0 = cx - cell_w * 2.5, cy - cell_h * 2
        for row_index, values in enumerate(labels):
            for col_index, value in enumerate(values):
                box = fitz.Rect(x0 + col_index * cell_w, y0 + row_index * cell_h, x0 + (col_index + 1) * cell_w, y0 + (row_index + 1) * cell_h)
                page.draw_rect(box, color=INK, fill=PALE if row_index == 0 or col_index == 0 else (1, 1, 1), width=0.4)
                html_box(page, box + (1, 2, -1, -1), value, f"map-{row_index}-{col_index}-{rect.y0}", 6.8, "center")
    elif kind == "bar_chart":
        bars = visual["bars"]
        baseline = rect.y1 - 10
        page.draw_line(fitz.Point(rect.x0 + 20, rect.y0 + 3), fitz.Point(rect.x0 + 20, baseline), color=INK, width=0.55)
        page.draw_line(fitz.Point(rect.x0 + 20, baseline), fitz.Point(rect.x1 - 8, baseline), color=INK, width=0.55)
        gap = (rect.width - 55) / len(bars)
        max_value = max(value for _, value in bars)
        scale = max(1.4, min(3.0, (rect.height - 28) / max_value))
        for index, (name, value) in enumerate(bars):
            x = rect.x0 + 28 + index * gap
            height = value * scale
            page.draw_rect(fitz.Rect(x, baseline - height, x + 13, baseline), color=INK, fill=TEAL, width=0.4)
            html_box(page, fitz.Rect(x - 5, baseline - height - 13, x + 19, baseline - height), str(value), f"bar-v-{index}-{rect.y0}", 6.8, "center")
            html_box(page, fitz.Rect(x - 8, baseline + 1, x + 22, baseline + 14), name, f"bar-l-{index}-{rect.y0}", 6.8, "center")
    elif kind == "spinner":
        counts = visual["counts"]
        labels = [colour for colour, count in counts.items() for _ in range(count)]
        radius = min(45, rect.height / 2 - 3)
        page.draw_circle(fitz.Point(cx, cy), radius, color=INK, fill=LIGHT, width=0.8)
        for index, label in enumerate(labels):
            angle = 2 * math.pi * index / len(labels) - math.pi / 2
            next_angle = 2 * math.pi * (index + 1) / len(labels) - math.pi / 2
            page.draw_line(fitz.Point(cx, cy), fitz.Point(cx + radius * math.cos(angle), cy + radius * math.sin(angle)), color=INK, width=0.5)
            middle = (angle + next_angle) / 2
            tx, ty = cx + radius * 0.58 * math.cos(middle), cy + radius * 0.58 * math.sin(middle)
            html_box(page, fitz.Rect(tx - 22, ty - 7, tx + 22, ty + 7), label, f"spinner-{index}-{rect.y0}", 6.8, "center")


def draw_numeracy_item(page, question, number, rect):
    page.draw_rect(rect, color=LINE, fill=(1, 1, 1), radius=0.035, width=0.55)
    draw_number(page, number, rect.x0 + 10, rect.y0 + 11, 7)
    prompt_bottom = rect.y0 + 38
    html_box(page, fitz.Rect(rect.x0 + 22, rect.y0 + 3, rect.x1 - 3, prompt_bottom), question["prompt"], f"prompt-{question['id']}", 8.0)
    if question.get("visual"):
        visual_bottom = rect.y1 - 37
        draw_visual(page, question["visual"], fitz.Rect(rect.x0 + 24, prompt_bottom, rect.x1 - 5, visual_bottom))
        option_top = visual_bottom
    else:
        option_top = prompt_bottom
    html_box(page, fitz.Rect(rect.x0 + 23, option_top, rect.x1 - 3, rect.y1 - 3), option_table(question["options"]), f"options-{question['id']}", 7.8)


def draw_numeracy_pages(doc):
    ranges = [(start, start + 3) for start in range(0, 30, 3)]
    for start, end in ranges:
        questions = PAPER["numeracy"][start:end]
        page = add_page(doc, "Numeracy", f"Questions {start + 1}–{end}")
        positions = [(34, 82, 561, 310), (34, 324, 561, 552), (34, 566, 561, 796)]
        for question, coords in zip(questions, positions):
            draw_numeracy_item(page, question, int(question["id"][1:]), fitz.Rect(*coords))


def answer_value(question):
    if "options" not in question:
        return question["answer"]
    return f"{question['answer']} — {question['options']['ABCD'.index(question['answer'])]}"


def draw_answer_entry(page, question, rect, size):
    page.draw_line(rect.bl, rect.br, color=(0.83, 0.89, 0.89), width=0.35)
    text = f"<b>{question['id']} · {html.escape(str(answer_value(question)))}</b><br>{question['explanation']}"
    html_box(page, rect + (2, 1, -2, -1), text, f"answer-{question['id']}", size)


def draw_answer_page(doc, title, questions, columns, font_size, extra=None):
    page = add_page(doc, "Answers and Explanations", title)
    content_top, content_bottom = 78, 805
    if extra:
        content_bottom = 735
        page.draw_rect(fitz.Rect(32, 744, 563, 804), color=None, fill=PALE, radius=0.04)
        html_box(page, fitz.Rect(44, 754, 550, 795), extra, f"answer-extra-{title}", 6.5)
    per_column = (len(questions) + columns - 1) // columns
    column_width = 532 / columns
    row_height = (content_bottom - content_top) / per_column
    for index, question in enumerate(questions):
        column, row = index // per_column, index % per_column
        x0 = 31 + column * column_width
        rect = fitz.Rect(x0, content_top + row * row_height, x0 + column_width - 5, content_top + (row + 1) * row_height - 1)
        draw_answer_entry(page, question, rect, font_size)


def draw_answers(doc):
    language = PAPER["language"]
    reading = [question for passage in PAPER["reading_passages"] for question in passage["questions"]]
    numeracy = PAPER["numeracy"]
    draw_answer_page(doc, "Conventions of Language · L1–L25", language[:25], 2, 7.4)
    draw_answer_page(doc, "Conventions of Language · L26–L50", language[25:], 2, 7.4)
    draw_answer_page(doc, "Reading · R1–R15", reading[:15], 2, 7.6)
    draw_answer_page(doc, "Reading · R16–R30", reading[15:], 2, 7.6)
    extra = "<b>Writing review:</b> Check for a clear opening, complication and ending; paragraphing; precise vocabulary; complete sentences; controlled punctuation; and carefully checked spelling."
    draw_answer_page(doc, "Numeracy · N1–N15", numeracy[:15], 2, 7.6)
    draw_answer_page(doc, "Numeracy · N16–N30", numeracy[15:], 2, 7.6, extra)


def validate_cache():
    cached = json.loads(SOURCE_HASHES.read_text(encoding="utf-8"))
    for item in cached["files"]:
        path = ROOT / "y3" / "orig" / item["file"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != item["sha256"]:
            raise RuntimeError(f"Source cache invalid: {item['file']}")


def validate_content():
    language = PAPER["language"]
    reading = [question for passage in PAPER["reading_passages"] for question in passage["questions"]]
    numeracy = PAPER["numeracy"]
    assert [question["id"] for question in language] == [f"L{number}" for number in range(1, 51)]
    assert [question["id"] for question in reading] == [f"R{number}" for number in range(1, 31)]
    assert [question["id"] for question in numeracy] == [f"N{number}" for number in range(1, 31)]
    for question in language + reading + numeracy:
        assert question["answer"] and question["explanation"]
        if "options" in question:
            assert len(question["options"]) == 4 and question["answer"] in "ABCD"
    return language, reading, numeracy


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
    document.set_metadata({"title": PAPER["title"], "author": "Independent practice material", "subject": "Year 3 NAPLAN-style practice"})
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.exists():
        OUTPUT.unlink()
    document.save(OUTPUT, garbage=4, deflate=True)
    document.close()
    if render_images:
        render_pages(OUTPUT)
    question_ids = [question["id"] for question in language + reading + numeracy]
    body_entries = [entry for entry in AUDIT.entries if entry["label"].startswith(("prompt-", "options-", "passage-", "writing-"))]
    diagram_entries = [entry for entry in AUDIT.entries if entry["label"].startswith(("map-", "bar-", "spinner-"))]
    answer_entries = [entry for entry in AUDIT.entries if entry["label"].startswith("answer-") and not entry["label"].startswith("answer-extra-")]
    assert min(entry["font_size"] for entry in body_entries) >= MIN_BODY_FONT
    assert min(entry["font_size"] for entry in diagram_entries) >= MIN_DIAGRAM_FONT
    assert min(entry["font_size"] for entry in answer_entries) >= MIN_APPENDIX_FONT
    INVENTORY.write_text(json.dumps({"paper": PAPER["title"], "reference_student_pages": 20, "student_pages": 20, "appendix_pages": 6, "total_pages": 26, "scored_question_counts": {"language": 50, "reading": 30, "numeracy": 30}, "writing_tasks": 1, "question_ids": question_ids, "answer_ids": question_ids}, indent=2) + "\n", encoding="utf-8")
    report = {"pdf": str(OUTPUT.relative_to(ROOT)), "student_pages": 20, "appendix_pages": 6, "pages": 26, "minimum_body_font": min(entry["font_size"] for entry in body_entries), "minimum_diagram_font": min(entry["font_size"] for entry in diagram_entries), "minimum_appendix_font": min(entry["font_size"] for entry in answer_entries), "layout_entries": AUDIT.entries, "minimum_scale": min(entry["scale"] for entry in AUDIT.entries), "negative_spare_entries": [entry for entry in AUDIT.entries if entry["spare_height"] < 0]}
    LAYOUT_REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT} · minimum scale {report['minimum_scale']:.4f}")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", type=int)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--no-render", action="store_true")
    args = parser.parse_args()
    numbers = range(1, 21) if args.all else [args.paper or 1]
    for number in numbers:
        render_one(number, render_images=not args.no_render)


if __name__ == "__main__":
    main()
