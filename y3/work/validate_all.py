from __future__ import annotations

import hashlib
import html
import json
import re
import statistics
import sys
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path

import fitz
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from content_factory import NAMES, PARTNERS, PLACES, build_all_papers

OUTPUT_DIR = ROOT / "y3" / "output"
GENERATED_DIR = ROOT / "y3" / "work" / "generated"
SOURCE_HASHES = ROOT / "y3" / "source-cache" / "source-hashes.json"
REPORT_PATH = ROOT / "y3" / "work" / "batch-validation.json"
LETTERS = "ABCD"


def normalise(value):
    value = re.sub(r"</?[A-Za-z][^>]*>", " ", str(value))
    value = html.unescape(value)
    for ligature, replacement in {"ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl", "ﬀ": "ff"}.items():
        value = value.replace(ligature, replacement)
    value = value.replace("−", "-").replace("___", " ")
    return re.sub(r"[^a-z0-9$]+", " ", value.lower()).strip()


def word_count(value):
    return len(re.findall(r"[A-Za-z0-9]+", re.sub(r"</?[A-Za-z][^>]*>", " ", str(value))))


def edit_distance(left, right):
    previous = list(range(len(right) + 1))
    for row, left_character in enumerate(left, start=1):
        current = [row]
        for column, right_character in enumerate(right, start=1):
            current.append(min(
                current[-1] + 1,
                previous[column] + 1,
                previous[column - 1] + (left_character != right_character),
            ))
        previous = current
    return previous[-1]


def plain_text(value):
    return html.unescape(re.sub(r"</?[A-Za-z][^>]*>", "", str(value)))


