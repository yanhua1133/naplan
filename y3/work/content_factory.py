from __future__ import annotations

from copy import deepcopy
from html import escape
import json
import re
from pathlib import Path


LETTERS = "ABCD"
SPELLING_BANK_PATH = Path(__file__).with_name("spelling-bank.json")
NAMES = [
    "Ava", "Noah", "Mia", "Leo", "Ruby", "Eli", "Zoe", "Kai", "Nina", "Arlo",
    "Ivy", "Owen", "Lila", "Finn", "Maya", "Hugo", "Sara", "Jude", "Tara", "Max",
]
PARTNERS = [
    "Ben", "Chloe", "Dylan", "Emma", "Grace", "Henry", "Isla", "Jack", "Layla", "Mason",
    "Nora", "Oscar", "Piper", "Quinn", "Riley", "Sofia", "Theo", "Uma", "Violet", "Will",
]
PLACES = [
    "the library", "the oval", "the garden", "the museum", "the jetty", "the hall", "the creek",
    "the market", "the workshop", "the farm", "the beach", "the gallery", "the reserve",
    "the campsite", "the theatre", "the orchard", "the station", "the aquarium", "the bakery", "the lookout",
]

PAPER_CONTEXTS = [
    ("reef centre", "coral survey"), ("rail museum", "heritage display"),
    ("bush nursery", "native garden"), ("harbour workshop", "sailing project"),
    ("wildlife clinic", "animal-care roster"), ("river camp", "waterway study"),
    ("science dome", "space exhibition"), ("farm market", "produce stall"),
    ("weather station", "storm journal"), ("sports pavilion", "community carnival"),
    ("art gallery", "mural project"), ("forest school", "habitat trail"),
    ("city library", "reading festival"), ("coastal reserve", "dune restoration"),
    ("music hall", "concert program"), ("aviation shed", "flight showcase"),
    ("botanic garden", "seed collection"), ("marine lab", "rockpool study"),
    ("history centre", "local archive"), ("mountain lodge", "walking guide"),
]

DIVERSITY_FRAMES = [
    "At the {setting}, {prompt}",
    "For the {project}, {prompt}",
    "During {setting} work, {prompt}",
    "The {project} team asks: {prompt}",
    "In the {project}, {prompt}",
    "A {setting} card asks: {prompt}",
    "Before the {project}, {prompt}",
    "The {setting} notice asks: {prompt}",
    "While preparing the {project}, {prompt}",
    "A {setting} challenge asks: {prompt}",
    "To check the {project}, {prompt}",
    "At the {setting}, decide: {prompt}",
    "The {project} question is: {prompt}",
    "In a {setting} activity, {prompt}",
    "The {project} sheet asks: {prompt}",
    "For today's {setting} task, {prompt}",
    "A {project} clue asks: {prompt}",
    "During the {setting} session, {prompt}",
    "The {project} check asks: {prompt}",
    "On a {setting} card, {prompt}",
]

LANGUAGE_TASKS = {
    "L1": "article choice", "L2": "word-class check", "L3": "tense check",
    "L4": "describing-word check", "L5": "pronoun choice", "L6": "joining-word choice",
    "L7": "ownership-word choice", "L8": "agreement check", "L9": "category-word choice",
    "L10": "end-mark check", "L11": "apostrophe check", "L12": "comma check",
    "L13": "question-mark check", "L14": "speech-mark check", "L15": "capital-letter check",
    "L16": "possession check", "L17": "homophone choice", "L18": "sentence check",
    "L19": "pronoun replacement", "L20": "subject–verb check", "L21": "clause punctuation",
    "L22": "plural possession", "L23": "direct-question check", "L24": "reported-speech check",
    "L25": "agreement check",
}

NUMERACY_TASKS = {
    1: "number trail", 2: "place-value label", 3: "number comparison", 4: "total calculation",
    5: "difference calculation", 6: "equal-group count", 7: "fair-sharing problem", 8: "odd-number sort",
    9: "missing-factor puzzle", 10: "coin total", 11: "finishing-time check", 12: "calendar jump",
    13: "length conversion", 14: "boundary measurement", 15: "square-unit diagram", 16: "capacity match",
    17: "mass comparison", 18: "fraction diagram", 19: "halving problem", 20: "symmetry diagram",
    21: "angle description", 22: "solid-shape check", 23: "grid-location clue", 24: "data-table question",
    25: "graph comparison", 26: "chance experiment", 27: "growing pattern", 28: "missing-addend puzzle",
    29: "array-and-remainder problem", 30: "two-step grouping problem",
}


def diversity_frame(paper_number, prompt, offset=0):
    setting, project = PAPER_CONTEXTS[paper_number - 1]
    frame = DIVERSITY_FRAMES[(paper_number - 1 + offset) % len(DIVERSITY_FRAMES)]
    prompt = prompt[0].lower() + prompt[1:] if prompt else prompt
    return frame.format(setting=setting, project=project, prompt=prompt)


LANGUAGE_VERBS = [
    "sorted", "painted", "folded", "polished", "carried", "collected", "labelled", "counted", "sketched", "washed",
    "stacked", "folded", "mended", "displayed", "packed", "tested", "measured", "filled", "printed", "checked",
]
LANGUAGE_NOUNS = [
    "shells", "tickets", "flags", "lanterns", "bandages", "samples", "models", "baskets", "clouds", "cones",
    "frames", "maps", "ropes", "posters", "instruments", "wings", "seedlings", "tanks", "photographs", "backpacks",
]
LANGUAGE_ANIMALS = [
    "puppies", "kittens", "ducklings", "wallabies", "parrots", "dolphins", "lizards", "rabbits", "penguins", "koalas",
    "wombats", "frogs", "horses", "possums", "turtles", "echidnas", "seals", "pelicans", "butterflies", "beetles",
]
LANGUAGE_ADJECTIVES = [
    "striped", "golden", "wooden", "tiny", "clean", "river", "silver", "woven", "stormy", "bright",
    "square", "old", "strong", "colourful", "musical", "paper", "native", "shallow", "historic", "heavy",
]
LANGUAGE_ADVERBS = [
    "carefully", "neatly", "evenly", "carefully", "gently", "carefully", "securely", "correctly", "carefully", "thoroughly",
    "neatly", "carefully", "firmly", "proudly", "safely", "carefully", "regularly", "steadily", "clearly", "carefully",
]
PAST_VERBS = [
    ("sort", "sorted", "sorts", "sorting"), ("paint", "painted", "paints", "painting"),
    ("fold", "folded", "folds", "folding"), ("polish", "polished", "polishes", "polishing"),
    ("carry", "carried", "carries", "carrying"), ("collect", "collected", "collects", "collecting"),
    ("label", "labelled", "labels", "labelling"), ("count", "counted", "counts", "counting"),
    ("sketch", "sketched", "sketches", "sketching"), ("wash", "washed", "washes", "washing"),
    ("stack", "stacked", "stacks", "stacking"), ("fold", "folded", "folds", "folding"),
    ("mend", "mended", "mends", "mending"), ("display", "displayed", "displays", "displaying"),
    ("pack", "packed", "packs", "packing"), ("test", "tested", "tests", "testing"),
    ("measure", "measured", "measures", "measuring"), ("fill", "filled", "fills", "filling"),
    ("print", "printed", "prints", "printing"), ("check", "checked", "checks", "checking"),
]
CONTRACTIONS = [
    ("can't", "cannot"), ("won't", "will not"), ("isn't", "is not"), ("aren't", "are not"),
    ("hasn't", "has not"), ("haven't", "have not"), ("we're", "we are"), ("they're", "they are"),
    ("you're", "you are"), ("it's", "it is"), ("I'll", "I will"), ("she'll", "she will"),
    ("he'll", "he will"), ("we've", "we have"), ("they've", "they have"), ("couldn't", "could not"),
    ("shouldn't", "should not"), ("wouldn't", "would not"), ("doesn't", "does not"), ("wasn't", "was not"),
]


def reset_language_mcq(question, correct, distractors, explanation, shift):
    options, answer = rotate_options(correct, distractors, shift)
    question["options"] = options
    question["answer"] = answer
    question["explanation"] = explanation


