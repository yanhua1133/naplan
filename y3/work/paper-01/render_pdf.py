from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path

import fitz

from content import PAPER


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "y3" / "output" / "year3-naplan-style-practice-paper-01.pdf"
RENDER_DIR = ROOT / "y3" / "build" / "paper-01" / "rendered"
LAYOUT_REPORT = ROOT / "y3" / "work" / "paper-01" / "layout-report.json"
INVENTORY = ROOT / "y3" / "work" / "paper-01" / "question-inventory.json"
SOURCE_HASHES = ROOT / "y3" / "source-cache" / "source-hashes.json"

A4 = fitz.paper_rect("a4")
INK = (0.06, 0.18, 0.21)
TEAL = (0.03, 0.42, 0.47)
PALE = (0.84, 0.95, 0.94)
LIGHT = (0.96, 0.99, 0.99)
LINE = (0.52, 0.72, 0.72)
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

    def record(self, label, spare, scale):
        entry = {"label": label, "spare_height": round(float(spare), 2), "scale": round(float(scale), 4)}
        self.entries.append(entry)
        if spare < -0.01:
            raise RuntimeError(f"Overflow: {entry}")
        if scale < 0.89:
            raise RuntimeError(f"Text too compressed: {entry}")


AUDIT = Audit()


def html_box(page, rect, body, label, size=8, align="left", css=""):
    markup = f'<div style="font-size:{size}pt;line-height:1.22;text-align:{align}">{body}</div>'
    spare, scale = page.insert_htmlbox(rect, markup, css=CSS + css, scale_low=0)
    AUDIT.record(label, spare, scale)


def add_page(doc, section, title):
    page = doc.new_page(width=A4.width, height=A4.height)
    number = len(doc)
    page.draw_rect(fitz.Rect(26, 20, 569, 48), color=None, fill=PALE, radius=0.12)
    page.draw_rect(fitz.Rect(32, 27, 76, 43), color=None, fill=TEAL, radius=0.45)
    html_box(page, fitz.Rect(35, 29, 73, 41), '<b style="color:white">Year 3</b>', f"year-{number}", 7.1, "center")
    html_box(page, fitz.Rect(84, 27, 360, 43), f"<b>{section}</b>", f"section-{number}", 8.6)
    html_box(page, fitz.Rect(440, 27, 562, 43), "Practice Paper 01", f"paper-{number}", 7.5, "right")
    html_box(page, fitz.Rect(30, 51, 565, 70), f"<b>{title}</b>", f"title-{number}", 10.5)
    page.draw_line(fitz.Point(27, 816), fitz.Point(568, 816), color=LINE, width=0.55)
    html_box(page, fitz.Rect(30, 820, 430, 833), "Independent NAPLAN-style practice material", f"footer-{number}", 6.2)
    html_box(page, fitz.Rect(530, 820, 563, 833), str(number), f"page-{number}", 6.5, "right")
    return page


def option_table(options):
    letters = "ABCD"
    cells = [f'<td style="width:50%;padding:1pt 4pt 1pt 0"><b>{letters[index]}</b>&nbsp;{option}</td>' for index, option in enumerate(options)]
    return f"<table><tr>{cells[0]}{cells[1]}</tr><tr>{cells[2]}{cells[3]}</tr></table>"


def draw_number(page, number, x, y, radius=8):
    page.draw_circle(fitz.Point(x, y), radius, color=None, fill=TEAL)
    html_box(page, fitz.Rect(x - radius, y - 5, x + radius, y + 5), f'<b style="color:white">{number}</b>', f"qnum-{number}-{x}-{y}", 5.8, "center")


def draw_grammar_item(page, question, number, rect):
    page.draw_line(rect.bl, rect.br, color=(0.84, 0.90, 0.90), width=0.45)
    draw_number(page, number, rect.x0 + 10, rect.y0 + 11, 7.5)
    html_box(page, fitz.Rect(rect.x0 + 23, rect.y0 + 2, rect.x1 - 4, rect.y0 + 35), question["prompt"], f"prompt-{question['id']}", 7.6)
    html_box(page, fitz.Rect(rect.x0 + 25, rect.y0 + 35, rect.x1 - 3, rect.y1 - 3), option_table(question["options"]), f"options-{question['id']}", 6.7)


