from signature import make_signature


def test_basic_word():
    assert make_signature("eat") == "aet"


def test_uppercase():
    assert make_signature("EAT") == "aet"


def test_mixed_case():
    assert make_signature("Listen") == "eilnst"


def test_single_char():
    assert make_signature("a") == "a"


def test_anagram_pair_produces_same_key():
    assert make_signature("eat") == make_signature("tea")


def test_all_same_letters():
    assert make_signature("aaa") == "aaa"


def test_longer_word():
    assert make_signature("triangle") == make_signature("relating")
