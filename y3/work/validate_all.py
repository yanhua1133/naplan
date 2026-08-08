from __future__ import annotations

import hashlib
import html
import json
import math
import re
import sys
from collections import defaultdict
from html.parser import HTMLParser
from itertools import permutations
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content_factory import ANIMALS, FORCE_CONTEXTS, NAMES, PARTNERS, PLACES, build_all_papers


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "y3" / "output"
GENERATED_DIR = ROOT / "y3" / "work" / "generated"
SOURCE_HASHES = ROOT / "y3" / "source-cache" / "source-hashes.json"
BLUEPRINT = ROOT / "y3" / "source-cache" / "year3-reference-blueprint.md"
REPORT_PATH = ROOT / "y3" / "work" / "batch-validation.json"
ISSUE_LOG = ROOT / "y3" / "work" / "batch-issue-log.md"

LANGUAGE_KINDS = {
    **{f"L{number}": "mcq" for number in range(1, 26)},
    "L2": "circle", "L4": "circle", "L7": "cloze",
    **{f"L{number}": "dictation" for number in range(26, 41)},
    **{f"L{number}": "spelling" for number in range(41, 51)},
}
READING_KINDS = {
    **{f"R{number}": "mcq" for number in range(1, 40)},
    "R3": "true_false", "R7": "order", "R14": "match", "R16": "cloze",
    "R19": "match", "R26": "cloze", "R32": "select_two", "R35": "match", "R36": "order",
}
NUMERACY_KINDS = {
    **{f"N{number}": "mcq" for number in range(1, 37)},
    **{f"N{number}": "open" for number in [2, 6, 13, 14, 21, 23, 25, 27, 28, 33, 36]},
    "N20": "select_two", "N22": "select_two",
}
READING_RANGES = [(1, 6), (7, 12), (13, 18), (19, 24), (25, 29), (30, 34), (35, 39)]
NUMERACY_RANGES = [(1, 5), (6, 9), (10, 15), (16, 19), (20, 23), (24, 27), (28, 33), (34, 36)]


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def plain_text(value):
    parser = TextExtractor()
    parser.feed(str(value))
    return html.unescape(" ".join(parser.parts))


def normalise(value):
    value = plain_text(value).casefold().replace("’", "'").replace("–", "-").replace("−", "-")
    value = re.sub(r"\s+", " ", value).strip()
    return re.sub(r"\s+([,.;:!?])", r"\1", value)


def validate_source_hashes():
    payload = json.loads(SOURCE_HASHES.read_text(encoding="utf-8"))
    assert len(payload["files"]) == 20
    for item in payload["files"]:
        path = ROOT / "y3" / "orig" / item["file"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], item["file"]
    blueprint = BLUEPRINT.read_text(encoding="utf-8")
    for locked in ["50 questions", "39 questions", "36 questions", "4 Language + 7 Reading + 1 Writing + 8 Numeracy"]:
        assert locked in blueprint
    return len(payload["files"])


def all_questions(paper):
    return paper["language"] + [item for passage in paper["reading_passages"] for item in passage["questions"]] + paper["numeracy"]


def validate_mcq(item, expected_count=4):
    assert item["kind"] == "mcq"
    assert len(item["options"]) == expected_count, (item["id"], item["options"])
    assert len(set(item["options"])) == expected_count
    assert 0 <= item["answer_index"] < expected_count
    assert item["options"][item["answer_index"]] == str(item["answer"])


