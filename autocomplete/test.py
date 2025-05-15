"""
6.101 Lab:
Autocomplete
"""

#!/usr/bin/env python3
import os.path
import lab
import json
import types
import pickle

import sys
sys.setrecursionlimit(10000)

import pytest

TEST_DIRECTORY = os.path.dirname(__file__)


# convert prefix tree into a dictionary...
def dictify(t):
    assert set(t.__dict__) == {'value', 'children'}, "PrefixTree instances should only contain the two instance attributes mentioned in the lab writeup."
    out = {'value': t.value, 'children': {}}
    for ch, child in t.children.items():
        out['children'][ch] = dictify(child)
    return out

# ...and back
def from_dict(d):
    t = lab.PrefixTree()
    for k, v in d.items():
        t[k] = v
    return t

# make sure the keys are not explicitly stored in any node
def any_key_stored(tree, keys):
    keys = [tuple(k) for k in keys]
    for i in dir(tree):
        try:
            val = tuple(getattr(tree, i))
        except:
            continue
        for j in keys:
            if j == val:
                return repr(i), repr(j)
    for child in tree.children:
        if len(child) != 1:
            return repr(child), repr(child)
    for child in tree.children.values():
        key_stored = any_key_stored(child, keys)
        if key_stored:
            return key_stored
    return None

# read in expected result
def read_expected(fname):
    with open(os.path.join(TEST_DIRECTORY, 'testing_data', fname), 'rb') as f:
        return pickle.load(f)

def test_set():
    t = lab.PrefixTree()
    t['cat'] = 'kitten'
    t['car'] = 'tricycle'
    t['carpet'] = 'rug'
    expect = read_expected('1.pickle')
    assert dictify(t) == expect, "Your prefix tree is incorrect."
    assert any_key_stored(t, ('cat', 'car', 'carpet')) is None

    t = lab.PrefixTree()
    t['a'] = 1
    t['an'] = 1
    t['ant'] = 0
    t['anteater'] = 1
    t['ants'] = 1
    t['a'] = 2
    t['an'] = 2
    t['a'] = 3
    expect = read_expected('2.pickle')
    assert dictify(t) == expect, "Your prefix tree is incorrect."
    assert any_key_stored(t, ('an', 'ant', 'anteater', 'ants')) is None
    with pytest.raises(TypeError):
        t[(1, 2, 3)] = 20

    t = lab.PrefixTree()
    t['man'] = ''
    t['mat'] = 'object'
    t['mattress'] = ()
    t['map'] = 'pam'
    t['me'] = 'you'
    t['met'] = 'tem'
    t['a'] = '?'
    t['map'] = -1000
    expect = read_expected('3.pickle')
    assert dictify(t) == expect, "Your prefix tree is incorrect."
    assert any_key_stored(t, ('man', 'mat', 'mattress', 'map', 'me', 'met', 'map')) is None
    with pytest.raises(TypeError):
        t['something',] = 'pam'

    t = lab.PrefixTree()
    t[''] = 'hello'
    expected = {'value': "hello", 'children': {}}
    assert dictify(t) == expected, "Your prefix tree is incorrect."


def test_get():
    d = {'name': 'John', 'favorite_numbers': [2, 4, 3], 'age': 39, 'children': 0}
    t = from_dict(d)
    assert dictify(t) == read_expected('person.pickle')
    for k in d:
        assert t[k] == d[k], f'Expected key {repr(k)} to have value {repr(d[k])}, got {repr(t[k])}'

    assert any_key_stored(t, tuple(d)) is None
    t[''] = 5
    assert t[''] == 5

    c = {'make': 'Toyota', 'model': 'Corolla', 'year': 2006, 'color': 'beige', 'storage space': ''}
    t = from_dict(c)
    assert dictify(t) == read_expected('car.pickle')
    assert all(t[k] == c[k] for k in c)
    assert any_key_stored(t, tuple(c)) is None
    for i in ('these', 'keys', 'dont', 'exist', 'storage'):
        with pytest.raises(KeyError):
            x = t[i]
    with pytest.raises(TypeError):
        x = t[(1, 2, 3)]