def diversify_language_core(question, paper_number):
    index = paper_number - 1
    number = int(question["id"][1:])
    name, partner = NAMES[index], PARTNERS[index]
    setting, project = PAPER_CONTEXTS[index]
    verb, noun = LANGUAGE_VERBS[index], LANGUAGE_NOUNS[index]
    adjective, adverb = LANGUAGE_ADJECTIVES[index], LANGUAGE_ADVERBS[index]
    shift = index + number

    if number == 2:
        question["prompt"] = f"Which word is the verb in this sentence?<br><strong>{partner} {verb} the {adjective} {noun} {adverb}.</strong>"
        reset_language_mcq(question, verb, [partner, adjective, noun], f"<em>{verb.title()}</em> names the action {partner} performed, so it is the verb.", shift)
    elif number == 3:
        base, past, third, ing = PAST_VERBS[index]
        question["prompt"] = f"Which word correctly completes this sentence?<br><strong>Last week, {name} ___ the {noun} for the {project}.</strong>"
        reset_language_mcq(question, past, [base, third, ing], f"<em>Last week</em> shows the action happened in the past, so <em>{past}</em> is correct.", shift)
    elif number == 4:
        question["prompt"] = f"Which word tells how the action was done?<br><strong>The team {verb} each {noun[:-1] if noun.endswith('s') else noun} {adverb} at the {setting}.</strong>"
        reset_language_mcq(question, adverb, ["team", verb, setting.split()[-1]], f"<em>{adverb.title()}</em> describes how the team completed the action.", shift)
    elif number == 5:
        action = f"prepared the {noun}"
        question["prompt"] = f"Which sentence uses the correct subject pronoun for work on the {project}?"
        reset_language_mcq(question, f"{name} and I {action}.", [f"{name} and me {action}.", f"Me and {name} {action}.", f"{name} and myself {action}."], "The subject pronoun <em>I</em> is correct because the speaker is part of the subject.", shift)
    elif number == 6:
        question["prompt"] = f"Which word correctly joins these ideas?<br><strong>{name} worked {adverb} ___ the {project} had to be ready that afternoon.</strong>"
        reset_language_mcq(question, "because", ["but", "or", "until"], "<em>Because</em> introduces the reason for working that way.", shift)
    elif number == 7:
        singular_noun = noun[:-1] if noun.endswith("s") else noun
        question["prompt"] = f"The {adjective} {singular_noun} belongs to {name} and {partner}. Which word can replace <strong>the {singular_noun} belonging to {name} and {partner}</strong>?"
        reset_language_mcq(question, "theirs", ["his", "hers", "ours"], "<em>Theirs</em> shows that the item belongs to the two named people.", shift)
    elif number == 8:
        plural_animal = LANGUAGE_ANIMALS[index]
        singular_animal = plural_animal[:-3] + "y" if plural_animal.endswith("ies") else plural_animal[:-1]
        question["prompt"] = f"Which sentence about the {plural_animal} has correct subject–verb agreement?"
        reset_language_mcq(
            question,
            f"The {plural_animal} move towards the shelter.",
            [
                f"The {plural_animal} moves towards the shelter.",
                f"The {singular_animal} move towards the shelter.",
                f"The {plural_animal} moving towards the shelter.",
            ],
            f"The plural subject <em>{plural_animal}</em> agrees with the verb <em>move</em>.",
            shift,
        )
    elif number == 10:
        command = f"Please place the {noun} beside the {setting} desk___"
        question["prompt"] = f"Which punctuation mark correctly completes this calm command?<br><strong>{command}</strong>"
        reset_language_mcq(question, ".", ["?", "!", ","], "A calm command is a complete sentence and can end with a full stop.", shift)
    elif number == 11:
        correct, expanded = CONTRACTIONS[index]
        bare = correct.replace("'", "")
        misplaced = [bare[:position] + "'" + bare[position:] for position in range(len(bare) + 1)]
        misplaced = [candidate for candidate in misplaced if candidate != correct]
        wrong1, wrong2 = misplaced[:2]
        question["prompt"] = f"Which contraction is punctuated correctly for the words <strong>{expanded}</strong>?"
        reset_language_mcq(question, correct, [bare, wrong1, wrong2], f"The apostrophe in <em>{correct}</em> marks letters omitted from <em>{expanded}</em>.", shift)
    elif number == 12:
        intro = ["After the gates opened", "Before the first tour", "During the morning break", "When the rain stopped", "As the visitors arrived"][index % 5]
        clause = f"we arranged the {noun}"
        question["prompt"] = f"Which sentence uses a comma correctly for the {project}?"
        reset_language_mcq(question, f"{intro}, {clause}.", [f"{intro} {clause.split()[0]}, {' '.join(clause.split()[1:])}.", f"{intro},, {clause}.", f"{intro}; {clause}."], "A comma separates the introductory clause from the main clause.", shift)
    elif number == 13:
        direct = f"Where should we store the {noun} after the {project}"
        question["prompt"] = f"Which sentence spoken at the {setting} should end with a question mark?"
        reset_language_mcq(question, direct, [f"I know where the {noun} belong", f"Please store the {noun} now", f"The {noun} are beside the door"], "The correct option asks a direct question, so it needs a question mark.", shift)
    elif number == 14:
        speech = f"The {noun} are ready!"
        question["prompt"] = f"Which sentence punctuates {partner}'s excited words correctly?"
        reset_language_mcq(question, f"“{speech}” called {partner}.", [f"“{speech} called {partner}.”", f"{speech}” called {partner}.", f"“{speech}” Called {partner}."], "The spoken words and exclamation mark stay inside the speech marks.", shift)
    elif number == 16:
        animal = ["dog", "cat", "horse", "rabbit", "parrot", "goat", "pony", "kitten", "puppy", "donkey", "koala", "wombat", "possum", "lizard", "turtle", "echidna", "seal", "pelican", "otter", "penguin"][index]
        item = ["bowl", "blanket", "brush", "hutch", "perch", "rope", "saddle", "basket", "lead", "shelter", "branch", "burrow", "box", "rock", "tank", "nest", "pool", "platform", "toy", "gate"][index]
        question["prompt"] = f"Which words show that one {animal} owns the {item}?<br><strong>The ___ {item} was cleaned at the {setting}.</strong>"
        reset_language_mcq(question, f"{animal}'s", [f"{animal}s", f"{animal}s'", f"{animal} is"], f"The singular possessive form <em>{animal}'s</em> shows ownership.", shift)
    elif number == 17:
        question["prompt"] = f"Which word completes the sentence about the {project}?<br><strong>___ {noun} won a special award.</strong>"
        reset_language_mcq(question, "Their", ["There", "They're", "Theirs"], "<em>Their</em> shows that the items belong to a group.", shift)
    elif number == 18:
        complete = f"The {adjective} {noun[:-1] if noun.endswith('s') else noun} was placed beside the {setting}."
        question["prompt"] = f"Which option is a complete sentence connected with the {project}?"
        reset_language_mcq(question, complete, [f"Beside the {setting}.", f"Because the {project} finished.", f"Carrying the {noun} carefully."], "The correct option has a subject, a verb and a complete idea.", shift)
    elif number == 19:
        action = f"{verb} the {noun} for the {project}"
        question["prompt"] = f"Which pronoun can replace <strong>{name} and {partner}</strong>?<br><strong>{name} and {partner} {action}.</strong>"
        reset_language_mcq(question, "They", ["She", "We", "It"], "<em>They</em> replaces two named people.", shift)
    elif number == 20:
        subject = f"The box of {noun}"
        question["prompt"] = f"Which word agrees with the main subject?<br><strong>{subject} ___ beside the {setting} entrance.</strong>"
        reset_language_mcq(question, "is", ["are", "were", "be"], "The main subject <em>box</em> is singular, so <em>is</em> is correct.", shift)
    elif number == 21:
        opening = ["Before leaving", "When ready", "After checking", "As you leave", "Once finished"][index % 5]
        clause = f"return the {noun}"
        question["prompt"] = f"Which instruction for the {project} is punctuated correctly?"
        reset_language_mcq(question, f"{opening}, {clause}.", [f"{opening} {clause.split()[0]}, {' '.join(clause.split()[1:])}.", f"{opening},, {clause}.", f"{opening};, {clause}."], "A comma follows the introductory clause.", shift)
    elif number == 23:
        direct = f"When will the {project} begin at the {setting}"
        question["prompt"] = f"Which sentence is a direct question and needs a question mark?"
        reset_language_mcq(question, direct, [f"I wonder when the {project} will begin", f"Tell me when the {project} begins", f"The {project} begins at the {setting}"], "The correct option directly asks for information.", shift)
    elif number == 24:
        words = f"Bring the {noun}, please,"
        question["prompt"] = f"Which sentence correctly reports what {name} said during the {project}?"
        reset_language_mcq(question, f"“{words}” called {name}.", [f"“{words}”, called {name}.", f"“{words}” Called {name}.", f"“{words} called {name}.”"], "The comma stays inside the closing speech mark before the reporting clause.", shift)
    elif number == 25:
        adjective_end = [
            "damaged", "missing", "torn", "unlit", "clean", "labelled", "complete", "empty", "dark", "damaged",
            "square", "missing", "frayed", "finished", "damaged", "folded", "dry", "empty", "blurred", "open",
        ][index]
        singular = noun[:-1] if noun.endswith("s") else noun
        question["prompt"] = f"Which sentence has correct agreement for the {project}?"
        reset_language_mcq(question, f"Neither of the {noun} is {adjective_end}.", [f"Neither of the {noun} are {adjective_end}.", f"Neither of the {singular} is {adjective_end}.", f"Neither the {noun} are {adjective_end}."], "The singular subject <em>neither</em> agrees with <em>is</em>.", shift)
    return question


def diversify_language_questions(questions, paper_number):
    for question in questions:
        number = int(question["id"][1:])
        if number <= 25:
            diversify_language_core(question, paper_number)
            question["prompt"] = diversity_frame(paper_number, question["prompt"], number)
    return questions


def diversify_reading_passages(passages, paper_number):
    for passage_index, passage in enumerate(passages):
        for question_index, question in enumerate(passage["questions"]):
            question["prompt"] = diversity_frame(
                paper_number,
                question["prompt"],
                31 + question_index + passage_index * 6,
            )
    return passages


def diversify_numeracy_prompt(paper_number, number, prompt):
    setting, project = PAPER_CONTEXTS[paper_number - 1]
    task = NUMERACY_TASKS[number]
    frames = [
        "At the {setting}, solve this {task}: {prompt}",
        "For the {project}, answer this {task}: {prompt}",
        "A {setting} activity includes this {task}: {prompt}",
        "The {project} team needs this {task} solved: {prompt}",
        "In the {project}, complete this {task}: {prompt}",
        "A {setting} card gives this {task}: {prompt}",
        "Before the {project}, solve this {task}: {prompt}",
        "The {setting} notice shows this {task}: {prompt}",
        "While preparing the {project}, answer this {task}: {prompt}",
        "A {setting} challenge uses this {task}: {prompt}",
        "To check the {project}, solve this {task}: {prompt}",
        "At the {setting}, decide this {task}: {prompt}",
        "The next {project} task is a {task}: {prompt}",
        "In a {setting} session, complete this {task}: {prompt}",
        "The {project} sheet includes this {task}: {prompt}",
        "For today's {setting} work, solve this {task}: {prompt}",
        "A {project} clue requires this {task}: {prompt}",
        "During the {setting} session, answer this {task}: {prompt}",
        "The {project} check uses this {task}: {prompt}",
        "On a {setting} card, complete this {task}: {prompt}",
    ]
    return frames[(paper_number - 1 + number) % len(frames)].format(
        setting=setting,
        project=project,
        task=task,
        prompt=prompt,
    )



def rotate_options(correct, distractors, shift):
    options = [str(correct)] + [str(value) for value in distractors]
    shift %= 4
    options = options[shift:] + options[:shift]
    return options, LETTERS[options.index(str(correct))]


def mcq(question_id, prompt, correct, distractors, explanation, shift):
    options, answer = rotate_options(correct, distractors, shift)
    return {
        "id": question_id,
        "prompt": prompt,
        "options": options,
        "answer": answer,
        "explanation": explanation,
    }


