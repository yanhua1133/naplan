from __future__ import annotations

import json
import re
from pathlib import Path

from reading_factory import build_reading as build_diverse_reading
from numeracy_variants import apply_numeracy_variant


LETTERS = "ABCDEF"
SPELLING_BANK_PATH = Path(__file__).with_name("spelling-bank.json")
PAPER_COUNT = 50

NAMES = [
    "Ava", "Noah", "Mia", "Leo", "Ruby", "Eli", "Zoe", "Kai", "Nina", "Arlo",
    "Ivy", "Owen", "Lila", "Finn", "Maya", "Hugo", "Sara", "Jude", "Tara", "Max",
    "Ada", "Liam", "Evie", "Sam", "Cleo", "Luca", "Anya", "Remy", "Ella", "Toby",
    "Freya", "Amir", "Poppy", "Miles", "Alice", "Felix", "Sienna", "Rowan", "Hazel", "Isaac",
    "Olive", "Jasper", "Elsie", "Caleb", "Ayla", "Mila", "Rory", "Nadia", "Ethan", "Skye",
]
PARTNERS = [
    "Ben", "Chloe", "Dylan", "Emma", "Grace", "Henry", "Isla", "Jack", "Layla", "Mason",
    "Nora", "Oscar", "Piper", "Quinn", "Riley", "Sofia", "Theo", "Uma", "Violet", "Will",
    "Abel", "Bella", "Cody", "Daisy", "Evan", "Faye", "Gus", "Holly", "Imran", "Josie",
    "Kiran", "Lucy", "Milo", "Nell", "Omar", "Paige", "Rafi", "Stella", "Tess", "Uri",
    "Wade", "Xanthe", "Yara", "Zane", "April", "Blake", "Ciara", "Dean", "Esme", "Frank",
]
ANIMALS = [
    "otter", "wombat", "penguin", "dolphin", "koala", "wallaby", "platypus", "possum", "echidna", "quokka",
    "turtle", "pelican", "cockatoo", "lizard", "bilby", "seal", "frog", "owl", "bandicoot", "kangaroo",
    "emu", "dingo", "stingray", "seahorse", "lorikeet", "gecko", "crab", "swan", "butterfly", "beetle",
    "magpie", "cuttlefish", "albatross", "wallaroo", "goanna", "manta ray", "parrot", "skink", "heron", "possum joey",
    "dragonfly", "starfish", "potoroo", "tawny frogmouth", "sea lion", "sugar glider", "kingfisher", "mallee fowl", "blue-tongue lizard", "whale",
]
OBJECTS = [
    "orange", "umbrella", "apple", "apron", "egg", "insect model", "octopus toy", "engine", "ice cube", "alarm clock",
    "atlas", "envelope", "igloo model", "orchid", "acorn", "elephant card", "ink bottle", "oven mitt", "arrow", "opal",
    "easel", "owl badge", "avocado", "astronaut card", "emu feather", "ocean map", "ice pack", "elephant puzzle", "acacia leaf", "apricot",
    "earphone case", "octopus badge", "insect poster", "orange ribbon", "artist's brush", "animal mask", "engine part", "olive branch", "island map", "alarm bell",
    "empty jar", "eagle picture", "ink stamp", "orchid pot", "apple badge", "ant model", "ice tray", "emu postcard", "oyster shell", "arrow sign",
]
PLACES = [
    "library", "garden", "museum", "jetty", "hall", "creek", "market", "workshop", "farm", "beach",
    "gallery", "reserve", "campsite", "theatre", "orchard", "station", "aquarium", "bakery", "lookout", "nursery",
    "boathouse", "courtyard", "science room", "sports shed", "community centre", "bird hide", "harbour", "lighthouse", "greenhouse", "art studio",
    "reading room", "school oval", "nature trail", "picnic ground", "visitor centre", "music room", "craft room", "riverbank", "boardwalk", "town square",
    "camp kitchen", "ferry stop", "wildlife park", "plant house", "history room", "assembly area", "vegetable patch", "boat ramp", "school office", "shade house",
]
TOYS = [
    "wooden train", "rag doll", "tin robot", "toy dinosaur", "music-box horse", "teddy bear", "model aeroplane", "puppet",
    "wind-up mouse", "toy dragon", "building-block figure", "toy boat", "plush koala", "toy astronaut", "marionette",
    "clockwork duck", "toy fire engine", "paper clown", "toy knight", "stuffed penguin",
    "felt fox", "wooden crane", "toy submarine", "plush wombat", "clockwork rabbit", "model tram", "paper dragon", "toy helicopter", "sock monkey", "miniature bus",
    "wooden whale", "felt astronaut", "wind-up beetle", "toy lighthouse", "plush echidna", "cardboard robot", "model ferry", "toy crocodile", "cloth mermaid", "wooden scooter",
    "clockwork turtle", "toy rescue boat", "felt cockatoo", "model hot-air balloon", "plush quokka", "wooden spaceship", "toy delivery van", "paper puppet", "wind-up penguin", "stuffed bilby",
]

EXTRA_DICTATION_WORDS = """
above likely inside player sense break event higher middle present result sorry finally guess alone average brought certain longer movie original received tried worth exactly giving ground meeting sound source usually evidence reading round stand amount drive feeling green match model trust forward range review science trade various cannot character football lower quality style amazing involved itself language related stage title article decided entire perhaps release turned written choice cover increase seven simply staff built daily difficult figure modern starting version voice whose earth forget practice success towards waiting access below missing sleep table truth recent seeing straight wrote culture growth included respect response river speak standard tonight write album century charge effect eight except funny limited moving peace provided spent store tomorrow track watching weight addition ahead brown difference double expect normal radio western beginning certainly completely content cross despite focus nearly previous quickly region section speed contact positive welcome beyond extra leaving nature unless winning episode movement photo posted safety scene spend statement ability calling coach collection continued designed heavy knowledge subject train author claim generally interested leader material nobody product annual brain degree finished floor growing image meant opening opinion physical reach sports approach biggest dance master weekend awesome beach clearly effort ended impact learning older secret spring telling anyway bought choose dream easily grand necessary speaking sweet touch yesterday caught closed damage directly doubt drink driving greater overall shown basic captain effective effects fully highly holding plant reality advice agreement award block broken challenge comment equipment lived primary purpose showing theory avoid catch coast meaning
""".split()

EXTRA_DICTATION_WORDS += """
corner distance drawing excited journey kindness thunder whisper anchor dancer doorway handle insect kitten narrow picnic sandwich velvet yellow daylight golden hungry jungle lesson morning number outside silver
""".split()


def spelling_target_words():
    cached = [entry["word"] for entry in json.loads(SPELLING_BANK_PATH.read_text(encoding="utf-8"))["entries"]]
    words = cached + EXTRA_DICTATION_WORDS
    return list(dict.fromkeys(word for word in words if 4 <= len(word) <= 10 and word.isalpha()))