def draw_spelling_item(page, question, number, rect):
    page.draw_line(rect.bl, rect.br, color=(0.84, 0.90, 0.90), width=0.4)
    draw_number(page, number, rect.x0 + 9, rect.y0 + 10, 7)
    html_box(page, fitz.Rect(rect.x0 + 21, rect.y0 + 1, rect.x1 - 3, rect.y0 + 32), question["prompt"], f"prompt-{question['id']}", 6.85)
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
    html_box(page, fitz.Rect(rect.x0 + 22, rect.y0 + 3, rect.x1 - 3, rect.y0 + 31), question["prompt"], f"prompt-{question['id']}", 6.9)
    html_box(page, fitz.Rect(rect.x0 + 23, rect.y0 + 31, rect.x1 - 3, rect.y1 - 3), option_table(question["options"]), f"options-{question['id']}", 6.0)


def draw_reading_pages(doc):
    for passage in PAPER["reading_passages"]:
        first = int(passage["questions"][0]["id"][1:])
        last = int(passage["questions"][-1]["id"][1:])
        page = add_page(doc, "Reading", f"{passage['title']} · Questions {first}–{last}")
        page.draw_rect(fitz.Rect(31, 75, 564, 430), color=LINE, fill=LIGHT, radius=0.035, width=0.65)
        html_box(page, fitz.Rect(47, 88, 548, 418), f"<h2 style='text-align:center;margin:0 0 7pt 0'>{passage['title']}</h2>{passage_markup(passage)}", f"passage-{passage['id']}", 8.8)
        questions = passage["questions"]
        for index, question in enumerate(questions):
            column, row = index // 3, index % 3
            x0, x1 = (32, 295) if column == 0 else (301, 564)
            y0 = 440 + row * 119
            draw_reading_question(page, question, int(question["id"][1:]), fitz.Rect(x0, y0, x1, y0 + 111))


def draw_tree(page, rect):
    page.draw_rect(rect, color=LINE, fill=LIGHT, radius=0.04, width=0.6)
    page.draw_line(fitz.Point(rect.x0, rect.y1 - 28), fitz.Point(rect.x1, rect.y1 - 38), color=(0.55, 0.75, 0.58), width=10)
    trunk = fitz.Rect(rect.x0 + rect.width * 0.42, rect.y0 + 55, rect.x0 + rect.width * 0.62, rect.y1 - 28)
    page.draw_rect(trunk, color=(0.28, 0.18, 0.12), fill=(0.55, 0.40, 0.28), width=1.5)
    for fx, fy, radius in [(0.30, 0.24, 28), (0.42, 0.18, 32), (0.55, 0.20, 31), (0.68, 0.22, 29)]:
        page.draw_circle(fitz.Point(rect.x0 + rect.width * fx, rect.y0 + rect.height * fy), radius, color=None, fill=(0.34, 0.59, 0.39))
    door = fitz.Rect(trunk.x0 + 13, trunk.y1 - 58, trunk.x1 - 10, trunk.y1)
    page.draw_rect(door, color=INK, fill=(0.05, 0.30, 0.34), radius=0.45, width=1.2)
    page.draw_circle(fitz.Point(door.x1 - 7, door.y0 + 31), 2.4, color=None, fill=(0.95, 0.78, 0.25))


def draw_writing_page(doc):
    writing = PAPER["writing"]
    page = add_page(doc, "Writing", "Narrative Writing Task")
    draw_tree(page, fitz.Rect(35, 80, 292, 310))
    html_box(page, fitz.Rect(45, 317, 285, 367), f"<b>{writing['title']}</b><br>{writing['prompt']}", "writing-prompt", 8.7, "center")
    ideas = "".join(f"<li>{item}</li>" for item in writing["ideas"])
    reminders = "".join(f"<li>{item}</li>" for item in writing["reminders"])
    page.draw_rect(fitz.Rect(35, 380, 292, 792), color=LINE, fill=(1, 1, 1), radius=0.03, width=0.6)
    html_box(page, fitz.Rect(48, 392, 280, 550), f"<b>Plan your story</b><ul>{ideas}</ul>", "writing-ideas", 7.2)
    html_box(page, fitz.Rect(48, 560, 280, 682), f"<b>Remember</b><ul>{reminders}</ul>", "writing-reminders", 7.2)
    html_box(page, fitz.Rect(48, 700, 280, 770), "<b>Check:</b> characters, setting, complication, ending, paragraphs, spelling and punctuation.", "writing-check", 7)
    page.draw_rect(fitz.Rect(307, 80, 560, 792), color=LINE, fill=(1, 1, 1), radius=0.03, width=0.6)
    html_box(page, fitz.Rect(320, 91, 548, 116), "<b>Writing space</b>", "writing-space", 8.5)
    y = 132
    while y < 777:
        page.draw_line(fitz.Point(320, y), fitz.Point(548, y), color=(0.66, 0.78, 0.78), width=0.45)
        y += 21