def build_language(paper_number):
    index = paper_number - 1
    name = NAMES[index]
    partner = PARTNERS[index]
    place = PLACES[index]
    article_nouns = [
        "umbrella", "orange", "igloo", "engine", "octopus", "apron", "acorn", "elephant", "island", "owl",
        "astronaut", "oven", "insect", "envelope", "avocado", "easel", "anchor", "orchid", "otter", "iceberg",
    ]
    article_noun = article_nouns[index]
    location_name = [
        "Canberra", "Darwin", "Hobart", "Perth", "Adelaide", "Sydney", "Brisbane", "Broome", "Ballarat", "Cairns",
        "Geelong", "Newcastle", "Orange", "Fremantle", "Bendigo", "Wollongong", "Albany", "Toowoomba", "Launceston", "Mildura",
    ][index]
    animal = [
        "puppies", "kittens", "ducklings", "wallabies", "parrots", "dolphins", "lizards", "rabbits", "penguins", "koalas",
        "wombats", "frogs", "horses", "possums", "turtles", "echidnas", "seals", "pelicans", "butterflies", "beetles",
    ][index]
    category = [
        ("violin, trumpet and drum", "instruments", ["games", "buildings", "vehicles"]),
        ("oak, gum and maple", "trees", ["rivers", "insects", "tools"]),
        ("ruby, emerald and sapphire", "gems", ["planets", "fabrics", "spices"]),
        ("soccer, tennis and cricket", "sports", ["metals", "flowers", "roads"]),
        ("carrot, bean and pumpkin", "vegetables", ["birds", "clouds", "machines"]),
        ("Monday, Tuesday and Friday", "weekdays", ["months", "seasons", "colours"]),
        ("circle, square and triangle", "shapes", ["animals", "drinks", "buildings"]),
        ("copper, silver and gold", "metals", ["trees", "oceans", "songs"]),
        ("rose, daisy and orchid", "flowers", ["tools", "planets", "sports"]),
        ("Mercury, Earth and Mars", "planets", ["instruments", "vegetables", "fabrics"]),
        ("cotton, wool and silk", "fabrics", ["rivers", "reptiles", "vehicles"]),
        ("hammer, saw and drill", "tools", ["birds", "clouds", "gems"]),
        ("red, blue and yellow", "colours", ["months", "metals", "roads"]),
        ("January, March and June", "months", ["weekdays", "spices", "trees"]),
        ("eagle, robin and magpie", "birds", ["flowers", "tools", "planets"]),
        ("Pacific, Indian and Atlantic", "oceans", ["cities", "fabrics", "sports"]),
        ("basil, mint and parsley", "herbs", ["metals", "insects", "buildings"]),
        ("ant, beetle and moth", "insects", ["oceans", "drinks", "roads"]),
        ("bus, train and ferry", "transport", ["gems", "trees", "seasons"]),
        ("spring, autumn and winter", "seasons", ["tools", "birds", "vehicles"]),
    ][index]
    q = []
    q.append(mcq("L1", f"Which word correctly completes this sentence?<br><strong>{name} drew ___ {article_noun} on a card before visiting {place}.</strong>", "an", ["a", "some", "many"], f"Use <em>an</em> before the vowel sound at the start of <em>{article_noun}</em>.", index + 1))
    q.append(mcq("L2", f"Which word is the verb in this sentence?<br><strong>{partner} measured the bright banner carefully.</strong>", "measured", [partner, "bright", "banner"], f"<em>Measured</em> tells what {partner} did, so it is the verb.", index + 2))
    q.append(mcq("L3", f"Which word correctly completes this sentence?<br><strong>Yesterday, {name} ___ the heavy basket into {place}.</strong>", "carried", ["carry", "carries", "carrying"], "The word <em>Yesterday</em> shows that the action happened in the past, so <em>carried</em> is correct.", index + 3))
    q.append(mcq("L4", f"Which word tells how the action was done?<br><strong>The group waited patiently beside {place}.</strong>", "patiently", ["group", "waited", "beside"], "<em>Patiently</em> describes how the group waited, so it is an adverb.", index + 4))
    q.append(mcq("L5", "Which sentence is correct?", f"{name} and I planted the seeds.", [f"{name} and me planted the seeds.", f"Me and {name} planted the seeds.", f"{name} and myself planted the seeds."], "The subject pronoun <em>I</em> is correct because the speaker is part of the subject.", index + 5))
    q.append(mcq("L6", f"Which word correctly joins these ideas?<br><strong>{name} wore a hat ___ the afternoon was sunny at {place}.</strong>", "because", ["but", "or", "until"], "<em>Because</em> introduces the reason for wearing the hat.", index + 6))
    q.append(mcq("L7", f"Which word correctly completes this sentence?<br><strong>{partner} packed ___ striped backpack.</strong>", "their", ["there", "they're", "theirs"], f"<em>Their</em> is the possessive word that shows the backpack belongs to {partner}.", index + 7))
    q.append(mcq("L8", f"Which sentence about the {animal} is correct?", f"The {animal} chase the ball.", [f"The {animal} chases the ball.", f"The {animal} chases the balls.", f"The {animal} chasing the ball."], f"The plural subject <em>{animal}</em> agrees with the verb <em>chase</em>.", index + 8))
    category_words, category_answer, category_distractors = category
    q.append(mcq("L9", f"Which word can be used instead of <strong>{category_words}</strong>?", category_answer, category_distractors, f"All three examples are {category_answer}.", index + 9))
    q.append(mcq("L10", f"Which punctuation mark correctly completes this command?<br><strong>Please close the gate at {place}___</strong>", ".", ["?", "!", ","], "This calm command is a complete sentence and can end with a full stop.", index + 10))
    q.append(mcq("L11", f"Which word is punctuated correctly in the sentence about {name}?", "didn't", ["didnt", "did'nt", "d'idnt"], "The apostrophe in <em>didn't</em> replaces the missing letter <em>o</em> in <em>did not</em>.", index + 11))
    intro = ["After lunch", "Before sunrise", "During recess", "At the bell", "On Saturday"][index % 5]
    q.append(mcq("L12", f"Which sentence about {place} is punctuated correctly?", f"{intro}, we checked the seedlings.", [f"{intro} we, checked the seedlings.", f"{intro} we checked, the seedlings.", f"{intro}; we checked the seedlings."], f"A comma separates the introductory phrase <em>{intro}</em> from the main clause.", index + 12))
    q.append(mcq("L13", f"Which sentence should end with a question mark when {name} is speaking?", f"Where did you put the map for {place}", [f"I know where the map is", f"Please put the map away", f"The map is beside the door"], "The sentence asks a direct question, so it needs a question mark.", index + 13))
    speech = f"I found the token near {place}!"
    q.append(mcq("L14", f"Which sentence uses speech marks and punctuation correctly for {partner}'s words?", f"“{speech}” called {partner}.", [f"“{speech} called {partner}.”", f"{speech}” called {partner}.", f"“{speech}” Called {partner}."], "The spoken words and exclamation mark are inside the speech marks, followed by the reporting clause.", index + 14))
    q.append(mcq("L15", f"Which sentence uses capital letters correctly for {name}'s trip?", f"On Monday, {name} visited {location_name}.", [f"On monday, {name} visited {location_name}.", f"On Monday, {name.lower()} visited {location_name}.", f"On Monday, {name} visited {location_name.lower()}."], f"The sentence begins with a capital, and <em>Monday</em>, <em>{name}</em> and <em>{location_name}</em> are proper nouns.", index + 15))
    pet = ["dog", "cat", "horse", "rabbit", "parrot"][index % 5]
    q.append(mcq("L16", f"Which words correctly complete this sentence?<br><strong>The ___ bowl was beside {place}.</strong>", f"{pet}'s", [f"{pet}s", f"{pet}s'", f"{pet} is"], f"The bowl belongs to one {pet}, so the singular possessive form is <em>{pet}'s</em>.", index + 16))
    q.append(mcq("L17", f"Which word correctly completes this sentence?<br><strong>___ class display won a prize at {place}.</strong>", "Their", ["There", "They're", "Theirs"], "<em>Their</em> shows that the display belongs to the class members.", index + 17))
    q.append(mcq("L18", f"Which is a complete sentence about {place}?", f"The tiny frog jumped into the pond near {place}.", ["Under the old bridge.", "Because the rain stopped.", "Running across the wet grass."], "The correct option has a complete subject and verb and expresses a complete idea.", index + 18))
    q.append(mcq("L19", f"Which word can replace <strong>{name} and {partner}</strong> in this sentence?<br><strong>{name} and {partner} carried the posters into {place}.</strong>", "They", ["She", "We", "It"], "<em>They</em> is the plural pronoun that replaces two named people.", index + 19))
    q.append(mcq("L20", f"Which word correctly completes this sentence?<br><strong>The basket of apples ___ on the bench at {place}.</strong>", "is", ["are", "were", "be"], "The main subject is singular: <em>basket</em>. Therefore <em>is</em> is correct.", index + 20))
    q.append(mcq("L21", f"Which sentence about leaving {place} is correctly punctuated?", f"Before we leave, please check the gate at {place}.", [f"Before we leave please, check the gate at {place}.", f"Before, we leave please check the gate at {place}.", f"Before we leave please check, the gate at {place}."], "The introductory clause is followed by a comma.", index + 21))
    plural_noun = ["children", "teachers", "players", "artists", "visitors"][index % 5]
    possessive = "children's" if plural_noun == "children" else f"{plural_noun}'"
    if plural_noun == "children":
        distractors = ["childrens", "childrens'", "childrens's"]
    else:
        singular_noun = plural_noun[:-1]
        distractors = [plural_noun, f"{singular_noun}'s", f"{plural_noun}'s"]
    q.append(mcq("L22", f"Where should the missing apostrophe go?<br><strong>The {plural_noun} lunchboxes were packed beside {place}.</strong>", possessive, distractors, f"The lunchboxes belong to more than one member of the group; the possessive form is <em>{possessive}</em>.", index + 22))
    q.append(mcq("L23", f"Which sentence about travelling to {place} should end with a question mark?", f"When will the bus arrive at {place}", [f"I wonder when the bus will arrive at {place}", f"Tell me when the bus arrives at {place}", f"The bus will arrive near {place}"], "The correct option asks a direct question.", index + 23))
    q.append(mcq("L24", f"Which sentence uses speech punctuation correctly when {name} calls to {partner}?", f"“Wait for me,” called {name}.", [f"“Wait for me”, called {name}.", f"“Wait for me” called {name}.", f"“Wait for me called {name}.”"], "The comma belongs inside the closing speech mark before the reporting clause.", index + 24))
    q.append(mcq("L25", f"Which sentence about the boxes at {place} is correct?", "Neither of the boxes is empty.", ["Neither of the boxes are empty.", "Neither of the box is empty.", "Neither the boxes are empty."], "The singular subject <em>neither</em> agrees with <em>is</em>.", index + 25))

    bank = json.loads(SPELLING_BANK_PATH.read_text(encoding="utf-8"))
    if bank["status"] != "verified" or len(bank["entries"]) != 500:
        raise ValueError("Spelling bank is not verified or has the wrong size")
    dictation_start = index * 15
    proofreading_start = 300 + index * 10
    dictation_entries = bank["entries"][dictation_start:dictation_start + 15]
    proofreading_entries = bank["entries"][proofreading_start:proofreading_start + 10]

    for offset, entry in enumerate(dictation_entries, start=26):
        correct = entry["word"]
        q.append({
            "id": f"L{offset}",
            "spelling_type": "dictation",
            "prompt": f"Teacher or parent spelling word: <strong>{correct}</strong>.",
            "spoken_word": correct,
            "spoken_sentence": f"Your spelling word is {correct}.",
            "answer": correct,
            "explanation": f"Teacher script: say <em>{correct}</em>, pause, then repeat <em>{correct}</em>.",
        })

    for item_index, entry in enumerate(proofreading_entries):
        offset = 41 + item_index
        correct = entry["word"]
        wrong = entry["wrong"]
        sentence = entry["sentence"]
        if sentence.lower().count(correct.lower()) != 1:
            raise ValueError(f"Proofreading sentence must contain {correct!r} exactly once")
        escaped_sentence = escape(sentence)
        token = escape(wrong)
        if offset <= 45:
            token = (
                '<span style="text-decoration:underline;'
                'text-decoration-thickness:1.2px;text-underline-offset:1px">'
                f"{token}</span>"
            )
        prompt = re.sub(
            rf"\b{re.escape(correct)}\b",
            lambda _: token,
            escaped_sentence,
            count=1,
            flags=re.IGNORECASE,
        )
        q.append({
            "id": f"L{offset}",
            "spelling_type": "underlined" if offset <= 45 else "identify",
            "prompt": prompt,
            "correct_sentence": sentence,
            "incorrect_word": wrong,
            "answer": correct,
            "explanation": f"The incorrect word <em>{wrong}</em> should be spelled <em>{correct}</em>.",
        })
    return diversify_language_questions(q, paper_number)


