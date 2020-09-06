import random
import time

from blessed import Terminal


TERM = Terminal()
HEIGHT = Terminal().height
WIDTH = Terminal().width
WORDLIST_FP = 'words.txt'
BACKSPACE = [263, 330]  # codes for blessed to recognize user deletion


def load_words(word_file: str = WORDLIST_FP):
    """Returns a list of words from file.

    Keywords:
    word_file -- filepath to word file (default: WORDLIST_FP)"""
    words = []

    with open(word_file, 'r') as f:
        for word in f:
            words.append(word.rstrip())

    return words


def make_word_lines(words: list, lines: int = 5):
    """Returns a list of 5 strings of random words under width length.

    words: list of words
    lines: number of lines to create"""
    words_to_type = []
    # -2 for user area, -2 for overlaps
    type_width = WIDTH-4

    for i in range(lines):
        line = ''
        while len(line) < type_width:
            r_word = random.choice(words)

            if (len(line) + len(r_word)) > type_width:
                break
            else:
                if len(line) != 0:
                    line += ' '
                line += r_word
        words_to_type.append(line)

    return words_to_type


def get_time():
    """Returns current time in seconds."""
    current_time = int(time.time())
    return current_time


def get_word_info(words: str, w_start: int = 0):
    """Returns current word and start index of next word.

    words: line of words still to be typed
    w_start: index of start of current word (default=0)"""
    w_end = w_start
    while w_end < len(words) and words[w_end] != ' ':
        w_end += 1

    return words[w_start:w_end], w_end + 1


def type_screen(disp: str, line: str, user_l: str, user_w: str):
    """Displays current typing session.

    disp: subset of current line containing colored already typed words
    line: subset of current line containing words yet to be typed
    user_l: string of all already typed words, as typed by user
    user_w: string of attempt at current word, as typed by user"""
    print(TERM.clear)
    read_row = TERM.move_y(HEIGHT//2 - 1)
    type_row = TERM.move_y(HEIGHT//2 + 1)
    print(read_row + '  ' + disp + line)
    print(type_row
          + TERM.bright_white('>')
          + user_l
          + ' '
          + user_w
          + TERM.bright_white('_'))


def game_over(c: int, c_err: int, w_err: int, s_time: int, e_time: int):
    """Displays end screen with WPM and accuracy.

    c: total keystrokes typed
    c_err: total keystroke errors typed
    w_err: total words completed incorrectly
    s_time: time test was started in seconds
    e_time: time test was ended in seconds"""
    print(TERM.clear)

    minutes = (e_time - s_time) / 60
    wpm = int(((c / 5) - w_err) // minutes)
    accuracy = round(100 * (c - c_err) / c, 2)

    print(TERM.move_y(HEIGHT//2 - 1)
          + f'Your WPM was {wpm}.\nYour accuracy was {accuracy}%.'
          + TERM.move_y(HEIGHT//2 + 1))


if __name__ == '__main__':
    all_words = load_words(WORDLIST_FP)

    while True:
        word_lines = make_word_lines(all_words)
        curr_line_index = 0
        chars = 0
        char_errors = 0
        word_errors = 0
        start = False

        with TERM.hidden_cursor():
            with TERM.cbreak():
                while curr_line_index != len(word_lines):
                    curr_line = word_lines[curr_line_index]
                    disp_line = ''
                    user_line = ''
                    word_p = 0
                    user_word = ''
                    curr_char = 0

                    while curr_line != '':
                        type_screen(disp_line, curr_line, user_line, user_word)
                        val = TERM.inkey()
                        chars += 1

                        # get start time as first key is pressed
                        if not start:
                            start_time = get_time()
                            start = True
                        # check if input correct
                        if val.code in BACKSPACE:
                            # delete last letter in user field
                            if len(user_word) > 0:
                                user_word = user_word[:len(user_word)-1]

                        elif val == ' ':
                            curr_word, next_word_p = get_word_info(curr_line)
                            curr_line = curr_line[next_word_p:]

                            if user_word == curr_word:
                                color = TERM.green
                            else:
                                color = TERM.red
                                word_errors += 1

                            disp_line = (disp_line
                                         + color
                                         + curr_word
                                         + ' '
                                         + TERM.normal)
                            user_line += ' ' + user_word
                            word_p = 0
                            user_word = ''
                            curr_char = 0

                        else:
                            user_word += val

                            if val == curr_line[curr_char]:
                                curr_char += 1
                            else:
                                char_errors += 1

                    # clear previous word line
                    curr_line_index += 1

            # when all lines have been typed
            end_time = get_time()

        game_over(chars, char_errors, word_errors, start_time, end_time)
        if 'y' not in input('Play again? ').lower():
            print(TERM.clear)
            break