SPELLING_TARGET_WORDS = spelling_target_words()
DICTATION_BLOCKED_WORDS = {
    "year", "conventions", "language", "practice", "paper", "questions", "spelling", "independent", "style",
    "material", "complete", "each", "some", "ask", "listen", "choose", "correct", "error", "write", "word", "question",
    "hear", "mark", "option", "select", "accurately", "written", "only", "acceptable", "version", "formed",
    "properly", "which", "misspelt", "wrote", "today", "neatly", "class", "chart", "underlined",
}
SPELLING_DICTATION_WORDS = [word for word in SPELLING_TARGET_WORDS if word.casefold() not in DICTATION_BLOCKED_WORDS]


def rotate(correct, distractors, shift):
    options = [correct, *distractors]
    offset = shift % len(options)
    options = options[offset:] + options[:offset]
    return options, options.index(correct)


def question(question_id, kind, prompt, answer, explanation, **extra):
    item = {
        "id": question_id,
        "kind": kind,
        "prompt": prompt,
        "answer": answer,
        "explanation": explanation,
    }
    item.update(extra)
    return item


def mcq(question_id, prompt, correct, distractors, explanation, shift=0, **extra):
    options, answer_index = rotate(str(correct), [str(value) for value in distractors], shift)
    return question(
        question_id,
        "mcq",
        prompt,
        str(correct),
        explanation,
        options=options,
        answer_index=answer_index,
        **extra,
    )


def distinct_numbers(correct, candidates, count=3):
    result = []
    used = {str(correct)}
    for candidate in candidates:
        value = candidate
        while str(value) in used:
            value += 1
        used.add(str(value))
        result.append(value)
        if len(result) == count:
            return result
    raise ValueError("Not enough distinct numeric distractors")