INFO_RECORDS = [
    ("Leaf-Tailed Geckos", "leaf-tailed geckos", "rainforest trees", "mottled skin and flat tails", "blend with bark", "small insects", "tree clearing", "protecting old forest"),
    ("City Microbats", "microbats", "tree hollows and roof spaces", "high-pitched calls", "find insects in darkness", "moths and mosquitoes", "loss of safe roosts", "keeping old hollow trees"),
    ("Rockpool Crabs", "rockpool crabs", "shallow pools beside the sea", "hard shells and strong claws", "stay safe between tides", "algae and tiny animals", "plastic litter", "taking rubbish home"),
    ("Busy Blue-Banded Bees", "blue-banded bees", "gardens and bushland", "rapidly vibrating wings", "shake pollen from flowers", "nectar and pollen", "fewer flowering plants", "planting native flowers"),
    ("Mountain Pygmy Possums", "mountain pygmy possums", "rocky alpine slopes", "thick fur and gripping feet", "move among cold rocks", "seeds, fruit and insects", "warmer winters", "protecting alpine habitat"),
    ("Murray River Turtles", "river turtles", "slow rivers and wetlands", "webbed feet and smooth shells", "swim and rest near logs", "water plants and small animals", "damaged nesting banks", "keeping riverbanks undisturbed"),
    ("Echidnas on the Move", "echidnas", "woodlands and grasslands", "strong claws and a long sticky tongue", "dig for hidden food", "ants and termites", "busy roads", "driving carefully near wildlife signs"),
    ("Little Penguins", "little penguins", "rocky coasts and sandy burrows", "waterproof feathers and flipper-like wings", "swim quickly after fish", "small fish and squid", "bright lights near nests", "shielding lights along the coast"),
    ("Wetland Frogs", "wetland frogs", "reed beds and shallow ponds", "powerful legs and moist skin", "leap and breathe near water", "insects and spiders", "polluted water", "keeping drains free of chemicals"),
    ("Wombat Burrows", "wombats", "woodland slopes", "strong shoulders and digging claws", "build cool underground shelters", "grasses and roots", "blocked burrow entrances", "leaving known burrows clear"),
    ("Mangroves at Work", "mangrove trees", "muddy tropical shorelines", "tangled roots", "hold soil and shelter young animals", "sunlight and nutrients", "rubbish caught in roots", "joining shoreline clean-ups"),
    ("Swift Parrots", "swift parrots", "flowering forests", "fast wings and brush-tipped tongues", "travel between nectar trees", "nectar and insects", "loss of flowering habitat", "protecting mature food trees"),
    ("Sand Goannas", "sand goannas", "dry woodland and dunes", "long claws and a forked tongue", "dig and detect nearby food", "insects, eggs and small animals", "discarded fishing line", "removing tangled litter"),
    ("Seagrass Meadows", "seagrass plants", "shallow coastal water", "long flexible leaves", "slow waves and shelter sea life", "sunlight and nutrients", "cloudy polluted water", "reducing soil runoff"),
    ("Flying Fox Camps", "flying foxes", "tall trees near food sources", "wide wings and a strong sense of smell", "find blossoms at night", "nectar, pollen and fruit", "heatwaves", "protecting shaded camp trees"),
    ("Bilbies After Dark", "bilbies", "dry grasslands", "large ears and strong front claws", "hear danger and dig burrows", "seeds, bulbs and insects", "introduced predators", "supporting fenced wildlife areas"),
    ("Pelicans at the Lake", "Australian pelicans", "lakes, rivers and estuaries", "large bills with flexible pouches", "scoop fish from water", "fish and crustaceans", "fishing hooks", "disposing of tackle safely"),
    ("Orchid Pollinators", "native orchids", "open forests", "special flower shapes and scents", "attract particular insects", "sunlight, water and minerals", "trampled plants", "staying on marked tracks"),
    ("Sea Lions Ashore", "Australian sea lions", "sandy islands and rocky beaches", "streamlined bodies and strong flippers", "dive and steer underwater", "fish and squid", "discarded nets", "reporting marine debris"),
    ("Termite Mounds", "termites", "tropical grasslands", "tall mounds with narrow air passages", "keep the nest temperature steady", "dry grass and wood", "damage from vehicles", "keeping vehicles on formed tracks"),
]


PROCEDURE_RECORDS = [
    ("Make a Wind Direction Arrow", "a simple arrow that shows wind direction", ["a paper plate", "a straw", "cardboard", "a split pin", "a compass"], "mark north, south, east and west", "attach the cardboard arrow to the straw", "fasten the straw so it turns freely", "place the plate outside and record where the arrow points"),
    ("Test a Paper Bridge", "a paper bridge and compare how much mass it holds", ["two books", "two sheets of paper", "coins", "a ruler", "a results table"], "place the books 20 cm apart", "lay one flat sheet across the gap", "add coins one at a time", "fold the second sheet and repeat the fair test"),
    ("Grow a Seed Viewer", "a clear seed viewer for observing roots", ["a clear cup", "paper towel", "bean seeds", "water", "a marker"], "line the cup with damp paper towel", "slide seeds between the towel and cup", "mark the water level", "observe and record changes each day"),
    ("Build a Rain Gauge", "a gauge that measures rainfall", ["a straight plastic bottle", "scissors used by an adult", "small stones", "a ruler", "a marker"], "ask an adult to remove the bottle top", "place stones in the base", "mark centimetre lines on the side", "set the gauge outside and record the water level"),
    ("Track a Moving Shadow", "a chart showing how a shadow moves", ["chalk", "a tall bottle", "a ruler", "a clock", "a sunny paved place"], "stand the bottle in one position", "trace the shadow at 9 am", "label the time beside the line", "repeat each hour without moving the bottle"),
    ("Make a Paper Helicopter", "a paper spinner and compare its fall", ["paper strips", "scissors", "paper clips", "a ruler", "a timer"], "cut two equal blades", "fold the blades in opposite directions", "attach one paper clip", "drop from the same height and time each fall"),
    ("Create a String Telephone", "a telephone that carries sound along string", ["two paper cups", "string", "a pencil", "two paper clips", "a partner"], "ask an adult to make one hole in each cup", "thread and secure the string", "stand apart until the string is tight", "speak softly while a partner listens"),
    ("Make a Mini Greenhouse", "a covered container for observing seedlings", ["a clear container", "soil", "three seeds", "water", "a label"], "add equal soil to the container", "plant the seeds at the same depth", "add a small measured amount of water", "cover loosely and observe each day"),
    ("Compare Soil Drainage", "a fair test of how quickly soils drain", ["three cups with holes", "sand", "garden soil", "clay soil", "equal cups of water"], "place equal soil amounts in the cups", "stand each cup over a container", "pour in equal water amounts", "compare the water collected after five minutes"),
    ("Make a Sundial", "a dial that estimates time from a shadow", ["a paper plate", "a pencil", "reusable adhesive", "a marker", "a clock"], "stand the pencil upright at the centre", "place the plate in a sunny fixed position", "mark the shadow at 10 am", "return hourly to add labelled marks"),
    ("Test Ramp Surfaces", "a fair test of how surfaces affect a toy car", ["a board", "a toy car", "books", "three surface materials", "a tape measure"], "raise one end of the board", "cover the ramp with the first surface", "release the car without pushing", "measure the distance and repeat for each surface"),
    ("Build a Bird Water Station", "a shallow water station for garden birds", ["a shallow dish", "clean stones", "fresh water", "a shady place", "a cleaning brush"], "wash the dish and stones", "arrange stones so they rise above the water", "place the dish in shade", "replace the water and clean the dish daily"),
    ("Observe Evaporation", "a test showing where water evaporates fastest", ["three identical dishes", "water", "a measuring cup", "labels", "three locations"], "pour equal water into each dish", "label the dishes", "place them in sun, shade and indoors", "measure the water left after one day"),
    ("Make a Compass Rose Map", "a map that uses directions to show locations", ["grid paper", "a pencil", "coloured pencils", "a ruler", "a compass"], "draw a large grid", "add a north arrow", "mark three classroom objects", "write directions from the door to each object"),
    ("Test Fabric Absorbency", "a fair test of how much water fabrics absorb", ["equal fabric squares", "a dropper", "water", "small trays", "a results table"], "place each fabric in a separate tray", "add ten drops to each square", "wait one minute", "compare the amount of water left in each tray"),
    ("Make a Balance Scale", "a simple scale for comparing masses", ["a coat hanger", "two paper cups", "string", "a hook", "small objects"], "attach equal strings to the cups", "hang one cup from each end", "suspend the hanger so it moves freely", "place objects in the cups and compare their levels"),
    ("Record Cloud Cover", "a chart for comparing cloud cover", ["a notebook", "a pencil", "a clock", "a safe viewing place", "a four-part sky diagram"], "choose the same observation time", "look at the whole sky", "shade the matching part of the diagram", "repeat for five days and compare"),
    ("Build a Foil Boat", "a foil boat and test how many counters it holds", ["equal foil squares", "a tub of water", "counters", "a towel", "a results table"], "shape the first foil square into a boat", "float it carefully", "add counters one at a time", "redesign with a new square and repeat"),
    ("Compare Sound Barriers", "a test of materials that reduce sound", ["a ticking timer", "three boxes", "fabric", "paper", "a quiet room"], "place the timer in the first empty box", "listen from the same distance", "wrap the timer with one material", "repeat and compare how clearly it can be heard"),
    ("Map a Playground Route", "a scaled route around the playground", ["grid paper", "a clipboard", "a pencil", "a metre wheel", "a ruler"], "choose a safe starting point", "measure each straight section", "record turns and distances", "draw the route using one square for each metre"),
]


