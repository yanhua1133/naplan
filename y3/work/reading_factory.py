from __future__ import annotations


LETTERS = "ABCDEF"


def question(question_id, kind, prompt, answer, explanation, *, skill, **extra):
    item = {
        "id": question_id,
        "kind": kind,
        "prompt": prompt,
        "answer": answer,
        "explanation": explanation,
        "skill": skill,
    }
    item.update(extra)
    return item


def mcq(question_id, prompt, correct, distractors, explanation, *, skill, shift=0, **extra):
    options = [str(correct), *[str(value) for value in distractors]]
    shift %= len(options)
    options = options[shift:] + options[:shift]
    return question(
        question_id,
        "mcq",
        prompt,
        str(correct),
        explanation,
        skill=skill,
        options=options,
        answer_index=options.index(str(correct)),
        **extra,
    )


def _select_questions(family, questions, count, seed):
    shift = seed % len(questions)
    selected = (questions[shift:] + questions[:shift])[:count]
    for index, item in enumerate(selected, start=1):
        item["template_id"] = f"{family}-Q{(shift + index - 1) % len(questions) + 1}"
        item["family"] = f"reading-{family}-{item['skill']}"
    return selected


def _passage(family, genre, title, questions, count, seed, **content):
    return {
        "family": family,
        "genre": genre,
        "title": title,
        "type": content.pop("type", genre),
        "questions": _select_questions(family, questions, count, seed),
        **content,
    }


def animal_information(context, count, seed):
    profile = context["animal_profiles"][seed % len(context["animal_profiles"])]
    animal = profile["animal"]
    food = profile["food"]
    shelter = profile["shelter"]
    title = f"A close look at the {animal}"
    text = (
        f"During a lesson at the {context['place']}, {context['name']} read about this animal. The {animal} lives {profile['habitat']}, where it can find {food}. It shelters in {shelter}. "
        f"It is most active in the {profile['active_time']}. {profile['adaptation']} "
        f"When danger is close, the {animal} {profile['defence']}. Young animals learn where to feed by following an adult. "
        "Protecting feeding places and leaving wild animals undisturbed gives them the best chance to survive."
    )
    questions = [
        mcq("A1", f"Where does the {animal} find shelter?", f"in {shelter}", ["inside a classroom", "under a road", "beside a fireplace"], "The opening details name the shelter.", skill="literal", shift=seed),
        mcq("A2", f"When is the {animal} most active?", profile["active_time"], ["only at noon", "during every lesson", "only in winter"], "The second sentence gives its active time.", skill="literal", shift=seed + 1),
        mcq("A3", f"Which feature helps the {animal} survive?", profile["feature_answer"], profile["feature_distractors"], "The text directly describes this useful feature.", skill="cause_effect", shift=seed + 2),
        mcq("A4", "What does <strong>undisturbed</strong> mean here?", "not bothered", ["not counted", "not coloured", "not hungry"], "The final sentence asks people to leave wild animals alone.", skill="vocabulary", shift=seed + 3),
        mcq("A5", "What is the main purpose of this text?", f"to give facts about the {animal}", ["to advertise an animal toy", "to tell a joke", "to explain game rules"], "The text presents factual information.", skill="purpose", shift=seed),
        question("A6", "true_false", "Decide whether each statement is true or false.", [True, False, True], "Each answer can be checked against the passage.", skill="evidence", statements=[f"The {animal} eats {food}.", "Young animals always feed alone.", "Protecting feeding places helps survival."]),
    ]
    return _passage("animal-information", "information", title, questions, count, seed, text=text)


def public_notice(context, count, seed):
    place = context["place"].title()
    day = context["days"][seed % 5]
    open_time = 9 + seed % 2
    close_time = 3 + seed % 3
    other_days = [value for value in context["days"] if value != day][:3]
    title = f"{place} open day"
    text = (
        f"<p><strong>{day}, {open_time}:00 am–{close_time}:00 pm</strong></p>"
        "<ul><li>Enter through the front gate.</li><li>Children must stay with an adult.</li>"
        "<li>Bring a water bottle and a hat.</li><li>The quiet tour begins at 11:30 am.</li>"
        "<li>No pets or bicycles inside the gate.</li></ul>"
        "<p>If heavy rain closes the event, a notice will be placed outside the school office.</p>"
    )
    questions = [
        mcq("N1", "On which day is the open day?", day, other_days, "The day is printed at the top of the notice.", skill="text_feature", shift=seed),
        mcq("N2", "Who must children stay with?", "an adult", ["a pet", "a bicycle", "a tour sign"], "The second rule states this requirement.", skill="literal", shift=seed + 1),
        mcq("N3", "What should visitors bring for sun safety?", "a hat", ["a blanket", "a bell", "a torch"], "The notice tells visitors to bring a hat.", skill="literal", shift=seed + 2),
        mcq("N4", "Why might someone look outside the school office?", "to find out whether rain has closed the event", ["to borrow a bicycle", "to feed a pet", "to begin the quiet tour"], "The final sentence explains where a closure notice will be placed.", skill="inference", shift=seed + 3),
        mcq("N5", "What is the purpose of the bullet points?", "to make important rules easy to find", ["to show who wrote the notice", "to turn the notice into a story", "to rank visitors from best to worst"], "Bullets separate short pieces of practical information.", skill="text_feature", shift=seed),
        question("N6", "select_two", "Choose the two things that are not allowed inside the gate.", ["pets", "bicycles"], "The final bullet bans pets and bicycles.", skill="literal", options=["pets", "hats", "bicycles", "water bottles"]),
    ]
    return _passage("public-notice", "notice", title, questions, count, seed, text=text)