def test_contains():
    d = {'name': 'John', 'favorite_numbers': [2, 4, 3], 'age': 39, 'children': 0}
    t = from_dict(d)
    assert dictify(t) == read_expected('person.pickle')
    for k in d:
        assert k in t, f'Expected key {repr(k)} to be in tree!'

    with pytest.raises(TypeError):
        (1, 2, 3) in t

    c = {'make': 'Toyota', 'model': 'Corolla', 'year': 2006, 'color': 'beige', 'storage space': ''}
    t = from_dict(c)
    assert dictify(t) == read_expected('car.pickle')
    for k in c:
        assert k in t, f'Expected key {repr(k)} to be in tree!'


    badkeys = ('these', 'keys', 'dont', 'exist', 'm', 'ma', 'mak', 'mo',
               'mod', 'mode', 'ye', 'yea', 'y', '', 'car.pickle',)
    for k in badkeys:
        assert k not in t, f'key {repr(k)} should not be in tree!'

    assert '' not in t  # this key has no value in the tree

    t[''] = 0
    assert '' in t      # now it should have a value


def test_iter():
    t = lab.PrefixTree()
    t['man'] = ''
    t['mat'] = 'object'
    t['mattress'] = ()
    t['map'] = 'pam'
    t['me'] = 'you'
    t['met'] = 'tem'
    t['a'] = '?'
    t['map'] = -1000
    assert isinstance(iter(t), types.GeneratorType), "__iter__ must produce a generator"
    expected = [('a', '?'), ('man', ''), ('map', -1000), ('mat', 'object'),
                ('mattress', ()), ('me', 'you'), ('met', 'tem')]
    assert sorted(list(t)) == expected

    t = lab.PrefixTree()
    t[''] = ()
    t['a'] = 0
    t['ab'] = set()
    t['abc'] = []
    t['abcd'] = ''
    t['abcde'] = False
    t['ad'] = True
    expected = [('', ()), ('a', 0), ('ab', set()), ('abc', []), ('abcd', ''),
                ('abcde', False), ('ad', True)]
    assert isinstance(iter(t), types.GeneratorType), "__iter__ must produce a generator"
    assert sorted(list(t)) == expected



def test_delete():
    c = {'make': 'Toyota', 'model': 'Corolla', 'year': 2006, 'color': 'beige', 'storage space': ''}
    t = from_dict(c)
    assert dictify(t) == read_expected('car.pickle')
    del t['color']
    assert isinstance(iter(t), types.GeneratorType), "__iter__ must produce a generator"
    with pytest.raises(KeyError):
        del t['color'] # can't delete again
    assert set(t) == set(c.items()) - {('color', 'beige')}
    t['color'] = 'silver'  # new paint job
    for i in t:
        if i[0] != 'color':
            assert i in c.items()
        else:
            assert i[1] == 'silver'

    for i in ('cat', 'dog', 'ferret', 'tomato'):
        with pytest.raises(KeyError):
            del t[i]

    with pytest.raises(TypeError):
        del t[1,2,3]

    t = lab.PrefixTree()
    t['man'] = ''
    t['mat'] = 'object'
    t['mattress'] = ()
    t['map'] = 'pam'
    t['me'] = 'you'
    t['met'] = 'tem'
    t['a'] = '?'
    t['map'] = -1000
    t[''] = 500
    assert isinstance(iter(t), types.GeneratorType), "__iter__ must produce a generator"
    expected = [('', 500), ('a', '?'), ('man', ''), ('map', -1000),
                ('mat', 'object'), ('mattress', ()), ('me', 'you'), ('met', 'tem')]
    assert sorted(list(t)) == expected
    del t['mat']
    del t['']
    expected = [('a', '?'), ('man', ''), ('map', -1000),
                ('mattress', ()), ('me', 'you'), ('met', 'tem')]
    assert sorted(list(t)) == expected



def test_word_frequencies():
    # small test
    l = lab.word_frequencies('toonces was a cat who could drive a car very fast until he crashed.')
    assert dictify(l) == read_expected('6.pickle')

    l = lab.word_frequencies('a man at the market murmered that he had met a mermaid. '
                           'mark didnt believe the man had met a mermaid.')
    assert dictify(l) == read_expected('7.pickle')

    l = lab.word_frequencies('what happened to the cat who had eaten the ball of yarn?  she had mittens!')
    assert dictify(l) == read_expected('8.pickle')