def misspellings(word):
    positions = [max(1, len(word) // 3), max(1, (2 * len(word)) // 3), len(word) - 1, *range(1, len(word)), 0]
    result = []
    for index in positions:
        candidate = word[:index] + word[index] + word[index:]
        if candidate not in result:
            result.append(candidate)
        if len(result) == 3:
            break
    if len(result) != 3:
        raise ValueError(f"Could not create three unambiguous misspellings for {word!r}")
    return result


def rotate_and_renumber(items, groups, prefix, form):
    reordered = []
    for start, end in groups:
        group = items[start:end]
        shift = form % len(group)
        reordered.extend(group[shift:] + group[:shift])
    for number, item in enumerate(reordered, start=1):
        item["template_id"] = item.get("template_id", item["id"])
        item["id"] = f"{prefix}{number}"
    return reordered


def diversify_language(items, paper_number):
    form = (paper_number - 1) % 5
    place = PLACES[paper_number - 1]
    name = NAMES[paper_number - 1]
    partner = PARTNERS[paper_number - 1]
    items = rotate_and_renumber(items, [(0, 9), (9, 18), (18, 25), (25, 40), (40, 45), (45, 50)], "L", form)
    for index, item in enumerate(items[:25]):
        if item["template_id"] == "L2":
            sentence, verb = [
                (f"Near {name}'s tent, a wombat climbed over the log.", "climbed"),
                (f"{name} opened the gate carefully.", "opened"),
                (f"The class waited beside the {place}.", "waited"),
                (f"{partner} carried the basket inside.", "carried"),
                (f"At {name}'s pond, three ducks paddled across the water.", "paddled"),
            ][form]
            item.update({
                "kind": "circle",
                "prompt": f"Circle the verb in this sentence.<br><strong>{sentence}</strong>",
                "answer": verb,
                "explanation": f"<em>{verb.title()}</em> tells what happened in the sentence.",
                "sentence": sentence,
            })
        elif item["template_id"] == "L7":
            prompt, answers = [
                (f"{name} saw ___ ant beside ___ leaf. ___ ant carried a crumb.", ["an", "a", "The"]),
                (f"{name} drew ___ kite beside ___ oval. ___ oval was blue.", ["a", "an", "The"]),
                (f"___ sun was bright, so {name} packed ___ umbrella and ___ hat.", ["The", "an", "a"]),
                (f"{partner} found ___ egg in ___ nest. ___ egg was warm.", ["an", "a", "The"]),
                (f"___ owl watched ___ mouse beside ___ old tree while {name} waited.", ["The", "a", "an"]),
            ][form]
            item.update({
                "kind": "cloze",
                "prompt": f"Complete the sentence using each word once.<br>{prompt}",
                "answer": answers,
                "explanation": "The articles match the following noun sounds, and <em>The</em> identifies the specific noun in context.",
                "word_bank": ["a", "an", "The"],
                "gaps": 3,
            })
        elif item["template_id"] == "L22":
            correct, distractors, explanation = [
                ("Dr Patel spoke to the doctor.", ["dr Patel spoke to the Doctor.", "Dr patel spoke to the doctor.", "Dr Patel spoke to the Doctor."], "The title and surname take capitals; the common profession noun does not."),
                ("Aunt Maria visited us on Sunday.", ["aunt Maria visited us on Sunday.", "Aunt maria visited us on Sunday.", "Aunt Maria visited us on sunday."], "The family title used as a name, the person's name and the day need capitals."),
                ("Our class walked along River Street.", ["Our Class walked along River Street.", "Our class walked along river Street.", "our class walked along River street."], "The sentence begins with a capital, and both words in the street name are capitalised."),
                ("The festival begins in August.", ["the festival begins in August.", "The Festival begins in August.", "The festival begins in august."], "The first word and the month name take capitals; the common noun does not."),
                ("Professor Chen flew to Perth.", ["professor Chen flew to Perth.", "Professor chen flew to Perth.", "Professor Chen flew to perth."], "The title, surname and place name require capitals."),
            ][form]
            replacement = mcq(item["id"], f"{name} is checking capital letters. Which sentence is correct?", correct, distractors, explanation, paper_number + index)
            template_id = item["template_id"]
            item.clear()
            item.update(replacement)
            item["template_id"] = template_id
        item["variant_id"] = f"{item['template_id']}-v{form + 1}"
        item["family"] = f"language-{item['template_id']}"
        if item["kind"] == "mcq" and form in {2, 4} and index % 5 == form % 5:
            item["kind"] = "open"
            item.pop("options", None)
            item.pop("answer_index", None)
            item["prompt"] += "<br><b>Write your answer.</b>"
    assert len(SPELLING_DICTATION_WORDS) >= PAPER_COUNT * 15
    for index, item in enumerate(items[25:50], start=25):
        word = item.get("spoken_word") or str(item["answer"])
        if index < 40:
            mode = "dictation"
            local_index = index - 25
            word = dictation_word(paper_number, local_index)
            item["kind"] = "dictation"
            item["prompt"] = ""
            item["answer"] = word
            item["spoken_word"] = word
            item["spoken_sentence"] = f"Write the word {word}."
            item["explanation"] = f"The dictated word is <em>{word}</em>."
        else:
            mode = "correct_underlined" if index < 45 else "locate_error"
            original_wrong = item["incorrect_word"]
            wrong = misspellings(word)[(paper_number + index) % 3]
            assert item["prompt"].casefold().count(original_wrong.casefold()) == 1, (paper_number, item["id"], original_wrong)
            sentence = item["prompt"].replace(original_wrong, wrong)
            item["kind"] = "spelling"
            item["answer"] = word
            item["incorrect_word"] = wrong
            item["correction"] = word
            item["explanation"] = f"The correct spelling is <em>{word}</em>."
            item.pop("options", None)
            item.pop("answer_index", None)
            item.pop("spoken_word", None)
            if mode == "correct_underlined":
                item["prompt"] = (
                    f"In {name}'s sentence, write the underlined word correctly.<br>{sentence}"
                )
            else:
                item["prompt"] = (
                    f"Check {name}'s sentence. Find the misspelt word and write it correctly.<br>{sentence}"
                )
        item["spelling_mode"] = mode
        item["variant_id"] = f"{item['template_id']}-{mode}-v{form + 1}"
        item["family"] = f"spelling-{item['template_id']}-{mode}"
    return items


def diversify_reading(passages, paper_number):
    form = (paper_number - 1) % 10
    next_number = 1
    for passage_index, passage in enumerate(passages):
        questions = passage["questions"]
        shift = form % len(questions)
        questions = questions[shift:] + questions[:shift]
        for local_index, item in enumerate(questions):
            item["template_id"] = item.get("template_id", item["id"])
            item["family"] = item.get("family", f"reading-{passage['family']}-{item['skill']}")
            if item["kind"] == "mcq" and form in {1, 3} and local_index == passage_index % len(questions):
                item["kind"] = "open"
                item.pop("options", None)
                item.pop("answer_index", None)
                item["prompt"] += "<br><b>Write your answer.</b>"
            item["id"] = f"R{next_number}"
            next_number += 1
        passage["questions"] = questions
    return passages


def diversify_numeracy(items, paper_number):
    form = (paper_number - 1) % 5
    groups = [(0, 5), (5, 9), (9, 15), (15, 19), (19, 23), (23, 27), (27, 33), (33, 36)]
    context_leads = {
        "N2": "{owner} recorded the two groups shown.",
        "N4": "{owner} made the equal groups shown.",
        "N6": "{owner} recorded this decreasing pattern.",
        "N8": "{owner} marked a point on this grid.",
        "N9": "{owner} wrote this number pattern.",
        "N10": "{owner} is sorting solid objects.",
        "N16": "{owner} is reading the clock shown.",
        "N17": "{owner} is using this room map.",
        "N18": "{owner} is checking mirror symmetry.",
        "N19": "{owner} is planning a badge purchase.",
        "N20": "{owner} built the four shapes shown.",
        "N23": "{owner} wrote clues for a number.",
        "N24": "{owner} joined the two solids shown.",
        "N26": "{owner} is arranging equal groups.",
        "N27": "{owner} recorded two temperatures.",
        "N30": "{owner} is packing pencils.",
        "N35": "{owner} is comparing the four spinners.",
        "N36": "{owner} counted the coins shown.",
    }
    items = rotate_and_renumber(items, groups, "N", form)
    for index, item in enumerate(items):
        apply_numeracy_variant(item, form)
        if item["template_id"] in context_leads:
            template_number = int(item["template_id"][1:])
            owner = NAMES[(paper_number - 1 + template_number * 7) % PAPER_COUNT]
            lead = context_leads[item["template_id"]].format(owner=owner)
            item["prompt"] = f"{lead}<br>{item['prompt']}"
        if item["kind"] == "mcq" and form in {1, 3} and index % 6 == form:
            item["kind"] = "open"
            item.pop("options", None)
            item.pop("answer_index", None)
            item["prompt"] += "<br><b>Write your answer.</b>"
    return items


def build_language(paper_number):
    p = paper_number
    name = NAMES[p - 1]
    partner = PARTNERS[p - 1]
    animal = ANIMALS[p - 1]
    obj = OBJECTS[p - 1]
    place = PLACES[p - 1]
    past_pairs = [
        ("catch", "caught"), ("teach", "taught"), ("bring", "brought"), ("think", "thought"),
        ("leave", "left"), ("find", "found"), ("keep", "kept"), ("sleep", "slept"),
        ("send", "sent"), ("spend", "spent"), ("hear", "heard"), ("hold", "held"),
        ("make", "made"), ("take", "took"), ("write", "wrote"), ("drive", "drove"),
        ("choose", "chose"), ("break", "broke"), ("speak", "spoke"), ("wear", "wore"),
    ]
    base, past = past_pairs[(p - 1) % len(past_pairs)]
    adverbs = [
        "quietly", "carefully", "briskly", "patiently", "softly", "neatly", "slowly", "cheerfully", "gently", "quickly",
        "calmly", "politely", "eagerly", "firmly", "brightly", "smoothly", "safely", "silently", "proudly", "steadily",
    ]
    adverb = adverbs[(p - 1) % len(adverbs)]
    q = []
    q.append(mcq("L1", f"{name} packed ___ {obj} for the visit.", "an", ["a", "the", "some"], f"{obj.title()} begins with a vowel sound, so the correct article is <em>an</em>.", p))
    q.append(question("L2", "circle", f"Circle the verb in this sentence.<br><strong>The {animal} climbed over the log.</strong>", "climbed", "<em>Climbed</em> tells what the animal did.", sentence=f"The {animal} climbed over the log."))
    q.append(mcq("L3", f"Yesterday, {name} ___ the rope before lunch.", past, [base, f"{base}s", f"will {base}"], f"The word <em>yesterday</em> requires the past-tense form <em>{past}</em>.", p + 3))
    q.append(question("L4", "circle", f"Circle the adverb in this sentence.<br><strong>{partner} carried the glass jar {adverb}.</strong>", adverb, f"<em>{adverb.title()}</em> tells how {partner} carried the jar.", sentence=f"{partner} carried the glass jar {adverb}."))
    q.append(mcq("L5", f"{name} placed ___ hat beside the bag.", "my", ["me", "I", "mine"], "<em>My</em> is the possessive determiner used before the noun <em>hat</em>.", p + 5))
    q.append(mcq("L6", f"{name} should wash their hands ___ preparing the fruit.", "before", ["because", "although", "unless"], "<em>Before</em> shows the correct sequence in time.", p + 6))
    q.append(question("L7", "cloze", f"Complete the sentence using each word once.<br>{name} saw ___ ant beside ___ leaf. ___ ant carried a crumb.", ["an", "a", "The"], "Use <em>an</em> before <em>ant</em>, <em>a</em> before <em>leaf</em>, then <em>The</em> for the ant already mentioned.", word_bank=["a", "an", "the"], gaps=3))
    q.append(mcq("L8", f"___ will carry the boxes to the {place}.", f"{partner} and I", [f"Me and {partner}", f"Her and {partner}", f"{partner} and me"], "A compound subject uses the subject pronoun <em>I</em>.", p + 8))
    q.append(mcq("L9", f"{name} may choose a pear, a plum ___ a peach.", "or", ["but", "because", "although"], "<em>Or</em> joins alternatives in a list.", p + 9))
    q.append(mcq("L10", f"At the {place}, the pencils, rulers and erasers were new. ___ were placed in a tray.", "They", ["It", "She", "Them"], "The plural pronoun <em>They</em> replaces the three plural nouns and is the subject of the sentence.", p + 10))
    q.append(mcq("L11", f"{name} is checking four sentences. Which sentence is correct?", "They are waiting near the gate.", ["They is waiting near the gate.", "Them are waiting near the gate.", "They am waiting near the gate."], "The plural subject <em>They</em> agrees with <em>are</em>.", p + 11))
    q.append(mcq("L12", f"By the time {name} arrived, {partner} ___ the hole.", "had dug", ["digs", "will dig", "is digging"], "<em>Had dug</em> shows an action completed before another past action.", p + 12))
    q.append(mcq("L13", f"{name} and I are ready. ___ can begin now.", "We", ["Us", "They", "Them"], "<em>We</em> is the first-person plural subject pronoun.", p + 13))
    q.append(mcq("L14", f"Where did the {animal} hide___", "?", [".", "!", ","], "A direct question ends with a question mark.", p + 14))
    q.append(mcq("L15", f"{name} wants to shorten <em>we will</em>. Which contraction is correct?", "we’ll", ["well", "we’l", "w’ell"], "The apostrophe in <em>we’ll</em> replaces the missing letters in <em>will</em>.", p + 15))
    q.append(mcq(
        "L16",
        f"Where is the missing full stop?<br><strong>{name} reached the gate The path turned left beside the pond.</strong>",
        "after gate",
        ["after path", "after left", "after pond"],
        "The first sentence ends after <em>gate</em>. The next sentence begins with <em>The path</em>.",
        p + 16,
    ))
    q.append(mcq("L17", "Which sentence is punctuated correctly?", f'“Wait for me,” called {name}.', [f'“Wait for me” called {name}.', f'Wait for me,” called {name}.', f'“Wait for me, called {name}.”'], "The spoken words need opening and closing quotation marks, with a comma before the reporting clause.", p + 17))
    q.append(mcq("L18", f"{name} said, ‘This notebook is mine. Is that one ___?’", "yours", ["your", "you", "you’re"], "<em>Yours</em> is the possessive pronoun that can stand without a noun after it.", p + 18))
    q.append(mcq("L19", f"Which sentence has the comma in the correct place?", f"After the bell rang, {name} entered the room.", [f"After, the bell rang {name} entered the room.", f"After the bell, rang {name} entered the room.", f"After the bell rang {name}, entered the room."], "A comma separates the introductory clause from the main clause.", p + 19))
    q.append(mcq(
        "L20",
        f"The apostrophe is missing from a contraction.<br><strong>{name} cant leave yet.</strong><br>Where should the apostrophe go?",
        "between n and t in cant",
        [f"after {name}", "after leave", "after yet"],
        "The contraction <em>can’t</em> needs an apostrophe between <em>n</em> and <em>t</em>.",
        p + 20,
    ))
    q.append(mcq("L21", "Which sentence is a direct question?", f"Did {name} close the window?", [f"I wonder whether {name} closed the window.", f"Tell me if {name} closed the window.", f"We know that {name} closed the window."], "A direct question asks the reader for an answer and ends with a question mark.", p + 21))
    q.append(mcq("L22", f"{name} is checking capital letters. Which sentence is correct?", f"Dr Patel spoke to the doctor.", ["dr Patel spoke to the Doctor.", "Dr patel spoke to the doctor.", "Dr Patel spoke to the Doctor."], "The title and surname take capitals; the common profession noun <em>doctor</em> does not.", p + 22))
    q.append(mcq("L23", "Which sentence needs quotation marks?", f"Please close the gate, said {partner}.", [f"{partner} closed the gate quietly.", f"The gate beside the shed was closed.", f"Closing the gate kept the {animal} safe."], "The first sentence contains the exact words spoken by a character.", p + 23))
    q.append(mcq("L24", f"{name} is checking apostrophes. Which sentence is punctuated correctly?", f"The girl’s boots were beside the boys’ bags.", [f"The girls boots were beside the boy’s bags.", f"The girls’ boots were beside the boys bag’s.", f"The girl’s boot’s were beside the boys bags."], "<em>Girl’s</em> shows one girl owns the boots; <em>boys’</em> shows several boys own the bags.", p + 24))
    q.append(mcq(
        "L25",
        f"The closing quotation mark is missing.<br><strong>“I found the key, said {name}, as the door opened.</strong><br>Where should the closing quotation mark go?",
        "after the comma following key",
        ["after found", f"after {name}", "after opened"],
        "The closing quotation mark belongs after the comma following the final spoken word <em>key</em> and before the reporting clause.",
        p + 25,
    ))

    bank = [entry["word"] for entry in json.loads(SPELLING_BANK_PATH.read_text(encoding="utf-8"))["entries"]]
    bank.extend(EXTRA_DICTATION_WORDS)
    simple_bank = [word for word in bank if 4 <= len(word) <= 10 and word.isalpha()]
    start = (p - 1) * 15
    dictation = simple_bank[start:start + 15]
    if len(dictation) < 15:
        dictation += simple_bank[:15 - len(dictation)]
    for number, word in enumerate(dictation, start=26):
        q.append(question(f"L{number}", "dictation", "", word, f"The dictated word is <em>{word}</em>.", spelling_type="dictation", spoken_word=word, spoken_sentence=f"Write the word {word}."))

    correction_sets = [
        ("which", "wich", "I could not decide {word} path to take."),
        ("cupboard", "cubord", "The {word} door was painted blue."),
        ("edge", "edje", "Stand near the {word} of the mat."),
        ("except", "exept", "Everyone came {word} Sam, who was ill."),
        ("keys", "keyes", "The spare {word} are in this drawer."),
        ("because", "becaus", "We stayed inside {word} the rain was heavy."),
        ("people", "peple", "Several {word} waited near the gate."),
        ("enough", "enuf", "There was {word} water for the walk."),
        ("thought", "thort", f"{name} {{word}} carefully before answering."),
        ("caught", "cought", f"{partner} {{word}} the ball safely."),
        ("answer", "anser", "Write the complete {word} on the line."),
        ("colour", "collor", "Choose one bright {word} for the sign."),
        ("different", "diferent", "The two shells were {word} shapes."),
        ("February", "Febuary", "Our excursion is in {word}."),
        ("library", "libary", "Return the book to the {word}."),
        ("straight", "strait", "Draw one {word} line across the page."),
        ("through", "threw", "The path went {word} the forest."),
        ("piece", "peice", "Take one {word} of fruit."),
        ("quiet", "quite", "The room became {word} during reading."),
        ("weather", "wether", "The {word} changed before lunch."),
    ]
    selected = [correction_sets[(p - 1 + offset * 4) % len(correction_sets)] for offset in range(5)]
    for offset, (correct, wrong, frame) in enumerate(selected, start=41):
        prompt = frame.format(word=f'<span style="text-decoration:underline">{wrong}</span>')
        q.append(question(f"L{offset}", "spelling", prompt, correct, f"The correct spelling is <em>{correct}</em>.", spelling_type="underlined", incorrect_word=wrong))

    identify_sets = [
        ("misunderstood", "missunderstood", f"{name} had {{word}}, so the message was explained again."),
        ("wholemeal", "wholmeal", "The bakery sold fresh {word} bread."),
        ("friendly", "freindly", f"The guide was patient and {{word}} to {partner}."),
        ("cleaning", "cleanning", "We finished {word} the tables before lunch."),
        ("whether", "wether", "I asked {word} the excursion would continue."),
        ("disappear", "dissappear", "The clouds seemed to {word} at sunset."),
        ("tomorrow", "tommorrow", "The class will return {word}."),
        ("beginning", "begining", "The clue appeared near the {word} of the story."),
        ("surprise", "suprise", "The parcel contained a wonderful {word}."),
        ("separate", "seperate", "Keep the wet towels in a {word} bag."),
        ("necessary", "neccessary", "Only take the equipment that is {word}."),
        ("beautiful", "beautifull", "A {word} bird landed beside the creek."),
        ("business", "buisness", "The family opened a small {word}."),
        ("minute", "minuite", "Wait one {word} before opening the lid."),
        ("believe", "beleive", f"I {{word}} that {partner} told the truth."),
        ("address", "adress", "Write the return {word} on the envelope."),
        ("careful", "carefull", "Be {word} near the slippery rocks."),
        ("really", "realy", "The puzzle was {word} interesting."),
        ("stopped", "stoped", "The bus {word} beside the station."),
        ("writing", "writting", f"{name} was {{word}} a note to the teacher."),
    ]
    selected = [identify_sets[(p - 1 + offset * 3) % len(identify_sets)] for offset in range(5)]
    for offset, (correct, wrong, frame) in enumerate(selected, start=46):
        q.append(question(f"L{offset}", "spelling", frame.format(word=wrong), correct, f"The misspelt word is <em>{wrong}</em>; the correct spelling is <em>{correct}</em>.", spelling_type="identify", incorrect_word=wrong))
    return q


_DICTATION_ASSIGNMENTS = None


def build_dictation_assignments():
    required = PAPER_COUNT * 15
    assert len(SPELLING_DICTATION_WORDS) >= required
    assignments = [SPELLING_DICTATION_WORDS[(index * 149) % required] for index in range(required)]
    reserve = [word for word in SPELLING_DICTATION_WORDS[required:] if word not in assignments]
    fixed_text = (
        "Year 3 Conventions of Language Practice Paper Questions 26-50 Spelling Independent NAPLAN-style "
        "practice material 26-40 write each dictated word 41-45 write the underlined word correctly "
        "46-50 find the misspelt word and write it correctly Check sentence"
    )
    for paper_number in range(1, PAPER_COUNT + 1):
        form = (paper_number - 1) % 5
        items = rotate_and_renumber(
            build_language(paper_number),
            [(0, 9), (9, 18), (18, 25), (25, 40), (40, 45), (45, 50)],
            "L",
            form,
        )
        visible_text = " ".join([fixed_text, NAMES[paper_number - 1], *[item["prompt"] for item in items[40:50]]])
        visible_words = set(re.findall(r"[A-Za-z]+", visible_text.casefold()))
        for local_index in range(15):
            linear_index = (paper_number - 1) * 15 + local_index
            if assignments[linear_index].casefold() not in visible_words:
                continue
            replacement = next((word for word in reserve if word.casefold() not in visible_words), None)
            assert replacement is not None, (paper_number, local_index, assignments[linear_index])
            assignments[linear_index] = replacement
            reserve.remove(replacement)
    assert len(assignments) == required and len(set(assignments)) == required
    return assignments


def dictation_word(paper_number, local_index):
    global _DICTATION_ASSIGNMENTS
    if _DICTATION_ASSIGNMENTS is None:
        _DICTATION_ASSIGNMENTS = build_dictation_assignments()
    return _DICTATION_ASSIGNMENTS[(paper_number - 1) * 15 + local_index]


FORCE_CONTEXTS = [
    ("toy car", "smooth plastic", "rough carpet"), ("wooden block", "laminated board", "felt"),
    ("marble", "glass", "rubber mat"), ("small sled", "polished tile", "coarse fabric"),
    ("book", "waxed paper", "towel"), ("tin box", "smooth card", "sandpaper"),
    ("eraser", "plastic sheet", "wool cloth"), ("spool", "metal tray", "foam"),
    ("coin", "ceramic tile", "cork"), ("button", "glass sheet", "carpet"),
    ("toy boat", "vinyl", "felt"), ("cube", "laminate", "rubber"),
    ("bottle cap", "smooth card", "hessian"), ("counter", "polished wood", "towel"),
    ("toy wheel", "glass", "coarse mat"), ("small puck", "tile", "foam sheet"),
    ("wooden disc", "plastic", "rough cloth"), ("bead", "metal", "felt"),
    ("toy truck", "laminated card", "carpet"), ("block", "smooth board", "sandpaper"),
    ("toy train", "polished timber", "coarse mat"), ("wooden bead", "acrylic sheet", "felt cloth"),
    ("bottle", "smooth tile", "rough canvas"), ("toy plane", "laminated card", "woollen rug"),
    ("small wheel", "glass panel", "cork sheet"), ("plastic lid", "polished board", "hessian"),
    ("toy bus", "vinyl sheet", "thick carpet"), ("rubber ball", "smooth concrete", "coarse towel"),
    ("wooden peg", "metal tray", "foam mat"), ("toy submarine", "plastic board", "rough fabric"),
    ("small cylinder", "waxed card", "rubber sheet"), ("toy helicopter", "glass tile", "felt mat"),
    ("wooden ring", "laminated desk", "coarse cloth"), ("plastic counter", "polished stone", "wool mat"),
    ("toy van", "smooth cardboard", "rough carpet"), ("wooden marble", "ceramic tile", "foam sheet"),
    ("small roller", "metal plate", "hessian mat"), ("toy scooter", "vinyl board", "coarse fabric"),
    ("plastic cube", "smooth timber", "rubber mat"), ("wooden button", "glass sheet", "felt cloth"),
    ("toy ferry", "polished tile", "rough canvas"), ("small disc", "acrylic panel", "wool rug"),
    ("toy tractor", "laminated card", "cork mat"), ("wooden spool", "smooth metal", "thick towel"),
    ("plastic wheel", "waxed paper", "coarse carpet"), ("toy crane", "glass panel", "foam mat"),
    ("wooden cube", "polished board", "rough hessian"), ("toy hockey puck", "ceramic tile", "felt sheet"),
    ("toy tram", "smooth plastic", "woollen cloth"), ("wooden token", "metal tray", "rubber mat"),
]


def build_reading(paper_number):
    return build_diverse_reading(paper_number, NAMES, PARTNERS, ANIMALS, OBJECTS, PLACES)


def build_writing(paper_number):
    form = (paper_number - 1) % 5
    toy = TOYS[paper_number - 1]
    place = PLACES[paper_number - 1]
    if form == 1:
        topic = ["a vegetable garden", "a shaded play area", "a class pet", "a lunchtime music club", "a weekly nature walk"][paper_number % 5]
        return {
            "title": "A change for our school",
            "prompt": f"Write a persuasive text explaining whether a school near the {place} should have {topic}.",
            "mode": "persuasive",
            "illustration": "school",
            "ideas": ["State your opinion clearly.", "Give several convincing reasons.", "Use examples to support your reasons.", "Finish by reminding the reader of your view."],
            "reminders": ["Plan an introduction, reasons and conclusion.", "Group related ideas into paragraphs.", "Use persuasive words and complete sentences.", "Check spelling and punctuation."],
        }
    if form == 2:
        return {
            "title": "The unexpected message",
            "prompt": f"Write a narrative about a message that appears in the {place} and changes an ordinary day.",
            "mode": "narrative",
            "illustration": "message",
            "ideas": ["Who discovers the message?", "What does the message say?", "Why is it surprising or important?", "How is the problem resolved?"],
            "reminders": ["Plan the setting, characters, complication and ending.", "Use paragraphs to organise events.", "Choose precise verbs and describing words.", "Check spelling, punctuation and sentence boundaries."],
        }
    if form == 3:
        activity = ["reading outdoors", "visiting a museum", "learning to cook", "playing team games", "caring for wildlife"][paper_number % 5]
        return {
            "title": "The best class activity",
            "prompt": f"Write a persuasive text explaining why {activity} would be valuable for a class visiting the {place}.",
            "mode": "persuasive",
            "illustration": "activity",
            "ideas": ["Explain what students would learn.", "Describe how the activity could be organised.", "Give reasons it would be enjoyable or useful.", "Answer one possible concern."],
            "reminders": ["State a clear position.", "Organise reasons into paragraphs.", "Use linking words and persuasive language.", "Check spelling and punctuation."],
        }
    if form == 4:
        return {
            "title": "Everything went backwards",
            "prompt": f"Write a narrative about a day when everything in the {place} began happening backwards.",
            "mode": "narrative",
            "illustration": "backwards",
            "ideas": ["What is the first strange thing that happens?", "How do the characters react?", "What complication follows?", "How does the day return to normal?"],
            "reminders": ["Plan a clear beginning, complication and ending.", "Use paragraphs to show changes in time or place.", "Choose details that make the event believable.", "Check spelling, punctuation and sentence boundaries."],
        }
    return {
        "title": "The toy that came to life",
        "prompt": f"Write a narrative about a {toy} that suddenly comes to life in a {place}.",
        "mode": "narrative",
        "illustration": "toy",
        "ideas": [
            f"What can the {toy} do when it becomes alive?",
            "How does it feel, and what does it want?",
            "Who sees it, and how do they react?",
            "What complication happens before the story can end?",
        ],
        "reminders": [
            "Plan the setting, characters, complication and ending.",
            "Use paragraphs to organise the events.",
            "Choose precise words and complete sentences.",
            "Check spelling, punctuation and sentence boundaries.",
        ],
    }


def build_numeracy(paper_number):
    p = paper_number
    q = []

    def add_mcq(number, prompt, correct, distractors, explanation, **extra):
        q.append(mcq(f"N{number}", prompt, correct, distractors, explanation, p + number, **extra))

    def add_open(number, prompt, answer, explanation, **extra):
        q.append(question(f"N{number}", "open", prompt, str(answer), explanation, **extra))

    missing = 8 + p
    total = missing + 17
    add_mcq(1, f"Which number makes this true?<br><strong>17 + □ = {total}</strong>", missing, [missing - 2, missing + 2, total], f"{total} − 17 = {missing}.")
    total_balls = 28 + p
    red = 7 + p % 5
    blue = 6 + (p * 2) % 5
    add_open(2, f"A bag holds {total_balls} balls. {red} are red and {blue} are blue. How many are red or blue altogether?", red + blue, f"{red} + {blue} = {red + blue}.")
    start = 12 + p
    step = 4 + p % 4
    next_value = start + step * 4
    add_mcq(3, f"What comes next?<br><strong>{start}, {start + step}, {start + 2 * step}, {start + 3 * step}, ___</strong>", next_value, [next_value - step, next_value + step, next_value + 1], f"The sequence increases by {step} each time.")
    factor_a = 3 + p % 5
    factor_b = 4 + (p + 1) % 4
    product = factor_a * factor_b
    correct4 = " + ".join([str(factor_b)] * factor_a)
    distractors4 = [
        " + ".join([str(factor_b)] * max(1, factor_a - 1)),
        " + ".join([str(factor_a)] * (factor_b + 1)),
        f"{product} + {factor_a}",
    ]
    add_mcq(4, f"Which addition is equal to <strong>{factor_a} × {factor_b}</strong>?", correct4, distractors4, f"{factor_a} groups of {factor_b} total {product}.")
    rows, cols, cut = 4 + p % 3, 5 + p % 4, 2 + p % 3
    cover = rows * cols - cut
    add_mcq(5, "How many square stickers cover the unshaded part of this sheet?", cover, distinct_numbers(cover, [rows * cols, cover - 1, cover + 2]), f"The full grid has {rows * cols} squares; {cut} are removed, leaving {cover}.", visual={"kind": "l_grid", "rows": rows, "cols": cols, "cut": cut})
    first = 16 + p % 5
    decrease = 3 + p % 3
    fourth = first - 3 * decrease
    add_open(6, "How many circles belong in the fourth group?", fourth, f"The groups decrease by {decrease}: {first}, {first-decrease}, {first-2*decrease}, {fourth}.", visual={"kind": "circle_pattern", "values": [first, first-decrease, first-2*decrease, None]})
    icons = 4 + p % 4
    key = 2 + p % 3
    add_mcq(7, f"The pictograph shows {icons} shells for one group. Each shell stands for the same number. The group collected {icons * key} items. What is the key?", key, distinct_numbers(key, [key - 1, key + 1, key + 2]), f"{icons * key} ÷ {icons} = {key} items per shell.", visual={"kind": "pictograph", "icons": icons})
    add_mcq(8, "Which shape is the top view of a cone?", "circle", ["triangle", "rectangle", "semicircle"], "Looking straight down at a cone shows its circular base.", visual={"kind": "top_view"})
    digit_sets = [
        ("7", "4", "3"), ("6", "5", "1"), ("7", "2", "5"), ("6", "3", "1"), ("7", "5", "2"),
        ("6", "4", "3"), ("7", "3", "1"), ("6", "5", "3"), ("7", "4", "1"), ("6", "3", "2"),
        ("7", "6", "5"), ("5", "4", "3"), ("7", "2", "1"), ("6", "5", "4"), ("7", "5", "3"),
        ("6", "2", "1"), ("7", "4", "5"), ("5", "3", "2"), ("7", "6", "1"), ("6", "4", "1"),
    ]
    digits = list(digit_sets[(p - 1) % len(digit_sets)])
    candidates = sorted({int(a + b + c) for a in digits for b in digits for c in digits if len({a, b, c}) == 3 and int(c) % 2 == 1 and int(a + b + c) < 800}, reverse=True)
    correct9 = candidates[0]
    other_numbers = sorted({int("".join(order)) for order in __import__("itertools").permutations(digits) if int("".join(order)) != correct9}, reverse=True)
    add_mcq(9, f"Use the digit cards {', '.join(digits)} once each. What is the largest odd number less than 800?", correct9, other_numbers[:3], "Place the greatest possible digit in the hundreds place while keeping an odd digit in the ones place.")
    add_mcq(10, "Which diagram has exactly one third shaded?", "2 of 6 equal parts", ["1 of 4 equal parts", "3 of 6 equal parts", "2 of 5 equal parts", "3 of 8 equal parts"], "Two of six equal parts is 2/6, which simplifies to 1/3.", visual={"kind": "fractions"})
    left = 24 + p
    target = 60 + p * 2
    missing11 = target - left
    add_mcq(11, f"Which number makes this true?<br><strong>{left} + □ = {target}</strong>", missing11, [missing11 - 5, missing11 + 5, left, target], f"{target} − {left} = {missing11}.")
    start_hour = 8 + p % 3
    start_minute = [10, 15, 20, 25][p % 4]
    elapsed = 35 + (p % 3) * 5
    offset = 10
    event_minutes = start_hour * 60 + start_minute + elapsed - offset
    event_time = f"{event_minutes // 60}:{event_minutes % 60:02d}"
    add_mcq(12, f"A lesson began at {start_hour}:{start_minute:02d} and lasted {elapsed} minutes. A bell rang 10 minutes before it ended. When did the bell ring?", event_time, [f"{start_hour}:{(start_minute + 10) % 60:02d}", f"{event_minutes // 60}:{(event_minutes + 10) % 60:02d}", f"{start_hour + 1}:{start_minute:02d}"], f"The bell time is the start plus {elapsed - offset} minutes: {event_time}.")
    pages1, pages2 = 38 + p, 27 + 2 * p
    add_open(13, f"{NAMES[p-1]} read {pages1} pages on Monday and {pages2} pages on Tuesday. How many pages altogether?", pages1 + pages2, f"{pages1} + {pages2} = {pages1 + pages2}.")
    score1, score2 = 75 + p * 2, 48 + p
    add_open(14, f"One team scored {score1} points and another scored {score2}. What was the difference?", score1 - score2, f"{score1} − {score2} = {score1 - score2}.")
    prices = [2.5 + p * .1, 3.2 + p * .1, 4.1 + p * .1, 5.0 + p * .1]
    difference = round(prices[3] - prices[1], 2)
    add_mcq(15, "Use the price table. How much more does item D cost than item B?", f"${difference:.2f}", [f"${prices[3]:.2f}", f"${prices[1]:.2f}", f"${difference + .5:.2f}"], f"${prices[3]:.2f} − ${prices[1]:.2f} = ${difference:.2f}.", visual={"kind": "money_table", "values": prices})
    clock_hour = 2 + p % 8
    clock_minute = 0 if p % 2 else 30
    finish_minutes = clock_hour * 60 + clock_minute + 30
    finish_time = f"{finish_minutes // 60}:{finish_minutes % 60:02d}"
    add_mcq(16, "The clock shows the starting time. What time is half an hour later?", finish_time, [f"{clock_hour}:15", f"{clock_hour + 1}:30", f"{max(1, clock_hour - 1)}:30"], "Add 30 minutes to the time shown.", visual={"kind": "clock", "hour": clock_hour, "minute": clock_minute})
    rooms = ["library", "art room", "hall", "garden", "music room"]
    target_room = rooms[p % len(rooms)]
    add_mcq(17, "Walk east along the corridor. After passing the office, which room comes next?", target_room, [room for room in rooms if room != target_room], "The map order shows the named room immediately after the office when moving east.", visual={"kind": "room_map", "target": target_room})
    symmetry_letter = ["A", "H", "I", "M", "O", "T", "U", "V", "W", "X"][p % 10]
    add_mcq(18, "Which capital letter looks unchanged after reflection in a vertical mirror line?", symmetry_letter, ["F", "G", "J"], f"Capital {symmetry_letter} has vertical line symmetry in the printed form shown.", visual={"kind": "letters", "answer": symmetry_letter})
    unit_cost = 3 + p % 4
    budget = unit_cost * (5 + p % 5) + (unit_cost - 1)
    quantity = budget // unit_cost
    add_mcq(19, f"Each badge costs ${unit_cost}. What is the greatest number that can be bought for ${budget}?", quantity, [quantity - 1, quantity + 1, budget - unit_cost], f"{quantity} badges cost ${quantity * unit_cost}; one more would cost more than ${budget}.")
    q.append(question("N20", "select_two", "Which two shapes have the same area?", ["A", "C"], "Count the unit squares: shapes A and C contain the same number.", options=["A", "B", "C", "D"], visual={"kind": "equal_area"}))
    cubes = 7 + p % 6
    mass = 3 + p % 4
    add_open(21, f"The solid shown is made from identical cubes. Each cube has a mass of {mass} g. What is the total mass?", cubes * mass, f"There are {cubes} cubes. {cubes} × {mass} = {cubes * mass} g.", visual={"kind": "cubes", "count": cubes})
    seq_start = 100 + p * 3
    seq_step = 7 + p % 4
    members = [seq_start - seq_step * i for i in range(6)]
    correct22 = [str(members[3]), str(members[5])]
    q.append(question("N22", "select_two", f"The pattern begins {members[0]}, {members[1]}, {members[2]}, ... Which two numbers belong to the pattern?", correct22, f"Subtract {seq_step} each time; both selected values occur in the sequence.", options=[str(members[3]), str(members[3] + 1), str(members[5]), str(members[4] - 2), str(members[2] + 3)]))
    tens = 2 + p % 2
    ones = tens + 3
    number23 = tens * 10 + ones
    add_open(23, "A two-digit number is below 40. Its digits differ by 3 and add to " + str(tens + ones) + ". The tens digit is smaller. What is the number?", number23, f"The digits are {tens} and {ones}, so the number is {number23}.")
    add_mcq(24, "A hemisphere is joined to the top of a cylinder. How many curved outside surfaces does the combined solid have?", 2, [1, 3, 4], "The hemisphere contributes one curved surface and the cylinder contributes one curved side.", visual={"kind": "composite_solid"})
    three_cost = 6 + p * .3
    five_cost = three_cost / 3 * 5
    add_open(25, f"Three cups cost ${three_cost:.2f}. At the same price per cup, how much do five cups cost?", f"${five_cost:.2f}", f"One cup costs ${three_cost/3:.2f}; five cost ${five_cost:.2f}.")
    buses, seats = 3 + p % 4, 24 + p % 5
    add_mcq(26, f"There are {buses} buses with {seats} seats on each bus. How many seats are there altogether?", buses * seats, [buses + seats, buses * seats - seats, buses * seats + buses], f"{buses} × {seats} = {buses * seats}.")
    high, low = 24 + p % 7, 11 + p % 5
    add_open(27, "The thermometers show the temperature before and after a cold change. How many degrees did it fall?", high - low, f"{high} − {low} = {high - low} degrees.", visual={"kind": "thermometers", "high": high, "low": low})
    halfway = 40 + p * 2
    beyond = 7 + p % 6
    total_distance = halfway * 2
    remaining = halfway - beyond
    add_open(28, f"A trip is {total_distance} km long. After reaching halfway, the bus travels {beyond} km farther. How many kilometres remain?", remaining, f"Halfway is {halfway} km; {halfway} − {beyond} = {remaining} km remain.")
    line_start, line_step = 20 + p, 5 + p % 4
    line_values = [line_start + line_step * i for i in range(4)]
    add_mcq(29, "Which list gives the four labelled values on the number line?", ", ".join(map(str, line_values)), [", ".join(map(str, [value + 1 for value in line_values])), ", ".join(map(str, line_values[::-1])), ", ".join(map(str, [line_start + i for i in range(4)]))], f"The equally spaced marks increase by {line_step}.", visual={"kind": "number_line", "values": line_values})
    dozens, group = 4 + p % 5, 7 + p % 4
    remainder = dozens * 12 % group
    add_mcq(30, f"There are {dozens} dozen pencils. They are packed into groups of {group}. How many pencils are left over?", remainder, distinct_numbers(remainder, [remainder + 1, max(0, remainder - 1), group, group + 1], 4), f"{dozens} dozen is {dozens * 12}; dividing by {group} leaves {remainder}.")
    mass_a, mass_b = 34 + p * 2, 18 + p
    difference31 = mass_a - mass_b
    add_mcq(31, "About how much heavier is object A than object B?", f"{difference31} kg", [f"{mass_a} kg", f"{mass_b} kg", f"{difference31 + 10} kg"], f"The scales show about {mass_a} kg and {mass_b} kg; the difference is about {difference31} kg.", visual={"kind": "scales", "values": [mass_a, mass_b]})
    pattern_end, pattern_step32 = 70 + p * 2, 6 + p % 4
    previous = pattern_end - pattern_step32 * 3
    add_mcq(32, f"The number-line pattern is ___, {previous + pattern_step32}, {previous + 2*pattern_step32}, {pattern_end}. What number is missing?", previous, [previous - pattern_step32, previous + 1, pattern_end + pattern_step32], f"The pattern increases by {pattern_step32}, so the preceding value is {previous}.", visual={"kind": "backward_line"})
    table_total = 80 + p * 3
    known = [18 + p, 21 + p, 16 + p]
    missing33 = table_total - sum(known)
    add_open(33, f"A table total is {table_total}. Three categories contain {known[0]}, {known[1]} and {known[2]}. How many are in the missing category?", missing33, f"{table_total} − ({known[0]} + {known[1]} + {known[2]}) = {missing33}.", visual={"kind": "total_table", "known": known, "total": table_total})
    bars = [9 + p, 14 + p, 7 + p, 11 + p]
    difference34 = bars[1] - bars[0]
    add_mcq(34, "How many more votes did B receive than A?", difference34, [bars[1], bars[0], difference34 + 2], f"B has {bars[1]} votes and A has {bars[0]}; the difference is {difference34}.", visual={"kind": "bar_chart", "labels": ["A", "B", "C", "D"], "values": bars})
    add_mcq(35, "Which spinner gives the smallest chance of landing on blue?", "Spinner C", ["Spinner A", "Spinner B", "Spinner D"], "Spinner C has the smallest blue sector compared with its whole circle.", visual={"kind": "spinners"})
    twos, ones = 5 + p % 6, 4 + p % 5
    total36 = twos * 2 + ones
    add_open(36, f"A stack contains {twos} two-dollar coins and {ones} one-dollar coins. What is the total value?", f"${total36}", f"{twos} × $2 + {ones} × $1 = ${total36}.", visual={"kind": "coins", "twos": twos, "ones": ones})
    return q


def build_paper(paper_number):
    if not 1 <= paper_number <= PAPER_COUNT:
        raise ValueError(f"paper_number must be between 1 and {PAPER_COUNT}")
    paper = {
        "paper_number": paper_number,
        "title": f"Year 3 NAPLAN-Style Practice Paper {paper_number:02d}",
        "language": build_language(paper_number),
        "reading_passages": build_reading(paper_number),
        "writing": build_writing(paper_number),
        "numeracy": build_numeracy(paper_number),
    }
    paper["language"] = diversify_language(paper["language"], paper_number)
    paper["reading_passages"] = diversify_reading(paper["reading_passages"], paper_number)
    paper["numeracy"] = diversify_numeracy(paper["numeracy"], paper_number)
    paper["form"] = (paper_number - 1) % 5
    return paper


def build_all_papers():
    return [build_paper(number) for number in range(1, PAPER_COUNT + 1)]


if __name__ == "__main__":
    papers = build_all_papers()
    total = sum(len(paper["language"]) + sum(len(passage["questions"]) for passage in paper["reading_passages"]) + len(paper["numeracy"]) for paper in papers)
    print(f"Built {len(papers)} papers with {total} scored questions.")
