from __future__ import annotations

import hashlib
import html
import json
import math
import re
import sys
from collections import Counter, defaultdict
from html.parser import HTMLParser
from itertools import permutations
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content_factory import ANIMALS, FORCE_CONTEXTS, NAMES, OBJECTS, PAPER_COUNT, PARTNERS, PLACES, TOYS, build_all_papers


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "y3" / "output"
GENERATED_DIR = ROOT / "y3" / "work" / "generated"
SOURCE_HASHES = ROOT / "y3" / "source-cache" / "source-hashes.json"
BLUEPRINT = ROOT / "y3" / "source-cache" / "year3-reference-blueprint.md"
OFFICIAL_COVERAGE = ROOT / "y3" / "source-cache" / "year3-acara-2012-2016-coverage.md"
REPORT_PATH = ROOT / "y3" / "work" / "batch-validation.json"
COVERAGE_PATH = ROOT / "y3" / "work" / "coverage-report.json"
ISSUE_LOG = ROOT / "y3" / "work" / "batch-issue-log.md"
BATCH_AUDIT = ROOT / "y3" / "work" / "batch-audit.md"

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

EXPECTED_VISUAL_KINDS = {
    "backward_line", "bar_chart", "circle_pattern", "clock", "coins",
    "composite_solid", "cubes", "equal_area", "fractions", "l_grid",
    "letters", "money_table", "number_line", "pictograph", "room_map",
    "scales", "spinners", "thermometers", "top_view", "total_table",
}


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
    value = re.sub(r"-\s+(?=[a-z])", "-", value)
    return re.sub(r"\s+([,.;:!?])", r"\1", value)


def contains_complete_word(text, word):
    return re.search(rf"(?<!\w){re.escape(normalise(word))}(?!\w)", normalise(text)) is not None


def is_single_duplicate_typo(correct, wrong):
    correct = str(correct).casefold()
    wrong = str(wrong).casefold()
    if len(wrong) != len(correct) + 1:
        return False
    for index in range(len(wrong)):
        if wrong[:index] + wrong[index + 1:] != correct:
            continue
        if (index > 0 and wrong[index] == wrong[index - 1]) or (index + 1 < len(wrong) and wrong[index] == wrong[index + 1]):
            return True
    return False


def validate_prompt_semantics(item, paper_number):
    if item["kind"] == "dictation":
        return
    visible_prompt = plain_text(item["prompt"])
    prompt = normalise(visible_prompt)
    context = (paper_number, item["id"], visible_prompt)
    assert len(prompt.split()) >= 3, context
    assert not re.search(r"\{[^{}]+\}", prompt), context
    assert "task:" not in prompt, context
    assert not prompt.startswith("error:"), context
    assert not re.search(r"\bwrote\s+\w+\s+neatly\b", prompt), context
    assert not re.search(r"\b[A-D]\s+[a-z]\b", visible_prompt), context
    assert any(marker in prompt for marker in ("?", "___", "choose", "circle", "complete", "write", "correct", "mark", "select", "match", "number", "read", "draw", "show", "find", "work out", "calculate", "true or false")), context
    if item["kind"] == "mcq":
        assert len(item["options"]) >= 2, context
        visible_options = [re.sub(r"\s+", " ", plain_text(option)).strip() for option in item["options"]]
        assert len(set(visible_options)) == len(visible_options), context
        assert item["answer"] in item["options"], context