@pytest.mark.parametrize('bigtext', ['holmes', 'earnest', 'frankenstein'])
def test_big_corpora(bigtext):
    with open(os.path.join(TEST_DIRECTORY, 'testing_data', '%s.txt' % bigtext), encoding='utf-8') as f:
        text = f.read()
        w = lab.word_frequencies(text)

        w_e = read_expected('%s_words.pickle' % bigtext)

        assert w_e == dictify(w), 'word frequencies prefix tree does not match for %s' % bigtext


def test_autocomplete_small():
    # Autocomplete on simple prefix trees with less than N valid words
    t = lab.word_frequencies("cat car carpet")
    result = lab.autocomplete(t, 'car', 3)
    assert set(result) == {"car", "carpet"}

    t = lab.word_frequencies("a an ant anteater a an ant a")
    result = lab.autocomplete(t, 'a', 2)
    assert set(result) in [{"a", "an"}, {"a", "ant"}]

    t = lab.word_frequencies("man mat mattress map me met a man a a a map man met")
    result = lab.autocomplete(t, 'm', 3)
    assert set(result) == {"man", "map", "met"}

    t = lab.word_frequencies("hello helm history")
    result = lab.autocomplete(t, 'help', 3)
    assert result == []
    with pytest.raises(TypeError):
        result = lab.autocomplete(t, ('tuple', ), None)


def test_autocomplete_big_1():
    alphabet = a = "abcdefghijklmnopqrstuvwxyz"

    word_list = ["aa" + l1 + l2 + l3 + l4 for l1 in a for l2 in a for l3 in a for l4 in a]
    word_list.extend(["apple", "application", "apple", "apricot", "apricot", "apple"])
    word_list.append("bruteforceisbad")

    t = lab.word_frequencies(' '.join(word_list))
    for i in range(50_000):
        result1 = lab.autocomplete(t, 'ap', 1)
        result2 = lab.autocomplete(t, 'ap', 2)
        result3 = lab.autocomplete(t, 'ap', 3)
        result4 = lab.autocomplete(t, 'ap')
        result5 = lab.autocomplete(t, 'b')

        assert set(result1) == {'apple'}
        assert set(result2) == {'apple', 'apricot'}
        assert set(result4) == set(result3) == {'apple', 'apricot', 'application'}
        assert set(result5) == {'bruteforceisbad'}


def test_autocomplete_big_2():
    nums = {'t': [0, 1, 25, None],
            'th': [0, 1, 21, None],
            'the': [0, 5, 21, None],
            'thes': [0, 1, 21, None]}
    with open(os.path.join(TEST_DIRECTORY, 'testing_data', 'frankenstein.txt'), encoding='utf-8') as f:
        text = f.read()
    w = lab.word_frequencies(text)
    for i in sorted(nums):
        for n in nums[i]:
            result = lab.autocomplete(w, i, n)
            expected = read_expected('frank_autocomplete_%s_%s.pickle' % (i, n))
            assert len(expected) == len(result), ('missing' if len(result) < len(expected) else 'too many') + ' autocomplete results for ' + repr(i) + ' with maxcount = ' + str(n)
            assert set(expected) == set(result), 'autocomplete included ' + repr(set(result) - set(expected)) + ' instead of ' + repr(set(expected) - set(result)) + ' for ' + repr(i) + ' with maxcount = '+str(n)
    with pytest.raises(TypeError):
        result = lab.autocomplete(w, ('tuple', ), None)


def test_autocomplete_big_3():
    with open(os.path.join(TEST_DIRECTORY, 'testing_data', 'frankenstein.txt'), encoding='utf-8') as f:
        text = f.read()
    w = lab.word_frequencies(text)
    the_word = 'accompany'
    for ix in range(len(the_word)+1):
        test = the_word[:ix]
        result = lab.autocomplete(w, test)
        expected = read_expected('frank_autocomplete_%s_%s.pickle' % (test, None))
        assert len(expected) == len(result), ('missing' if len(result) < len(expected) else 'too many') + ' autocomplete results for ' + repr(test) + ' with maxcount = ' + str(None)
        assert set(expected) == set(result), 'autocomplete included ' + repr(set(result) - set(expected)) + ' instead of ' + repr(set(expected) - set(result)) + ' for ' + repr(test) + ' with maxcount = '+str(None)
    with pytest.raises(TypeError):
        result = lab.autocomplete(w, ('tuple', ), None)


