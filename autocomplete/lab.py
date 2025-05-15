"""
6.101 Lab:
Autocomplete
"""

# NO ADDITIONAL IMPORTS!

# import string # optional import
# import pprint # optional import
# import typing # optional import
import doctest
from text_tokenize import tokenize_sentences


class PrefixTree:
    """Object that stores the words in terms of prefix relations
    as a Tree"""

    def __init__(self):
        """Method to initiallise the PrefixTree Object"""
        self.value = None
        self.children = {}

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the prefix tree,
        or reassign the associated value if it is already present.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError("Key must be a string")

        current_node = self
        if key == "":
            current_node.value = value
            return

        for char in key:
            if char not in current_node.children:
                current_node.children[char] = PrefixTree()
            current_node = current_node.children[char]
        current_node.value = value

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        Raise a KeyError if the given key doesn't have a value
        """
        if not isinstance(key, str):
            raise TypeError("The input key must be string")

        curr_node = self
        if key == "":
            if self.value is not None:
                return self.value
            else:
                raise KeyError(f"The input key {key} is not in the prefix tree.")

        for char in key:
            if char not in curr_node.children:
                raise KeyError(f"The given {key} is not in the prefix tree")
            # go into the sub_tree
            curr_node = curr_node.children[char]

        if curr_node.value is None:
            raise KeyError(f"The given {key} does not have value in the prefix tree.")

        return curr_node.value

    def __contains__(self, key):
        """
        Is key a key in the prefix tree?  Return True or False.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError("Key should be string")
        try:
            self[key]
            return True
        except KeyError:
            return False

    def __iter__(self, curr_list=None):
        """
        Generator of (key, value) pairs for all keys/values in this prefix tree
        and its children.  Must be a generator!
        """
        if curr_list is None:
            curr_list = []

        ##Base case
        if self.value is not None:
            curr_string = "".join(curr_list)
            yield (curr_string, self.value)

        # recursive case
        for key, sub_node in self.children.items():
            curr_list.append(key)
            yield from sub_node.__iter__(curr_list)
            curr_list.pop(-1)

    def __delitem__(self, key):
        """
        Delete the given key from the prefix tree if it exists.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError("Key should be string")

        curr_node = self
        if key == "":
            if curr_node.value is not None:
                curr_node.value = None
                return
        for char in key:
            if char not in curr_node.children:
                raise KeyError("Given Key not in the Prefix Tree")
            curr_node = curr_node.children[char]
        if curr_node.value is not None:
            curr_node.value = None
        else:
            raise KeyError("Given Key not in the Prefix Tree")

    def __repr__(self):
        """Function to represent the Prefix Tree object,
        if needed."""
        first_string = "{ " + f"{self.value}"
        rest = self.children
        rest_string = ""
        for key, sub_node in rest.items():
            sub_string = "{ " f" {key}: {sub_node.__repr__()}" + " } \n"
            rest_string += sub_string
        return f"{first_string} \n {rest_string}" + " }"


def get_sub_tree(tree, prefix):
    """Given some key value in the Prefix Tree,
    this function returns the sub_tree associated with the prefix
    and raises KeyError otherwise"""
    curr_node = tree
    for char in prefix:
        if char not in curr_node.children:
            raise KeyError("Given prefix is not in the Prefix Tree")
        curr_node = curr_node.children[char]
    return curr_node


def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.
    """
    sentence_strings = tokenize_sentences(text)
    freq_dict = {}
    for sentence in sentence_strings:
        words_list = sentence.split()
        for word in words_list:
            word = word.lower()
            if word not in freq_dict:
                freq_dict[word] = 1
            else:
                freq_dict[word] += 1
    out_tree = PrefixTree()
    for word, frequency in freq_dict.items():
        out_tree[word] = frequency
    return out_tree

##Helper functions for Valid edits 

def valid_inserts(word, tree, seen_words):
    """Returns a dictionary of valid words
    created through inserts"""
    # insert characters
    alphabets = "abcdefghijklmnopqrstuvwxyz"
    valids = {}
    for i in range(len(word) + 1):
        for char in alphabets:
            edits = word[:i] + char + word[i:]
            if edits in valids or edits in seen_words:
                continue
            if edits in tree:
                valids[edits] = tree[edits]
    return valids


def valid_dels(word, tree, seen_words):
    """Returns a dictionary of valid edits
    created through deletion of chars"""
    # character deletions:
    valids = {}
    for i in range(len(word)):
        edits = word[:i] + word[i + 1 :]
        if edits in valids or edits in seen_words:
            continue
        if edits in tree:
            valids[edits] = tree[edits]
    return valids


def valid_replacement(word, tree, seen_words):
    """Returns a dictionary of valid edits
    created through replacement of chars"""
    alphabets = "abcdefghijklmnopqrstuvwxyz"
    valids = {}
    # character replacement:
    for i in range(len(word)):
        for char in alphabets:
            edits = word[:i] + char + word[i + 1 :]
            if edits in valids or edits in seen_words:
                continue
            if edits in tree:
                valids[edits] = tree[edits]
    return valids