def recipe_procedure(context, count, seed):
    fruit = context["fruits"][seed % len(context["fruits"])]
    title = f"Make a {fruit} yoghurt cup"
    intro = f"For a food activity at the {context['place']}, {context['name']} uses a cup, a spoon, yoghurt, sliced {fruit}, oats and a clean container. Ask an adult to help cut the fruit."
    steps = [
        "Wash your hands and place the clean container on the bench.",
        "Spoon a layer of yoghurt into the container.",
        f"Add a layer of sliced {fruit}, then sprinkle oats on top.",
        "Repeat the layers once, cover the container and keep it cold until serving.",
    ]
    questions = [
        question("P1", "order", "Number these actions from 1 to 4.", [2, 4, 1, 3], "The numbered method gives the correct sequence.", skill="sequence", choices=[steps[1], steps[3], steps[0], steps[2]]),
        mcq("P2", "Why should an adult help?", "The fruit needs to be cut safely.", ["The yoghurt is too cold.", "The oats are too heavy.", "The container must be painted."], "The introduction links adult help with cutting fruit.", skill="cause_effect", shift=seed),
        mcq("P3", "What is added immediately after the first yoghurt layer?", f"sliced {fruit}", ["the lid", "another container", "warm water"], "Step 3 follows the first yoghurt layer.", skill="sequence", shift=seed + 1),
        mcq("P4", "What does <strong>repeat</strong> mean in the final step?", "do the layering again", ["remove every layer", "serve it at once", "change the ingredients"], "The instruction asks for the same layering action again.", skill="vocabulary", shift=seed + 2),
        mcq("P5", "Why is the container covered?", "to protect the food before it is served", ["to make the spoon longer", "to change the fruit colour", "to count the oats"], "Covering stored food keeps it protected.", skill="inference", shift=seed + 3),
        mcq("P6", "What type of text is this?", "a procedure", ["a poem", "a news report", "a book review"], "It lists materials and ordered instructions.", skill="purpose", shift=seed),
    ]
    return _passage("recipe-procedure", "procedure", title, questions, count, seed, type="procedure", intro=intro, steps=steps)


def timetable(context, count, seed):
    place = context["place"].title()
    activities = context["activities"]
    title = f"Saturday at the {place}"
    times = ["9:15", "10:00", "11:20", "12:10"]
    text = (
        "<table border='1' cellpadding='3'><tr><th>Time</th><th>Activity</th><th>Meet at</th></tr>"
        + "".join(f"<tr><td>{time}</td><td>{activities[index]}</td><td>{context['meeting_points'][index]}</td></tr>" for index, time in enumerate(times))
        + "</table><p>Bookings are needed only for the second activity. The final activity finishes at 12:45.</p>"
    )
    questions = [
        mcq("T1", f"What begins at {times[2]}?", activities[2], [activities[0], activities[1], activities[3]], "The third row pairs the time and activity.", skill="table", shift=seed),
        mcq("T2", f"Where do visitors meet for {activities[0]}?", context["meeting_points"][0], context["meeting_points"][1:], "The first row gives the meeting point.", skill="table", shift=seed + 1),
        mcq("T3", "Which activity must be booked?", activities[1], [activities[0], activities[2], activities[3]], "The note says only the second activity needs a booking.", skill="cross_reference", shift=seed + 2),
        mcq("T4", "How long does the final activity last?", "35 minutes", ["25 minutes", "45 minutes", "55 minutes"], "It starts at 12:10 and finishes at 12:45.", skill="time", shift=seed + 3),
        mcq("T5", "Why are the times arranged in the first column?", "so readers can quickly find when each activity starts", ["to show which activity is hardest", "to explain how each activity works", "to name the person in charge"], "A timetable organises events by starting time.", skill="text_feature", shift=seed),
        question("T6", "match", "Match each activity to its meeting point.", context["meeting_points"][:3], "Each pair appears in the same timetable row.", skill="table", left=activities[:3], right=[context["meeting_points"][2], context["meeting_points"][0], context["meeting_points"][1]]),
    ]
    return _passage("event-timetable", "timetable", title, questions, count, seed, text=text)