NARRATIVE_RECORDS = [
    ("The Clockwork Feather", "Ava", "a silver feather", "the school storeroom", "it began ticking and pointed towards a locked drawer", "asked the caretaker for help and followed a faded diagram", "the drawer opened to reveal a box of old school badges"),
    ("The Lantern Under the Jetty", "Noah", "a brass lantern", "a quiet jetty", "its light flashed even though it held no candle", "matched the flashes to marks carved in the timber", "a hidden message thanked people who protected the bay"),
    ("The Map in the Music Case", "Mia", "a folded map", "the rehearsal room", "the map showed a room that was not on the school plan", "compared the drawing with the corridor windows", "a narrow cupboard held instruments from the first school band"),
    ("The Button That Hummed", "Leo", "a blue glass button", "the community hall", "it hummed louder near one wall", "listened carefully and found a loose wooden panel", "behind it was a time capsule ready to be opened"),
    ("The Tiny Door in the Fence", "Ruby", "a painted key", "the botanic garden", "a tiny door appeared between two fence posts", "used the key only after asking the gardener", "the door opened onto a model garden built by children long ago"),
    ("The Message in the Bottle", "Eli", "a green bottle", "a rocky beach", "the message inside used symbols instead of words", "copied the symbols and compared them with trail signs", "the symbols led to a safe nesting area that needed protection"),
    ("The Bell in the Attic", "Zoe", "a small handbell", "her grandmother's attic", "the bell rang whenever it faced north", "followed its direction through stacked boxes", "she found a missing album of family photographs"),
    ("The Book That Changed Shelves", "Kai", "a red library book", "the town library", "it appeared on a different shelf each morning", "recorded each shelf number and noticed a pattern", "the pattern pointed to a forgotten reading club notice"),
    ("The Kite Above the Fog", "Nina", "a bright kite", "a misty oval", "the kite string tugged towards the empty equipment shed", "followed the string while staying with her coach", "a trapped bird flew free when the shed door opened"),
    ("The Stone with a Warm Centre", "Arlo", "a smooth black stone", "a creek crossing", "the stone stayed warm after sunset", "showed it to the park ranger and marked its location", "the ranger explained it covered a tiny natural warm spring"),
    ("The Window in the Tree", "Ivy", "a round window", "an old fig tree", "a light flickered behind the glass", "looked through without disturbing the bark", "she saw a miniature display made from fallen leaves"),
    ("The Ticket for Platform Zero", "Owen", "an old train ticket", "the railway museum", "the ticket named a platform that no longer existed", "asked a guide and searched an archived station map", "a painted platform sign was found behind a display wall"),
    ("The Robot in the Recycling Bin", "Lila", "a palm-sized robot", "the science room", "it sorted objects but refused every metal lid", "tested the lids and found one was magnetic", "the robot used it as the missing wheel for its cart"),
    ("The Telescope That Pointed Down", "Finn", "a wooden telescope", "the lookout tower", "it pointed towards the ground instead of the sky", "followed the marked direction to a loose floorboard", "beneath it was a logbook of past weather watchers"),
    ("The Garden Gate at Midnight", "Maya", "a copper gate", "the school garden", "it opened only when the moonlight crossed its centre", "waited with an adult and observed the shadow pattern", "the gate revealed a night-flowering plant in bloom"),
    ("The Island Drawn in Chalk", "Hugo", "a chalk island", "the covered playground", "new paths appeared whenever rain tapped the roof", "photographed each change and joined the paths", "the completed map showed where a lost class token had rolled"),
    ("The Quiet Room at the Museum", "Sara", "a carved wooden bird", "the local museum", "it made a soft call near one display case", "told the curator and checked the case label", "the call came from a hidden sound recording in the base"),
    ("The Snow Globe in Summer", "Jude", "a cracked snow globe", "a second-hand shop", "tiny paper stars moved without being shaken", "held it near the window and noticed warm air entering", "the shopkeeper repaired the loose base and saved the stars"),
    ("The Tunnel Behind the Mural", "Tara", "a painted tunnel", "the art room", "one painted brick felt cooler than the others", "asked the teacher before pressing it", "a storage hatch opened to reveal unused art frames"),
    ("The Last Light in the Tower", "Max", "a blinking lamp", "an old coastal tower", "the lamp flashed a repeating group of numbers", "wrote the pattern and compared it with a visitor map", "the numbers identified steps needing repair before the tour"),
]


TABLE_ITEMS = [
    ["Carrots", "Tomatoes", "Beans", "Pumpkins"], ["Apples", "Pears", "Oranges", "Melons"],
    ["Rice", "Pasta", "Flour", "Oats"], ["Storybooks", "Atlases", "Dictionaries", "Comics"],
    ["Towels", "Blankets", "Jackets", "Hats"], ["Cans", "Bottles", "Boxes", "Cartons"],
    ["Potatoes", "Onions", "Peas", "Corn"], ["Pencils", "Rulers", "Erasers", "Markers"],
    ["Soap", "Shampoo", "Toothpaste", "Brushes"], ["Seedlings", "Seeds", "Bulbs", "Cuttings"],
    ["Mugs", "Plates", "Bowls", "Spoons"], ["Notebooks", "Folders", "Paper packs", "Envelopes"],
    ["Lentils", "Beans", "Chickpeas", "Rice bags"], ["Socks", "Shoes", "Scarves", "Gloves"],
    ["Paint tins", "Brush packs", "Canvas rolls", "Clay blocks"], ["Toy cars", "Puzzles", "Balls", "Blocks"],
    ["Water bottles", "Lunch boxes", "Backpacks", "Raincoats"], ["Herbs", "Flowers", "Ferns", "Shrubs"],
    ["Batteries", "Torches", "Radios", "Chargers"], ["Biscuits", "Crackers", "Cereal", "Fruit cups"],
]


POEM_RECORDS = [
    ("After the Rain", "rain in the gutter", "silver", "clouds", "puddle", "boots", "street", "curious and delighted"),
    ("Morning at the Jetty", "ropes against the jetty", "golden", "mist", "harbour", "shoes", "jetty", "calm and observant"),
    ("Wind in the Orchard", "wind in the branches", "green", "clouds", "water trough", "feet", "orchard", "playful and alert"),
    ("Evening on the Oval", "the flag in the breeze", "purple", "birds", "wet grass", "shoes", "oval", "peaceful and thoughtful"),
    ("Moon over the Creek", "reeds beside the water", "pale", "mist", "creek", "boots", "track", "quiet and amazed"),
    ("Sunrise at the Beach", "waves on the shore", "orange", "gulls", "rockpool", "sandals", "shore", "hopeful and excited"),
    ("Fog in the Garden", "leaves in the breeze", "white", "mist", "birdbath", "boots", "path", "careful and curious"),
    ("Night at the Station", "wheels on the rails", "blue", "clouds", "window", "steps", "platform", "patient and watchful"),
    ("Storm Leaving Town", "rain on the roofs", "copper", "clouds", "drain", "boots", "lane", "relieved and interested"),
    ("Dawn in the Bush", "magpies in the trees", "gold", "mist", "billabong", "shoes", "trail", "awake and delighted"),
    ("Light on the River", "water against the bank", "silver", "clouds", "river bend", "paddles", "bank", "calm and thankful"),
    ("Autumn in the Park", "leaves under my feet", "bronze", "clouds", "fountain", "feet", "path", "cheerful and thoughtful"),
    ("Rain on the Roof", "rain on the roof", "silver", "clouds", "window", "socks", "room", "safe and relaxed"),
    ("Stars above the Camp", "wood in the fire", "amber", "smoke", "billy can", "boots", "clearing", "peaceful and amazed"),
    ("Tide at Twilight", "shells in the wash", "pink", "gulls", "rockpool", "feet", "beach", "curious and content"),
    ("Winter at the Lookout", "wind along the rail", "grey", "clouds", "telescope lens", "gloves", "lookout", "cold but excited"),
    ("Spring beside the Lake", "frogs beside the lake", "green", "clouds", "lake", "shoes", "boardwalk", "lively and pleased"),
    ("Shadows in the Lane", "wind against the fence", "violet", "clouds", "window", "steps", "lane", "curious and brave"),
    ("Quiet in the Library", "turning pages", "cream", "dust", "glass case", "shoes", "library", "calm and absorbed"),
    ("Clouds over the Farm", "the turning windmill", "pearl", "clouds", "dam", "boots", "field", "hopeful and observant"),
]