def valid_transpose(word, tree, seen_words):
    """Returns a dictionary of valid edits
    created through transpose of chars"""
    valids = {}
    # two character transpose
    for i in range(len(word) - 1):
        edits = word[:i] + word[i + 1] + word[i] + word[i + 2 :]
        if edits in valids or edits in seen_words:
            continue
        if edits in tree:
            valids[edits] = tree[edits]
    return valids


def valid_edits(word, tree, seen_words):
    """Returns a dictionary of valid edits for
    a given word string with corresponding values in the prefix tree
    given"""

    valid_inserts_dict = valid_inserts(word, tree, seen_words)
    valid_dels_dict = valid_dels(word, tree, seen_words)
    valid_replacement_dict = valid_replacement(word, tree, seen_words)
    valid_transpose_dict = valid_transpose(word, tree, seen_words)

    return (
        valid_inserts_dict
        | valid_dels_dict
        | valid_replacement_dict
        | valid_transpose_dict
    )


def autocomplete(tree, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is not a string.
    """
    if not isinstance(prefix, str):
        raise TypeError("Key is not a string")

    max_count_dict = {}
    try:
        sub_tree = get_sub_tree(tree, prefix)
    except KeyError:
        return []

    for key, val in sub_tree:
        full_key = prefix + key
        max_count_dict[full_key] = val

    if max_count is None:
        return sorted(max_count_dict, key=lambda x: max_count_dict[x], reverse=True)
    else:
        return sorted(max_count_dict, key=lambda x: max_count_dict[x], reverse=True)[
            :max_count
        ]


def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    first_max_count = autocomplete(tree, prefix, max_count)
    seen_words = set(first_max_count)
    if max_count is not None:
        if len(first_max_count) == max_count:
            return first_max_count

        if len(first_max_count) < max_count:
            valid_edits_dict = valid_edits(prefix, tree, seen_words)
            selected_edits = sorted(
                valid_edits_dict, key=lambda x: valid_edits_dict[x], reverse=True
            )[: max_count - len(first_max_count)]
            return first_max_count + selected_edits
    else:
        valid_edits_dict = valid_edits(prefix, tree, seen_words)
        selected_edits = sorted(
            valid_edits_dict, key=lambda x: valid_edits_dict[x], reverse=True
        )
        return first_max_count + selected_edits


def word_filter(tree, pattern):
    """
    Return set of (word, value) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    out = set()

    def recursive_filter(node, pattern_id, current_word=""):

        # Base Case:
        if pattern_id == len(pattern):
            if node.value is not None:
                out.add((current_word, node.value))
            return

        curr_char = pattern[pattern_id]

        # Case 1: '*'
        if curr_char == "*":
            # Sub case: Skip '*'
            recursive_filter(node, pattern_id + 1, current_word)

            # Sub case: Search for words
            for char, child_node in node.children.items():
                new_char = current_word + char
                recursive_filter(child_node, pattern_id, new_char)

        # Case 2: '?'
        elif curr_char == "?":
            # search for single characters
            for char, child_node in node.children.items():
                new_char = current_word + char
                recursive_filter(child_node, pattern_id + 1, new_char)

        # Case 3: Regular character
        else:
            if curr_char in node.children:
                child_node = node.children[curr_char]
                new_char = current_word + curr_char
                recursive_filter(child_node, pattern_id + 1, new_char)

    recursive_filter(tree, 0)
    return out


if __name__ == "__main__":
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests
    # doctest.run_docstring_examples( # runs doctests for one function
    #    PrefixTree.__getitem__,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=True
    # )

    # Metamorphosis
    # with open("books/metamorphosis.txt", encoding="utf-8") as f:
    #     text = f.read()
    #     meta_tree = word_frequencies(text)
    #     # max_count_1 = autocomplete(meta_tree, 'gre', max_count=6)
    #     # print(max_count_1)
    #     max_count_2 = word_filter(meta_tree, 'c*h')
    #     print(max_count_2)

    # Pride and Prejudice
    # with open("books/pride_and_prejudice.txt", encoding="utf-8") as f:
    #     text = f.read()
    #     pride_tree = word_frequencies(text)
    #     max_counts = autocorrect(pride_tree, 'hear', flush = False)
    #     print(max_counts)

    # Tale of Two Cities
    # with open("books/a_tale.txt", encoding="utf-8") as f:
    #     text = f.read()
    #     tale_tree = word_frequencies(text)
    #     max_counts = word_filter(tale_tree, 'r?c*t')
    #     print(max_counts)

    # Alice in wonderland
    # with open("books/alice_in_wonderland.txt", encoding="utf-8") as f:
    #     text = f.read()
    #     alice_tree = word_frequencies(text)
    #     max_counts = autocorrect(alice_tree, 'hear', max_count=12)
    #     print(max_counts)

    # #Dracula
    # with open("books/dracula.txt", encoding="utf-8") as f:
    #     text = f.read()
    #     bram_tree = word_frequencies(text)
    #     # print(len(set(bram_tree)))
    #     #summing up total words
    #     sum = 0
    #     for key, val in bram_tree:
    #         sum += val
    #     print(sum)

    # t = PrefixTree()
    # t['bat'] = True
    # t['bate'] = 2
    # t
