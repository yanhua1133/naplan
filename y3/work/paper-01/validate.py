from __future__ import annotations

import hashlib
import html
import importlib.util
import json
import re
from pathlib import Path

import fitz
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[3]
PDF_PATH = ROOT / "y3" / "output" / "year3-naplan-style-practice-paper-01.pdf"
INVENTORY_PATH = ROOT / "y3" / "work" / "paper-01" / "question-inventory.json"
LAYOUT_PATH = ROOT / "y3" / "work" / "paper-01" / "layout-report.json"
FIDELITY_PATH = ROOT / "y3" / "work" / "paper-01" / "fidelity-report.json"
CONTENT_PATH = ROOT / "y3" / "work" / "paper-01" / "content.py"
SOURCE_HASHES_PATH = ROOT / "y3" / "source-cache" / "source-hashes.json"


def load_paper():
    spec = importlib.util.spec_from_file_location("paper_content", CONTENT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.PAPER


def normalise(value):
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    for ligature, replacement in {"ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl", "ﬀ": "ff"}.items():
        value = value.replace(ligature, replacement)
    value = value.replace("−", "-").replace("___", " ")
    return re.sub(r"[^a-z0-9$]+", " ", value.lower()).strip()


def word_count(value):
    return len(re.findall(r"[A-Za-z0-9]+", re.sub(r"<[^>]+>", " ", value)))


def validate_source_cache():
    cache = json.loads(SOURCE_HASHES_PATH.read_text(encoding="utf-8"))
    assert cache["cache_status"] == "verified"
    assert cache["ocr_policy"] == "one-time"
    assert len(cache["files"]) == 20
    for item in cache["files"]:
        source = ROOT / "y3" / "orig" / item["file"]
        assert source.stat().st_size == item["bytes"], item["file"]
        assert hashlib.sha256(source.read_bytes()).hexdigest() == item["sha256"], item["file"]
    return cache


def passage_word_count(passage):
    parts = [passage.get("intro", "")]
    parts.extend(passage.get("text", []))
    parts.extend(passage.get("materials", []))
    parts.extend(passage.get("steps", []))
    parts.extend(passage.get("lines", []))
    parts.extend(" ".join(row) for row in passage.get("table", []))
    return word_count(" ".join(parts))


def validate_content(paper):
    language = paper["language"]
    reading = [question for passage in paper["reading_passages"] for question in passage["questions"]]
    numeracy = paper["numeracy"]
    expected_ids = [f"L{number}" for number in range(1, 51)] + [f"R{number}" for number in range(1, 31)] + [f"N{number}" for number in range(1, 31)]
    questions = language + reading + numeracy
    assert [question["id"] for question in questions] == expected_ids
    assert len(paper["reading_passages"]) == 5
    assert all(len(passage["questions"]) == 6 for passage in paper["reading_passages"])
    assert paper["writing"]["prompt"] and paper["writing"]["reminders"]

    for question in questions:
        assert question["prompt"].strip(), question["id"]
        assert question["answer"].strip(), question["id"]
        assert question["explanation"].strip(), question["id"]
        if "options" in question:
            assert len(question["options"]) == 4, question["id"]
            assert question["answer"] in "ABCD", question["id"]
            assert len({option.strip() for option in question["options"]}) == 4, question["id"]

    language_lengths = [word_count(question["prompt"] + " " + " ".join(question.get("options", []))) for question in language]
    reading_lengths = [word_count(question["prompt"] + " " + " ".join(question["options"])) for question in reading]
    numeracy_lengths = [word_count(question["prompt"] + " " + " ".join(question.get("options", []))) for question in numeracy]
    passage_lengths = [passage_word_count(passage) for passage in paper["reading_passages"]]
    assert min(language_lengths) >= 8 and max(language_lengths) <= 40
    assert min(reading_lengths) >= 10 and max(reading_lengths) <= 45
    assert min(numeracy_lengths) >= 7 and max(numeracy_lengths) <= 40
    assert min(passage_lengths) >= 40 and max(passage_lengths) <= 300

    fidelity = {
        "reference": "y3/source-cache/year3-reference-test-2.md",
        "source_hashes_verified": 20,
        "ocr_rerun": False,
        "required_total_pages": 20,
        "required_counts": {"language": 50, "reading": 30, "writing": 1, "numeracy": 30},
        "actual_counts": {"language": len(language), "reading": len(reading), "writing": 1, "numeracy": len(numeracy)},
        "question_word_count_ranges": {
            "language": {"min": min(language_lengths), "max": max(language_lengths), "average": round(sum(language_lengths) / len(language_lengths), 2)},
            "reading": {"min": min(reading_lengths), "max": max(reading_lengths), "average": round(sum(reading_lengths) / len(reading_lengths), 2)},
            "numeracy": {"min": min(numeracy_lengths), "max": max(numeracy_lengths), "average": round(sum(numeracy_lengths) / len(numeracy_lengths), 2)},
        },
        "reading_passage_word_counts": passage_lengths,
        "difficulty_features": [
            "grammar and punctuation control",
            "25 contextual spelling corrections",
            "literal, vocabulary, inference and purpose reading items",
            "multi-step and visual numeracy items",
        ],
    }
    FIDELITY_PATH.write_text(json.dumps(fidelity, indent=2) + "\n", encoding="utf-8")
    return questions, expected_ids


def main():
    cache = validate_source_cache()
    paper = load_paper()
    questions, expected_ids = validate_content(paper)

    document = fitz.open(PDF_PATH)
    assert len(document) == 20
    for page_number, page in enumerate(document, start=1):
        assert abs(page.rect.width - 595.276) < 0.5
        assert abs(page.rect.height - 841.89) < 0.5
        assert len(page.get_text().strip()) > 20, f"Blank or textless page: {page_number}"

    reader = PdfReader(str(PDF_PATH))
    assert len(reader.pages) == 20
    student_text = normalise("\n".join(page.get_text() for page in list(document)[:17]))
    appendix_text = normalise("\n".join(page.get_text() for page in list(document)[17:]))
    extracted_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    assert "\ufffd" not in extracted_text
    assert "answers and explanations" in normalise(extracted_text)

    missing_prompts = [question["id"] for question in questions if normalise(question["prompt"]) not in student_text]
    missing_explanations = [question["id"] for question in questions if normalise(question["explanation"]) not in appendix_text]
    assert not missing_prompts, missing_prompts
    assert not missing_explanations, missing_explanations

    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    assert inventory["reference_pages"] == 20
    assert inventory["student_pages"] == 17
    assert inventory["appendix_pages"] == 3
    assert inventory["question_ids"] == expected_ids
    assert inventory["answer_ids"] == expected_ids
    assert inventory["scored_question_counts"] == {"language": 50, "reading": 30, "numeracy": 30}

    layout = json.loads(LAYOUT_PATH.read_text(encoding="utf-8"))
    assert layout["pages"] == 20
    assert layout["minimum_scale"] >= 0.89
    assert not layout["negative_spare_entries"]

    render_hashes = []
    for page in document:
        pixmap = page.get_pixmap(matrix=fitz.Matrix(0.7, 0.7), alpha=False)
        render_hashes.append(hashlib.sha256(pixmap.samples).hexdigest())
    assert len(render_hashes) == len(set(render_hashes)), "Unexpected duplicate rendered pages"

    result = {
        "pdf": str(PDF_PATH.relative_to(ROOT)),
        "file_bytes": PDF_PATH.stat().st_size,
        "pages": len(document),
        "student_pages": 17,
        "appendix_pages": 3,
        "scored_questions": len(questions),
        "writing_tasks": 1,
        "source_hashes_verified": len(cache["files"]),
        "ocr_rerun": False,
        "replacement_characters": extracted_text.count("\ufffd"),
        "unique_render_hashes": len(set(render_hashes)),
        "minimum_text_scale": layout["minimum_scale"],
        "missing_prompts": missing_prompts,
        "missing_explanations": missing_explanations,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