def build_information_passage(paper_number, start_id=1):
    title, subject, habitat, feature, benefit, food, threat, action = INFO_RECORDS[paper_number - 1]
    text = [
        f"{subject.capitalize()} live in {habitat}. They are well suited to this place, but they still need food, water and shelter to survive. Conditions can change across the day and through the seasons, so safe resting places are important.",
        f"Features such as {feature} help them {benefit}. These adaptations make everyday tasks easier and can also help them avoid danger. Young organisms survive best when their surroundings provide suitable food or nutrients and shelter.",
        f"They obtain what they need from {food}. As they live and grow in their habitat, they also become part of a larger food web that connects plants and animals. Changes to one part of this web can affect many other living things.",
        f"One challenge is {threat}. People can help by {action}, observing living things responsibly and leaving natural shelters undisturbed. Small, repeated actions can protect the habitat without preventing people from learning about it.",
    ]
    q = []
    q.append(mcq(f"R{start_id}", f"What is the main purpose of <strong>{title}</strong>?", f"to explain how {subject} live and survive", [f"to tell a fantasy story about {subject}", f"to give instructions for catching {subject}", "to advertise a wildlife toy"], f"The text gives factual information about the habitat, features, food and needs of {subject}.", paper_number + start_id))
    q.append(mcq(f"R{start_id+1}", f"In <strong>{title}</strong>, what does <strong>adaptation</strong> mean?", "a feature that helps a living thing survive", ["a sudden loud warning", "a place where tickets are sold", "a change in the weather forecast"], "The passage explains that the feature helps the living thing complete tasks and avoid danger.", paper_number + start_id + 1))
    q.append(mcq(f"R{start_id+2}", f"How do features such as {feature} help {subject}?", benefit, ["make their habitat disappear", "turn their food into water", "stop every kind of danger"], f"Paragraph 2 states that these features help them {benefit}.", paper_number + start_id + 2))
    q.append(mcq(f"R{start_id+3}", f"Which change would probably cause the greatest problem for {subject}?", threat, ["a protected shelter", "more suitable food", "careful wildlife watching"], f"The final paragraph identifies {threat} as a challenge.", paper_number + start_id + 3))
    q.append(mcq(f"R{start_id+4}", f"In paragraph 2 of <strong>{title}</strong>, who does <strong>them</strong> refer to?", subject, ["the people", "the natural shelters", "the food sources"], f"The pronoun <em>them</em> refers back to {subject}.", paper_number + start_id + 4))
    q.append(mcq(f"R{start_id+5}", f"Which heading would best suit the final paragraph of <strong>{title}</strong>?", f"Helping {subject.title()}", ["A Make-Believe Adventure", "How to Build a Toy", "A List of Australian Cities"], f"The paragraph describes a threat and actions people can take to help {subject}.", paper_number + start_id + 5))
    return {"id": "P1", "title": title, "type": "information", "text": text, "questions": q}


def build_procedure_passage(paper_number, start_id=7):
    title, purpose, materials, step1, step2, step3, step4 = PROCEDURE_RECORDS[paper_number - 1]
    intro = f"Follow these steps to make {purpose}. Work carefully and ask an adult for help whenever a material needs cutting or a location must be checked for safety. Read every step before beginning so the equipment can be arranged in the correct order. Keep the workspace tidy and use each material only as described. Check each observation before recording it."
    steps = [
        step1.capitalize() + ".",
        step2.capitalize() + ".",
        step3.capitalize() + ".",
        step4.capitalize() + ".",
        "Record the result clearly, then pack away all equipment.",
    ]
    q = []
    q.append(mcq(f"R{start_id}", f"What is the purpose of <strong>{title}</strong>?", f"to make {purpose}", ["to write a fictional story", "to advertise expensive equipment", "to decorate a party invitation"], f"The introduction states that the steps are used to make {purpose}.", paper_number + start_id))
    q.append(mcq(f"R{start_id+1}", f"What should be done first in <strong>{title}</strong>?", step1, [step2, step3, "pack away all equipment"], f"The first numbered step says to {step1}.", paper_number + start_id + 1))
    q.append(mcq(f"R{start_id+2}", f"Why should the instructions for <strong>{title}</strong> be followed in order?", "so each stage is completed before the next one begins", ["so the title becomes longer", "so the materials change colour", "so no observations are recorded"], "The earlier steps prepare the activity, while the later steps produce and record the result.", paper_number + start_id + 2))
    q.append(mcq(f"R{start_id+3}", f"What does <strong>record</strong> mean in the final step of <strong>{title}</strong>?", "write down", ["hide", "erase", "guess"], "Here, <em>record</em> means to write down the observation or result.", paper_number + start_id + 3))
    q.append(mcq(f"R{start_id+4}", f"Why should the result in <strong>{title}</strong> be recorded carefully?", "to make the result easier to check and compare", ["to make the equipment heavier", "to use every material at once", "to prevent the title from changing"], "A clear record makes an observation or result easier to check and compare.", paper_number + start_id + 4))
    q.append(mcq(f"R{start_id+5}", f"Which text feature most clearly shows that <strong>{title}</strong> is a procedure?", "a materials list and numbered steps", ["characters speaking to each other", "rhyming lines", "a labelled story setting"], "Procedures commonly use a materials list and ordered steps.", paper_number + start_id + 5))
    return {"id": "P2", "title": title, "type": "procedure", "intro": intro, "materials": materials, "steps": steps, "questions": q}


def build_narrative_passage(paper_number, start_id=13):
    title, name, item, location, problem, action, ending = NARRATIVE_RECORDS[paper_number - 1]
    text = [
        f"{name} was helping near {location} when {name} noticed {item}. It looked ordinary at first, but one detail seemed new. {name} looked around for clues before touching or moving anything.",
        f"As {name} examined it more closely, {problem}. {name} hesitated. The discovery was exciting, yet it might belong to someone else or be too delicate to handle alone. A hurried choice could damage both the object and the clues around it.",
        f"Instead of rushing ahead, {name} {action}. Each new clue matched something already visible in {location}, so the search became careful rather than wild. {name} paused after every step to record what had changed.",
        f"At last, {ending}. {name} wrote a short note explaining where the object had been found and what had happened. The note included the order of the clues so another person could check the discovery.",
        f"By the end of the afternoon, the discovery had become part of the place's story. {name} was proud, not because the object was valuable, but because patience and careful thinking had protected it. The adults agreed that the object should stay with a clear label for future visitors.",
    ]
    q = []
    q.append(mcq(f"R{start_id}", f"Why did {name} hesitate in <strong>{title}</strong>?", "the object might belong to someone or be delicate", ["the location was already closed", "the object was too heavy to see", "the clues had all disappeared"], "The second paragraph says the object might belong to someone else or be too delicate to handle alone.", paper_number + start_id))
    q.append(mcq(f"R{start_id+1}", f"What does <strong>hesitated</strong> mean in <strong>{title}</strong>?", "paused because of uncertainty", ["shouted with excitement", "ran away immediately", "forgot the discovery"], "The character pauses to think about ownership and safety.", paper_number + start_id + 1))
    q.append(mcq(f"R{start_id+2}", f"What did {name} find at the beginning of <strong>{title}</strong>?", item, ["a new school bag", "a box of fresh food", "a broken sports trophy"], f"The first paragraph says that {name} noticed {item}.", paper_number + start_id + 2))
    q.append(mcq(f"R{start_id+3}", f"Why was {name}'s careful action important in <strong>{title}</strong>?", "it protected the object and used the clues safely", ["it made the object disappear", "it stopped anyone learning the result", "it changed the location into a shop"], "The character asks for help or checks evidence instead of handling the discovery carelessly.", paper_number + start_id + 3))
    q.append(mcq(f"R{start_id+4}", f"What changes by the end of <strong>{title}</strong>?", "the discovery becomes part of the place's known story", ["the location is permanently closed", "the character throws the object away", "all records of the discovery are removed"], "The final paragraph explains that the discovery becomes part of the place's story.", paper_number + start_id + 4))
    q.append(mcq(f"R{start_id+5}", f"Which idea is most important in <strong>{title}</strong>?", "Patience and careful thinking can protect a discovery.", ["Valuable objects should always be hidden.", "Every old place is unsafe to visit.", "Clues are useful only when found quickly."], "The character succeeds by slowing down, checking clues and protecting the object.", paper_number + start_id + 5))
    return {"id": "P3", "title": title, "type": "narrative", "text": text, "questions": q}


def build_table_passage(paper_number, start_id=19):
    index = paper_number - 1
    items = TABLE_ITEMS[index]
    masses = [18 + index, 24 + 8 * (index % 3), 15 + 5 * (index % 4), 32 + 4 * (index % 5)]
    baskets = [6, 8, 5, 4]
    title = f"{NAMES[index]}'s Community Collection"
    intro = f"The Year 3 team weighed four groups of donated supplies for a community project at {PLACES[index]}. The supplies were packed into containers before delivery."
    table = [["Supply", "Total mass", "Containers"]] + [[item, f"{mass} kg", str(count)] for item, mass, count in zip(items, masses, baskets)]
    greatest_index = max(range(4), key=lambda i: masses[i])
    combined = masses[0] + masses[2]
    each = masses[1] / baskets[1]
    if each.is_integer():
        each_text = f"{int(each)} kg"
    else:
        each_text = f"{each:g} kg"
    q = []
    q.append(mcq(f"R{start_id}", f"Which supply in <strong>{title}</strong> had the greatest total mass?", items[greatest_index], [items[i] for i in range(4) if i != greatest_index], f"{items[greatest_index]} had a total mass of {masses[greatest_index]} kg, the greatest value in the table.", paper_number + start_id))
    q.append(mcq(f"R{start_id+1}", f"What was the combined mass of the {items[0].lower()} and {items[2].lower()} in <strong>{title}</strong>?", f"{combined} kg", [f"{combined-6} kg", f"{combined+6} kg", f"{abs(masses[0]-masses[2])} kg"], f"{masses[0]} kg + {masses[2]} kg = {combined} kg.", paper_number + start_id + 1))
    q.append(mcq(f"R{start_id+2}", f"If the {items[1].lower()} were shared equally among {baskets[1]} containers, what mass would be in each container?", each_text, [f"{baskets[1]} kg", f"{masses[1]-baskets[1]} kg", f"{masses[1]} kg"], f"{masses[1]} kg shared among {baskets[1]} containers gives {each_text} in each container.", paper_number + start_id + 2))
    q.append(mcq(f"R{start_id+3}", f"Why could fewer containers in <strong>{title}</strong> still have a greater total mass?", "Each container could be much heavier.", ["The table counts only empty containers.", "The supplies have no mass.", "A smaller number is always greater."], "The number of containers does not show the mass inside each one.", paper_number + start_id + 3))
    q.append(mcq(f"R{start_id+4}", f"What does <strong>donated</strong> mean in the introduction to <strong>{title}</strong>?", "given to help others", ["sold at a high price", "hidden underground", "weighed a second time"], "The supplies were given for a community project.", paper_number + start_id + 4))
    q.append(mcq(f"R{start_id+5}", f"Which sentence best summarises <strong>{title}</strong>?", "Several supplies were weighed, packed and given to a community project.", ["Only one type of supply was collected.", "Every container had exactly the same mass.", "The community returned all the supplies."], "This option includes the main ideas from the introduction and table.", paper_number + start_id + 5))
    return {"id": "P4", "title": title, "type": "table", "intro": intro, "table": table, "questions": q}


