from __future__ import annotations

import json
from pathlib import Path


LETTERS = "ABCDEF"
SPELLING_BANK_PATH = Path(__file__).with_name("spelling-bank.json")

NAMES = [
    "Ava", "Noah", "Mia", "Leo", "Ruby", "Eli", "Zoe", "Kai", "Nina", "Arlo",
    "Ivy", "Owen", "Lila", "Finn", "Maya", "Hugo", "Sara", "Jude", "Tara", "Max",
]
PARTNERS = [
    "Ben", "Chloe", "Dylan", "Emma", "Grace", "Henry", "Isla", "Jack", "Layla", "Mason",
    "Nora", "Oscar", "Piper", "Quinn", "Riley", "Sofia", "Theo", "Uma", "Violet", "Will",
]
ANIMALS = [
    "otter", "wombat", "penguin", "dolphin", "koala", "wallaby", "platypus", "possum", "echidna", "quokka",
    "turtle", "pelican", "cockatoo", "lizard", "bilby", "seal", "frog", "owl", "bandicoot", "kangaroo",
]
OBJECTS = [
    "orange", "umbrella", "apple", "apron", "egg", "insect model", "octopus toy", "engine", "ice cube", "alarm clock",
    "atlas", "envelope", "igloo model", "orchid", "acorn", "elephant card", "ink bottle", "oven mitt", "arrow", "opal",
]
PLACES = [
    "library", "garden", "museum", "jetty", "hall", "creek", "market", "workshop", "farm", "beach",
    "gallery", "reserve", "campsite", "theatre", "orchard", "station", "aquarium", "bakery", "lookout", "nursery",
]
TOYS = [
    "wooden train", "rag doll", "tin robot", "toy dinosaur", "music-box horse", "teddy bear", "model aeroplane", "puppet",
    "wind-up mouse", "toy dragon", "building-block figure", "toy boat", "plush koala", "toy astronaut", "marionette",
    "clockwork duck", "toy fire engine", "paper clown", "toy knight", "stuffed penguin",
]


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
    base, past = past_pairs[p - 1]
    adverbs = [
        "quietly", "carefully", "briskly", "patiently", "softly", "neatly", "slowly", "cheerfully", "gently", "quickly",
        "calmly", "politely", "eagerly", "firmly", "brightly", "smoothly", "safely", "silently", "proudly", "steadily",
    ]
    adverb = adverbs[p - 1]
    q = []
    q.append(mcq("L1", f"{name} packed ___ {obj} for the visit.", "an", ["a", "the", "some"], f"{obj.title()} begins with a vowel sound, so the correct article is <em>an</em>.", p))
    q.append(question("L2", "circle", f"Circle the verb in this sentence.<br><strong>The {animal} climbed over the log.</strong>", "climbed", "<em>Climbed</em> tells what the animal did.", sentence=f"The {animal} climbed over the log."))
    q.append(mcq("L3", f"Yesterday, {name} ___ the rope before lunch.", past, [base, f"{base}s", f"will {base}"], f"The word <em>yesterday</em> requires the past-tense form <em>{past}</em>.", p + 3))
    q.append(question("L4", "circle", f"Circle the adverb in this sentence.<br><strong>{partner} carried the glass jar {adverb}.</strong>", adverb, f"<em>{adverb.title()}</em> tells how {partner} carried the jar.", sentence=f"{partner} carried the glass jar {adverb}."))
    q.append(mcq("L5", f"{name} placed ___ hat beside the bag.", "my", ["me", "I", "mine"], "<em>My</em> is the possessive determiner used before the noun <em>hat</em>.", p + 5))
    q.append(mcq("L6", f"Wash your hands ___ you prepare the fruit.", "before", ["because", "although", "unless"], "<em>Before</em> shows the correct sequence in time.", p + 6))
    q.append(question("L7", "cloze", f"Complete the sentence using each word once.<br>{name} saw ___ ant beside ___ leaf. ___ ant carried a crumb.", ["an", "a", "The"], "Use <em>an</em> before <em>ant</em>, <em>a</em> before <em>leaf</em>, then <em>The</em> for the ant already mentioned.", word_bank=["a", "an", "the"], gaps=3))
    q.append(mcq("L8", f"___ will carry the boxes to the {place}.", f"{partner} and I", [f"Me and {partner}", f"Her and {partner}", f"{partner} and me"], "A compound subject uses the subject pronoun <em>I</em>.", p + 8))
    q.append(mcq("L9", f"Choose a pear, a plum ___ a peach.", "or", ["but", "because", "although"], "<em>Or</em> joins alternatives in a list.", p + 9))
    q.append(mcq("L10", f"The pencils, rulers and erasers were new. ___ were placed in a tray.", "They", ["It", "She", "Them"], "The plural pronoun <em>They</em> replaces the three plural nouns and is the subject of the sentence.", p + 10))
    q.append(mcq("L11", "Which sentence is correct?", "They are waiting near the gate.", ["They is waiting near the gate.", "Them are waiting near the gate.", "They am waiting near the gate."], "The plural subject <em>They</em> agrees with <em>are</em>.", p + 11))
    q.append(mcq("L12", f"By the time {name} arrived, {partner} ___ the hole.", "had dug", ["digs", "will dig", "is digging"], "<em>Had dug</em> shows an action completed before another past action.", p + 12))
    q.append(mcq("L13", f"{name} and I are ready. ___ can begin now.", "We", ["Us", "They", "Them"], "<em>We</em> is the first-person plural subject pronoun.", p + 13))
    q.append(mcq("L14", f"Where did the {animal} hide___", "?", [".", "!", ","], "A direct question ends with a question mark.", p + 14))
    q.append(mcq("L15", "Which contraction correctly means <em>we will</em>?", "we’ll", ["well", "we’l", "w’ell"], "The apostrophe in <em>we’ll</em> replaces the missing letters in <em>will</em>.", p + 15))
    q.append(mcq("L16", "Where should the missing full stop go?<br><strong>We reached the gate A the path B turned left C beside the pond D</strong>", "A", ["B", "C", "D"], "The first sentence ends after <em>gate</em>; the next sentence begins with <em>The</em>.", 0))
    q.append(mcq("L17", "Which sentence is punctuated correctly?", f'“Wait for me,” called {name}.', [f'“Wait for me” called {name}.', f'Wait for me,” called {name}.', f'“Wait for me, called {name}.”'], "The spoken words need opening and closing quotation marks, with a comma before the reporting clause.", p + 17))
    q.append(mcq("L18", f"This notebook is mine. Is that one ___?", "yours", ["your", "you", "you’re"], "<em>Yours</em> is the possessive pronoun that can stand without a noun after it.", p + 18))
    q.append(mcq("L19", f"Which sentence has the comma in the correct place?", f"After the bell rang, {name} entered the room.", [f"After, the bell rang {name} entered the room.", f"After the bell, rang {name} entered the room.", f"After the bell rang {name}, entered the room."], "A comma separates the introductory clause from the main clause.", p + 19))
    q.append(mcq("L20", "Where should the apostrophe go?<br><strong>We can A t leave B yet C today D.</strong>", "A", ["B", "C", "D"], "The contraction <em>can’t</em> needs an apostrophe between <em>n</em> and <em>t</em>.", 0))
    q.append(mcq("L21", "Which sentence is a direct question?", f"Did {name} close the window?", [f"I wonder whether {name} closed the window.", f"Tell me if {name} closed the window.", f"We know that {name} closed the window."], "A direct question asks the reader for an answer and ends with a question mark.", p + 21))
    q.append(mcq("L22", "Which sentence uses capital letters correctly?", f"Dr Patel spoke to the doctor.", ["dr Patel spoke to the Doctor.", "Dr patel spoke to the doctor.", "Dr Patel spoke to the Doctor."], "The title and surname take capitals; the common profession noun <em>doctor</em> does not.", p + 22))
    q.append(mcq("L23", "Which sentence needs quotation marks?", f"Please close the gate, said {partner}.", [f"{partner} closed the gate quietly.", f"The gate beside the shed was closed.", f"Closing the gate kept the {animal} safe."], "The first sentence contains the exact words spoken by a character.", p + 23))
    q.append(mcq("L24", "Which sentence is punctuated correctly?", f"The girl’s boots were beside the boys’ bags.", [f"The girls boots were beside the boy’s bags.", f"The girls’ boots were beside the boys bag’s.", f"The girl’s boot’s were beside the boys bags."], "<em>Girl’s</em> shows one girl owns the boots; <em>boys’</em> shows several boys own the bags.", p + 24))
    q.append(mcq("L25", f"Where should the missing closing quotation mark go?<br><strong>“I found the key A, said {name} B, as the door C opened D.</strong>", "A", ["B", "C", "D"], "The closing quotation mark belongs after the final spoken word <em>key</em> and before the reporting clause.", 0))

    bank = [entry["word"] for entry in json.loads(SPELLING_BANK_PATH.read_text(encoding="utf-8"))["entries"]]
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
    context = f"<em>{place.title()} task:</em> "
    for item in q:
        if item["kind"] != "dictation":
            item["prompt"] = context + item["prompt"]
    return q


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
]