def class_data(context, count, seed):
    categories = context["survey_categories"]
    base = 4 + seed % 3
    values = [base + 2, base + 5, base + 1, base + 3]
    title = f"{context['name']}'s class survey: {context['survey_topic']}"
    text = f"The class asked, ‘{context['survey_question']}’ Each student chose one answer. The tally and bar graph show the same results."
    questions = [
        mcq("D1", f"How many students chose {categories[1]}?", str(values[1]), [values[0], values[2], values[3]], "The tallest bar and its tally show this value.", skill="data", shift=seed),
        mcq("D2", "Which choice was least popular?", categories[2], [categories[0], categories[1], categories[3]], "It has the smallest value.", skill="data", shift=seed + 1),
        mcq("D3", f"How many more students chose {categories[1]} than {categories[2]}?", str(values[1] - values[2]), [values[1] - values[0], values[3] - values[2], values[0]], "Subtract the smaller count from the larger count.", skill="data_reasoning", shift=seed + 2),
        mcq("D4", "Why must each student choose only one answer?", "so the totals count each student once", ["so every bar is the same height", "so no title is needed", "so the tally can be hidden"], "One response per student prevents double-counting.", skill="method", shift=seed + 3),
        mcq("D5", "What is the main advantage of the bar graph?", "It makes the sizes of the groups easy to compare.", ["It explains why students voted.", "It lists the students' names.", "It changes the survey results."], "Bar lengths allow quick visual comparison.", skill="text_feature", shift=seed),
        question("D6", "match", "Match each choice to its number of votes.", [str(value) for value in values], "The tally and bars display the four counts.", skill="data", left=categories, right=[str(values[2]), str(values[0]), str(values[3]), str(values[1])]),
    ]
    return _passage("class-data", "data", title, questions, count, seed, type="data", text=text, data={"labels": categories, "values": values, "category_heading": "Choice", "value_heading": "Tally"})


def poem(context, count, seed):
    subject = context["poem_subjects"][seed % len(context["poem_subjects"])]
    title = f"The {subject} after rain"
    lines = [
        f"The {subject} wears a silver shine,",
        "while drops keep time along the rail.",
        "A sleepy cloud slips out of sight,",
        "and sunlight draws a golden trail.",
        f"{context['name']} steps around the puddled ground,",
        "then hear the waking morning sound."
    ]
    questions = [
        mcq("O1", "Which two words rhyme?", "ground and sound", ["shine and rail", "sight and trail", "cloud and morning"], "The final words share the same ending sound.", skill="poetic_device", shift=seed),
        mcq("O2", "What does the cloud do?", "It slips out of sight.", ["It draws a trail.", "It steps around puddles.", "It taps on the rail."], "The third line describes the cloud.", skill="literal", shift=seed + 1),
        mcq("O3", "What picture is created by ‘sunlight draws a golden trail’?", "a bright path of light", ["a painted railway line", "a pile of yellow leaves", "a road made from metal"], "The words compare sunlight to a golden path.", skill="figurative_language", shift=seed + 2),
        mcq("O4", "How does the speaker probably feel?", "calm and interested", ["furious and noisy", "lost and frightened", "bored by everything"], "The speaker quietly notices changes after rain.", skill="inference", shift=seed + 3),
        mcq("O5", "Why is the word <strong>waking</strong> used?", "Morning sounds are beginning again.", ["The rail has fallen asleep.", "The speaker has missed the night.", "The puddles are getting deeper."], "The final line suggests the day is becoming active.", skill="vocabulary", shift=seed),
        question("O6", "select_two", "Choose the two details that show the rain has stopped.", ["the cloud slips away", "sunlight appears"], "Both details show the weather clearing.", skill="evidence", options=["the cloud slips away", "drops keep time", "sunlight appears", "the ground has puddles"]),
    ]
    return _passage("lyric-poem", "poem", title, questions, count, seed, type="poem", lines=lines)


