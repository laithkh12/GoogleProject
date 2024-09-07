from typing import List
from PriorityList import PriorityList
from data import init_words
from AutoCompleteData import AutoCompleteData
from pathlib import Path

base_path = Path(__file__).parent
archive_path = base_path / 'Archive'

def get_best_k_completions(prefix: str, words) -> List[AutoCompleteData]:
    # Create an instance of AutoCompleteData
    auto_complete_data = AutoCompleteData("", "", 0, 0)

    # Extract the first word from the input
    first_word = prefix.split()[0] if prefix else ""

    # Retrieve sentences using the prefix
    sentences = words.get_sentences(first_word)

    # Process the user input again
    processed_input = auto_complete_data.process_sentence(prefix)

    # Loop through each sentence and calculate the score based on the input
    for sentence in sentences:
        completed_sentence = auto_complete_data.process_sentence(sentence.completed_sentence)

        # Find the index of the prefix in the completed sentence
        start_index = completed_sentence.find(prefix)

        if start_index != -1:
            # Compare the substring starting from the prefix in the sentence with the input
            sub_sentence = completed_sentence[start_index:]
            sentence.calc_sentence_score(processed_input, sub_sentence)
        else:
            # If the prefix is not found, consider the score as 0 or handle it as needed
            sentence.score = 0

    # Assuming you want to return the top K completions (for example, K = 5)
    top_k = 5
    pl = PriorityList(top_k)
    for sentence in sentences:
        pl.insert(sentence)

    return pl.to_list()


def main():
    # Load the words from the Archive directory once
    words = init_words(archive_path)

    # Create an instance of AutoCompleteData
    auto_complete_data = AutoCompleteData("", "", 0, 0)

    last_input = ""
    first_run = True

    while True:
        if first_run:
            # On the first run, prompt the user to enter a sentence
            print("Enter a sentence:", end=" ")
            first_run = False
        else:
            # On subsequent runs, show the last input directly without additional space
            print(last_input, end="")

        # Get user input
        user_input = auto_complete_data.get_input()

        # Check if user input contains the # symbol
        if "#" in user_input:
            # Clear the input and start again
            last_input = ""
            print("Enter a sentence:", end=" ")
            continue  # Restart the loop to get new input

        # Continue from the last input
        if last_input:
            user_input = last_input + user_input

        # Extract the first word from the input and get best completions
        best_sentences = get_best_k_completions(user_input, words)
        for s in best_sentences:
            print(s)

        # Update last_input with the current user_input
        last_input = user_input


if __name__ == "__main__":
    main()