def build_reading(paper_number):
    p = paper_number
    name = NAMES[p - 1]
    partner = PARTNERS[p - 1]
    item, smooth, rough = FORCE_CONTEXTS[p - 1]
    passages = []

    info_title = f"Why a {item} slows down"
    info_text = (
        f"A force is a push or a pull. When a moving {item} touches a surface, friction acts in the opposite direction to its movement. "
        f"Friction makes the {item} slow down. A smooth surface such as {smooth} usually creates less friction than {rough}. "
        "With very little friction, an object travels farther before stopping. The amount of friction also depends on how firmly two surfaces press together. "
        "Friction is useful too: it helps shoes grip the ground and bicycle brakes stop wheels. Without enough friction, people could slip and tyres could slide. "
        "Too much friction can be unhelpful because moving parts may heat up or wear away, so machines sometimes use oil to reduce it."
    )
    info_q = [
        mcq("R1", f"What makes the moving {item} slow down?", "friction acting against its movement", ["gravity pulling it sideways", "light warming the surface", "sound pushing it forward"], "The text says friction acts opposite to movement and slows the object.", p),
        mcq("R2", f"What would most likely happen if there were very little friction?", f"The {item} would travel farther before stopping.", [f"The {item} would become heavier.", f"The {item} would change colour.", f"The {item} would stop at once."], "The text directly links little friction with travelling farther.", p + 1),
        question("R3", "true_false", "Mark each statement True or False.", [True, False, True], "Friction can help brakes; rough surfaces do not usually create less friction; friction acts against movement.", statements=["Friction can help bicycle brakes work.", f"{rough.title()} usually creates less friction than {smooth}.", "Friction acts against a moving object."]),
        mcq("R4", "Which surface would probably let the object travel farthest?", smooth, [rough, "a thick towel", "a rubber mat"], f"The text identifies {smooth} as the smoother, lower-friction surface.", p + 3),
        mcq("R5", "Which diagram shows the applied force and friction acting in opposite directions?", "push →    ← friction", ["push →    friction →", "push ←    friction ←", "push ↓    friction ↓"], "Friction acts opposite to the applied movement force.", p + 4, visual={"kind": "force_arrows"}),
        mcq("R6", "Which pair of statements is correct?<br>1 The text explains how friction changes movement.<br>2 The text gives examples of useful friction.<br>3 The text tells a fictional adventure.", "1 and 2", ["1 and 3", "2 and 3", "3 only"], "The text explains movement and gives useful examples; it is not fiction.", p + 5),
    ]
    passages.append({"id": "P1", "title": info_title, "type": "information", "text": info_text, "questions": info_q})

    trials = 3 + p % 3
    procedure_title = f"Testing surfaces with a {item}"
    procedure_intro = f"This experiment compares how far the same {item} travels across {smooth}, paper and {rough}. Use the same ramp each time."
    steps = [
        "Place the ramp at the marked height.",
        f"Put {smooth} at the bottom of the ramp.",
        f"Release the {item} without pushing it.",
        "Measure and record the distance travelled.",
        f"Repeat the trial {trials} times for each surface, then compare the results.",
    ]
    procedure_q = [
        question("R7", "order", "Number these steps from 1 to 4.", [2, 4, 1, 3], "First set the ramp, then place the surface, release the object and measure the distance.", choices=[steps[1], steps[3], steps[0], steps[2]]),
        mcq("R8", "How many times is each surface tested?", str(trials), [str(trials - 1), str(trials + 1), str(trials * 3)], f"The final step says to repeat the trial {trials} times for each surface.", p + 8),
        mcq("R9", "What type of text is this?", "a procedure", ["a narrative", "a book review", "a poem"], "A purpose, equipment and ordered steps are features of a procedure.", p + 9),
        mcq("R10", "Why are several surfaces tested?", "to compare how each surface affects the distance", ["to make the ramp taller each time", "to change the size of the object", "to avoid measuring any result"], "Changing the surface and measuring the distance allows a fair comparison.", p + 10),
        mcq("R11", f"Which material would be the best replacement for {rough}?", "a woollen mat", ["a glass sheet", "smooth foil", "polished plastic"], "A woollen mat is rough like the material it replaces.", p + 11),
        mcq("R12", f"Using both texts, where should the {item} travel the shortest distance?", rough, [smooth, "in the air", "on no surface"], f"The information text says rough surfaces create more friction, so {rough} should stop the object sooner.", p + 12, cross_text=True),
    ]
    passages.append({"id": "P2", "title": procedure_title, "type": "procedure", "intro": procedure_intro, "steps": steps, "questions": procedure_q})

    aerobic = ["jogging", "swimming", "cycling", "fast walking", "skipping"][p % 5]
    strength = ["climbing", "lifting light weights", "push-ups", "carrying groceries", "rowing"][p % 5]
    flexibility = ["stretching", "yoga", "gentle bends", "dance stretches", "reaching exercises"][p % 5]
    health_title = f"{name}'s guide to three kinds of fitness"
    health_text = (
        f"During a health lesson at the {PLACES[p - 1]}, {name}'s class learned that a sedentary person spends long periods sitting and moving very little. Regular activity helps the heart, muscles and joints. "
        f"Aerobic activities such as {aerobic} make the heart beat faster. Strength activities such as {strength} make muscles work against resistance. "
        f"Flexibility activities such as {flexibility} help joints move through a comfortable range. Each type has a different purpose, so doing only one type leaves out other benefits. "
        "Children can build activity into ordinary days by walking, playing active games and helping with safe physical jobs. Activity should suit the person's ability and surroundings. "
        "A balanced week includes all three kinds, water, sleep and time to rest."
    )
    health_q = [
        mcq("R13", "What does <strong>sedentary</strong> mean in this text?", "spending much time sitting and moving very little", ["training for a race every day", "moving safely in deep water", "stretching every muscle"], "The first sentence defines the word directly.", p + 13),
        question("R14", "match", "Match each fitness type to its description.", ["makes the heart beat faster", "makes muscles work against resistance", "helps joints move comfortably"], "The text gives a separate function for aerobic, strength and flexibility activities.", left=["aerobic", "strength", "flexibility"], right=["helps joints move comfortably", "makes the heart beat faster", "makes muscles work against resistance"]),
        mcq("R15", "Which activity is aerobic?", aerobic, [strength, flexibility, "sitting quietly"], f"The text names {aerobic} as an aerobic activity.", p + 15),
        question("R16", "cloze", "Complete the sentence using two words from the box.<br>A balanced week includes ___ activity and time to ___.", ["regular", "rest"], "The text recommends regular activity as well as rest.", word_bank=["regular", "rest", "sedentary", "resistance", "range"], gaps=2),
        mcq("R17", "Which statement is most likely true of a fit person?", "They can use heart, muscles and joints in different activities.", ["They never need to rest.", "They do only one kind of activity.", "They sit still for most of every day."], "The text recommends a balance of activities that support different parts of the body.", p + 17),
        mcq("R18", "What is the main message of the text?", "Different kinds of activity help the body in different ways.", ["Only competitive sport improves fitness.", "Rest should replace all exercise.", "Muscles are the only part of fitness."], "The text explains three fitness types and the benefit of balancing them.", p + 18),
    ]
    passages.append({"id": "P3", "title": health_title, "type": "information", "text": health_text, "questions": health_q})

    sports = ["soccer", "netball", "swimming", "tennis"]
    counts = [5 + p % 4, 8 + p % 5, 4 + (p * 2) % 5, 6 + (p * 3) % 5]
    survey_title = f"Favourite class sports — {name}'s class"
    survey_text = f"In {name}'s class, each student chose one favourite sport. The tally table and bar graph show the same {sum(counts)} answers collected by {partner}."
    survey_q = [
        question("R19", "match", "Match each sport to its number of votes.", [str(value) for value in counts], "Each value is read from the tally table.", left=sports, right=[str(value) for value in counts[2:] + counts[:2]], visual={"kind": "tally", "labels": sports, "values": counts}),
        mcq("R20", "Why was a tally table used?", "to record each response as it was collected", ["to explain the rules of each sport", "to show where games are played", "to rank players by skill"], "Tallies are a quick way to record responses during a survey.", p + 20),
        mcq("R21", "What do the two axes of the bar graph show?", "sports and numbers of votes", ["days and temperatures", "players and scores", "distances and times"], "The categories are sports and the scale counts votes.", p + 21),
        mcq("R22", "Why is the bar graph useful?", "It makes the vote totals easy to compare.", ["It gives instructions for playing.", "It changes the survey answers.", "It shows every student's name."], "Bar lengths allow the category totals to be compared quickly.", p + 22),
        mcq("R23", "Which question was most likely asked in the survey?", "Which sport is your favourite?", ["How old is your coach?", "What time does school begin?", "How far is your home from school?"], "The table records one favourite sport from each student.", p + 23),
        mcq("R24", "Using both fitness and survey texts, which pair are team sports?", "soccer and netball", ["swimming and tennis", "soccer and swimming", "netball and tennis"], "Soccer and netball are normally played by teams; the other listed activities can be individual.", p + 24, cross_text=True, visual={"kind": "bar_chart", "labels": sports, "values": counts}),
    ]
    passages.append({"id": "P4", "title": survey_title, "type": "data", "text": survey_text, "data": {"labels": sports, "values": counts}, "questions": survey_q})

    day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][p % 7]
    trait = ["bright", "kind", "quick", "calm", "bold", "wise", "merry"][p % 7]
    rhyme_title = f"{name} reads: The child of {day}"
    rhyme_lines = [
        f"{day}'s child wakes with the sun,",
        f"Ready for work and ready for fun;",
        f"With a {trait} little smile and a helpful way,",
        f"The child brings cheer to the end of the day.",
        "When a task is tangled, the child will try,",
        "And ask a good question instead of asking why;",
        f"Then {name} hears evening settle, gentle and mild,",
        f"Around the dreams of {day}'s child.",
    ]
    rhyme_q = [
        mcq("R25", "What does <strong>ready for work and ready for fun</strong> suggest?", "The child is willing to take part in different activities.", ["The child refuses to help.", "The child sleeps through the day.", "The child is afraid of games."], "The line shows willingness to join both duties and enjoyable activities.", p + 25),
        question("R26", "cloze", "Complete the sentence using two words from the box.<br>The child is ___ and brings ___ to others.", [trait, "cheer"], "The poem directly describes the child's smile and the cheer brought to others.", word_bank=[trait, "cheer", "sleep", "anger", "silence"], gaps=2),
        mcq("R27", f"In the title, <strong>{day}</strong> refers to", "a day of the week", ["a month of the year", "a place in a town", "a kind of weather"], f"{day} is one of the seven days of the week.", p + 27),
        mcq("R28", "What type of text is this?", "a poem", ["a procedure", "a news report", "an advertisement"], "The text is arranged in lines and uses rhyme and rhythm.", p + 28),
        mcq("R29", "Why was this poem most likely written?", "to describe a child's character in an enjoyable rhyme", ["to teach how to repair a toy", "to report a sporting result", "to list rules for a classroom"], "The poem gives a playful description rather than instructions or factual reporting.", p + 29),
    ]
    passages.append({"id": "P5", "title": rhyme_title, "type": "poem", "lines": rhyme_lines, "questions": rhyme_q})

    book_title = [
        "Odd Animals", "Amazing Machines", "Secrets of the Sea", "Wild Weather", "Hidden Habitats", "Brilliant Bridges", "Night Creatures", "Curious Caves", "Tiny Inventors", "Great Garden Mysteries",
        "Remarkable Reptiles", "Inside Volcanoes", "Clever Camouflage", "Unusual Journeys", "Wonderful Wetlands", "Beneath the City", "Fantastic Fossils", "Busy Bee Worlds", "Surprising Space", "Strange but True",
    ][p - 1]
    author = [
        "Tessa Green", "Mark Liu", "Priya Shah", "Daniel Frost", "Amelia Ward", "Jon Bell", "Sofia King", "Ravi Stone", "Lucy Chen", "Omar Reed",
        "Ella James", "Ben Ortiz", "Mina Park", "Theo Brown", "Nora White", "Samir Khan", "Grace Young", "Leo Martin", "Ruby Clark", "Hana Scott",
    ][p - 1]
    included = ["surprising facts", "labelled pictures", "short explanations"]
    absent = ["a recipe", "a fictional diary"]
    stars = 3 + p % 3
    review_text = (
        f"<strong>{book_title}</strong> by {author}<br>"
        f"This information book contains {included[0]}, {included[1]} and {included[2]}. Its chapters move from simple examples to less familiar ones. "
        "The opening chapter gives readers enough background to understand the later examples. The captions make the pictures easy to understand, and small fact boxes add details without interrupting the main explanation. "
        "The index is useful for finding a topic again. Some pages use words that younger readers may need to look up, and the final chapter feels too short. Even so, curious readers will probably return to the pictures and facts more than once. "
        f"Rating: {'★' * stars}{'☆' * (5 - stars)}"
    )
    review_q = [
        mcq("R30", "Who wrote the book being reviewed?", author, [NAMES[p - 1] + " Lee", PARTNERS[p - 1] + " Jones", "The reviewer"], "The author's name appears directly below the title.", p + 30),
        mcq("R31", "What is the main purpose of the review?", "to give information and an opinion about the book", ["to retell every chapter", "to sell equipment", "to teach a science experiment"], "A review summarises features and gives judgements about quality.", p + 31),
        question("R32", "select_two", "Which two topics are <strong>not</strong> included in the book?", absent, "The review lists facts, pictures and explanations, but it does not mention a recipe or a fictional diary.", options=[included[0], absent[0], included[1], "chapter headings", absent[1], included[2]]),
        mcq("R33", "What criticism does the reviewer make?", "Some words are difficult and the final chapter is too short.", ["The book has no pictures.", "Every chapter repeats the same page.", "The title is missing."], "These two limitations are stated in the review.", p + 33),
        mcq("R34", "What does the star rating show?", f"The reviewer gives the book {stars} out of 5.", ["The book has five authors.", "The book contains five chapters.", "The reviewer read it five times."], "A star rating records the reviewer's overall judgement out of five.", p + 34),
    ]
    passages.append({"id": "P6", "title": f"Review: {book_title}", "type": "review", "text": review_text, "questions": review_q})

    lost_item = ["silver whistle", "painted badge", "small compass", "red notebook", "brass key"][p % 5]
    narrative_title = ["The awkward discovery", "The muddy clue", "The unexpected parcel", "The stubborn knot", "The missing label"][p % 5]
    narrative_text = (
        f"{name} carried a heavy box into the {PLACES[p - 1]}. A loose corner caught on the doorway, and three dusty folders slid onto the floor. "
        f"While stacking them, {name} noticed a {lost_item} beneath the lowest folder. It was labelled with {partner}'s name. "
        f"{name} remembered seeing {partner} earlier, but could not remember which group had left first. Calling across the crowded room would only interrupt everyone. "
        f"{name} wanted to return it at once, but the crowded room made the search difficult. Instead of guessing, {name} placed the object safely on the desk and asked the supervisor to check the visitor list. "
        f"The supervisor found a contact note and sent a short message. Soon {partner} returned, relieved to see the missing object. The unpleasant job of moving the box had led to a welcome surprise."
    )
    narrative_q = [
        question("R35", "match", "Match each describing word to the noun it describes.", ["box", "folders", "room"], "The narrative says <em>heavy box</em>, <em>dusty folders</em> and <em>crowded room</em>.", left=["heavy", "dusty", "crowded"], right=["room", "box", "folders"]),
        question("R36", "order", "Number these events from 1 to 4.", [3, 1, 4, 2], "The box catches first, the object is found, the list is checked, and the owner returns.", choices=["The supervisor checked the visitor list.", "The box caught on the doorway.", f"{partner} returned for the object.", f"{name} found the {lost_item}."]),
        mcq("R37", f"Which word best describes {name}?", "responsible", ["careless", "selfish", "impatient"], f"{name} protects the object and checks who owns it instead of guessing.", p + 37),
        mcq("R38", f"Why was it difficult for {name} to return the object immediately?", "The room was crowded and the owner was not easy to find.", ["The object was too large to lift.", "The supervisor refused to help.", "The visitor list had been destroyed."], "The narrative explains that the crowded room made the search difficult.", p + 38),
        mcq("R39", f"Why is <strong>{narrative_title}</strong> a suitable title?", "An inconvenient task leads to an unexpected discovery.", ["The story explains how to build a box.", "The characters compete in a race.", "The story is mainly about bad weather."], "The title links the awkward task with the discovered object and happy outcome.", p + 39),
    ]
    passages.append({"id": "P7", "title": f"{name}'s story: {narrative_title}", "type": "narrative", "text": narrative_text, "questions": narrative_q})
    for passage in passages:
        context = f"<em>{passage['title']}:</em> "
        for item in passage["questions"]:
            item["prompt"] = context + item["prompt"]
    return passages


def build_writing(paper_number):
    toy = TOYS[paper_number - 1]
    place = PLACES[paper_number - 1]
    return {
        "title": "The toy that came to life",
        "prompt": f"Write a narrative about a {toy} that suddenly comes to life in a {place}.",
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
    digits = list(digit_sets[p - 1])
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
    rooms = ["library", "office", "art room", "hall", "garden"]
    target_room = rooms[p % 5]
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
    context = f"<em>{NAMES[p - 1]}'s {PLACES[p - 1]} task:</em> "
    for item in q:
        item["prompt"] = context + item["prompt"]
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
    total = sum(len(paper["language"]) + sum(len(passage["questions"]) for passage in paper["reading_passages"]) + len(paper["numeracy"]) for paper in papers)
    print(f"Built {len(papers)} papers with {total} scored questions.")