def draw_visual(page, kind, rect):
    cx, cy = (rect.x0 + rect.x1) / 2, (rect.y0 + rect.y1) / 2
    if kind == "area_grid":
        size = min(14, rect.height / 3.2)
        x0, y0 = cx - size * 2.5, cy - size * 1.5
        for row in range(3):
            for col in range(5):
                page.draw_rect(fitz.Rect(x0 + col * size, y0 + row * size, x0 + (col + 1) * size, y0 + (row + 1) * size), color=INK, fill=PALE, width=0.55)
    elif kind == "fraction_bar":
        width, height = 20, 15
        x0, y0 = cx - width * 4, cy - height / 2
        for index in range(8):
            page.draw_rect(fitz.Rect(x0 + index * width, y0, x0 + (index + 1) * width, y0 + height), color=INK, fill=TEAL if index < 3 else (1, 1, 1), width=0.55)
    elif kind == "square":
        side = min(50, rect.height - 3)
        page.draw_rect(fitz.Rect(cx - side / 2, cy - side / 2, cx + side / 2, cy + side / 2), color=INK, fill=LIGHT, width=1.2)
    elif kind == "cube":
        front = fitz.Rect(cx - 33, cy - 22, cx + 12, cy + 24)
        shift = fitz.Point(19, -14)
        page.draw_rect(front, color=INK, fill=LIGHT, width=1)
        for p1, p2 in [(front.tl, front.tl + shift), (front.tr, front.tr + shift), (front.br, front.br + shift), (front.tl + shift, front.tr + shift), (front.tr + shift, front.br + shift)]:
            page.draw_line(p1, p2, color=INK, width=1)
    elif kind == "map_grid":
        labels = [["", "A", "B", "C", "D"], ["1", "tree", "", "pond", ""], ["2", "", "gate", "bench", ""], ["3", "", "", "", "tree"]]
        cell_w, cell_h = 31, 14
        x0, y0 = cx - cell_w * 2.5, cy - cell_h * 2
        for row, values in enumerate(labels):
            for col, value in enumerate(values):
                box = fitz.Rect(x0 + col * cell_w, y0 + row * cell_h, x0 + (col + 1) * cell_w, y0 + (row + 1) * cell_h)
                page.draw_rect(box, color=INK, fill=PALE if row == 0 or col == 0 else (1, 1, 1), width=0.4)
                html_box(page, box + (1, 2, -1, -1), value, f"map-{row}-{col}-{rect.y0}", 4.8, "center")
    elif kind == "bar_chart":
        bars = [("W", 10), ("B", 14), ("J", 8), ("K", 12)]
        baseline = rect.y1 - 10
        page.draw_line(fitz.Point(rect.x0 + 20, rect.y0 + 3), fitz.Point(rect.x0 + 20, baseline), color=INK, width=0.55)
        page.draw_line(fitz.Point(rect.x0 + 20, baseline), fitz.Point(rect.x1 - 8, baseline), color=INK, width=0.55)
        gap = (rect.width - 55) / 4
        for index, (name, value) in enumerate(bars):
            x = rect.x0 + 28 + index * gap
            height = value * 2.6
            page.draw_rect(fitz.Rect(x, baseline - height, x + 13, baseline), color=INK, fill=TEAL, width=0.4)
            html_box(page, fitz.Rect(x - 2, baseline - height - 9, x + 15, baseline - height), str(value), f"bar-v-{index}-{rect.y0}", 4.5, "center")
            html_box(page, fitz.Rect(x - 4, baseline + 1, x + 17, baseline + 9), name, f"bar-l-{index}-{rect.y0}", 4.5, "center")
    elif kind == "spinner":
        radius = min(34, rect.height / 2 - 2)
        page.draw_circle(fitz.Point(cx, cy), radius, color=INK, fill=LIGHT, width=0.8)
        page.draw_line(fitz.Point(cx - radius, cy), fitz.Point(cx + radius, cy), color=INK, width=0.6)
        page.draw_line(fitz.Point(cx, cy - radius), fitz.Point(cx, cy + radius), color=INK, width=0.6)
        for text, box in [("red", (cx + 2, cy - radius + 5, cx + radius, cy)), ("blue", (cx + 2, cy, cx + radius, cy + radius - 3)), ("blue", (cx - radius, cy, cx - 2, cy + radius - 3)), ("green", (cx - radius, cy - radius + 5, cx - 2, cy))]:
            html_box(page, fitz.Rect(*box), text, f"spinner-{text}-{box[0]}-{box[1]}", 4.5, "center")


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
    html_box(page, fitz.Rect(rect.x0 + 23, option_top, rect.x1 - 3, rect.y1 - 3), option_table(question["options"]), f"options-{question['id']}", 7.0)