def narrative(context, count, seed):
    name = context["name"]
    partner = context["partner"]
    place = context["place"]
    object_name = context["story_object"]
    title = f"The sound behind the door"
    text = (
        f"At closing time, {name} and {partner} were putting equipment away at the {place}. A soft tapping came from behind a narrow door. "
        f"{name} wanted to fetch an adult, but {partner} noticed that the door was not locked. They called out before opening it. "
        f"Inside, a loose window latch was knocking in the wind beside a fallen {object_name}. The children closed the window, lifted the {object_name} and told the supervisor what had happened. "
        "The mysterious tapping had a simple cause, but checking carefully had kept everyone safe."
    )
    questions = [
        mcq("S1", "What first creates a problem?", "a tapping sound comes from behind the door", ["the children lose the key", "the supervisor closes the building", "the equipment becomes too heavy"], "The unexplained tapping begins the complication.", skill="plot", shift=seed),
        mcq("S2", f"Why does {name} want to find an adult?", "The cause of the sound is unknown.", ["The window is already repaired.", "The children want to leave the equipment outside.", f"{partner} has hidden the object."], "Seeking help is a cautious response to an unknown sound.", skill="motive", shift=seed + 1),
        mcq("S3", "What is actually making the tapping sound?", "a loose window latch", [f"the fallen {object_name}", "a locked door", "the supervisor"], "The third sentence reveals the cause.", skill="literal", shift=seed + 2),
        mcq("S4", "Which word best describes the children?", "careful", ["reckless", "dishonest", "unhelpful"], "They call out, investigate safely and report what happened.", skill="character", shift=seed + 3),
        mcq("S5", "What is the main message of the story?", "Check an uncertain situation calmly and safely.", ["Every strange sound is dangerous.", "Windows should always stay open.", "Equipment is easiest to store outdoors."], "The ending explains the value of careful checking.", skill="theme", shift=seed),
        question("S6", "order", "Number these events from 1 to 4.", [2, 4, 1, 3], "The story gives this sequence.", skill="sequence", choices=["They called out before opening the door.", "They told the supervisor.", "They heard a tapping sound.", "They found the loose latch."]),
    ]
    return _passage("short-narrative", "narrative", title, questions, count, seed, text=text)


def letter_message(context, count, seed):
    name = context["name"]
    partner = context["partner"]
    place = context["place"]
    title = f"A note from {name}"
    text = (
        f"<p>Dear {partner},</p><p>Our class is visiting the {place} on {context['days'][seed % 5]}. Please meet us at the main entrance at 9:40 am. "
        f"Bring a pencil and a small notebook because we will sketch one object and record three facts about it. Lunch will stay at school, so pack only a water bottle. "
        f"If you arrive after 9:40, ask a staff member to call our teacher.</p><p>From {name}</p>"
    )
    questions = [
        mcq("L1", "Who wrote the note?", name, [partner, "the desk worker", "the teacher"], "The sign-off names the writer.", skill="text_feature", shift=seed),
        mcq("L2", "Where should the reader meet the class?", "at the main entrance", ["at the lunch table", "outside the school gate", "beside the water bottles"], "The first paragraph gives the meeting place.", skill="literal", shift=seed + 1),
        mcq("L3", "Why is a notebook needed?", "to sketch an object and record facts", ["to order lunch", "to write a message to the desk worker", "to carry the water bottle"], "The second sentence explains the tasks.", skill="cause_effect", shift=seed + 2),
        mcq("L4", "What should a late visitor do?", "ask a staff member to call the teacher", ["return home immediately", "wait silently outside", "take the class lunch"], "The final instruction explains what to do when late.", skill="literal", shift=seed + 3),
        mcq("L5", "What is the main purpose of the note?", "to give practical information about a class visit", ["to review the place", "to tell an imaginary adventure", "to advertise notebooks"], "The note gives meeting and packing instructions.", skill="purpose", shift=seed),
        question("L6", "select_two", "Choose the two things the reader should bring.", ["a pencil", "a water bottle"], "Both are named in the note.", skill="literal", options=["a pencil", "lunch", "a water bottle", "a large bag"]),
    ]
    return _passage("personal-message", "letter", title, questions, count, seed, text=text)


