import os
import random
import time

from blessed import Terminal


TERM = Terminal()
HEIGHT = Terminal().height
WIDTH = Terminal().width
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
WORDLIST_FP = os.path.join(PROJECT_DIR, 'words.txt')

# Codes for blessed to recognize user input
BACKSPACE = [263, 330]
ENTER = 343


def load_words(word_file: str = WORDLIST_FP):
    """ Return a list of random words from word list. """

    with open(word_file, 'r') as f:
        return [word.rstrip() for word in f]


def make_word_lines(words: list, lines: int = 5):
    """ Return a list of random words under width length. """

    words_to_type = []
    type_width = WIDTH - 4  # -2 for user area, -2 for overlaps
    last_word = ''

    for _ in range(lines):
        line = ''
        while len(line) < type_width:
            r_word = random.choice(words)
            if r_word == last_word:
                continue
            if (len(line) + len(r_word)) > type_width:
                break
            line += r_word + ' '
            last_word = r_word
        words_to_type.append(line.rstrip())

    return words_to_type


def get_time():
    """ Return current time in seconds. """

    return int(time.time())


def get_word_info(words: str, w_start: int = 0):
    """ Return current word and start index of next word. """

    w_end = w_start
    while w_end < len(words) and words[w_end] != ' ':
        w_end += 1

    return words[w_start:w_end], w_end + 1


def type_screen(completed_words: str, remaining_words: str, next_word_line: str, user_input: str):
    """ Display current typing session. """

    print(TERM.clear)

    current_words_row = TERM.move_y(HEIGHT // 2 - 1)  # Above the center
    next_words_row = TERM.move_y(HEIGHT // 2)         # Center of the screen
    user_input_row = TERM.move_y(HEIGHT // 2 + 2)     # Below the center

    print(current_words_row + '  ' + completed_words + remaining_words)
    print(next_words_row + TERM.gray('  ' + next_word_line))
    print(user_input_row + TERM.bright_white('>') + ' ' + user_input + TERM.bright_white('_'))


def game_over(counts: dict, times: dict):
    """ Display end screen with WPM and accuracy. """

    print(TERM.clear)

    minutes = (times['end'] - times['start']) / 60
    wpm = max(int((counts['chars'] / 5 - counts['word_errors']) // minutes), 0)
    accuracy = round(100 * (counts['chars'] - counts['errors']) / counts['chars'], 2)

    print(TERM.move_y(HEIGHT // 2 - 1)+ f'Your WPM was {wpm}.\nYour accuracy was {accuracy}%.')


if __name__ == '__main__':
    all_words = load_words(WORDLIST_FP)

    while True:
        word_lines = make_word_lines(all_words)
        curr_line_index = 0
        chars = 0
        errors = 0
        word_errors = 0
        game_started = False

        with TERM.hidden_cursor():
            with TERM.cbreak():
                while curr_line_index != len(word_lines):
                    remaining_words = word_lines[curr_line_index]
                    if curr_line_index != len(word_lines) - 1:
                        next_line = word_lines[curr_line_index + 1]
                    else:
                        next_line = ''
                    completed_words = ''
                    user_input = ''
                    curr_char_index = 0

                    while remaining_words != '':
                        type_screen(completed_words, remaining_words, next_line, user_input)
                        val = TERM.inkey()
                        chars += 1

                        # Get start time as first key is pressed
                        if not game_started:
                            start_time = get_time()
                            game_started = True

                        if val.code in BACKSPACE:
                            # Delete last letter in user field
                            user_input = user_input[:-1]
                        elif val == ' ' or val.code == ENTER:
                            # Don't let a double space cause a failed word
                            if user_input == '':
                                continue

                            curr_word, next_word_index = get_word_info(remaining_words)
                            remaining_words = remaining_words[next_word_index:]

                            if user_input == curr_word:
                                completed_words += TERM.green
                            else:
                                completed_words += TERM.red
                                word_errors += 1

                            completed_words += curr_word + ' ' + TERM.normal
                            user_input = ''
                            curr_char_index = 0
                        else:
                            user_input += val

                        if curr_char_index < len(remaining_words) and val == remaining_words[curr_char_index]:
                            curr_char_index += 1
                        else:
                            errors += 1

                    curr_line_index += 1

        # When all lines have been typed, start game over sequence
        end_time = get_time()

        counts = {
            'chars': chars,
            'errors': errors,
            'word_errors': word_errors,
        }
        times = {
            'start': start_time,
            'end': end_time,
        }

        game_over(counts, times)

        play_again = TERM.move_y(HEIGHT // 2 + 1) + 'Play again? '

        if 'y' not in input(play_again).lower():
            print(TERM.clear)
            break