def test_autocorrect_small_1():
    # Autocorrect on cat in small text
    t = lab.word_frequencies("cats cattle hat car act at chat crate act car act")
    result = lab.autocorrect(t, 'cat',4)
    assert set(result) == {"act", "car", "cats", "cattle"}
    result = lab.autocorrect(t, 'cat')
    assert set(result) == {"act", "car", "cats", "cattle", "chat", "at", "hat"}


def test_autocorrect_small_2():
    # Autocorrect on ant in small text
    t = lab.word_frequencies("a art at art at art anteater ants ants ants ants")
    result = lab.autocorrect(t, 'ant')
    assert set(result) == {"anteater", "art", "at", "ants"}
    assert len(result) == 4

    # take the autocompletions first
    result = lab.autocorrect(t, 'ant', 2)
    assert set(result) == {"anteater", "ants"}
    assert len(result) == 2

    # take completions then fill remaining slots with edits sorted by frequency
    result = lab.autocorrect(t, 'ant', 3)
    assert set(result) == {"anteater", "ants", "art"}
    assert len(result) == 3


def test_autocorrect_big():
    nums = {'thin': [0, 8, 10, None],
            'tom': [0, 2, 4, None],
            'mon': [0, 2, 15, 17, 20, None]}
    with open(os.path.join(TEST_DIRECTORY, 'testing_data', 'frankenstein.txt'), encoding='utf-8') as f:
        text = f.read()
    w = lab.word_frequencies(text)
    #print(f'dmon in the prefix tree: {'dmon' in w}', flush = True)
    for i in sorted(nums):
        for n in nums[i]:
            result = lab.autocorrect(w, i, n)
            expected = read_expected('frank_autocorrect_%s_%s.pickle' % (i, n))
            assert len(expected) == len(result), ('missing' if len(result) < len(expected) else 'too many') + ' autocorrect results for ' + repr(i) + ' with maxcount = ' + str(n)
            assert set(expected) == set(result), 'autocorrect included ' + repr(set(result) - set(expected)) + ' instead of ' + repr(set(expected) - set(result)) + ' for ' + repr(i) + ' with maxcount = '+str(n)

def test_filter_word():
    # words can contain any characters
    t = lab.word_frequencies("1 man mat mattress map me met a man a a a map man met")
    # select specific words from the prefix tree
    result = lab.word_filter(t, 'a')
    assert isinstance(result, set)
    assert result == {("a", 4)}

    result = lab.word_filter(t, '1')
    assert isinstance(result, set)
    assert result == {("1", 1)}

    result = lab.word_filter(t, 'me')
    assert isinstance(result, set)
    assert result == {("me", 1)}

    result = lab.word_filter(t, 'mattress')
    assert isinstance(result, set)
    assert result == {("mattress", 1)}

    # patterns that don't exist in the prefix tree
    result = lab.word_filter(t, 'mattresses')
    assert isinstance(result, set)
    assert result == set()

    result = lab.word_filter(t, 'ma')
    assert isinstance(result, set)
    assert result == set()

    result = lab.word_filter(t, '!')
    assert isinstance(result, set)
    assert result == set()

    result = lab.word_filter(t, 'wh' + 'ee'*6_000)
    assert isinstance(result, set)
    assert result == set()

    # handle empty word?
    result = lab.word_filter(t, '')
    assert isinstance(result, set)
    assert result == set()

    t[''] = 5
    result = lab.word_filter(t, '')
    assert isinstance(result, set)
    assert result == {('', 5)}