def review(context, count, seed):
    book = context["book_titles"][seed % len(context["book_titles"])]
    stars = 3 + seed % 3
    title = f"Review: {book}"
    text = (
        f"<p><strong>{book}</strong> by {context['author']}<br>{'★' * stars}{'☆' * (5 - stars)}</p>"
        f"<p>This adventure follows {context['name']}, who must solve a problem at the {context['place']}. The opening is gentle, but the middle becomes lively when a careful plan goes wrong. "
        "The drawings add useful clues without giving away the ending. Some younger readers may need help with two unusual words, yet the short chapters make the story easy to pause and continue. "
        f"I recommend it to readers who enjoy {context['review_interest']}.</p>"
    )
    questions = [
        mcq("V1", "Who wrote the book?", context["author"], [context["name"], context["partner"], "the reviewer"], "The author's name appears below the title.", skill="bibliographic", shift=seed),
        mcq("V2", "What changes in the middle of the story?", "a careful plan goes wrong", ["the drawings disappear", "the chapters become longer", "the opening is repeated"], "The review identifies the event that makes the middle lively.", skill="literal", shift=seed + 1),
        mcq("V3", "How do the drawings help?", "They provide clues.", ["They reveal the ending.", "They replace every word.", "They make the chapters longer."], "The reviewer says the drawings add useful clues.", skill="literal", shift=seed + 2),
        mcq("V4", "Who is most likely to enjoy this book?", f"readers who enjoy {context['review_interest']}", ["readers looking for a recipe", "readers studying a bus timetable", "readers wanting only facts about weather"], "The recommendation identifies the likely audience.", skill="audience", shift=seed + 3),
        mcq("V5", "What is one criticism in the review?", "Two unusual words may be difficult for younger readers.", ["The ending is printed first.", "The book has no drawings.", "Every chapter is too long."], "This is the only concern the reviewer raises.", skill="evaluation", shift=seed),
        mcq("V6", "How many stars did the reviewer give?", f"{stars} out of 5", [f"{value} out of 5" for value in range(1, 6) if value != stars][:3], "Count the filled stars in the rating.", skill="text_feature", shift=seed + 1),
    ]
    return _passage("book-review", "review", title, questions, count, seed, text=text)


def incident_report(context, count, seed):
    name = context["name"]
    place = context["place"]
    item = context["incident_anchor"]
    title = "Playground incident report"
    text = (
        "<table border='1' cellpadding='3'>"
        f"<tr><th>Date</th><td>{12 + seed % 15} August</td></tr><tr><th>Time</th><td>1:{20 + seed % 30:02d} pm</td></tr>"
        f"<tr><th>Place</th><td>{place}</td></tr><tr><th>Reported by</th><td>{name}</td></tr>"
        f"<tr><th>What happened?</th><td>A loose strap on a bag caught around a {item}. Nobody was hurt.</td></tr>"
        "<tr><th>Action taken</th><td>The area was kept clear. An adult removed the bag and checked the equipment.</td></tr></table>"
    )
    questions = [
        mcq("F1", "Who completed the report?", name, [context["partner"], "an injured student", "the equipment maker"], "The ‘Reported by’ row names the person.", skill="form", shift=seed),
        mcq("F2", "Was anybody hurt?", "No", ["Yes, one adult", "Yes, two students", "The report does not say"], "The description states that nobody was hurt.", skill="literal", shift=seed + 1),
        mcq("F3", "Why was the area kept clear?", "so the bag could be removed safely", ["so a game could begin", "so the report could be hidden", "so the equipment could be painted"], "Keeping people away reduced risk while the problem was fixed.", skill="inference", shift=seed + 2),
        mcq("F4", "Which row explains how the problem was handled?", "Action taken", ["Date", "Place", "Reported by"], "That row records the response to the incident.", skill="text_feature", shift=seed + 3),
        mcq("F5", "Why is this information presented in labelled rows?", "so each fact can be found quickly", ["to make it rhyme", "to hide the time", "to create suspense"], "A form separates different kinds of factual information.", skill="text_feature", shift=seed),
        question("F6", "true_false", "Decide whether each statement is true or false.", [True, False, True], "The report confirms the place and adult check, but says nobody was hurt.", skill="evidence", statements=[f"The incident happened at the {place}.", "A student was injured.", "An adult checked the equipment."]),
    ]
    return _passage("incident-form", "form", title, questions, count, seed, text=text)


def opinion_article(context, count, seed):
    topic = context["opinion_topics"][seed % len(context["opinion_topics"])]
    title = f"Should our school have {topic}?"
    text = (
        f"In {context['name']}'s class, some students want the school to have {topic}. Supporters say it would give children a useful choice and could make break times more interesting. "
        "They also suggest starting with a short trial so the school can see how well the idea works. "
        "Other people worry about cost, space and supervision. These concerns matter, but clear rules and a small trial could solve many problems. "
        f"For these reasons, I think the school should test {topic} for one term before making a final decision."
    )
    questions = [
        mcq("E1", "What is the writer's opinion?", f"The school should trial {topic} for one term.", [f"The school should ban {topic} forever.", "No decision should ever be made.", "Every school must use the idea immediately."], "The final sentence states the writer's position.", skill="main_idea", shift=seed),
        mcq("E2", "What benefit do supporters mention?", "It could make break times more interesting.", ["It would remove every school rule.", "It would need no supervision.", "It would create more classroom space."], "The first paragraph gives this benefit.", skill="literal", shift=seed + 1),
        mcq("E3", "Which concern is mentioned?", "cost", ["weather forecasts", "book covers", "bus timetables"], "Cost is listed with space and supervision.", skill="literal", shift=seed + 2),
        mcq("E4", "Why does the writer suggest a trial?", "to test the idea before making a final decision", ["to avoid making any rules", "to guarantee that nobody disagrees", "to make the idea more expensive"], "A trial provides evidence before a permanent choice.", skill="reasoning", shift=seed + 3),
        mcq("E5", "What does <strong>concerns</strong> mean here?", "worries", ["celebrations", "instructions", "answers"], "The concerns are possible problems people worry about.", skill="vocabulary", shift=seed),
        question("E6", "select_two", "Choose the two problems the writer says clear rules may help solve.", ["space", "supervision"], "Both are named as concerns in the third sentence.", skill="evidence", options=["space", "supervision", "spelling", "sunrise"]),
    ]
    return _passage("opinion-article", "opinion", title, questions, count, seed, text=text)


