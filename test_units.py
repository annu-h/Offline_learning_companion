"""
Unit tests for answer_matcher.py
"""
from Python.answer_matcher import match_answer, extract_number, normalize_text, match_choice, match_command

def test_answers():
    # Test numbers
    assert match_answer("four", 4)
    assert match_answer("Four", 4)
    assert match_answer("4", 4)
    assert match_answer("the answer is four", 4)
    assert match_answer("the answer is 4", 4)
    assert match_answer("it is four", 4)
    assert match_answer("twenty one", 21)

    # Test words
    assert match_answer("cat", "cat")
    assert match_answer("the cat", "cat")
    assert match_answer("Cat", "cat")
    assert match_answer("a cat", "cat")
    assert match_answer("it's a cat", "cat")
    assert match_answer("i think it is blue", "blue")

    # Test accepted list
    assert match_answer("3", "three", ["3", "three"])
    assert match_answer("the cow", "cow", ["cow", "the cow"])

    # Test choices
    assert match_choice("i want apple", ["apple", "banana", "orange"]) == "apple"
    assert match_choice("the second one", ["red", "blue", "green"]) == "blue"

    # Test command matching
    cmd_map = {
        "alphabet": ["alphabet", "letters", "abcs"],
        "quiz": ["quiz", "test", "quiz time"],
        "story": ["story", "read a story", "stories"]
    }
    assert match_command("lets learn the alphabet", cmd_map) == "alphabet"
    assert match_command("can we do a quiz please", cmd_map) == "quiz"
    assert match_command("tell me a story", cmd_map) == "story"

    print("All answer matcher tests passed successfully!")

if __name__ == "__main__":
    test_answers()