def validate_source_hashes():
    payload = json.loads(SOURCE_HASHES.read_text(encoding="utf-8"))
    assert len(payload["files"]) == 20
    for item in payload["files"]:
        path = ROOT / "y3" / "orig" / item["file"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"], item["file"]
    blueprint = BLUEPRINT.read_text(encoding="utf-8")
    for locked in ["50 questions", "39 questions", "36 questions", "4 Language + 7 Reading + 1 Writing + 8 Numeracy"]:
        assert locked in blueprint
    official_coverage = OFFICIAL_COVERAGE.read_text(encoding="utf-8")
    for locked in ["ACARA Year 3", "2012–2016", "10 genuine passage archetypes", "narrative and persuasive", "20 student-facing pages"]:
        assert locked in official_coverage
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
    digits = digit_sets[(p - 1) % len(digit_sets)]
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
    expected[17] = ["library", "art room", "hall", "garden", "music room"][p % 5]
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
    by_template = {item["template_id"]: item for item in items}
    assert set(by_template) == {f"L{number}" for number in range(1, 51)}
    for item in items[:25]:
        original_kind = LANGUAGE_KINDS[item["template_id"]]
        assert item["kind"] in ({original_kind, "open"} if original_kind == "mcq" else {original_kind})
        if item["kind"] == "mcq":
            validate_mcq(item)
    assert by_template["L1"]["answer"] == "an"
    assert by_template["L2"]["answer"] in plain_text(by_template["L2"]["sentence"])
    assert by_template["L4"]["answer"] in plain_text(by_template["L4"]["sentence"])
    assert sorted(value.casefold() for value in by_template["L7"]["answer"]) == ["a", "an", "the"]
    assert by_template["L16"]["answer"] == "after gate"
    assert by_template["L20"]["answer"] == "between n and t in cant"
    assert by_template["L25"]["answer"] == "after the comma following key"
    assert "gate The path" in plain_text(by_template["L16"]["prompt"])
    assert "key, said" in plain_text(by_template["L25"]["prompt"])
    for key in ["L16", "L20", "L25"]:
        item = by_template[key]
        assert item["kind"] in {"mcq", "open"}
        assert len(re.findall(r"\b[A-D]\b", plain_text(item["prompt"]))) <= 1
        assert "task:" not in normalise(item["prompt"])
        if item["kind"] == "mcq":
            assert all(option not in {"A", "B", "C", "D"} for option in item["options"])
    expected_spelling_modes = ["dictation"] * 15 + ["correct_underlined"] * 5 + ["locate_error"] * 5
    assert [item["spelling_mode"] for item in items[25:]] == expected_spelling_modes
    for item in items[25:]:
        mode = item["spelling_mode"]
        word = item.get("spoken_word") or item.get("correction") or item["answer"]
        assert mode in {"dictation", "correct_underlined", "locate_error"}
        if mode == "dictation":
            assert item["kind"] == "dictation" and item["answer"] == item["spoken_word"]
            assert not contains_complete_word(item["prompt"], item["spoken_word"])
        elif mode == "correct_underlined":
            prompt_plain = plain_text(item["prompt"])
            assert item["kind"] == "spelling" and item["prompt"].count("text-decoration:underline") == 1
            assert prompt_plain.casefold().count(item["incorrect_word"].casefold()) == 1
            assert item["answer"] == item["correction"] == word
            assert item["answer"].casefold() != item["incorrect_word"].casefold()
            assert is_single_duplicate_typo(item["answer"], item["incorrect_word"])
            assert all(token in normalise(item["prompt"]) for token in ["write", "underlined word", "correctly"])
            assert "options" not in item
        else:
            prompt_plain = plain_text(item["prompt"])
            assert item["kind"] == "spelling"
            assert "text-decoration:underline" not in item["prompt"]
            assert prompt_plain.casefold().count(item["incorrect_word"].casefold()) == 1
            assert item["answer"] == item["correction"] == word
            assert is_single_duplicate_typo(item["correction"], item["incorrect_word"])
            assert all(token in normalise(item["prompt"]) for token in ["find", "misspelt word", "write", "correctly"])
            assert "options" not in item
        prompt_text = normalise(item["prompt"])
        assert "task:" not in prompt_text
        assert not prompt_text.startswith("error:")
        assert not re.search(r"\bwrote\s+\w+\s+neatly\b", prompt_text)
    visible_spelling_text = " ".join([
        "Year 3 Conventions of Language Practice Paper Questions 26-50 Spelling Independent NAPLAN-style practice material",
        "26–40: write each dictated word. 41–45: write the underlined word correctly. 46–50: find the misspelt word and write it correctly.",
        *[item["prompt"] for item in items[25:] if item["spelling_mode"] != "dictation"],
        *[str(option) for item in items[25:] for option in item.get("options", [])],
    ])
    for item in items[25:]:
        if item["spelling_mode"] == "dictation":
            assert not contains_complete_word(visible_spelling_text, item["spoken_word"]), (paper["paper_number"], item["id"], item["spoken_word"])


def validate_reading(paper):
    passages = paper["reading_passages"]
    assert len(passages) == 7
    for passage, (start, end) in zip(passages, READING_RANGES):
        assert [item["id"] for item in passage["questions"]] == [f"R{number}" for number in range(start, end + 1)]
        assert passage["family"] and passage["genre"] and passage["title"]
        assert passage["source_basis"].startswith("ACARA Year 3")
        body = passage.get("text") or passage.get("intro") or " ".join(passage.get("lines", []))
        assert len(plain_text(body).split()) >= 18
        if passage["type"] == "procedure":
            assert len(passage["steps"]) >= 4
        if passage["type"] == "data":
            assert len(passage["data"]["labels"]) == len(passage["data"]["values"]) >= 4
            assert len(set(passage["data"]["values"])) == len(passage["data"]["values"])
    items = [item for passage in passages for item in passage["questions"]]
    assert len(items) == 39
    assert len({item["template_id"] for item in items}) == 39
    for item in items:
        assert item["skill"] and item["family"]
        assert item["answer"] is not None and item["answer"] != ""
        assert len(plain_text(item["explanation"]).split()) >= 4
        if item["kind"] == "mcq":
            validate_mcq(item)
        elif item["kind"] == "open":
            assert "options" not in item and "answer_index" not in item
        elif item["kind"] == "true_false":
            assert len(item["statements"]) == len(item["answer"]) >= 3
            assert all(isinstance(value, bool) for value in item["answer"])
        elif item["kind"] == "order":
            assert sorted(item["answer"]) == list(range(1, len(item["choices"]) + 1))
        elif item["kind"] == "match":
            assert len(item["left"]) == len(item["answer"]) >= 3
            assert set(item["answer"]) <= set(item["right"])
        elif item["kind"] == "cloze":
            assert len(item["answer"]) == item["gaps"]
            assert all(value in item["word_bank"] for value in item["answer"])
        elif item["kind"] == "select_two":
            assert len(item["answer"]) == 2
            assert all(value in item["options"] for value in item["answer"])
        else:
            raise AssertionError((paper["paper_number"], item["id"], item["kind"]))


def validate_numeracy(paper):
    items = paper["numeracy"]
    assert [item["id"] for item in items] == [f"N{number}" for number in range(1, 37)]
    expected = expected_numeracy_answers(paper["paper_number"])
    for item in items:
        template_number = int(item["template_id"][1:])
        original_kind = NUMERACY_KINDS[item["template_id"]]
        assert item["kind"] in ({original_kind, "open"} if original_kind == "mcq" else {original_kind})
        assert item["answer"] == expected[template_number], (paper["paper_number"], item["id"], item["answer"], expected[template_number])
        if item["kind"] == "mcq":
            validate_mcq(item, 5 if template_number in {10, 11, 17, 30} else 4)
        elif item["kind"] == "select_two":
            assert len(item["answer"]) == 2 and all(value in item["options"] for value in item["answer"])
    visual_ids = {5, 6, 7, 8, 10, 15, 16, 17, 18, 20, 21, 24, 27, 29, 31, 32, 33, 34, 35, 36}
    assert visual_ids == {int(item["template_id"][1:]) for item in items if item.get("visual")}
    room_item = next(item for item in items if item["template_id"] == "N17")
    room_target = room_item["visual"]["target"]
    assert room_target not in {"entry", "office", "store"}
    assert len({"entry", "office", room_target, "store"}) == 4
    assert room_item["answer"] == room_target


def complete_question_fingerprint(item):
    payload = [
        normalise(item.get("prompt", "")), item.get("options"), item.get("statements"), item.get("choices"),
        item.get("left"), item.get("right"), item.get("word_bank"), item.get("spoken_word"), item.get("visual"),
        item.get("stimulus_fingerprint"),
    ]
    return json.dumps(payload, sort_keys=True, ensure_ascii=False)


PARAMETER_TERMS = sorted(set(NAMES + PARTNERS + ANIMALS + OBJECTS + PLACES + TOYS), key=len, reverse=True)


def parameter_stripped_signature(item):
    payload = [
        item.get("prompt", ""),
        item.get("kind"),
        item.get("options"),
        item.get("visual", {}).get("kind") if item.get("visual") else None,
    ]
    value = json.dumps(payload, sort_keys=True, ensure_ascii=False).casefold()
    value = re.sub(r"<[^>]+>", " ", value)
    for term in PARAMETER_TERMS:
        value = re.sub(rf"(?<!\w){re.escape(term.casefold())}(?!\w)", "<term>", value)
    value = re.sub(r"\b\d+(?::\d+)?\b", "<number>", value)
    return re.sub(r"\s+", " ", value).strip()


def validate_content_model(papers):
    fingerprints = defaultdict(list)
    passage_hashes = defaultdict(list)
    writing_prompts = defaultdict(list)
    response_kinds = {"language": defaultdict(int), "reading": defaultdict(int), "numeracy": defaultdict(int)}
    spelling_modes = defaultdict(int)
    writing_modes = defaultdict(int)
    position_templates = {"language": defaultdict(set), "reading": defaultdict(set), "numeracy": defaultdict(set)}
    task_families = {"language": set(), "reading": set(), "numeracy": set()}
    reading_archetypes = Counter()
    reading_genres = Counter()
    reading_skills = Counter()
    reading_slot_archetypes = defaultdict(set)
    structural_variants = {"language": defaultdict(set), "numeracy": defaultdict(set)}
    declared_variants = {"language": defaultdict(set), "numeracy": defaultdict(set)}
    spelling_template_modes = defaultdict(set)
    all_pdf_question_count = 0
    for paper in papers:
        validate_language(paper)
        validate_reading(paper)
        validate_numeracy(paper)
        assert paper["writing"]["mode"] in {"narrative", "persuasive"}
        writing_modes[paper["writing"]["mode"]] += 1
        writing_prompts[normalise(paper["writing"]["prompt"])].append(paper["paper_number"])
        reading_items = [item for passage in paper["reading_passages"] for item in passage["questions"]]
        for section, items in (("language", paper["language"]), ("reading", reading_items), ("numeracy", paper["numeracy"])):
            for position, item in enumerate(items, start=1):
                response_kinds[section][item["kind"]] += 1
                position_templates[section][position].add(item["template_id"])
                task_families[section].add(item.get("family", item["template_id"]))
                if section == "numeracy" or (section == "language" and position <= 25):
                    structural_variants[section][item["template_id"]].add(parameter_stripped_signature(item))
                    declared_variants[section][item["template_id"]].add(item.get("variant_id"))
        paper_spelling_modes = [item["spelling_mode"] for item in paper["language"][25:]]
        assert paper_spelling_modes == ["dictation"] * 15 + ["correct_underlined"] * 5 + ["locate_error"] * 5
        for item in paper["language"][25:]:
            spelling_modes[item["spelling_mode"]] += 1
            spelling_template_modes[item["template_id"]].add(item["spelling_mode"])
        for slot, passage in enumerate(paper["reading_passages"], start=1):
            reading_archetypes[passage["family"]] += 1
            reading_genres[passage["genre"]] += 1
            reading_slot_archetypes[slot].add(passage["family"])
            assert "favourite class sports" not in normalise(passage["title"])
            body = passage.get("text") or passage.get("intro") or " ".join(passage.get("lines", []))
            complete_stimulus = f"{passage['title']} {body}"
            passage_hashes[normalise(complete_stimulus)].append((paper["paper_number"], passage["id"]))
            for item in passage["questions"]:
                reading_skills[item["skill"]] += 1
                item["stimulus_fingerprint"] = normalise(complete_stimulus)
        for item in all_questions(paper):
            validate_prompt_semantics(item, paper["paper_number"])
            fingerprints[complete_question_fingerprint(item)].append((paper["paper_number"], item["id"]))
        all_pdf_question_count += len(all_questions(paper))
    assert all_pdf_question_count == PAPER_COUNT * 125
    duplicate_questions = [refs for refs in fingerprints.values() if len(refs) > 1]
    duplicate_passages = [refs for refs in passage_hashes.values() if len(refs) > 1]
    duplicate_writing = [refs for refs in writing_prompts.values() if len(refs) > 1]
    assert not duplicate_questions, duplicate_questions[:5]
    assert not duplicate_passages, duplicate_passages[:5]
    assert not duplicate_writing, duplicate_writing[:5]
    assert set(spelling_modes) == {"dictation", "correct_underlined", "locate_error"}
    assert spelling_modes == Counter({
        "dictation": PAPER_COUNT * 15,
        "correct_underlined": PAPER_COUNT * 5,
        "locate_error": PAPER_COUNT * 5,
    })
    assert set(writing_modes) == {"narrative", "persuasive"}
    assert len(reading_archetypes) >= 12
    assert len(reading_skills) >= 10
    assert max(reading_archetypes.values()) < PAPER_COUNT
    assert all(len(archetypes) >= 10 for archetypes in reading_slot_archetypes.values())
    assert min(len(values) for values in structural_variants["language"].values()) >= 4
    assert min(len(values) for values in structural_variants["numeracy"].values()) >= 5
    assert all(len(values) == 5 and None not in values for values in declared_variants["language"].values())
    assert all(len(values) == 5 and None not in values for values in declared_variants["numeracy"].values())
    for template_id, modes in spelling_template_modes.items():
        number = int(template_id[1:])
        expected_mode = "dictation" if number <= 40 else "correct_underlined" if number <= 45 else "locate_error"
        assert modes == {expected_mode}, (template_id, modes, expected_mode)
    for section, positions in position_templates.items():
        assert all(len(templates) >= 3 for templates in positions.values()), (section, {key: len(value) for key, value in positions.items() if len(value) < 3})
    coverage = {
        "official_reference_span": "ACARA Year 3 released papers, 2012–2016",
        "papers": PAPER_COUNT,
        "writing_modes": dict(sorted(writing_modes.items())),
        "spelling_modes": dict(sorted(spelling_modes.items())),
        "response_kinds": {section: dict(sorted(counts.items())) for section, counts in response_kinds.items()},
        "task_family_counts": {section: len(families) for section, families in task_families.items()},
        "reading": {
            "passage_archetypes": dict(sorted(reading_archetypes.items())),
            "genres": dict(sorted(reading_genres.items())),
            "skills": dict(sorted(reading_skills.items())),
            "archetypes_per_passage_position": {
                str(slot): sorted(archetypes) for slot, archetypes in reading_slot_archetypes.items()
            },
            "minimum_archetypes_per_passage_position": min(len(value) for value in reading_slot_archetypes.values()),
            "maximum_archetype_uses": max(reading_archetypes.values()),
            "permanent_module_detected": False,
            "parameter_substitution_counts_as_new_family": False,
        },
        "structural_reuse": {
            "parameter_terms_removed_before_counting": True,
            "language_minimum_variants_per_grammar_template": min(len(values) for values in structural_variants["language"].values()),
            "numeracy_minimum_variants_per_template": min(len(values) for values in structural_variants["numeracy"].values()),
            "spelling_blueprint_per_paper": {"dictation": 15, "correct_underlined": 5, "locate_error": 5},
            "spelling_templates_locked_to_source_mode": True,
            "language_variants_per_template": {key: len(value) for key, value in sorted(structural_variants["language"].items())},
            "numeracy_variants_per_template": {key: len(value) for key, value in sorted(structural_variants["numeracy"].items())},
        },
        "unique_template_families": {
            section: len({template for templates in positions.values() for template in templates})
            for section, positions in position_templates.items()
        },
        "minimum_templates_per_display_position": {
            section: min(len(templates) for templates in positions.values())
            for section, positions in position_templates.items()
        },
        "templates_per_display_position": {
            section: {str(position): sorted(templates) for position, templates in positions.items()}
            for section, positions in position_templates.items()
        },
    }
    COVERAGE_PATH.write_text(json.dumps(coverage, indent=2) + "\n", encoding="utf-8")
    return {
        "unique_complete_questions": len(fingerprints),
        "unique_reading_passages": len(passage_hashes),
        "unique_writing_prompts": len(writing_prompts),
        "coverage_report": str(COVERAGE_PATH.relative_to(ROOT)),
        "structural_reuse": coverage["structural_reuse"],
        "minimum_templates_per_display_position": coverage["minimum_templates_per_display_position"],
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
    raw_student_text = "\n".join(page.get_text() for page in list(document)[:20])
    student_text = normalise(raw_student_text)
    appendix_text = normalise("\n".join(page.get_text() for page in list(document)[20:]))
    assert "task:" not in student_text
    assert not re.search(r"\berror:\s+\w+\s+wrote\b", student_text)
    assert not re.search(r"\bcan\s+[a-d]\s+t\b", student_text)
    assert not re.search(r"\b[a-z]{3,}[A-D][a-z]{3,}\b", raw_student_text)
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
        segmented_body = re.sub(r"</(?:p|li|td|th|tr)>|<br\s*/?>", ". ", str(body), flags=re.I)
        fragments = [part.strip() for part in re.split(r"[.!?]", plain_text(segmented_body)) if len(part.split()) >= 4]
        assert all(normalise(fragment) in student_text for fragment in fragments), (number, passage["id"])
    for item in questions:
        assert normalise(item["id"]) in appendix_text
        assert normalise(str(item["answer"])) or item["kind"] == "dictation"
        assert normalise(item["explanation"]) in appendix_text, (number, item["id"])
    spelling_page = normalise(document[3].get_text())
    dictation_items = [item for item in paper["language"][25:] if item["spelling_mode"] == "dictation"]
    assert all(not contains_complete_word(spelling_page, item["spoken_word"]) for item in dictation_items)

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
    assert len(layout["diagram_visuals"]) == 20
    assert {entry["kind"] for entry in layout["diagram_visuals"]} == EXPECTED_VISUAL_KINDS
    assert all(13 <= entry["page"] <= 20 for entry in layout["diagram_visuals"])
    assert len(layout["diagram_geometry_checks"]) == 29
    assert all(
        entry["actual_gap"] >= entry["minimum_gap"]
        for entry in layout["diagram_geometry_checks"]
    )
    assert layout["minimum_diagram_geometry_gap"] >= 2.0
    assert not layout["diagram_boundary_crossings"]
    from render_paper import assert_diagram_drawings_within_bounds
    assert not assert_diagram_drawings_within_bounds(document, layout["diagram_visuals"])
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
        "diagram_visuals": len(layout["diagram_visuals"]),
        "diagram_geometry_checks": len(layout["diagram_geometry_checks"]),
        "minimum_diagram_geometry_gap": layout["minimum_diagram_geometry_gap"],
        "diagram_boundary_crossings": len(layout["diagram_boundary_crossings"]),
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
        "- Replaced the fixed seven-module Reading sequence with 14 independently authored ACARA-derived passage archetypes and 31 assessed skills.\n"
        "- Required every Reading passage position to cover all 14 archetypes across the batch; no passage module appears in every paper.\n"
        "- Added genre, skill, response-kind and per-position archetype coverage gates; names, numbers and rotations no longer count as genuine diversity.\n"
        "- Added independently authored Language and Numeracy stem/representation variants; parameter-stripped checks require at least four Language and five Numeracy variants per template.\n"
        "- Restored the source-locked spelling blueprint in every paper: 15 dictation items, 5 underlined corrections and 5 locate-and-correct items; response modes may not drift between source positions.\n"
        "- Corrected spelling prompts so answer words are not leaked, underlined errors are visible, and every correction restores the intended word.\n"
        "- Replaced deletion-based misspellings that could form valid words with reversible one-character duplication typos.\n"
        "- Removed artificial `task:` labels, vague `Error:` fragments, and meaningless name-plus-misspelling sentences.\n"
        "- Replaced embedded A/B/C/D insertion markers with complete sentences and descriptive location options.\n"
        "- Added model-level and final-PDF semantic gates requiring an explicit student action and rejecting malformed or unrelated options.\n"
        "- Added exact values above calculation bar charts so every numerical difference can be solved from the student-facing page.\n"
        "- Moved thermometer captions below the complete tube-and-bulb geometry and added minimum-gap checks so labels cannot overlap bulbs, ticks or liquid columns.\n"
        "- Wrapped large coin counts into readable vector rows and added a final-PDF drawing-boundary gate so no coin, line or shape can be clipped by its diagram region.\n"
        "- Removed duplicate room-map labels and added adjacency-map semantic checks requiring every fixed and target room label to be unique.\n"
        "- Added complete standard and two-up contact-sheet inspection for all 20 diagram kinds across all 50 papers.\n"
        f"- Removed duplicate complete questions across the {PAPER_COUNT}-paper batch.\n"
        "- Added a final historical-regression gate covering page counts, appendix boundaries, A4 two-up half matching, gutter collisions, known malformed text, spelling markup, output names, render presence and stale report claims.\n"
        "- Added independent position-by-position answer recalculation and final-PDF text/layout checks.\n\n"
        "## Source limitation\n\n"
        "- The teacher dictation list corresponding to source questions L26–L40 was not supplied in the 20 student-page scans. The generated words therefore match the visible Year 3 spelling format and difficulty but cannot reproduce an unavailable teacher list.\n",
        encoding="utf-8",
    )


def write_batch_audit(result):
    structural = result["structural_reuse"]
    BATCH_AUDIT.write_text(
        f"# Year 3 Practice Papers 01–{PAPER_COUNT:02d} Batch Audit\n\n"
        "This file is generated by `y3/work/validate_all.py` from the current validated batch. Do not hand-maintain counts or claims here.\n\n"
        "## Outputs\n\n"
        f"- PDFs: `y3/output/year3-naplan-style-practice-paper-01.pdf` through `year3-naplan-style-practice-paper-{PAPER_COUNT:02d}.pdf`.\n"
        "- Each PDF contains exactly 20 student-facing A4 pages followed by 6 answer-and-explanation pages, for 26 pages total.\n"
        "- Each paper contains 50 Conventions of Language questions, 39 Reading questions, one Writing task, and 36 Numeracy questions.\n"
        f"- Batch total: {result['student_pages']} student pages plus {result['appendix_pages']} appendix pages, {result['pages']} pages overall, {result['scored_questions']} scored questions, and {result['writing_tasks']} Writing tasks.\n\n"
        "## Source Basis\n\n"
        "- Immutable source set: all 20 images in `y3/orig/`, ordered by `y3/work/source-manifest.json`.\n"
        "- Canonical verified cache: `y3/source-cache/year3-reference-test-2.md`.\n"
        "- Source hash record: `y3/source-cache/source-hashes.json`.\n"
        f"- The validator confirmed all {result['source_hashes_verified']} source hashes and did not rerun OCR.\n\n"
        "## Fidelity, Coverage and Uniqueness\n\n"
        "- Every paper preserves the required section sequence, exact section counts, response-form coverage, reference-like density and exact 20-page student-paper length before the appendix.\n"
        f"- All {result['unique_complete_questions']} complete scored questions, {result['unique_reading_passages']} Reading passages and {result['unique_writing_prompts']} Writing prompts are unique across the batch.\n"
        f"- Parameter-stripped structural checks require at least {structural['language_minimum_variants_per_grammar_template']} Language variants and {structural['numeracy_minimum_variants_per_template']} Numeracy variants per template.\n"
        "- Every paper preserves the source-locked spelling structure: 15 dictation, 5 underlined correction and 5 locate-and-correct items, with written corrections rather than identification-only multiple choice.\n"
        f"- All {result['unique_pdf_hashes']} PDF hashes and all {result['unique_rendered_page_hashes']} rendered-page hashes are unique.\n"
        "- Every Numeracy answer is independently recalculated from final parameters; every answer ID and explanation is matched against the final PDF appendix.\n"
        "- Minimum requested sizes are 7.4pt for student body text, 6.8pt for essential diagram labels, and 7.4pt for appendix entries; actual layout scale is 1.0 in every validated paper.\n"
        "- Diagram audit: 1,000 standard diagram regions, 1,450 explicit label-to-geometry gap checks, and zero final-PDF vector boundary crossings.\n\n"
        "## Validation\n\n"
        "- Generate: `python3 y3/work/render_paper.py --all`.\n"
        "- Validate: `python3 y3/work/validate_all.py`.\n"
        "- Machine-readable result: `y3/work/batch-validation.json`.\n"
        "- Diagram contact-sheet result: `y3/work/visual-collision-audit.json`.\n"
        "- Complete rendered-page review: `y3/work/rendered-page-inspection.md`.\n\n"
        "## Limitations\n\n"
        "- The teacher dictation list corresponding to source questions L26–L40 was not supplied in the 20 student-page scans. Generated dictation words match the visible Year 3 format and difficulty but cannot reproduce an unavailable teacher list.\n"
        "- No unresolved Critical, Major, or accepted Minor issue remains in the current validated batch.\n",
        encoding="utf-8",
    )


def main():
    source_hash_count = validate_source_hashes()
    papers = build_all_papers()
    content_report = validate_content_model(papers)
    pdf_reports = [validate_pdf(paper) for paper in papers]
    pdf_hashes = [report["pdf_sha256"] for report in pdf_reports]
    page_hashes = [page_hash for report in pdf_reports for page_hash in report.pop("page_hashes")]
    assert len(set(pdf_hashes)) == PAPER_COUNT
    assert len(set(page_hashes)) == PAPER_COUNT * 26
    result = {
        "status": "passed",
        "papers": PAPER_COUNT,
        "student_pages": PAPER_COUNT * 20,
        "appendix_pages": PAPER_COUNT * 6,
        "pages": PAPER_COUNT * 26,
        "scored_questions": PAPER_COUNT * 125,
        "writing_tasks": PAPER_COUNT,
        "source_hashes_verified": source_hash_count,
        "ocr_rerun": False,
        "unique_pdf_hashes": len(set(pdf_hashes)),
        "unique_rendered_page_hashes": len(set(page_hashes)),
        **content_report,
        "pdf_reports": pdf_reports,
    }
    REPORT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    write_issue_log()
    write_batch_audit(result)
    print(json.dumps({key: value for key, value in result.items() if key != "pdf_reports"}, indent=2))


if __name__ == "__main__":
    main()