def paired_texts(context, count, seed):
    profile = context["paired_profiles"][seed % len(context["paired_profiles"])]
    animal_a = profile["animal_a"]
    animal_b = profile["animal_b"]
    title = f"Two night visitors: {animal_a} and {animal_b}"
    text = (
        f"<p>{context['name']}'s class at the {context['place']} compared two animals.</p>"
        f"<p><strong>{animal_a}</strong><br>{profile['text_a']}</p>"
        f"<p><strong>{animal_b}</strong><br>{profile['text_b']}</p>"
        "<p>Both animals need connected areas of shelter so they can move without crossing busy roads.</p>"
    )
    questions = [
        mcq("C1", f"Where does the {animal_a} search for food?", "near the ground", ["above the clouds", "inside a classroom", "under deep water"], "The first text gives this detail.", skill="literal", shift=seed),
        mcq("C2", f"What food is named for the {animal_b}?", "fruit or flowers", ["oats and yoghurt", "fish and seaweed", "bread and cheese"], "The second text names fruit and flowers.", skill="literal", shift=seed + 1),
        mcq("C3", "What do both animals do?", "feed at night", ["rest under water", "eat only insects", "sleep on the ground"], "Both descriptions say the animals are active at night.", skill="compare", shift=seed + 2),
        mcq("C4", "How are their daytime shelters different?", f"The {animal_a} shelters in plants, while the {animal_b} rests above the ground.", ["Both rest on busy roads.", f"Only the {animal_a} rests above the ground.", "Neither animal uses shelter."], "The two paragraphs describe different resting places.", skill="contrast", shift=seed + 3),
        mcq("C5", "Why are connected shelter areas important?", "They help the animals avoid busy roads.", ["They make sunrise happen earlier.", "They stop plants from growing.", "They keep every insect away."], "The final sentence explains the safety benefit.", skill="cause_effect", shift=seed),
        question("C6", "match", "Match each feature to the correct animal.", [animal_a, animal_b, "both"], "The first two texts and final sentence identify these features.", skill="compare", left=["searches near the ground", "climbs for food", "feeds at night"], right=["both", animal_b, animal_a]),
    ]
    return _passage("paired-information", "paired", title, questions, count, seed, text=text)


def map_directions(context, count, seed):
    place = context["place"].title()
    title = f"Finding your way around the {place}"
    text = (
        "<p>The entrance is on the south side. The information desk is directly north of the entrance. "
        "The café is east of the desk, and the toilets are west of it. The activity room is north of the café. "
        "A path joins the entrance, desk and activity room. Visitors using wheelchairs should follow this path because it has no steps.</p>"
    )
    questions = [
        mcq("M1", "What is directly north of the entrance?", "the information desk", ["the café", "the toilets", "the activity room"], "The second sentence gives this position.", skill="spatial", shift=seed),
        mcq("M2", "Which place is east of the desk?", "the café", ["the entrance", "the toilets", "the south gate"], "The text places the café east of the desk.", skill="spatial", shift=seed + 1),
        mcq("M3", "Where is the activity room?", "north of the café", ["south of the entrance", "west of the toilets", "inside the information desk"], "The third sentence gives its position.", skill="spatial", shift=seed + 2),
        mcq("M4", "Why is one path recommended for wheelchair users?", "It has no steps.", ["It is the longest route.", "It passes every toilet.", "It is open only at night."], "The final sentence gives the reason.", skill="cause_effect", shift=seed + 3),
        mcq("M5", "What is the purpose of this text?", "to help visitors locate places", ["to review the café food", "to tell a story about the desk", "to explain how to build a path"], "The text gives positions and route advice.", skill="purpose", shift=seed),
        question("M6", "true_false", "Decide whether each statement is true or false.", [True, False, True], "The locations can be checked against the directions.", skill="spatial", statements=["The toilets are west of the desk.", "The entrance is north of the desk.", "The activity room is north of the café."]),
    ]
    return _passage("map-directions", "directions", title, questions, count, seed, text=text)