def expected_numeracy_answers(p):
    expected = {}
    expected[1] = str(8 + p)
    red, blue = 7 + p % 5, 6 + (p * 2) % 5
    expected[2] = str(red + blue)
    start, step = 12 + p, 4 + p % 4
    expected[3] = str(start + step * 4)
    factor_a, factor_b = 3 + p % 5, 4 + (p + 1) % 4
    expected[4] = " + ".join([str(factor_b)] * factor_a)
    rows, cols, cut = 4 + p % 3, 5 + p % 4, 2 + p % 3
    expected[5] = str(rows * cols - cut)
    first, decrease = 16 + p % 5, 3 + p % 3
    expected[6] = str(first - 3 * decrease)
    expected[7] = str(2 + p % 3)
    expected[8] = "circle"
    digit_sets = [
        ("7", "4", "3"), ("6", "5", "1"), ("7", "2", "5"), ("6", "3", "1"), ("7", "5", "2"),
        ("6", "4", "3"), ("7", "3", "1"), ("6", "5", "3"), ("7", "4", "1"), ("6", "3", "2"),
        ("7", "6", "5"), ("5", "4", "3"), ("7", "2", "1"), ("6", "5", "4"), ("7", "5", "3"),
        ("6", "2", "1"), ("7", "4", "5"), ("5", "3", "2"), ("7", "6", "1"), ("6", "4", "1"),
    ]
    digits = digit_sets[p - 1]
    candidates = [int("".join(order)) for order in permutations(digits) if int(order[-1]) % 2 == 1 and int("".join(order)) < 800]
    expected[9] = str(max(candidates))
    expected[10] = "2 of 6 equal parts"
    expected[11] = str((60 + p * 2) - (24 + p))
    start_hour, start_minute = 8 + p % 3, [10, 15, 20, 25][p % 4]
    elapsed = 35 + (p % 3) * 5
    event_minutes = start_hour * 60 + start_minute + elapsed - 10
    expected[12] = f"{event_minutes // 60}:{event_minutes % 60:02d}"
    expected[13] = str((38 + p) + (27 + 2 * p))
    expected[14] = str((75 + p * 2) - (48 + p))
    prices = [2.5 + p * .1, 3.2 + p * .1, 4.1 + p * .1, 5.0 + p * .1]
    expected[15] = f"${prices[3] - prices[1]:.2f}"
    clock_hour, clock_minute = 2 + p % 8, 0 if p % 2 else 30
    finish = clock_hour * 60 + clock_minute + 30
    expected[16] = f"{finish // 60}:{finish % 60:02d}"
    expected[17] = ["library", "office", "art room", "hall", "garden"][p % 5]
    expected[18] = ["A", "H", "I", "M", "O", "T", "U", "V", "W", "X"][p % 10]
    unit_cost = 3 + p % 4
    budget = unit_cost * (5 + p % 5) + unit_cost - 1
    expected[19] = str(budget // unit_cost)
    expected[20] = ["A", "C"]
    expected[21] = str((7 + p % 6) * (3 + p % 4))
    seq_start, seq_step = 100 + p * 3, 7 + p % 4
    expected[22] = [str(seq_start - seq_step * 3), str(seq_start - seq_step * 5)]
    tens = 2 + p % 2
    expected[23] = str(tens * 10 + tens + 3)
    expected[24] = "2"
    three_cost = 6 + p * .3
    expected[25] = f"${three_cost / 3 * 5:.2f}"
    expected[26] = str((3 + p % 4) * (24 + p % 5))
    expected[27] = str((24 + p % 7) - (11 + p % 5))
    expected[28] = str((40 + p * 2) - (7 + p % 6))
    line_start, line_step = 20 + p, 5 + p % 4
    expected[29] = ", ".join(str(line_start + line_step * index) for index in range(4))
    dozens, group = 4 + p % 5, 7 + p % 4
    expected[30] = str(dozens * 12 % group)
    expected[31] = f"{(34 + p * 2) - (18 + p)} kg"
    pattern_end, pattern_step = 70 + p * 2, 6 + p % 4
    expected[32] = str(pattern_end - pattern_step * 3)
    known = [18 + p, 21 + p, 16 + p]
    expected[33] = str((80 + p * 3) - sum(known))
    expected[34] = "5"
    expected[35] = "Spinner C"
    expected[36] = f"${(5 + p % 6) * 2 + (4 + p % 5)}"
    return expected


def validate_language(paper):
    items = paper["language"]
    assert [item["id"] for item in items] == [f"L{number}" for number in range(1, 51)]
    for item in items:
        assert item["kind"] == LANGUAGE_KINDS[item["id"]], (paper["paper_number"], item["id"], item["kind"])
        if item["kind"] == "mcq":
            validate_mcq(item)
    assert items[0]["answer"] == "an"
    assert items[1]["answer"] in plain_text(items[1]["sentence"])
    assert items[3]["answer"] in plain_text(items[3]["sentence"])
    assert [value.casefold() for value in items[6]["answer"]] == ["an", "a", "the"]
    assert items[15]["answer"] == "A" and items[19]["answer"] == "A" and items[24]["answer"] == "A"
    assert [item["spelling_type"] for item in items[25:]] == [*(["dictation"] * 15), *(["underlined"] * 5), *(["identify"] * 5)]
    for item in items[25:40]:
        assert item["answer"] == item["spoken_word"]
        assert not item["prompt"] or item["spoken_word"].casefold() not in plain_text(item["prompt"]).casefold()
    for item in items[40:45]:
        assert item["prompt"].count("text-decoration:underline") == 1
        assert item["incorrect_word"].casefold() in plain_text(item["prompt"]).casefold()
        assert item["answer"].casefold() != item["incorrect_word"].casefold()
    for item in items[45:]:
        assert "text-decoration:underline" not in item["prompt"]
        assert item["incorrect_word"].casefold() in plain_text(item["prompt"]).casefold()
        assert item["answer"].casefold() != item["incorrect_word"].casefold()


def validate_reading(paper):
    passages = paper["reading_passages"]
    assert len(passages) == 7
    for passage, (start, end) in zip(passages, READING_RANGES):
        assert [item["id"] for item in passage["questions"]] == [f"R{number}" for number in range(start, end + 1)]
    items = [item for passage in passages for item in passage["questions"]]
    for item in items:
        assert item["kind"] == READING_KINDS[item["id"]], (paper["paper_number"], item["id"], item["kind"])
        if item["kind"] == "mcq":
            validate_mcq(item)
    assert items[2]["answer"] == [True, False, True]
    assert items[6]["answer"] == [2, 4, 1, 3]
    assert items[13]["answer"] == ["makes the heart beat faster", "makes muscles work against resistance", "helps joints move comfortably"]
    assert len(items[15]["answer"]) == 2 and all(value in items[15]["word_bank"] for value in items[15]["answer"])
    assert len(items[18]["answer"]) == 4
    assert len(items[25]["answer"]) == 2 and all(value in items[25]["word_bank"] for value in items[25]["answer"])
    assert len(items[31]["answer"]) == 2 and all(value in items[31]["options"] for value in items[31]["answer"])
    assert items[34]["answer"] == ["box", "folders", "room"]
    assert items[35]["answer"] == [3, 1, 4, 2]

    p1 = plain_text(passages[0]["text"])
    assert "friction acts in the opposite direction" in p1
    assert "friction" in normalise(items[0]["answer"]) and "movement" in normalise(items[0]["answer"])
    smooth = FORCE_CONTEXTS[paper["paper_number"] - 1][1]
    rough = FORCE_CONTEXTS[paper["paper_number"] - 1][2]
    assert items[3]["answer"] == smooth and items[11]["answer"] == rough
    trial_match = re.search(r"Repeat the trial (\d+) times", " ".join(passages[1]["steps"]))
    assert trial_match and items[7]["answer"] == trial_match.group(1)
    health = normalise(passages[2]["text"])
    assert all(token in normalise(items[12]["answer"]) for token in ["sitting", "moving very little"])
    assert normalise(items[14]["answer"]) in health
    counts = passages[3]["data"]["values"]
    assert items[18]["answer"] == [str(value) for value in counts]
    assert items[23]["cross_text"] is True
    rhyme = " ".join(passages[4]["lines"])
    assert all(normalise(value) in normalise(rhyme) for value in items[25]["answer"])
    review = plain_text(passages[5]["text"])
    author_match = re.search(r" by ([A-Z][A-Za-z]+ [A-Z][A-Za-z]+)", review)
    assert author_match and items[29]["answer"] == author_match.group(1)
    assert review.count("★") == int(re.search(r"(\d+) out of 5", items[33]["answer"]).group(1))
    narrative = normalise(passages[6]["text"])
    for phrase in ["heavy box", "dusty folders", "crowded room"]:
        assert phrase in narrative


def validate_numeracy(paper):
    items = paper["numeracy"]
    assert [item["id"] for item in items] == [f"N{number}" for number in range(1, 37)]
    expected = expected_numeracy_answers(paper["paper_number"])
    for item in items:
        number = int(item["id"][1:])
        assert item["kind"] == NUMERACY_KINDS[item["id"]], (paper["paper_number"], item["id"], item["kind"])
        assert item["answer"] == expected[number], (paper["paper_number"], item["id"], item["answer"], expected[number])
        if item["kind"] == "mcq":
            validate_mcq(item, 5 if number in {10, 11, 17, 30} else 4)
        elif item["kind"] == "select_two":
            assert len(item["answer"]) == 2 and all(value in item["options"] for value in item["answer"])
    visual_ids = {5, 6, 7, 8, 10, 15, 16, 17, 18, 20, 21, 24, 27, 29, 31, 32, 33, 34, 35, 36}
    assert visual_ids == {int(item["id"][1:]) for item in items if item.get("visual")}


def complete_question_fingerprint(item):
    payload = [
        normalise(item.get("prompt", "")), item.get("options"), item.get("statements"), item.get("choices"),
        item.get("left"), item.get("right"), item.get("word_bank"), item.get("spoken_word"), item.get("visual"),
    ]
    return json.dumps(payload, sort_keys=True, ensure_ascii=False)


def validate_content_model(papers):
    fingerprints = defaultdict(list)
    passage_hashes = defaultdict(list)
    writing_prompts = defaultdict(list)
    all_pdf_question_count = 0
    for paper in papers:
        validate_language(paper)
        validate_reading(paper)
        validate_numeracy(paper)
        assert "comes to life" in paper["writing"]["prompt"]
        assert any(toy in paper["writing"]["prompt"] for toy in ["train", "doll", "robot", "dinosaur", "horse", "bear", "aeroplane", "puppet", "mouse", "dragon", "figure", "boat", "koala", "astronaut", "marionette", "duck", "engine", "clown", "knight", "penguin"])
        writing_prompts[normalise(paper["writing"]["prompt"])].append(paper["paper_number"])
        for passage in paper["reading_passages"]:
            body = passage.get("text") or passage.get("intro") or " ".join(passage.get("lines", []))
            passage_hashes[normalise(body)].append((paper["paper_number"], passage["id"]))
        for item in all_questions(paper):
            fingerprints[complete_question_fingerprint(item)].append((paper["paper_number"], item["id"]))
        all_pdf_question_count += len(all_questions(paper))
    assert all_pdf_question_count == 2500
    duplicate_questions = [refs for refs in fingerprints.values() if len(refs) > 1]
    duplicate_passages = [refs for refs in passage_hashes.values() if len(refs) > 1]
    duplicate_writing = [refs for refs in writing_prompts.values() if len(refs) > 1]
    assert not duplicate_questions, duplicate_questions[:5]
    assert not duplicate_passages, duplicate_passages[:5]
    assert not duplicate_writing, duplicate_writing[:5]
    return {
        "unique_complete_questions": len(fingerprints),
        "unique_reading_passages": len(passage_hashes),
        "unique_writing_prompts": len(writing_prompts),
    }


def validate_pdf(paper):
    number = paper["paper_number"]
    pdf_path = OUTPUT_DIR / f"year3-naplan-style-practice-paper-{number:02d}.pdf"
    inventory_path = GENERATED_DIR / f"paper-{number:02d}" / "question-inventory.json"
    layout_path = GENERATED_DIR / f"paper-{number:02d}" / "layout-report.json"
    render_dir = ROOT / "y3" / "build" / f"paper-{number:02d}" / "rendered"
    document = fitz.open(pdf_path)
    assert len(document) == 26
    assert all(abs(page.rect.width - 595.276) < .5 and abs(page.rect.height - 841.89) < .5 for page in document)
    assert all(len(page.get_text().strip()) > 20 for page in document)
    student_text = normalise("\n".join(page.get_text() for page in list(document)[:20]))
    appendix_text = normalise("\n".join(page.get_text() for page in list(document)[20:]))
    questions = all_questions(paper)
    missing_prompts = []
    for item in questions:
        if item["kind"] == "dictation":
            continue
        token = normalise(item["prompt"])
        if token not in student_text:
            missing_prompts.append(item["id"])
    assert not missing_prompts, (number, missing_prompts)
    for passage in paper["reading_passages"]:
        body = passage.get("text") or passage.get("intro") or " ".join(passage.get("lines", []))
        fragments = [part.strip() for part in re.split(r"[.!?]", plain_text(body)) if len(part.split()) >= 4]
        assert all(normalise(fragment) in student_text for fragment in fragments), (number, passage["id"])
    for item in questions:
        assert normalise(item["id"]) in appendix_text
        assert normalise(str(item["answer"])) or item["kind"] == "dictation"
        assert normalise(item["explanation"]) in appendix_text, (number, item["id"])
    dictation_area = normalise(document[3].get_text(clip=fitz.Rect(30, 100, 565, 365)))
    assert all(normalise(item["spoken_word"]) not in dictation_area for item in paper["language"][25:40])

    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    assert inventory["reference_student_pages"] == 20
    assert inventory["student_pages"] == 20
    assert inventory["appendix_pages"] == 6
    assert inventory["total_pages"] == 26
    assert inventory["scored_question_counts"] == {"language": 50, "reading": 39, "numeracy": 36}
    assert inventory["question_ids"] == [item["id"] for item in questions]
    assert inventory["answer_ids"] == inventory["question_ids"]

    layout = json.loads(layout_path.read_text(encoding="utf-8"))
    assert layout["student_pages"] == 20 and layout["appendix_pages"] == 6 and layout["pages"] == 26
    assert layout["minimum_body_font"] >= 7.4
    assert layout["minimum_diagram_font"] >= 6.8
    assert layout["minimum_appendix_font"] >= 7.4
    assert layout["minimum_scale"] == 1.0
    assert not layout["negative_spare_entries"]
    rendered = sorted(render_dir.glob("page-*.png"))
    assert len(rendered) == 26
    page_hashes = []
    for page in document:
        pixmap = page.get_pixmap(matrix=fitz.Matrix(.7, .7), alpha=False)
        page_hashes.append(hashlib.sha256(pixmap.samples).hexdigest())
    assert len(set(page_hashes)) == 26
    return {
        "paper": number,
        "pdf": str(pdf_path.relative_to(ROOT)),
        "bytes": pdf_path.stat().st_size,
        "student_pages": 20,
        "appendix_pages": 6,
        "pages": 26,
        "questions": 125,
        "minimum_body_font": layout["minimum_body_font"],
        "minimum_diagram_font": layout["minimum_diagram_font"],
        "minimum_appendix_font": layout["minimum_appendix_font"],
        "minimum_scale": layout["minimum_scale"],
        "page_hashes": page_hashes,
        "pdf_sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
    }


def write_issue_log():
    ISSUE_LOG.write_text(
        "# Batch Issue Log\n\n"
        "Status: all critical and major issues found during the source-structure audit are closed.\n\n"
        "## Closed root causes\n\n"
        "- Replaced the incorrect cached structure of 30 Reading and 30 Numeracy items with the scan-verified 39 Reading and 36 Numeracy items.\n"
        "- Restored seven Reading texts and eight Numeracy pages so the student paper is exactly 20 pages before the appendix.\n"
        "- Restored non-MCQ response forms: circle-word, cloze, true/false, ordering, matching, select-two and open response.\n"
        "- Corrected spelling prompts so every underlined item visibly underlines exactly one error and every correction restores its sentence.\n"
        "- Removed duplicate complete questions across the 20-paper batch.\n"
        "- Added independent position-by-position answer recalculation and final-PDF text/layout checks.\n\n"
        "## Source limitation\n\n"
        "- The teacher dictation list corresponding to source questions L26–L40 was not supplied in the 20 student-page scans. The generated words therefore match the visible Year 3 spelling format and difficulty but cannot reproduce an unavailable teacher list.\n",
        encoding="utf-8",
    )


def main():
    source_hash_count = validate_source_hashes()
    papers = build_all_papers()
    content_report = validate_content_model(papers)
    pdf_reports = [validate_pdf(paper) for paper in papers]
    pdf_hashes = [report["pdf_sha256"] for report in pdf_reports]
    page_hashes = [page_hash for report in pdf_reports for page_hash in report.pop("page_hashes")]
    assert len(set(pdf_hashes)) == 20
    assert len(set(page_hashes)) == 520
    result = {
        "status": "passed",
        "papers": 20,
        "student_pages": 400,
        "appendix_pages": 120,
        "pages": 520,
        "scored_questions": 2500,
        "writing_tasks": 20,
        "source_hashes_verified": source_hash_count,
        "ocr_rerun": False,
        "unique_pdf_hashes": len(set(pdf_hashes)),
        "unique_rendered_page_hashes": len(set(page_hashes)),
        **content_report,
        "pdf_reports": pdf_reports,
    }
    REPORT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    write_issue_log()
    print(json.dumps({key: value for key, value in result.items() if key != "pdf_reports"}, indent=2))


if __name__ == "__main__":
    main()