def test_filter_question():
    t = lab.word_frequencies("I met a man with a mat who followed a map. The map led to more maps, 5 cats, and a bat.")
    # patterns that exist
    result = lab.word_filter(t, '?')
    assert isinstance(result, set)
    assert result == {("5", 1), ("a", 4), ("i", 1)}

    result = lab.word_filter(t, 'ma?')
    assert isinstance(result, set)
    assert result == {("man", 1), ("map", 2), ("mat", 1)}

    result = lab.word_filter(t, '???s')
    assert isinstance(result, set)
    assert result == {("cats", 1), ("maps", 1)}

    result = lab.word_filter(t, '??t')
    assert isinstance(result, set)
    assert result == {('bat', 1), ('mat', 1), ('met', 1)}


    result = lab.word_filter(t, '???')
    assert isinstance(result, set)
    assert result == {('and', 1), ('bat', 1), ('led', 1), ('man', 1),
                      ('map', 2), ('mat', 1), ('met', 1), ('the', 1),
                      ('who', 1)}

    # non-existent patterns
    result = lab.word_filter(t, 'mat?')
    assert isinstance(result, set)
    assert result == set()

    result = lab.word_filter(t, 'ca?')
    assert isinstance(result, set)
    assert result == set()

    result = lab.word_filter(t, 't??????????')
    assert isinstance(result, set)
    assert result == set()

    result = lab.word_filter(t, 'i?')
    assert isinstance(result, set)
    assert result == set()

    result = lab.word_filter(t, '?o?')
    assert isinstance(result, set)
    assert result == set()

    result = lab.word_filter(t, 'm'+'?'*11_000)
    assert isinstance(result, set)
    assert result == set()

def test_filter_small():
    # Filter to select all words in prefix tree
    t = lab.word_frequencies("man mat mattress map me met a man a a a map man met")
    result = lab.word_filter(t, '*')
    assert isinstance(result, set)
    assert result == {("a", 4), ("man", 3), ("map", 2), ("mat", 1), ("mattress", 1), ("me", 1), ("met", 2)}

    # All three-letter words
    result = lab.word_filter(t, '???')
    assert isinstance(result, set)
    assert result == {("man", 3), ("map", 2), ("mat", 1), ("met", 2)}

    # Words beginning with 'mat'
    result = lab.word_filter(t, 'mat*')
    assert isinstance(result, set)
    assert result == {("mat", 1), ("mattress", 1)}

    # Words beginning with 'm', third letter is t
    result = lab.word_filter(t, 'm?t*')
    assert isinstance(result, set)
    assert result == {("mat", 1), ("mattress", 1), ("met", 2)}

    # Words with at least 4 letters
    result = lab.word_filter(t, '*????')
    assert isinstance(result, set)
    assert result == {("mattress", 1)}

    # All words
    result = lab.word_filter(t, '**')
    assert isinstance(result, set)
    assert result == {("a", 4), ("man", 3), ("map", 2), ("mat", 1), ("mattress", 1), ("me", 1), ("met", 2)}


def test_filter_big_1():
    alphabet = a = "abcdefghijklmnopqrstuvwxyz"

    word_list = ["aa" + l1 + l2 + l3 + l4 for l1 in a for l2 in a for l3 in a for l4 in a]
    word_list.extend(["apple", "application", "apple", "apricot", "apricot", "apple"])
    word_list.append("bruteforceisbad")

    t = lab.word_frequencies(' '.join(word_list))
    for i in range(1000):
        result = lab.word_filter(t, "ap*")
        expected = {('apple', 3), ('apricot', 2), ('application', 1)}
        assert len(expected) == len(result), 'incorrect word_filter of ap*'
        assert expected == result, 'incorrect word_filter of ap*'


def test_filter_big_2():
    patterns = ('*ing', '*ing?', '****ing', '**ing**', '????', 'mon*',
                '*?*?*?*', '*???')
    with open(os.path.join(TEST_DIRECTORY, 'testing_data', 'frankenstein.txt'), encoding='utf-8') as f:
        text = f.read()
    w = lab.word_frequencies(text)
    for ix, i in enumerate(patterns):
        result = lab.word_filter(w, i)
        expected = read_expected('frank_filter_%s.pickle' % (ix, ))
        assert len(expected) == len(result), 'incorrect word_filter of %r' % i
        assert set(expected) == result, 'incorrect word_filter of %r' % i