def science_explanation(context, count, seed):
    topic = context["science_topics"][seed % len(context["science_topics"])]
    title = topic["title"]
    text = f"During a lesson at the {context['place']}, {context['name']} read this explanation. " + topic["text"]
    questions = [
        mcq("X1", topic["literal_prompt"], topic["literal_answer"], topic["literal_distractors"], "The explanation states this fact directly.", skill="literal", shift=seed),
        mcq("X2", topic["cause_prompt"], topic["cause_answer"], topic["cause_distractors"], "The text links the cause and result.", skill="cause_effect", shift=seed + 1),
        mcq("X3", "What does the bold word mean in this explanation?", topic["word_meaning"], topic["word_distractors"], "Its meaning is clear from the surrounding sentence.", skill="vocabulary", shift=seed + 2),
        mcq("X4", "Which sentence best summarises the explanation?", topic["summary"], topic["summary_distractors"], "This option includes the central idea rather than one small detail.", skill="summary", shift=seed + 3),
        mcq("X5", "Why does the writer include an example?", "to make the explanation easier to understand", ["to change the topic", "to hide the main idea", "to turn facts into a timetable"], "The example shows how the process works in a familiar situation.", skill="author_choice", shift=seed),
        question("X6", "cloze", topic["cloze_prompt"], topic["cloze_answer"], "Both words complete the explanation accurately.", skill="summary", word_bank=topic["cloze_bank"], gaps=2),
    ]
    return _passage("science-explanation", "explanation", title, questions, count, seed, text=text)


BUILDERS = [
    animal_information,
    public_notice,
    recipe_procedure,
    timetable,
    class_data,
    poem,
    narrative,
    letter_message,
    review,
    incident_report,
    opinion_article,
    paired_texts,
    map_directions,
    science_explanation,
]