def build_poem_passage(paper_number, start_id=25):
    title, sound, colour, moving, mirror, movement, place, mood = POEM_RECORDS[paper_number - 1]
    lines = [
        f"A {colour} light spreads through the air,",
        f"while {moving} drift across the sky.",
        f"The sound of {sound} rises there,",
        f"and the {mirror} reflects the sky.",
        f"Small surfaces shine beneath the light;",
        "each one wears borrowed jewels bright.",
        f"My {movement} cast shapes, dark and round,",
        "then scatter them across the ground.",
        f"The {place}, so noisy in the day,",
        "grows soft as busy sounds fade away.",
        f"I feel {mood} as I see",
        "the changing world in front of me.",
    ]
    q = []
    q.append(mcq(f"R{start_id}", f"Which line in <strong>{title}</strong> shows that something is moving?", f"while {moving} drift across the sky", [f"A {colour} light spreads through the air", f"My {movement} cast shapes, dark and round", f"I feel {mood} as I see"], f"The words <em>{moving} drift across</em> describe movement through the sky.", paper_number + start_id))
    q.append(mcq(f"R{start_id+1}", f"What are the <strong>borrowed jewels</strong> in <strong>{title}</strong>?", "drops or bright reflections on surfaces", ["small hidden insects", "pieces of broken glass", "painted yellow flowers"], "The shining drops or reflections look like jewels under the light.", paper_number + start_id + 1))
    q.append(mcq(f"R{start_id+2}", f"In <strong>{title}</strong>, why does the poet say the <strong>{mirror} reflects the sky</strong>?", f"The {mirror} shows an image of the sky.", [f"The {mirror} is above the clouds.", "The sky has fallen to the ground.", f"The {mirror} is completely dry."], "A reflective surface can show an image of the sky like a mirror.", paper_number + start_id + 2))
    q.append(mcq(f"R{start_id+3}", f"Which detail from <strong>{title}</strong> appeals most strongly to hearing?", f"The sound of {sound} rises there.", [f"The {mirror} reflects the sky.", "Borrowed jewels shine brightly.", "Small surfaces shine beneath the light."], "This line directly describes a sound in the scene.", paper_number + start_id + 3))
    q.append(mcq(f"R{start_id+4}", f"How does the speaker feel in <strong>{title}</strong>?", mood, ["angry and frightened", "bored and impatient", "sleepy and confused"], f"The poem directly says that the speaker feels {mood}.", paper_number + start_id + 4))
    q.append(mcq(f"R{start_id+5}", f"What is the main idea of <strong>{title}</strong>?", "An ordinary place can look special when light, weather or time changes.", ["Walking outdoors is always dangerous.", "Busy sounds should never become quiet.", "Reflections make every surface impossible to see."], "The poem notices how familiar surroundings become beautiful and interesting.", paper_number + start_id + 5))
    return {"id": "P5", "title": title, "type": "poem", "lines": lines, "questions": q}


def build_reading(paper_number):
    passages = [
        build_information_passage(paper_number),
        build_procedure_passage(paper_number),
        build_narrative_passage(paper_number),
        build_table_passage(paper_number),
        build_poem_passage(paper_number),
    ]
    return diversify_reading_passages(passages, paper_number)


WRITING_RECORDS = [
    ("The Door in the Tree", "Write a narrative about a character who discovers a tiny door in the trunk of an old tree.", "door_tree"),
    ("The Light Beyond the Fog", "Write a narrative about a character who follows a strange light near a lighthouse.", "lighthouse"),
    ("The Box in the Attic", "Write a narrative about a character who opens a labelled box that has been hidden for years.", "attic"),
    ("The Map in the Bottle", "Write a narrative about a character who finds a map inside a bottle washed onto the beach.", "beach"),
    ("The Bridge That Appeared", "Write a narrative about a bridge that appears across a creek for only one hour.", "bridge"),
    ("The Sound from the Cave", "Write a narrative about a character who hears a repeating sound from a safe cave entrance.", "cave"),
    ("The Clock That Ran Backwards", "Write a narrative about a clock that begins moving backwards during a school visit.", "clock"),
    ("The Gate in the Garden", "Write a narrative about a locked garden gate that opens after a character solves a clue.", "garden"),
    ("The Chest under the Sand", "Write a narrative about a small chest uncovered on a beach after a storm.", "beach"),
    ("The Empty Train Carriage", "Write a narrative about a character who finds an unexpected message in an empty train carriage.", "train"),
    ("The Book with Blank Pages", "Write a narrative about a library book whose blank pages slowly begin to show pictures.", "book"),
    ("The Telescope in the Shed", "Write a narrative about a telescope that points towards something surprising nearby.", "telescope"),
    ("The Robot with One Request", "Write a narrative about a small robot that asks a character for help with one important task.", "robot"),
    ("The Kite That Would Not Land", "Write a narrative about a kite that keeps pulling its owner towards a mystery.", "kite"),
    ("The Footprints in Moonlight", "Write a narrative about unusual footprints that can be seen only in moonlight.", "moon"),
    ("The Island after the Tide", "Write a narrative about a tiny island that appears when the tide moves out.", "island"),
    ("The Museum after Closing", "Write a narrative about one museum display that changes after the visitors leave.", "museum"),
    ("The Summer Snow Globe", "Write a narrative about a snow globe that shows a place the character recognises.", "globe"),
    ("The Tunnel behind the Painting", "Write a narrative about a painted tunnel that turns out to hide a real passage.", "tunnel"),
    ("The Last Window in the Tower", "Write a narrative about a character who sees a signal from the highest window of an old tower.", "tower"),
]


def build_writing(paper_number):
    title, prompt, illustration = WRITING_RECORDS[paper_number - 1]
    return {
        "title": title,
        "prompt": prompt,
        "illustration": illustration,
        "ideas": [
            "Who is the main character, and where does the story begin?",
            "What makes the discovery unusual or important?",
            "What problem, risk or decision must the character face?",
            "Which clues or actions move the story forward?",
            "How is the problem resolved, and what changes at the end?",
        ],
        "reminders": [
            "Plan before you begin.",
            "Use paragraphs to organise events.",
            "Choose precise verbs and interesting details.",
            "Check spelling, punctuation and sentence boundaries.",
            "Give the narrative a clear ending.",
        ],
    }


