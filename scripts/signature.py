def make_signature(word: str) -> str:
    """Return the canonical anagram key for a word.

    Two words are anagrams if and only if they share the same signature.
    The signature is the word lowercased and its characters sorted alphabetically.

    Examples:
        make_signature("eat")    -> "aet"
        make_signature("Tea")    -> "aet"
        make_signature("listen") -> "eilnst"
    """
    return "".join(sorted(word.lower()))
