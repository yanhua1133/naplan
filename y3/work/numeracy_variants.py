from __future__ import annotations

import re


def _numbers(text):
    without_times = re.sub(r"\b\d{1,2}:\d{2}\b", "", str(text))
    return [int(value) for value in re.findall(r"\d+", without_times)]


def _times(text):
    return re.findall(r"\b\d{1,2}:\d{2}\b", str(text))


def apply_numeracy_variant(item, form):
    template = item["template_id"]
    prompt = item["prompt"]
    answer = str(item["answer"])
    visual = item.get("visual", {})
    explanation_numbers = _numbers(item["explanation"])
    prompt_numbers = _numbers(prompt)

    if template == "N1":
        known, total = prompt_numbers[:2]
        forms = [
            prompt,
            f"A number added to {known} gives {total}. What is the number?",
            f"Start at {known} and count on to {total}. How much did you count on?",
            f"A collection of {total} counters is split into {known} counters and another group. How many counters are in the other group?",
            f"Complete the related subtraction fact.<br><strong>{total} − {known} = ___</strong>",
        ]
    elif template == "N2":
        first, second = explanation_numbers[:2]
        forms = [
            prompt,
            f"One tray has {first} counters and another has {second}. How many counters are there altogether?",
            f"Complete the total in this table.<br><strong>Group A: {first} &nbsp; Group B: {second} &nbsp; Total: ___</strong>",
            f"A class collected {first} cans in the morning and {second} in the afternoon. What is the combined total?",
            f"Which number is the sum of {first} and {second}? Write the number.",
        ]
    elif template == "N3":
        sequence = prompt_numbers[:4]
        step = explanation_numbers[0]
        forms = [
            prompt,
            f"The rule is ‘add {step}’. Continue the pattern.<br><strong>{', '.join(map(str, sequence))}, ___</strong>",
            f"A number pattern starts at {sequence[0]} and increases by {step}. What is the fifth number?",
            f"Complete the last box.<br><strong>{sequence[0]} → {sequence[1]} → {sequence[2]} → {sequence[3]} → □</strong>",
            f"Four terms are {', '.join(map(str, sequence))}. Which number follows if the same rule continues?",
        ]
    elif template == "N4":
        factor_a, factor_b = prompt_numbers[:2]
        forms = [
            prompt,
            f"There are {factor_a} equal groups with {factor_b} in each group. Which repeated addition shows the total?",
            f"An array has {factor_a} rows of {factor_b}. Which addition sentence matches the array?",
            f"A number line makes {factor_a} equal jumps of {factor_b}. Which addition records those jumps?",
            f"Which sum represents <strong>{factor_b}</strong> added exactly <strong>{factor_a}</strong> times?",
        ]
    elif template == "N5":
        rows, cols, cut = visual["rows"], visual["cols"], visual["cut"]
        forms = [
            prompt,
            f"The grid began with {rows} rows of {cols} squares. The missing corner contains {cut} squares. How many squares remain?",
            "Count the equal square units in the L-shaped region. What is its area in square units?",
            f"A {rows}-by-{cols} sticker sheet has {cut} spaces cut away. How many sticker spaces are left?",
            "Use the grid to work out the number of unshaded unit squares.",
        ]
    elif template == "N6":
        values = visual["values"]
        step = values[0] - values[1]
        forms = [
            prompt,
            f"The groups contain {values[0]}, {values[1]} and {values[2]} circles. The number decreases by {step}. How many circles are in the next group?",
            "Continue the decreasing circle pattern. How many circles replace the question mark?",
            f"Start with {values[0]} and subtract {step} for each new group. What is the fourth term?",
            f"Complete the pattern: {values[0]}, {values[1]}, {values[2]}, ___.",
        ]
    elif template == "N7":
        icons, key = visual["icons"], int(answer)
        total = icons * key
        forms = [
            prompt,
            f"The pictograph uses {icons} symbols to represent {total} objects. How many objects does each symbol represent?",
            f"Complete the pictograph key.<br><strong>{icons} symbols = {total} objects, so 1 symbol = ___ objects.</strong>",
            f"A row has {icons} identical picture symbols and represents a total of {total}. What is the value of one symbol?",
            f"Divide the pictograph total, {total}, equally among its {icons} symbols. What is the key?",
        ]
    elif template == "N8":
        forms = [
            prompt,
            "Imagine looking straight down at the cone. Which 2D shape would you see?",
            "Which shape matches the circular footprint of a cone?",
            "A cone is viewed from directly above. Choose its top view.",
            "Which 2D shape is the base outline seen from above a cone?",
        ]
    elif template == "N9":
        digits = prompt_numbers[:3]
        digit_text = ", ".join(map(str, digits))
        forms = [
            prompt,
            f"Arrange {digit_text} to make the greatest possible 3-digit odd number below 800. Use every digit once.",
            f"A number uses the digit cards {digit_text} exactly once. It is odd and less than 800. What is the largest possible number?",
            f"Choose the greatest number below 800 that can be formed from {digit_text} and has an odd ones digit.",
            f"Place the cards {digit_text} into the hundreds, tens and ones places. Make the largest odd number that is still below 800.",
        ]
    elif template == "N10":
        forms = [
            prompt,
            "Which equal-parts model represents a fraction equivalent to one third?",
            "Choose the diagram where the shaded part is exactly 1/3 of the whole.",
            "Which option has one out of every three equal parts shaded?",
            "Find the fraction model that can be simplified to 1/3.",
        ]
    elif template == "N11":
        left, target = prompt_numbers[:2]
        forms = [
            prompt,
            f"What must be added to {left} to reach {target}?",
            f"Complete the subtraction fact that finds the missing addend.<br><strong>{target} − {left} = ___</strong>",
            f"A total of {target} is made from one part of {left} and a missing part. What is the missing part?",
            f"Count on from {left} to {target}. How much is added?",
        ]
    elif template == "N12":
        start_time = _times(prompt)[0]
        elapsed = prompt_numbers[-2]
        forms = [
            prompt,
            f"An activity starts at {start_time} and ends {elapsed} minutes later. A reminder sounds 10 minutes before the finish. What time is the reminder?",
            f"From {start_time}, move forward {elapsed - 10} minutes on a clock. What time do you reach?",
            f"A {elapsed}-minute session begins at {start_time}. Write the time that is 10 minutes before the session ends.",
            f"The finish time is {elapsed} minutes after {start_time}. What time is 10 minutes earlier than that finish?",
        ]
    elif template == "N13":
        first, second = explanation_numbers[:2]
        forms = [
            prompt,
            f"A reader completes {first} pages before lunch and {second} pages after lunch. How many pages are completed in total?",
            f"Find the combined total of two page counts: {first} and {second}.",
            f"A chart records {first} pages on Day 1 and {second} pages on Day 2. Complete the two-day total.",
            f"Add the two reading amounts, {first} pages and {second} pages. Write the total.",
        ]
    elif template == "N14":
        larger, smaller = explanation_numbers[:2]
        forms = [
            prompt,
            f"How many more points is {larger} than {smaller}?",
            f"Find the gap between scores of {larger} and {smaller}.",
            f"A scoreboard shows {larger} for Team A and {smaller} for Team B. What is the difference?",
            f"Calculate the difference: subtract the lower score, {smaller}, from the higher score, {larger}.",
        ]
    elif template == "N15":
        values = visual["values"]
        forms = [
            prompt,
            f"From the price list, find the difference between item D (${values[3]:.2f}) and item B (${values[1]:.2f}).",
            "Item D is dearer than item B. How much dearer is it?",
            "Use the table to calculate D minus B.",
            "A shopper changes from buying item B to item D. How much extra will the shopper pay?",
        ]
    elif template == "N16":
        hour, minute = visual["hour"], visual["minute"]
        start_time = f"{hour}:{minute:02d}"
        forms = [
            prompt,
            f"The clock shows {start_time}. What time will it be after 30 minutes?",
            f"A program starts at the time shown and runs for half an hour. When does it finish?",
            "Move the minute hand forward by half a turn. What new time is shown?",
            f"Calculate the finishing time by adding half an hour to {start_time}.",
        ]
    elif template == "N17":
        target = visual["target"]
        forms = [
            prompt,
            f"On the map, move east from the entry and pass the office. Which room is immediately next?",
            f"The route goes entry → office → ___. Which room completes the route?",
            "Follow the corridor arrow to the east. Write the name of the room directly after the office.",
            f"Which labelled room is one position east of the office?",
        ]
    elif template == "N18":
        letter = answer
        forms = [
            prompt,
            "Which printed capital has a vertical line of symmetry?",
            "A vertical mirror is placed through each letter. Which letter matches its reflection?",
            "Choose the capital letter that can be folded vertically into matching halves.",
            f"Which option has left and right halves that are mirror images?",
        ]
    elif template == "N19":
        cost, budget = prompt_numbers[:2]
        forms = [
            prompt,
            f"With ${budget}, how many ${cost} badges can be bought without going over the budget?",
            f"A badge costs ${cost}. Divide a budget of ${budget} into as many complete badge costs as possible.",
            f"What is the greatest whole number of badges affordable at ${cost} each from ${budget}?",
            f"Keep subtracting ${cost} from ${budget}. How many badges can be paid for?",
        ]
    elif template == "N20":
        forms = [
            prompt,
            "Count the unit squares. Which pair of labelled shapes covers an equal area?",
            "Two shapes contain the same number of square units. Select both shapes.",
            "Choose the two area models that are equal in size.",
            "Which two labelled arrangements use exactly the same number of unit squares?",
        ]
    elif template == "N21":
        cubes = visual["count"]
        mass = prompt_numbers[0]
        forms = [
            prompt,
            f"The picture contains {cubes} equal cubes. Each cube weighs {mass} g. Find the mass of the whole solid.",
            f"Multiply the {cubes} cubes by {mass} g per cube. What is the total mass?",
            f"A model uses {cubes} cubes of equal mass. One cube is {mass} g. How heavy is the model?",
            f"Complete: {cubes} cubes × {mass} g = ___ g.",
        ]
    elif template == "N22":
        values = prompt_numbers[:3]
        step = explanation_numbers[0]
        forms = [
            prompt,
            f"The sequence starts {values[0]}, {values[1]}, {values[2]} and subtracts {step}. Select the two later terms.",
            f"Which two options can be reached by repeatedly subtracting {step} from {values[0]}?",
            f"Continue the decreasing pattern from {values[0]}. Choose two numbers that belong.",
            f"A number chain follows the rule ‘minus {step}’. Which two choices fit the chain?",
        ]
    elif template == "N23":
        digit_sum = prompt_numbers[-1]
        forms = [
            prompt,
            f"Find a number under 40 whose digits total {digit_sum}. The ones digit is 3 greater than the tens digit.",
            f"A mystery number has a smaller tens digit, a digit difference of 3 and a digit sum of {digit_sum}. What is it?",
            f"Complete the digit puzzle: tens + ones = {digit_sum}, and ones − tens = 3.",
            f"Which two-digit number below 40 has digits that differ by 3 and add to {digit_sum}?",
        ]
    elif template == "N24":
        forms = [
            prompt,
            "Count only the curved outer surfaces of the cylinder-and-hemisphere solid. How many are there?",
            "A half-sphere sits on a cylinder. How many separate curved surfaces remain on the outside?",
            "Ignore the hidden joined faces. How many curved faces can be touched on the combined solid?",
            "Which number describes the curved surfaces on the outside of this composite object?",
        ]
    elif template == "N25":
        costs = re.findall(r"\$\d+\.\d{2}", prompt)
        three_cost = costs[0]
        forms = [
            prompt,
            f"A pack of 3 cups costs {three_cost}. At the same unit price, find the cost of 5 cups.",
            f"First find the price of 1 cup from 3 cups costing {three_cost}. Then calculate the price of 5 cups.",
            f"Complete the equivalent-rate table.<br><strong>3 cups: {three_cost} &nbsp; 5 cups: ___</strong>",
            f"The price per cup stays constant. How much are 5 cups if 3 cost {three_cost}?",
        ]
    elif template == "N26":
        groups, each = prompt_numbers[:2]
        forms = [
            prompt,
            f"A seating plan has {groups} equal groups of {each} seats. What is the total number of seats?",
            f"Calculate {groups} × {each} to find the capacity.",
            f"There are {each} seats in each of {groups} buses. How many seats altogether?",
            f"Complete the equal-groups total: {groups} groups × {each} per group = ___.",
        ]
    elif template == "N27":
        high, low = visual["high"], visual["low"]
        forms = [
            prompt,
            f"The temperature changes from {high}°C to {low}°C. By how many degrees does it decrease?",
            f"Find the difference between the two thermometer readings, {high}°C and {low}°C.",
            f"How far apart are {high} and {low} on a temperature scale?",
            f"Complete: {high}°C − {low}°C = ___°C.",
        ]
    elif template == "N28":
        total, beyond = prompt_numbers[:2]
        halfway = total // 2
        forms = [
            prompt,
            f"A {total} km route has a halfway point at {halfway} km. After travelling {beyond} km beyond halfway, how far is left?",
            f"From the remaining half of {halfway} km, subtract the extra {beyond} km already travelled. What remains?",
            f"A bus is {halfway + beyond} km into a {total} km trip. How many kilometres are still to go?",
            f"Complete the distance calculation: {total} − ({halfway} + {beyond}) = ___.",
        ]
    elif template == "N29":
        values = visual["values"]
        forms = [
            prompt,
            f"Read the equally spaced marks. Which list matches {values[0]}, {values[1]}, {values[2]}, {values[3]}?",
            "Choose the four numbers that belong under the number-line ticks from left to right.",
            f"The line starts at {values[0]} and uses an equal interval. Which option labels every tick correctly?",
            "Which ordered list agrees with the positions shown on the number line?",
        ]
    elif template == "N30":
        dozens, group = prompt_numbers[:2]
        total = dozens * 12
        forms = [
            prompt,
            f"Convert {dozens} dozen to {total} pencils, then share them into groups of {group}. What is the remainder?",
            f"How many pencils cannot be placed into complete groups of {group} when there are {total} pencils?",
            f"Complete the division with remainder: {total} ÷ {group} leaves ___.",
            f"After making as many full packs of {group} as possible from {dozens} dozen pencils, how many are left?",
        ]
    elif template == "N31":
        mass_a, mass_b = visual["values"]
        forms = [
            prompt,
            f"The scales read about {mass_a} kg and {mass_b} kg. Estimate the difference in mass.",
            "Use the two scale readings to find how much heavier A is than B.",
            f"Subtract the lighter mass, {mass_b} kg, from the heavier mass, {mass_a} kg.",
            "Which option is closest to the gap between the two displayed masses?",
        ]
    elif template == "N32":
        sequence = prompt_numbers[:3]
        step = explanation_numbers[0]
        forms = [
            prompt,
            f"The pattern increases by {step}. What number comes immediately before {sequence[0]}?",
            f"Work backwards one equal step from {sequence[0]}. Which number is missing?",
            f"Complete the four-term number-line pattern ending {', '.join(map(str, sequence))}.",
            f"A sequence adds {step} each time. Find the term before {sequence[0]}.",
        ]
    elif template == "N33":
        known, total = visual["known"], visual["total"]
        forms = [
            prompt,
            f"Four categories total {total}. Three values are {known[0]}, {known[1]} and {known[2]}. Find the fourth value.",
            f"Complete the table so all categories add to {total}.",
            f"Subtract the known subtotal from {total} to find the missing category.",
            f"What number makes {known[0]} + {known[1]} + {known[2]} + □ = {total}?",
        ]
    elif template == "N34":
        values = visual["values"]
        forms = [
            prompt,
            f"The chart shows A = {values[0]} and B = {values[1]}. Find B − A.",
            "Compare bars A and B. How much taller is B?",
            f"How many votes must be added to A's {values[0]} votes to equal B's {values[1]} votes?",
            "Use the exact values above the bars to calculate the difference between B and A.",
        ]
    elif template == "N35":
        forms = [
            prompt,
            "Compare the blue sectors as fractions of each whole spinner. Which probability is smallest?",
            "On which spinner is blue least likely?",
            "Choose the spinner with the smallest proportion coloured blue.",
            "Which spinner gives blue the least share of the circle?",
        ]
    elif template == "N36":
        twos, ones = visual["twos"], visual["ones"]
        forms = [
            prompt,
            f"Find the value of {twos} × $2 plus {ones} × $1.",
            f"The coin picture contains {twos} two-dollar coins and {ones} one-dollar coins. How much money is shown?",
            f"Complete the money calculation: ({twos} × $2) + ({ones} × $1) = ___.",
            "Count the value of the $2 coins, then add the value of the $1 coins. What is the total?",
        ]
    else:
        raise ValueError(f"Unknown numeracy template: {template}")

    item["prompt"] = forms[form]
    item["variant_id"] = f"{template}-v{form + 1}"
    item["family"] = f"numeracy-{item['variant_id']}"
    return item