def build_reading(paper_number, names, partners, animals, objects, places):
    index = paper_number - 1
    animal = animals[index]
    paired_animal = animals[(index + 17) % len(animals)]
    context = {
        "name": names[index],
        "partner": partners[index],
        "animal": animal,
        "paired_animal": paired_animal,
        "object": objects[index],
        "story_object": ["storage basket", "small toolbox", "folder box", "sports bag", "plastic crate"][index % 5],
        "incident_anchor": ["bench leg", "goal post", "fence rail", "climbing frame", "bike rack"][index % 5],
        "place": places[index],
        "alternate_place": places[(index + 9) % len(places)],
        "animal_profiles": [
            {"animal": "wombat", "habitat": "in forests and grasslands", "food": "grasses and roots", "shelter": "underground burrows", "active_time": "evening", "adaptation": "Its strong legs and claws help it dig.", "defence": "retreats into its burrow", "feature_answer": "strong legs and claws for digging", "feature_distractors": ["wings for flying", "fins for swimming at sea", "a beak for cracking shells"]},
            {"animal": "koala", "habitat": "in eucalypt woodland", "food": "eucalypt leaves", "shelter": "eucalypt branches", "active_time": "night", "adaptation": "Its gripping paws help it climb and hold branches.", "defence": "climbs higher into the tree", "feature_answer": "gripping paws for climbing", "feature_distractors": ["webbed feet for diving", "a shell for hiding", "wide wings for gliding"]},
            {"animal": "platypus", "habitat": "beside freshwater creeks and rivers", "food": "small water animals", "shelter": "burrows beside a creek", "active_time": "early morning", "adaptation": "Its webbed feet help it swim and search underwater.", "defence": "dives into the water", "feature_answer": "webbed feet for swimming", "feature_distractors": ["hooves for running", "wings for flying", "a mane for warmth"]},
            {"animal": "little penguin", "habitat": "along the southern coast", "food": "small fish", "shelter": "burrows near the coast", "active_time": "hours before dawn", "adaptation": "Its flippers help it move through water.", "defence": "swims away quickly", "feature_answer": "flippers for swimming", "feature_distractors": ["claws for digging soil", "a long trunk for lifting", "sticky toes for climbing glass"]},
            {"animal": "bottlenose dolphin", "habitat": "in coastal seas", "food": "fish and squid", "shelter": "sheltered coastal water", "active_time": "day", "adaptation": "Its streamlined body helps it move efficiently through water.", "defence": "swims with the group", "feature_answer": "a streamlined body for swimming", "feature_distractors": ["feathers for silent flight", "paws for climbing trees", "a shell for digging"]},
        ],
        "paired_profiles": [
            {"animal_a": "ground beetle", "animal_b": "ringtail possum", "text_a": "The ground beetle searches near the ground after sunset. It eats small insects and shelters under leaves before dawn.", "text_b": "The ringtail possum also feeds at night, but it climbs to reach leaves, fruit and flowers. During the day it rests above the ground."},
            {"animal_a": "bandicoot", "animal_b": "sugar glider", "text_a": "The bandicoot searches near the ground after sunset. It digs for insects and shelters in dense plants before dawn.", "text_b": "The sugar glider also feeds at night, but it climbs to reach sap, nectar and insects. During the day it rests above the ground."},
        ],
        "fruits": ["banana", "peach", "pear", "mango", "strawberry"],
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "activities": ["guided walk", "object sketching", "short science talk", "story session"],
        "meeting_points": ["front gate", "display room", "north bench", "reading corner"],
        "survey_topic": ["ways to travel", "library choices", "garden jobs", "wet-day activities", "healthy snacks"][index % 5],
        "survey_question": ["How do you usually travel to school?", "Which library section do you visit first?", "Which garden job would you choose?", "What should our class do on a wet day?", "Which snack would you pack?"][index % 5],
        "survey_categories": [
            ["walk", "bike", "bus", "car"],
            ["stories", "facts", "poetry", "comics"],
            ["watering", "weeding", "planting", "mulching"],
            ["drawing", "reading", "puzzles", "music"],
            ["fruit", "yoghurt", "crackers", "sandwich"],
        ][index % 5],
        "poem_subjects": ["garden", "playground", "roof", "footpath", "oval"],
        "book_titles": ["The Hidden Track", "Moonlight Map", "The Smallest Signal", "Bridge of Leaves", "The Borrowed Bell"],
        "author": ["Ari Lane", "Mina Cole", "Toby Reed", "Lena Park", "Owen Hart"][index % 5],
        "review_interest": ["mysteries", "animal adventures", "funny problems", "inventive characters", "outdoor discoveries"][index % 5],
        "opinion_topics": ["a lunchtime games shelf", "a small vegetable patch", "a quiet reading corner", "a weekly class walk", "a student art wall"],
        "science_topics": [
            {
                "title": "Why shadows change",
                "text": "A shadow forms when an object blocks light. When the light source moves, the shadow changes direction and length. <strong>Position</strong> means where something is placed. For example, a low morning Sun can make a long shadow. The object has not stretched; only the angle of the light has changed.",
                "literal_prompt": "What forms when an object blocks light?", "literal_answer": "a shadow", "literal_distractors": ["a sound", "a magnet", "a puddle"],
                "cause_prompt": "Why can a morning shadow be long?", "cause_answer": "The Sun is low in the sky.", "cause_distractors": ["The object has stretched.", "The ground has moved.", "The air has become heavier."],
                "word_meaning": "the place where something is", "word_distractors": ["the colour of something", "the noise something makes", "the age of something"],
                "summary": "Shadows change when the position of the light changes.", "summary_distractors": ["Objects grow longer every morning.", "All shadows point in the same direction.", "Light passes through every object."],
                "cloze_prompt": "Complete the sentence.<br>An object blocks ___, and the shadow changes when the light source ___.", "cloze_answer": ["light", "moves"], "cloze_bank": ["light", "moves", "sound", "rests"],
            },
            {
                "title": "How dew appears",
                "text": "Air contains water vapour that cannot usually be seen. During a cool night, some surfaces lose heat. Water vapour touching a cold surface can <strong>condense</strong> into tiny drops. For example, dew may appear on grass before sunrise. Dew has not fallen like rain; it has formed from vapour near the ground.",
                "literal_prompt": "Where may dew appear?", "literal_answer": "on grass", "literal_distractors": ["inside a flame", "under dry sand", "above the Sun"],
                "cause_prompt": "Why do tiny drops form on a cool surface?", "cause_answer": "Water vapour condenses there.", "cause_distractors": ["Rain rises from the ground.", "Grass produces glass.", "Sunlight freezes the air."],
                "word_meaning": "change from vapour into liquid drops", "word_distractors": ["change from solid into sound", "move quickly uphill", "become brighter"],
                "summary": "Dew forms when water vapour cools and becomes liquid.", "summary_distractors": ["Dew is rain stored in grass.", "Warm surfaces always make ice.", "Water vapour can always be seen."],
                "cloze_prompt": "Complete the sentence.<br>Dew forms when water ___ touches a cool surface and becomes liquid ___.", "cloze_answer": ["vapour", "drops"], "cloze_bank": ["vapour", "drops", "sunlight", "dust"],
            },
        ],
    }
    counts = [6, 6, 6, 6, 5, 5, 5]
    passages = []
    for slot, count in enumerate(counts):
        builder_index = (index * 5 + slot * 3) % len(BUILDERS)
        seed = index * 11 + slot * 7
        passage = BUILDERS[builder_index](context, count, seed)
        passage["id"] = f"P{slot + 1}"
        passage["source_basis"] = "ACARA Year 3 released-paper archetype, independently authored"
        passages.append(passage)
    return passages
