import re
import string

SENTENCE = []
DIFFERENCE = 0


class AutoCompleteData:
    """
    A class to process and save data

    Attributes:
        completed_sentence(str) : the sentence without spacing and punctuation marks
        source_text(str) : the file path that contain the sentence
        offset(int) : the number of the line in the file
        score(int) : the score of the sentence that contain the specific world

    Methods:
        init(self) : the constructor
        get_input(self) : receives the input from the user and split it by space and append each word in SENTENCE CONSTANT
        process_sentence(self, sentence: str):
        calc_sentence_score(self, sentence1: str, sentence2: str):
        _calculate_penalty
    """
    completed_sentence: str
    source_text: str
    offset: int
    score: int

    def __init__(self, completed_sentence: str, source_text: str, offset: int, score: int):
        self.completed_sentence = completed_sentence
        self.source_text = source_text
        self.offset = offset
        self.score = score

    def __lt__(self, other):
        if isinstance(other, AutoCompleteData):
            return self.score < other.score
        return NotImplemented

    def get_input(self):
        sentence = input("")
        SENTENCE.extend(sentence.split())
        input_user = self.process_sentence(sentence)
        completedSentence = self.process_sentence(self.completed_sentence)
        self.calc_sentence_score(input_user, completedSentence)
        return sentence

    def process_sentence(self, sentence: str):
        lower_case_sentence = sentence.lower()
        cleaned_string = lower_case_sentence.translate(str.maketrans('', '', string.punctuation))
        final_string = re.sub(r'\s+', ' ', cleaned_string).strip()
        return final_string

    def calc_sentence_score(self, sentence1: str, sentence2: str):
        if self.score != 0:
            pass
        else:
            # Remove spaces from both input and sentence
            stripped_sentence1 = sentence1.replace(" ", "")
            stripped_sentence2 = sentence2.replace(" ", "")

            # Initialize the score based on the length of the input
            sentence_score = len(stripped_sentence1) * 2

            # Check if the entire input is in the sentence
            if stripped_sentence1 in stripped_sentence2:
                self.score = sentence_score
                return sentence_score

            # Determine the length difference type
            if len(stripped_sentence1) > len(stripped_sentence2):
                difference_type = 1  # Input longer
            elif len(stripped_sentence1) < len(stripped_sentence2):
                difference_type = 2  # Input shorter
            else:
                difference_type = 0  # Same length

            # Apply penalties based on the first difference position
            min_length = min(len(stripped_sentence1), len(stripped_sentence2))

            for i in range(min_length):
                if stripped_sentence1[i] != stripped_sentence2[i]:
                    penalty = self._calculate_penalty(i, difference_type)
                    sentence_score -= penalty
                    break  # Exit loop after first difference

            # Assign the calculated score to the object's score attribute
            self.score = sentence_score
            return sentence_score

    def _calculate_penalty(self, index, difference_type):
        # Define penalties based on the difference type and index
        penalty_mapping = {
            0: [5, 4, 3, 2, 1],  # Same length
            1: [10, 8, 6, 4, 2],  # Input longer (deletion needed)
            2: [10, 8, 6, 4, 2]  # Input shorter (insertion needed)
        }
        # Return the penalty or the default for indices >= 5
        if index < 5:
            return penalty_mapping[difference_type][index]
        else:
            return penalty_mapping[difference_type][-1]  # Default penalty for indices 5 an above