def build_numeracy(paper_number):
    p = paper_number
    q = []

    def add(number, prompt, correct, distractors, explanation, visual=None):
        prompt = diversify_numeracy_prompt(p, number, prompt)
        item = mcq(f"N{number}", prompt, correct, distractors, explanation, p + number)
        if visual is not None:
            item["visual"] = visual
        q.append(item)

    start = 120 + p * 7
    step = 8 + (p % 5)
    next_value = start + 3 * step
    add(1, f"Which number comes next?<br><strong>{start}, {start+step}, {start+2*step}, ___</strong>", next_value, [next_value-step, next_value+step, start+2*step+1], f"The pattern adds {step} each time, so the next number is {next_value}.")

    digit = 6 + (p % 3)
    number = 3000 + digit * 100 + 40 + p
    add(2, f"What is the value of the digit {digit} in <strong>{number:,}</strong>?", digit * 100, [digit, digit * 10, digit * 1000], f"The digit {digit} is in the hundreds place, so its value is {digit*100}.")

    a = 410 + p * 3
    b = 460 + p * 2
    add(3, f"Which statement about <strong>{a}</strong> and <strong>{b}</strong> is true?", f"{a} < {b}", [f"{a} > {b}", f"{a} = {b}", f"{b} < {a}"], f"{a} has fewer tens than {b}, so {a} < {b}.")

    add_a = 240 + p * 4
    add_b = 130 + p * 3
    total = add_a + add_b
    add(4, f"What is <strong>{add_a} + {add_b}</strong>?", total, [total-10, total+10, abs(add_a-add_b)], f"{add_a} + {add_b} = {total}.")

    top = 620 + p * 5
    bottom = 270 + p * 2
    difference = top - bottom
    add(5, f"What is <strong>{top} − {bottom}</strong>?", difference, [difference-10, difference+10, top+bottom], f"{top} − {bottom} = {difference}.")

    groups = 5 + p % 4
    each = 6 + p % 5
    product = groups * each
    add(6, f"There are {groups} trays with {each} muffins on each tray. How many muffins are there altogether?", product, [product-groups, product+groups, groups+each], f"{groups} groups of {each} is {groups} × {each} = {product}.")

    children = 3 + p % 4
    each_share = 6 + p % 5
    stickers = children * each_share
    add(7, f"{stickers} stickers are shared equally among {children} children. How many stickers does each child receive?", each_share, [max(1, each_share-2), each_share+2, stickers-children], f"{stickers} ÷ {children} = {each_share} stickers each.")

    odd = 41 + 2 * p
    add(8, f"Which number is odd in Paper {p}?", odd, [odd-1, odd+1, odd+3], f"{odd} cannot be divided into pairs with none left over, so it is odd.")

    factor = 4 + p % 5
    product2 = factor * 7
    add(9, f"Which number makes this equation true?<br><strong>{factor} × □ = {product2}</strong>", 7, [5, 6, 8], f"{factor} × 7 = {product2}.")

    twos = 2 + p % 4
    ones = 3 + (p * 2) % 5
    money = twos * 2 + ones
    add(10, f"{NAMES[p-1]} has {twos} two-dollar coins and {ones} one-dollar coins. How much money is there altogether?", f"${money}", [f"${money-2}", f"${money+2}", f"${money+4}"], f"{twos} × $2 = ${twos*2}, and {ones} × $1 = ${ones}. Altogether this is ${money}.")

    hour = 8 + p % 3
    minute = [10, 20, 25, 35, 40][p % 5]
    duration = [20, 25, 30, 35][p % 4]
    finish_total = hour * 60 + minute + duration
    finish_h, finish_m = divmod(finish_total, 60)
    finish = f"{finish_h}:{finish_m:02d} am"
    add(11, f"A lesson starts at {hour}:{minute:02d} am and lasts {duration} minutes. When does it finish?", finish, [f"{hour}:{(minute+10)%60:02d} am", f"{finish_h}:{(finish_m+10)%60:02d} am", f"{finish_h+1}:{finish_m:02d} am"], f"Adding {duration} minutes to {hour}:{minute:02d} am gives {finish}.")

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    start_day_index = p % 7
    offset = 8 + p % 6
    answer_day = days[(start_day_index + offset) % 7]
    distractor_days = [days[(start_day_index + offset + shift) % 7] for shift in (-1, 1, 2)]
    add(12, f"Today is {days[start_day_index]}. What day will it be in {offset} days?", answer_day, distractor_days, f"Move forward {offset} days from {days[start_day_index]} to reach {answer_day}.")

    metres = 2 + p % 7
    centimetres = metres * 100
    add(13, f"How many centimetres are equal to {metres} metres?", f"{centimetres} cm", [f"{metres*10} cm", f"{centimetres*10} cm", f"{metres} cm"], f"1 metre = 100 centimetres, so {metres} metres = {centimetres} centimetres.")

    length = 6 + p % 6
    width = 3 + p % 5
    perimeter = 2 * (length + width)
    add(14, f"A rectangle is {length} cm long and {width} cm wide. What is its perimeter?", f"{perimeter} cm", [f"{length+width} cm", f"{perimeter+4} cm", f"{abs(length-width)} cm"], f"Perimeter = {length} + {width} + {length} + {width} = {perimeter} cm.")

    rows = 2 + p % 3
    cols = 4 + p % 4
    area = rows * cols
    add(15, f"How many square units cover the rectangle shown in Paper {p}?", area, [area-cols, area+cols, rows+cols], f"The rectangle has {rows} rows of {cols} squares: {rows} × {cols} = {area} square units.", {"kind": "area_grid", "rows": rows, "cols": cols})

    litres = 1 + p % 4
    millilitres = litres * 1000
    add(16, f"Which amount is equal to {litres} litre{'s' if litres > 1 else ''}?", f"{millilitres} mL", [f"{litres*100} mL", f"{litres*10} mL", f"{millilitres*10} mL"], f"1 litre = 1000 millilitres, so {litres} litre{'s' if litres > 1 else ''} = {millilitres} mL.")

    heavy = 900 + p * 20
    light = 600 + p * 10
    mass_diff = heavy - light
    add(17, f"A bag of rice has a mass of {heavy} g. A bag of pasta has a mass of {light} g. How much heavier is the rice?", f"{mass_diff} g", [f"{heavy+light} g", f"{mass_diff+100} g", f"{light} g"], f"{heavy} g − {light} g = {mass_diff} g.")

    total_parts = 6 + (p % 4) * 2
    shaded = 2 + p % (total_parts - 3)
    add(18, f"What fraction of the bar in Paper {p} is shaded?", f"{shaded}/{total_parts}", [f"{shaded}/{total_parts+1}", f"{shaded+1}/{total_parts}", f"{max(1, shaded-1)}/{total_parts}"], f"The bar has {total_parts} equal parts and {shaded} are shaded, so the fraction is {shaded}/{total_parts}.", {"kind": "fraction_bar", "total": total_parts, "shaded": shaded})

    even_number = 40 + p * 2
    half = even_number // 2
    add(19, f"What is half of {even_number}?", half, [half-3, half+3, even_number-2], f"{even_number} divided into 2 equal groups gives {half} in each group.")

    shape = "square" if p % 2 else "rectangle"
    symmetries = 4 if shape == "square" else 2
    add(20, f"How many lines of symmetry does the {shape} shown in Paper {p} have?", symmetries, [0, 1, 3 if symmetries == 4 else 4], f"A {shape} has {symmetries} lines of symmetry.", {"kind": "symmetry_shape", "shape": shape})

    angle = [35, 45, 60, 70][p % 4]
    add(21, f"Which description matches an angle of {angle} degrees?", "an acute angle", ["a right angle", "an obtuse angle", "a straight angle"], f"{angle} degrees is less than 90 degrees, so it is an acute angle.")

    solid = ["cube", "rectangular prism"][p % 2]
    add(22, f"How many faces does the {solid} shown in Paper {p} have?", 6, [4, 8, 12], f"A {solid} has 6 flat faces.", {"kind": "cube"})

    map_labels = ["pond", "bench", "gate", "tree"]
    target = map_labels[p % 4]
    positions = {"pond": "C1", "bench": "C2", "gate": "B2", "tree": "D3" if p % 2 else "A1"}
    add(23, f"On the Paper {p} map, which location is in square {positions[target]}?", target, [item for item in map_labels if item != target], f"The map shows {target} in column {positions[target][0]}, row {positions[target][1]}.", {"kind": "map_grid", "target": target, "tree_corner": "D3" if p % 2 else "A1"})

    values = [10 + p, 15 + p * 2, 12 + p, 8 + p]
    labels = ["Monday", "Tuesday", "Wednesday", "Thursday"]
    max_index = max(range(4), key=lambda i: values[i])
    add(24, f"A class recorded books read in Paper {p}: Monday {values[0]}, Tuesday {values[1]}, Wednesday {values[2]}, Thursday {values[3]}. On which day were the most books read?", labels[max_index], [label for i, label in enumerate(labels) if i != max_index], f"{labels[max_index]} has the greatest value, {values[max_index]}.")

    bars = [8 + p, 11 + p, 6 + p, 10 + p]
    difference_bars = bars[1] - bars[0]
    add(25, f"The Paper {p} graph shows points scored by four teams. How many more points did team B score than team W?", difference_bars, [difference_bars+2, bars[1], bars[0]], f"Team B scored {bars[1]} points and team W scored {bars[0]} points. {bars[1]} − {bars[0]} = {difference_bars}.", {"kind": "bar_chart", "bars": [["W", bars[0]], ["B", bars[1]], ["J", bars[2]], ["K", bars[3]]]})

    spinner_counts = [1, 2 + p % 3, 1, 1]
    colours = ["red", "blue", "green", "yellow"]
    likely_index = max(range(4), key=lambda i: spinner_counts[i])
    total_spinner = sum(spinner_counts)
    add(26, f"A Paper {p} spinner has {spinner_counts[0]} red, {spinner_counts[1]} blue, {spinner_counts[2]} green and {spinner_counts[3]} yellow equal sections. Which colour is most likely?", colours[likely_index], [colour for i, colour in enumerate(colours) if i != likely_index], f"{colours[likely_index].title()} covers {spinner_counts[likely_index]} of the {total_spinner} equal sections, more than any other colour.", {"kind": "spinner", "counts": dict(zip(colours, spinner_counts))})

    pattern_step = 3 + p % 5
    pattern_start = 2 + p
    pattern_next = pattern_start + 4 * pattern_step
    add(27, f"Which number comes next in Paper {p}?<br><strong>{pattern_start}, {pattern_start+pattern_step}, {pattern_start+2*pattern_step}, {pattern_start+3*pattern_step}, ___</strong>", pattern_next, [pattern_next-pattern_step, pattern_next+pattern_step, pattern_next+1], f"The pattern adds {pattern_step} each time, so the next number is {pattern_next}.")

    left = 18 + p
    target_sum = 45 + p * 2
    missing = target_sum - left
    add(28, f"Which number makes this equation true in Paper {p}?<br><strong>{left} + □ = {target_sum}</strong>", missing, [missing-5, left, target_sum+left], f"{target_sum} − {left} = {missing}, so {left} + {missing} = {target_sum}.")

    rows_bus = 4 + p % 4
    seats_each = 4 + (p + 1) % 3
    empty = 2 + p % 4
    occupied = rows_bus * seats_each - empty
    add(29, f"A small bus has {rows_bus} rows with {seats_each} seats in each row. {empty} seats are empty. How many seats are occupied?", occupied, [rows_bus*seats_each, occupied-empty, rows_bus+seats_each+empty], f"There are {rows_bus} × {seats_each} = {rows_bus*seats_each} seats. {rows_bus*seats_each} − {empty} = {occupied} occupied seats.")

    seedlings = 42 + p * 3
    planted_rows = 4 + p % 4
    per_row = 5 + p % 3
    planted = planted_rows * per_row
    left_seedlings = seedlings - planted
    add(30, f"A gardener has {seedlings} seedlings. She plants {planted_rows} rows of {per_row} seedlings. How many seedlings are left?", left_seedlings, [seedlings-planted_rows, planted+1, left_seedlings+per_row], f"{planted_rows} × {per_row} = {planted} seedlings are planted. {seedlings} − {planted} = {left_seedlings} seedlings remain.")
    return q


def build_paper(paper_number):
    if not 1 <= paper_number <= 20:
        raise ValueError("paper_number must be between 1 and 20")
    return {
        "paper_number": paper_number,
        "title": f"Year 3 NAPLAN-Style Practice Paper {paper_number:02d}",
        "language": build_language(paper_number),
        "reading_passages": build_reading(paper_number),
        "writing": build_writing(paper_number),
        "numeracy": build_numeracy(paper_number),
    }


def build_all_papers():
    return [build_paper(number) for number in range(1, 21)]


if __name__ == "__main__":
    papers = build_all_papers()
    print(f"Built {len(papers)} papers with {sum(len(p['language']) + 30 + len(p['numeracy']) for p in papers)} scored questions.")