def draw_numeracy_pages(doc):
    ranges = [(0, 4), (4, 8), (8, 12), (12, 16), (16, 21), (21, 25), (25, 30)]
    for start, end in ranges:
        questions = PAPER["numeracy"][start:end]
        page = add_page(doc, "Numeracy", f"Questions {start + 1}–{end}")
        if len(questions) == 4:
            positions = [(34, 82, 561, 250), (34, 262, 561, 430), (34, 442, 561, 610), (34, 622, 561, 796)]
        else:
            positions = [(34, 82, 561, 216), (34, 227, 561, 361), (34, 372, 561, 506), (34, 517, 561, 651), (34, 662, 561, 796)]
        for question, coords in zip(questions, positions):
            draw_numeracy_item(page, question, int(question["id"][1:]), fitz.Rect(*coords))


def answer_value(question):
    if "options" not in question:
        return question["answer"]
    return f"{question['answer']} — {question['options']['ABCD'.index(question['answer'])]}"


def draw_answer_entry(page, question, rect, size):
    page.draw_line(rect.bl, rect.br, color=(0.83, 0.89, 0.89), width=0.35)
    text = f"<b>{question['id']} · {answer_value(question)}</b><br>{question['explanation']}"
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
    draw_answer_page(doc, "Conventions of Language · L1–L50", language, 3, 6.15)
    draw_answer_page(doc, "Reading · R1–R30", reading, 2, 6.35)
    extra = "<b>Writing review:</b> Check for a clear opening, complication and ending; paragraphing; precise vocabulary; complete sentences; controlled punctuation; and carefully checked spelling."
    draw_answer_page(doc, "Numeracy · N1–N30", numeracy, 2, 6.25, extra)


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


def main():
    validate_cache()
    language, reading, numeracy = validate_content()
    document = fitz.open()
    draw_language_pages(document)
    draw_reading_pages(document)
    draw_writing_page(document)
    draw_numeracy_pages(document)
    assert len(document) == 17
    draw_answers(document)
    assert len(document) == 20
    document.set_metadata({"title": PAPER["title"], "author": "Independent practice material", "subject": "Year 3 NAPLAN-style practice"})
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document.save(OUTPUT, garbage=4, deflate=True)
    document.close()
    render_pages(OUTPUT)
    question_ids = [question["id"] for question in language + reading + numeracy]
    INVENTORY.write_text(json.dumps({"paper": PAPER["title"], "reference_pages": 20, "student_pages": 17, "appendix_pages": 3, "scored_question_counts": {"language": 50, "reading": 30, "numeracy": 30}, "writing_tasks": 1, "question_ids": question_ids, "answer_ids": question_ids}, indent=2) + "\n", encoding="utf-8")
    LAYOUT_REPORT.write_text(json.dumps({"pdf": str(OUTPUT.relative_to(ROOT)), "pages": 20, "layout_entries": AUDIT.entries, "minimum_scale": min(entry["scale"] for entry in AUDIT.entries), "negative_spare_entries": [entry for entry in AUDIT.entries if entry["spare_height"] < 0]}, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    print("Pages: 20; questions: 110; writing tasks: 1")
    print(f"Minimum text scale: {min(entry['scale'] for entry in AUDIT.entries):.4f}")


if __name__ == "__main__":
    main()
