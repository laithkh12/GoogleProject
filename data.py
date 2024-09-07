
import os
import re
import pickle
from utils import clean_line
from AutoCompleteData import AutoCompleteData
import Levenshtein
import threading
from queue import Queue

def find_words_one_letter_diff(word, word_list):
    """
    Finds words in the given list that have exactly one letter difference from the input word,
    allowing for one character addition or removal.

    :param word: The input word to compare.
    :param word_list: A list of words to search through.
    :return: A list of words with exactly one letter difference.
    """
    results = []

    for node in word_list:
        candidate = node.word
        len_word = len(word)
        len_candidate = len(candidate)

        if abs(len_word - len_candidate) <= 1:
            # Check if words differ by exactly one substitution or one addition/removal
            if len_word == len_candidate:
                # Same length: check for single substitution
                diff_count = sum(c1 != c2 for c1, c2 in zip(word, candidate))
                if diff_count == 1:
                    results.append(node)
            elif len_word + 1 == len_candidate:
                # Candidate is longer by one character: check for single addition
                for i in range(len_candidate):
                    if word == candidate[:i] + candidate[i + 1:]:
                        results.append(node)
                        break
            elif len_word == len_candidate + 1:
                # Word is longer by one character: check for single removal
                for i in range(len_word):
                    if candidate == word[:i] + word[i + 1:]:
                        results.append(node)
                        break

    return results


class FileSentencesArray:
    def __init__(self, filepath, stripped_sentences):
        self.filepath = filepath
        self.stripped_sentences = stripped_sentences


class SentencesData:
    def __init__(self, index, sentences_indices):
        self.file_index = index
        self._indices_array = sentences_indices


class WordNode:
    def __init__(self, word):
        self.word = word
        self.sentences_data_arr = []
        self.left = None
        self.right = None


class WordNode:
    def __init__(self, word):
        self.word = word
        self.left = None
        self.right = None
        self.sentences_data_arr = []


class WordBST:
    def __init__(self):
        self.root = None

    def insert(self, word, sentences_data):
        if self.root is None:
            self.root = WordNode(word)
            self.root.sentences_data_arr.append(sentences_data)
        else:
            self._insert_recursive(self.root, word, sentences_data)

    def _insert_recursive(self, node, word, sentences_data):
        if word < node.word:
            if node.left is None:
                node.left = WordNode(word)
                node.left.sentences_data_arr.append(sentences_data)
            else:
                self._insert_recursive(node.left, word, sentences_data)
        elif word > node.word:
            if node.right is None:
                node.right = WordNode(word)
                node.right.sentences_data_arr.append(sentences_data)
            else:
                self._insert_recursive(node.right, word, sentences_data)
        else:
            node.sentences_data_arr.append(sentences_data)

    def search(self, word):
        node = self._search_recursive(self.root, word)
        if node is not None:
            return iter(node.sentences_data_arr)
        return iter([])

    def _search_recursive(self, node, word):
        if node is None:
            return None
        if word == node.word:
            return node
        elif word < node.word:
            return self._search_recursive(node.left, word)
        else:
            return self._search_recursive(node.right, word)

    def __iter__(self):
        yield from self._in_order_traversal(self.root)

    def _in_order_traversal(self, node):
        if node is not None:
            yield from self._in_order_traversal(node.left)
            yield node
            yield from self._in_order_traversal(node.right)

    def search(self, word):
        return self._search_recursive(self.root, word)

    def _search_recursive(self, node, word):
        if node is None:
            return None
        if word == node.word:
            return node
        elif word < node.word:
            return self._search_recursive(node.left, word)
        else:
            return self._search_recursive(node.right, word)


class Words:
    def __init__(self, words, files):
        self.words_tree = words
        self.files_arr = files

    def get_sentences(self, word):
        node = self.words_tree.search(word)

        nodes = []
        if node is None:
            nodes = find_words_one_letter_diff(word, self.words_tree)
            if len(nodes) == 0: return []
        else:
            nodes = [node]

        sentences = []
        for node in nodes:
            for sentence_data in node.sentences_data_arr:
                file_obj = self.files_arr[sentence_data.file_index]
                filepath = file_obj.filepath
                filename = os.path.basename(filepath)

                for sentence_index in sentence_data._indices_array:
                    original_sentence = file_obj.stripped_sentences[sentence_index]
                    completed_sentence = original_sentence
                    source_text = [filepath, filename]
                    offset = sentence_index
                    score = 0

                    autocomplete_data = AutoCompleteData(
                        completed_sentence=completed_sentence,
                        source_text=source_text,
                        offset=offset,
                        score=score
                    )
                    sentences.append(autocomplete_data)

        return sentences


def process_files_in_directory(directory, *extensions):
    file_sentences_objects = []

    if not extensions:
        extensions = ('.txt',)

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(extensions):
                filepath = os.path.join(root, file)

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        stripped_sentences = [
                            clean_line(line) for line in f.readlines() if len(clean_line(line)) >= 5
                        ]
                except UnicodeDecodeError:
                    with open(filepath, 'r', encoding='latin-1') as f:
                        stripped_sentences = [
                            clean_line(line) for line in f.readlines() if len(clean_line(line)) >= 5
                        ]

                file_sentences_array = FileSentencesArray(filepath, stripped_sentences)
                file_sentences_objects.append(file_sentences_array)

    return file_sentences_objects


def get_words_set(files_array):
    word_set = set()

    for file_array in files_array:
        for sentence in file_array.stripped_sentences:
            words = set(sentence.lower().split())
            word_set.update(words)

    return word_set


def init_words(dir_path, *extensions, pickle_path='words_data.pkl'):
    if os.path.exists(pickle_path):
        with open(pickle_path, 'rb') as f:
            words_obj = pickle.load(f)
        return words_obj

    if not extensions:
        extensions = (".txt",)  # Default value if no extensions are passed

    files_array = process_files_in_directory(dir_path, *extensions)
    words_tree = WordBST()

    for file_index, file_obj in enumerate(files_array):
        for word in get_words_set([file_obj]):
            word_pattern = re.compile(rf'\b{re.escape(word)}\b')
            indices = [
                index for index, line in enumerate(file_obj.stripped_sentences) if word_pattern.search(line)
            ]
            if indices:
                sentences_data = SentencesData(file_index, indices)
                words_tree.insert(word, sentences_data)

    words_obj = Words(words_tree, files_array)

    # Save the tree and associated data for future runs
    with open(pickle_path, 'wb') as f:
        pickle.dump(words_obj, f)

    return words_obj