"""Keep Part III teaching copy consistent across H5P and standalone pages.

Run this file after changing the III.A or III.B authoring packages. III.E and
III.F call ``revise_content`` from their existing builder.
"""

import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "part_III"

# Each note connects this page to the preceding step and explains why the
# learner is being asked to use that step. Keep the notes brief and avoid
# disclosing the answers to the checks that follow them.
PAGE_NOTES = {
    "III_A_Q7_Counting_Names": [
        "Before counting anything, decide what counts as one unit. A tuple item, a character, and a name part give different counts, so choosing the unit first helps you select an operation that measures the right thing.",
        "Now keep the tuple's two fields apart before working with the names inside them. This preserves the boundary between first and last names when the printed full name alone cannot show it.",
        "With the fields separated, compare a few small examples before choosing a counting operation. The pattern you find should explain both a one-part name and a name with several parts.",
        "Once you can count each field, turn those counts into a message. Checking the fields separately keeps each wording choice tied to its own count.",
        "Bring the unit choice, counting rule, and wording together in your own function. Predicting several outputs before running code helps reveal which part of the plan needs correction.",
    ],
    "III_B_Q7_Tens_Digit": [
        "First decide which digit the result should represent, then choose a way to reach it. Starting with examples makes it easier to see why an index must be measured from the right.",
        "Now compare numbers with different lengths using the diagrams you started. Look for a position that still identifies the tens digit when another digit is added on the left.",
        "The position you found works only when that position exists. Checking short inputs before indexing lets your function follow the exercise's rule without an indexing error.",
        "After deciding when indexing is safe, trace the value through each conversion. This helps you distinguish a minus sign from a digit and a string character from the required integer result.",
        "Combine the position, missing-digit check, and type conversion in one plan. Test inputs that exercise each branch, including 100, before trying the optional float extension.",
    ],
    "III_E_Q1_Reversing_Sequences": [
        "Before choosing slice syntax, locate the items you want to visit. Separating positions from direction will make the later boundary choices easier to explain.",
        "Now use the position diagram to compare two slices that differ at one boundary. Changing one thing at a time shows what the stop value excludes and what type the slice returns.",
        "After checking the boundaries, change the step while keeping the endpoints in view. Tracing visited positions explains why a slice can move toward its stop or return nothing.",
        "The previous trace may leave an edge item behind. Compare a written stop with an omitted stop so you can explain how to reach the entire sequence in reverse.",
        "Use the boundary and step rules you discovered to make a slice that works for any length. Testing values and types on small inputs checks the whole requirement, not just the order.",
    ],
    "III_F_Q4_Removing_Parentheticals": [
        "Start by deciding which outside words must survive. A target result gives you something to check against before you choose positions or edit the string.",
        "Now locate the punctuation around the material to remove. Using exact positions keeps repeated words outside the parentheses from being removed by mistake.",
        "The boundary slices may still contain spaces from both sides of the gap. Inspecting those pieces before joining them explains why a correct deletion can still produce the wrong spacing.",
        "Once one parenthetical is removed, ask whether the old positions still identify the same characters. Rechecking this before the next removal helps preserve text between separate pairs.",
        "Combine boundary search, joining, and repetition in a plan you can test. Edge cases show whether the plan preserves outside text and avoids extra spaces.",
    ],
}


def revise_content(stem, book):
    """Add the page notes and the two wording fixes, without duplicating them."""
    notes = PAGE_NOTES[stem]
    assert len(book["chapters"]) == len(notes) == 5
    for chapter, note in zip(book["chapters"], notes):
        units = chapter["params"]["content"]
        text = units[0]["content"]["params"]["text"]
        note_html = f'<p class="part-iii-rationale">{note}</p>'
        text, count = re.subn(
            r"(<h2>.*?</h2>)(?:<p class=\"part-iii-rationale\">.*?</p>)?",
            lambda match: match[1] + note_html,
            text,
            count=1,
            flags=re.S,
        )
        assert count == 1
        units[0]["content"]["params"]["text"] = text

    if stem == "III_B_Q7_Tens_Digit":
        checks = book["chapters"][4]["params"]["content"]
        question = checks[1]["content"]["params"]
        old = "What should your integer function return for <code>100</code>?"
        new = ("For the input <code>100</code>, what integer should "
               "<code>extract_tens_digit()</code> return as the tens digit?")
        assert old in question["question"] or new in question["question"]
        question["question"] = question["question"].replace(old, new)
    elif stem == "III_E_Q1_Reversing_Sequences":
        checks = book["chapters"][1]["params"]["content"]
        question = checks[2]["content"]["params"]
        old = 'For <code>items = ("oak", "elm", "ash")</code>, what is the type of <code>items[1:2]</code>?'
        new = ('For <code>items = ("oak", "elm", "ash")</code>, what is the type of '
               'the value returned by <code>items[1:2]</code>? Answer for the entire slice result, '
               'not for the item inside it.')
        assert old in question["question"] or new in question["question"]
        question["question"] = question["question"].replace(old, new)
    return book


def sync_package_and_page(stem):
    package = OUT / f"{stem}.h5p"
    page = OUT / f"{stem}.html"
    with zipfile.ZipFile(package) as src:
        entries = [(info, src.read(info.filename)) for info in src.infolist()]
    book = json.loads(next(data for info, data in entries if info.filename == "content/content.json"))
    revise_content(stem, book)
    replacement = json.dumps(book, ensure_ascii=False).encode("utf-8")
    with zipfile.ZipFile(package, "w") as dest:
        for info, data in entries:
            dest.writestr(info, replacement if info.filename == "content/content.json" else data)

    html = page.read_text()
    marker = "H5PIntegration = "
    start = html.index(marker) + len(marker)
    integration, consumed = json.JSONDecoder().raw_decode(html[start:])
    for content in integration["contents"].values():
        content["jsonContent"] = json.dumps(book, ensure_ascii=False)
    html = html[:start] + json.dumps(integration, ensure_ascii=False).replace("</", "<\\/") + html[start + consumed:]
    page.write_text(html)


if __name__ == "__main__":
    for name in ("III_A_Q7_Counting_Names", "III_B_Q7_Tens_Digit"):
        sync_package_and_page(name)
