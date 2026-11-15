"""Easy read splits a problem into sentences and moves the question last. All examples
here are invented: no dataset text in a committed file."""

import re

import pytest

from student_app.easy_read import easy_read, sentences

CASES = {
    "plain": "Anna has 3 apples. How many does she have after eating one? She is 10.",
    "decimals": "A rope is 3.5 m long. Another is 1.000 mm and a third 2,5 m. Which is longest?",
    "abbreviations": "Use coins, e.g. of 2 cents, i.e. small ones, etc. and count. "
    "Fig. 3 shows 5 cm. of tape and 2 km. of road in 4 min. flat. What is núm. 7?",
    "catalan": "Tria un nombre, p. ex. el 4. Quin és el doble?",
    "brackets": "Pere asks (is it even?) and waits. Marta says “No. It is odd.” What is it?",
    "quotes": 'The sign says "Stop. Wait." in red. Who reads it?',
    "ellipsis": "The numbers go 2, 4, 6... and so on. What comes after 10?",
    "list": "Follow the steps:\n1. Add 2.\n2. Double it.\nWhat do you get from 5?",
    "no_question": "Draw a square. Colour half of it.",
    "spanish": "Luis tiene 12 canicas. ¿Cuántas le quedan si pierde 5? Juega cada día.",
}


def tokens(text):
    return sorted(re.findall(r"\S+", text))


@pytest.mark.parametrize("name", CASES)
def test_nothing_is_lost(name):
    assert tokens(easy_read(CASES[name])) == tokens(CASES[name])


def test_one_sentence_per_line_and_the_question_last():
    assert easy_read(CASES["plain"]) == (
        "Anna has 3 apples.\nShe is 10.\n\nHow many does she have after eating one?"
    )
    assert easy_read(CASES["spanish"]) == (
        "Luis tiene 12 canicas.\nJuega cada día.\n\n¿Cuántas le quedan si pierde 5?"
    )


def test_numbers_and_abbreviations_do_not_split():
    assert sentences(CASES["decimals"]) == [
        "A rope is 3.5 m long.",
        "Another is 1.000 mm and a third 2,5 m.",
        "Which is longest?",
    ]
    assert len(sentences(CASES["abbreviations"])) == 3
    assert sentences(CASES["catalan"]) == ["Tria un nombre, p. ex. el 4.", "Quin és el doble?"]


def test_brackets_quotes_and_ellipsis_do_not_split():
    assert sentences(CASES["brackets"]) == [
        "Pere asks (is it even?) and waits.",
        "Marta says “No. It is odd.” What is it?",
    ]
    assert sentences(CASES["quotes"]) == ['The sign says "Stop. Wait." in red.', "Who reads it?"]
    assert sentences(CASES["ellipsis"]) == [
        "The numbers go 2, 4, 6... and so on.",
        "What comes after 10?",
    ]


def test_existing_lines_and_numbered_steps_stay():
    assert easy_read(CASES["list"]) == (
        "Follow the steps:\n1. Add 2.\n2. Double it.\n\nWhat do you get from 5?"
    )


def test_without_a_question_only_the_lines_change():
    assert easy_read(CASES["no_question"]) == "Draw a square.\nColour half of it."


@pytest.mark.parametrize(
    "text", ["", "One sentence only.", "A (broken bracket. Here?", 'A "b. C?']
)
def test_text_that_cannot_be_split_comes_back_unchanged(text):
    assert easy_read(text) == text