def structural_normalise(value):
    value = normalise(value)
    replacements = sorted(
        [*NAMES, *PARTNERS, *PLACES],
        key=len,
        reverse=True,
    )
    for replacement in replacements:
        replacement_key = normalise(replacement)
        value = re.sub(rf"\b{re.escape(replacement_key)}\b", " <context> ", value)
    value = re.sub(r"\b\d+(?: \d+)*\b", " <number> ", value)
    value = re.sub(r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", " <day> ", value)
    return re.sub(r"\s+", " ", value).strip()




def answer_value(question):
    if "options" not in question:
        return question["answer"]
    return question["options"][LETTERS.index(question["answer"])]


def validate_source_hashes():
    cache = json.loads(SOURCE_HASHES.read_text(encoding="utf-8"))
    assert cache["cache_status"] == "verified"
    assert cache["ocr_policy"] == "one-time"
    assert len(cache["files"]) == 20
    for item in cache["files"]:
        source = ROOT / "y3" / "orig" / item["file"]
        assert source.stat().st_size == item["bytes"], item["file"]
        assert hashlib.sha256(source.read_bytes()).hexdigest() == item["sha256"], item["file"]
    return len(cache["files"])


def passage_body(passage):
    parts = [passage.get("intro", "")]
    parts.extend(passage.get("text", []))
    parts.extend(passage.get("materials", []))
    parts.extend(passage.get("steps", []))
    parts.extend(passage.get("lines", []))
    parts.extend(" ".join(row) for row in passage.get("table", []))
    return " ".join(parts)


def expected_numeracy_answers(p):
    start = 120 + p * 7
    step = 8 + p % 5
    digit = 6 + p % 3
    a = 410 + p * 3
    b = 460 + p * 2
    add_a = 240 + p * 4
    add_b = 130 + p * 3
    top = 620 + p * 5
    bottom = 270 + p * 2
    groups = 5 + p % 4
    each = 6 + p % 5
    children = 3 + p % 4
    each_share = 6 + p % 5
    odd = 41 + 2 * p
    twos = 2 + p % 4
    ones = 3 + (p * 2) % 5
    hour = 8 + p % 3
    minute = [10, 20, 25, 35, 40][p % 5]
    duration = [20, 25, 30, 35][p % 4]
    finish_h, finish_m = divmod(hour * 60 + minute + duration, 60)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    start_day_index = p % 7
    offset = 8 + p % 6
    metres = 2 + p % 7
    length = 6 + p % 6
    width = 3 + p % 5
    rows = 2 + p % 3
    cols = 4 + p % 4
    litres = 1 + p % 4
    heavy = 900 + p * 20
    light = 600 + p * 10
    total_parts = 6 + (p % 4) * 2
    shaded = 2 + p % (total_parts - 3)
    even_number = 40 + p * 2
    shape = "square" if p % 2 else "rectangle"
    target = ["pond", "bench", "gate", "tree"][p % 4]
    values = [10 + p, 15 + p * 2, 12 + p, 8 + p]
    labels = ["Monday", "Tuesday", "Wednesday", "Thursday"]
    bars = [8 + p, 11 + p, 6 + p, 10 + p]
    spinner_counts = [1, 2 + p % 3, 1, 1]
    colours = ["red", "blue", "green", "yellow"]
    pattern_step = 3 + p % 5
    pattern_start = 2 + p
    left = 18 + p
    target_sum = 45 + p * 2
    rows_bus = 4 + p % 4
    seats_each = 4 + (p + 1) % 3
    empty = 2 + p % 4
    seedlings = 42 + p * 3
    planted_rows = 4 + p % 4
    per_row = 5 + p % 3
    return [
        str(start + 3 * step),
        str(digit * 100),
        f"{a} < {b}",
        str(add_a + add_b),
        str(top - bottom),
        str(groups * each),
        str(each_share),
        str(odd),
        "7",
        f"${twos * 2 + ones}",
        f"{finish_h}:{finish_m:02d} am",
        days[(start_day_index + offset) % 7],
        f"{metres * 100} cm",
        f"{2 * (length + width)} cm",
        str(rows * cols),
        f"{litres * 1000} mL",
        f"{heavy - light} g",
        f"{shaded}/{total_parts}",
        str(even_number // 2),
        str(4 if shape == "square" else 2),
        "an acute angle",
        "6",
        target,
        labels[max(range(4), key=lambda index: values[index])],
        str(bars[1] - bars[0]),
        colours[max(range(4), key=lambda index: spinner_counts[index])],
        str(pattern_start + 4 * pattern_step),
        str(target_sum - left),
        str(rows_bus * seats_each - empty),
        str(seedlings - planted_rows * per_row),
    ]


def validate_content_model(papers):
    prompt_registry = {}
    structural_prompt_registry = {}
    prompts_by_position = {}
    passage_registry = {}
    writing_registry = {}
    length_data = {"grammar": [], "spelling": [], "reading_questions": [], "numeracy": [], "P1": [], "P2": [], "P3": [], "P4": [], "P5": []}
    visual_ids = {"N15", "N18", "N20", "N22", "N23", "N25", "N26"}

    for paper in papers:
        number = paper["paper_number"]
        language = paper["language"]
        reading = [question for passage in paper["reading_passages"] for question in passage["questions"]]
        numeracy = paper["numeracy"]
        assert [question["id"] for question in language] == [f"L{value}" for value in range(1, 51)]
        assert [question["id"] for question in reading] == [f"R{value}" for value in range(1, 31)]
        assert [question["id"] for question in numeracy] == [f"N{value}" for value in range(1, 31)]
        assert len(paper["reading_passages"]) == 5
        assert all(len(passage["questions"]) == 6 for passage in paper["reading_passages"])
        assert {question["id"] for question in numeracy if question.get("visual")} == visual_ids
        assert " drew " in f" {normalise(language[0]['prompt'])} "
        assert " belonging to " in f" {normalise(language[6]['prompt'])} "
        assert "move towards the shelter" in normalise(answer_value(language[7]))
        assert "was placed beside" in normalise(answer_value(language[17]))

        questions = language + reading + numeracy
        for question in questions:
            prompt_key = normalise(question["prompt"])
            assert prompt_key not in prompt_registry, (number, question["id"], prompt_registry.get(prompt_key))
            prompt_registry[prompt_key] = [number, question["id"]]
            structural_key = structural_normalise(question["prompt"])
            assert structural_key not in structural_prompt_registry, (
                number,
                question["id"],
                structural_prompt_registry.get(structural_key),
            )
            structural_prompt_registry[structural_key] = [number, question["id"]]
            prompts_by_position.setdefault(question["id"], []).append(structural_key)
            assert question["prompt"].strip()
            assert question["answer"].strip()
            assert question["explanation"].strip()
            if "options" in question:
                assert len(question["options"]) == 4
                assert len(set(question["options"])) == 4
                assert question["answer"] in LETTERS
                assert answer_value(question).strip()

        spelling = language[25:]
        assert [question["spelling_type"] for question in spelling] == [
            *(["dictation"] * 15),
            *(["underlined"] * 5),
            *(["identify"] * 5),
        ]
        for question in spelling[:15]:
            assert question["spoken_word"] == question["answer"]
            assert normalise(question["spoken_word"]) in normalise(question["spoken_sentence"])
            assert "incorrect_word" not in question
            assert "underline" not in normalise(question["prompt"])
        for question in spelling[15:20]:
            assert question["prompt"].count("text-decoration:underline") == 1
            assert normalise(question["incorrect_word"]) != normalise(question["answer"])
            assert normalise(question["incorrect_word"]) in normalise(question["prompt"])
            assert normalise(question["answer"]) in normalise(question["correct_sentence"])
        for question in spelling[20:]:
            assert "text-decoration:underline" not in question["prompt"]
            assert normalise(question["incorrect_word"]) != normalise(question["answer"])
            assert normalise(question["incorrect_word"]) in normalise(question["prompt"])
            assert normalise(question["answer"]) in normalise(question["correct_sentence"])
        for question in spelling:
            assert normalise(question["answer"]) in normalise(question["explanation"])
        for question in spelling[15:]:
            wrong = question["incorrect_word"]
            correct = question["answer"]
            assert 1 <= edit_distance(wrong.lower(), correct.lower()) <= 2
            assert not re.search(r"(.)\1\1", wrong.lower())
            restored = re.sub(
                rf"\b{re.escape(wrong)}\b",
                correct,
                plain_text(question["prompt"]),
                count=1,
                flags=re.IGNORECASE,
            )
            assert normalise(restored) == normalise(question["correct_sentence"])

        expected_answers = expected_numeracy_answers(number)
        actual_answers = [answer_value(question) for question in numeracy]
        assert actual_answers == expected_answers, (number, list(zip(actual_answers, expected_answers)))

        for passage in paper["reading_passages"]:
            body = passage_body(passage)
            key = normalise(body)
            assert key not in passage_registry
            passage_registry[key] = [number, passage["id"]]
            length_data[passage["id"]].append(word_count(body))
            assert " the the " not in f" {body.lower()} "
            assert not re.search(r"\b(\w+)\s+\1\b", plain_text(body), re.IGNORECASE)
        narrative = paper["reading_passages"][2]
        narrative_name = narrative["text"][0].split()[0]
        assert f"when {narrative_name.lower()} noticed" not in narrative["text"][0]
        assert "dust lay everywhere" not in normalise(passage_body(narrative))
        poem = paper["reading_passages"][4]
        assert normalise(answer_value(poem["questions"][4])) in normalise(" ".join(poem["lines"]))
        assert "taps a" not in normalise(" ".join(poem["lines"]))
        writing_key = normalise(paper["writing"]["prompt"])
        assert writing_key not in writing_registry
        writing_registry[writing_key] = number

        length_data["grammar"].extend(word_count(question["prompt"] + " " + " ".join(question["options"])) for question in language[:25])
        length_data["spelling"].extend(
            word_count(question["prompt"])
            for question in language[40:]
        )
        length_data["reading_questions"].extend(word_count(question["prompt"] + " " + " ".join(question["options"])) for question in reading)
        length_data["numeracy"].extend(word_count(question["prompt"] + " " + " ".join(question["options"])) for question in numeracy)

    assert len(prompt_registry) == 2200
    assert len(structural_prompt_registry) == 2200
    same_position_similarity = {
        question_id: statistics.mean(
            SequenceMatcher(None, left, right).ratio()
            for left, right in combinations(prompts, 2)
        )
        for question_id, prompts in prompts_by_position.items()
    }
    assert len(same_position_similarity) == 110
    assert max(same_position_similarity.values()) < 0.90, sorted(
        same_position_similarity.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:10]
    assert len(passage_registry) == 100
    assert len(writing_registry) == 20
    assert min(length_data["grammar"]) >= 18 and max(length_data["grammar"]) <= 58
    assert min(length_data["spelling"]) >= 5 and max(length_data["spelling"]) <= 14
    assert min(length_data["reading_questions"]) >= 20 and max(length_data["reading_questions"]) <= 52
    assert min(length_data["numeracy"]) >= 16 and max(length_data["numeracy"]) <= 46
    bands = {"P1": (145, 180), "P2": (105, 140), "P3": (210, 245), "P4": (40, 70), "P5": (70, 100)}
    for passage_id, (low, high) in bands.items():
        assert min(length_data[passage_id]) >= low
        assert max(length_data[passage_id]) <= high

    return {
        "unique_question_prompts": len(prompt_registry),
        "unique_structural_question_prompts": len(structural_prompt_registry),
        "maximum_same_position_similarity": max(same_position_similarity.values()),
        "same_position_similarity_threshold": 0.90,
        "unique_reading_passages": len(passage_registry),
        "unique_writing_prompts": len(writing_registry),
        "word_count_ranges": {key: {"min": min(values), "max": max(values), "average": round(sum(values) / len(values), 2)} for key, values in length_data.items()},
        "independently_recalculated_numeracy_answers": 600,
    }


def fragments_for_passage(passage):
    fragments = [passage["title"], passage.get("intro", "")]
    fragments.extend(passage.get("text", []))
    fragments.extend(passage.get("materials", []))
    fragments.extend(passage.get("steps", []))
    fragments.extend(passage.get("lines", []))
    fragments.extend(cell for row in passage.get("table", []) for cell in row)
    return [fragment for fragment in fragments if normalise(fragment)]


def validate_pdf(paper):
    number = paper["paper_number"]
    pdf_path = OUTPUT_DIR / f"year3-naplan-style-practice-paper-{number:02d}.pdf"
    inventory_path = GENERATED_DIR / f"paper-{number:02d}" / "question-inventory.json"
    layout_path = GENERATED_DIR / f"paper-{number:02d}" / "layout-report.json"
    render_dir = ROOT / "y3" / "build" / f"paper-{number:02d}" / "rendered"

    document = fitz.open(pdf_path)
    reader = PdfReader(str(pdf_path))
    assert len(document) == 26
    assert len(reader.pages) == 26
    for page_number, page in enumerate(document, start=1):
        assert abs(page.rect.width - 595.276) < 0.5
        assert abs(page.rect.height - 841.89) < 0.5
        assert len(page.get_text().strip()) > 20, (number, page_number)

    student_text = normalise("\n".join(page.get_text() for page in list(document)[:20]))
    appendix_text = normalise("\n".join(page.get_text() for page in list(document)[20:]))
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    assert "\ufffd" not in extracted
    assert f"practice paper {number:02d}" in normalise(extracted)
    assert "answers and explanations" in normalise(extracted)

    questions = paper["language"] + [question for passage in paper["reading_passages"] for question in passage["questions"]] + paper["numeracy"]
    missing_prompts = [
        question["id"]
        for question in questions
        if question.get("spelling_type") != "dictation"
        and normalise(question["prompt"]) not in student_text
    ]
    missing_options = []
    for question in questions:
        for option in question.get("options", []):
            token = normalise(option)
            if token and token not in student_text:
                missing_options.append([question["id"], option])
    missing_explanations = [question["id"] for question in questions if normalise(question["explanation"]) not in appendix_text]
    missing_answers = [question["id"] for question in questions if normalise(answer_value(question)) and normalise(answer_value(question)) not in appendix_text]
    missing_passage_fragments = []
    for passage in paper["reading_passages"]:
        for fragment in fragments_for_passage(passage):
            if normalise(fragment) not in student_text:
                missing_passage_fragments.append([passage["id"], fragment])
    assert not missing_prompts, (number, missing_prompts)
    assert not missing_options, (number, missing_options)
    assert not missing_explanations, (number, missing_explanations)
    assert not missing_answers, (number, missing_answers)
    assert not missing_passage_fragments, (number, missing_passage_fragments)
    assert normalise(paper["writing"]["prompt"]) in student_text

    dictation_area_text = normalise(
        document[3].get_text(clip=fitz.Rect(31, 130, 564, 385))
    )
    for question in paper["language"][25:40]:
        assert normalise(question["spoken_word"]) not in dictation_area_text, (
            number,
            question["id"],
            question["spoken_word"],
        )

    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    assert inventory["reference_student_pages"] == 20
    assert inventory["student_pages"] == 20
    assert inventory["appendix_pages"] == 6
    assert inventory["total_pages"] == 26
    assert inventory["scored_question_counts"] == {"language": 50, "reading": 30, "numeracy": 30}
    assert inventory["question_ids"] == [question["id"] for question in questions]
    assert inventory["answer_ids"] == inventory["question_ids"]

    layout = json.loads(layout_path.read_text(encoding="utf-8"))
    assert layout["student_pages"] == 20
    assert layout["appendix_pages"] == 6
    assert layout["pages"] == 26
    assert layout["minimum_body_font"] >= 7.4
    assert layout["minimum_diagram_font"] >= 6.8
    assert layout["minimum_appendix_font"] >= 7.4
    assert layout["minimum_scale"] >= 0.89
    assert not layout["negative_spare_entries"]

    rendered_files = sorted(render_dir.glob("page-*.png"))
    assert len(rendered_files) == 26
    render_hashes = []
    for page in document:
        pixmap = page.get_pixmap(matrix=fitz.Matrix(0.7, 0.7), alpha=False)
        render_hashes.append(hashlib.sha256(pixmap.samples).hexdigest())
    assert len(set(render_hashes)) == 26
    return {
        "paper": number,
        "pdf": str(pdf_path.relative_to(ROOT)),
        "bytes": pdf_path.stat().st_size,
        "student_pages": 20,
        "appendix_pages": 6,
        "pages": 26,
        "minimum_body_font": layout["minimum_body_font"],
        "minimum_diagram_font": layout["minimum_diagram_font"],
        "minimum_appendix_font": layout["minimum_appendix_font"],
        "questions": 110,
        "writing_tasks": 1,
        "minimum_scale": layout["minimum_scale"],
        "page_hashes": render_hashes,
        "pdf_sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
    }


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
        "scored_questions": 2200,
        "writing_tasks": 20,
        "source_hashes_verified": source_hash_count,
        "ocr_rerun": False,
        "unique_pdf_hashes": len(set(pdf_hashes)),
        "unique_rendered_page_hashes": len(set(page_hashes)),
        **content_report,
        "pdf_reports": pdf_reports,
    }
    REPORT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "pdf_reports"}, indent=2))


if __name__ == "__main__":
    main()
