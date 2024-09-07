import bisect


class PriorityList:
    """
    A priority list that maintains elements in descending order up to a specified size.
    The list is designed to store elements with attributes completed_sentence, source_text,
    offset, and score, and it provides methods for inserting elements, retrieving the maximum
    element, printing the list data, and converting the list to a string.
    """
    def __init__(self, size=5):
        self.size = size
        self.list = []

    def is_empty(self) -> bool:
        return len(self.list) == 0

    def insert(self, element) -> None:
        if element.score == 0:
            return
        if self.is_empty():
            self.list.append(element)
        else:
            if element < self.list[-1] and len(self.list) == self.size:
                return
            # Insert element in descending order manually
            bisect.insort(self.list, element)
            self.list.sort(reverse=True)  # Ensure the list is in descending order
            if len(self.list) > self.size:
                self.list.pop()

    def get_max(self):
        if self.is_empty():
            raise RuntimeError("List is empty!")
        return self.list[0]  # The max element is always the first element in a sorted list

    def print_data(self) -> None:
        for sentence in self.list:
            print(
                f"Sentence: {sentence.completed_sentence}, Source: {sentence.source_text[1]}, Offset: {sentence.offset}, Score: {sentence.score}")
    def to_list(self) -> list:
        ret = []
        for sentence in self.list:
            ret.append(f"Sentence: {sentence.completed_sentence}, Source: {sentence.source_text[1]}, Offset: {sentence.offset}, Score: {sentence.score}")
        return ret