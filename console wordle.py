# Console wordle.py
# Bowie Luckie
#
# @TODO add animations using time module?
# @TODO fix hard mode

from random import choice
from dataclasses import dataclass
from string import ascii_lowercase
from time import sleep
# from json import load, dump

# i kept the json functionality in as comnments

# allows letter objects to be created with a char and colour attribute which are then called when rendering the stack
@dataclass # i use a data class because the __init__ function does not need args. this is more lightweight and cleaner than a regular class
class LetterInStack(): # proper class naming conventions
    char: str
    colour: str

class WordleGame: # putting the game code in a class is better than excessive global variables
    def __init__(self):
        self.debug_mode = False # displays internal workings for debugging
        self.hard_mode = False 
        self.contrast_mode = False # if its on, colour codes become bold

        # opens the word file and creates a list of the words to guess from
        with open("wordle-answers-alphabetical.txt") as f:
            self.word_list = f.read().splitlines()
            self.spec_print(f'{("words available" if len(self.word_list)>1 else "words unable to be found") if self.debug_mode else ""}') # debug statement to check if the word list was loaded correctly

        self.colours = self.build_colours()

        self.keyboard = {letter: None for letter in ascii_lowercase} # creates a dict with every lettter and its colour which is None be default

        self.stack = []
        self.score = 0
    
    def spec_print(self, text="\n", end="\n"):
        for i in text:
            print(i, end="", flush=True) # prints each character at a time
            sleep(0.02)
        print(end=end) # prints the end argument if it exists

    # with open(r"modes.json") as f:
    #     modes = load(f)
    #     debug_mode = modes["debug_mode"]
    #     hard_mode = modes["hard_mode"]


    # colours and their escape codes
    def style(self, normal, contrast):
        return contrast if self.contrast_mode else normal # returns the correct colour code based of contrast mode

    # colours can still be pretty hard to see. the nature of console based colours are also pretty limited
    def build_colours(self): # returns the right colours based off contrast mode
        return {
            "grey":   self.style("\033[90;40m", "\033[1;90;40m"),
            "yellow": self.style("\033[93;40m", "\033[1;93;40m"),
            "green":  self.style("\033[92;40m", "\033[1;92;40m"),
            "red":    self.style("\033[91;40m", "\033[1;91;40m"),
            "white": "\033[97;40m",
            "RESET":  "\033[0m"
        }


    # json is opned and the dump function is used to write the modes dict back into the file
    # def save_modes(self):
    #     with open("modes.json", "w") as f:
    #         dump(modes, f, indent=4)


    # displays the stack into the console with the correct colours by looping through the objects in the stack 
    def render_stack(self):
        for row in self.stack:
            for letter in row:
                print(self.colours[letter.colour] + letter.char.upper() + self.colours["RESET"], end="") 
            print()

        # make the rest of the stack grey like real wordle
        empty_rows = 6 - len(self.stack)
        for _ in range(empty_rows):
            for _ in range(5):
                print(self.colours["grey"] + " " + self.colours["RESET"], end="")
            print()

    def update_keyboard(self, guess_result):
        priority = {"grey": 0, "yellow": 1, "green": 2} # colour priority. this is handy for when theres a green and a yellow/grey instance of the same letter in a word

        for colour, char in guess_result: # guess result returns a list of tuples which are unpacked as colour, char
            current = self.keyboard[char] # checks the current top colour

            if current is None or priority[colour] > priority[current]: # if colour has never been seen or if current colour is stronger
                self.keyboard[char] = colour # overrides lower priority colours

    def initialize(self):
        self.spec_print("Welcome to Console Wordle!")
        # basic command loop for entering the game, getting help and changing modes
        while True:
            self.spec_print("type start, exit, help or modes", end="\n\n")
            init_comm = input("").lower().strip()
            if init_comm == "help":
                self.spec_print("wordle is a game where you have to guess a 5 letter word in 6 tries or less. after each guess, the letters will be coloured to show how close your guess was. green means the letter is in the correct position, yellow means the letter is in the word but in the wrong position and grey means the letter is not in the word at all. you can also enable hard mode which forces you to use the clues you have been given. good luck!")
            elif init_comm == "modes":
                self.spec_print("type mode name to toggle it, type 'back' to go back")
                self.spec_print("debug mode: " + ("enabled" if self.debug_mode else "disabled"))
                self.spec_print("hard mode (subsequent guesses cannot use incorrect letters): " + ("enabled" if self.hard_mode else "disabled"))
                self.spec_print("contrast mode: " + ("enabled" if self.contrast_mode else "disabled")) 
                while True:
                    mode = input("Enter mode name: ").lower().strip()
                    if mode == "debug" or mode == "debug mode":
                        self.debug_mode = not self.debug_mode # toggle mode
                        self.spec_print("debug mode: " + ("enabled" if self.debug_mode else "disabled"))
                        # modes["debug_mode"] = debug_mode 
                        # save_modes()
                    elif mode == "hard" or mode == "hard mode":
                        self.hard_mode = not self.hard_mode
                        self.spec_print("hard mode: " + ("enabled" if self.hard_mode else "disabled"))
                        # modes["hard_mode"] = hard_mode
                        # save_modes()
                    elif mode == "contrast" or mode == "contrast mode":
                        self.contrast_mode = not self.contrast_mode
                        self.spec_print("contrast mode: " + ("enabled" if self.contrast_mode else "disabled"))
                        self.colours = self.build_colours()
                    elif mode == "back":
                        break
                    else:
                        self.spec_print("Invalid mode name.")
            elif init_comm == "exit":
                self.spec_print("Goodbye!")
                break
            elif init_comm == "start":
                play_again = True
                while play_again:
                    play_again = self.main()
                self.spec_print("Thanks for playing! score: " + str(self.score)) # triggers when the main loop returns false
            else:
                self.spec_print("Invalid command.")
                    
    def colour_pass(self, guess, word_to_guess, wrong_letters):
            checked_letters = list(word_to_guess)
            result:list = [None] * 5

            # green pass
            for i, char in enumerate(guess): # enumerate function will supply the index and the char as [(0, char), (1, char), (2, char)] allowing me to iterate over both values
                if char == word_to_guess[i]:
                    result[i] = ("green", char)
                    checked_letters[i] = None

            # yellow and grey pass
            for i, char in enumerate(guess): # creates an enumerate object
                if result[i] is not None:
                    continue
                elif char in checked_letters:
                    result[i] = ("yellow", char)
                    checked_letters[checked_letters.index(char)] = None # removes the first instance of the letter so if there are duplicate letters they arent both counted as yellow
                else:
                    result[i] = ("grey", char)
                    if char not in wrong_letters:
                        wrong_letters.append(char)

            return result, wrong_letters

    def render_keyboard(self):
        print("\nKeyboard:")

        for i, letter in enumerate(self.keyboard): # enumerate object
            colour = self.keyboard[letter] or "RESET" # RESET acts as a white color which is chosen if there is no colour (None)
            print(self.colours[colour] + letter.upper() + self.colours["RESET"], end=" ")

            if (i + 1) % 13 == 0:
                print() # makes a new line after 13 letters
        print() # prints a new line

    def main(self):
        # loop initializations
        self.stack.clear()
        self.keyboard = {letter: None for letter in ascii_lowercase} # reload keyboard colours
        required_positions = [None] * 5   # greens locked by index. these are refrenced by hard mode 
        required_letters = [] # yellows that must appear somewhere
        wrong_letters = []
        word_to_guess = choice(self.word_list)
        if self.debug_mode:
            self.spec_print(f"DEBUG: The word to guess is '{word_to_guess}'")
        self.spec_print(f"\nScore: {self.colours['red'] if self.score < 0 else self.colours['green']}{self.score}{self.colours['RESET']}")
        self.render_stack() # prints an empty stack
        while True:
            guess = input("Enter your guess: ").lower().strip()
            if len(guess) != 5 or guess not in self.word_list:
                self.spec_print(f"Invalid guess, try again. {'too short' if len(guess) != 5 else 'guess not in word list'}") # using inline if statements to compactly determine the fault
                self.render_stack()
                continue
            elif self.hard_mode and len(self.stack) > 0:
                invalid_guess = False
                for i in guess:
                    if i in wrong_letters:
                        self.spec_print("guess must not contain letters that have been guessed wrong (hard mode), try again.")
                        self.render_stack()
                        invalid_guess = True
                        break
                if invalid_guess: # continue off the loop 1 indent outside
                    continue

            # check letter colours and return the result 
            result, wrong_letters = self.colour_pass(guess, word_to_guess, wrong_letters)
            self.update_keyboard(result) # update all letter colours


            # build stack
            row = []
            for entry in result: # creates a tuple for cleaner code
                colour, char = entry
                row.append(LetterInStack(char, colour))

            self.stack.append(row)

            # rendering and win/loss conditions
            self.render_stack()
            self.render_keyboard()
            if self.debug_mode:
                self.spec_print(f"DEBUG: stack")
                self.spec_print(f'DEBUG: {result}')
                self.spec_print(f"DEBUG: {len(self.stack)}")
            if guess == word_to_guess:
                self.score += 8 - len(self.stack) # the earlier you guess the word the more points you get
                self.spec_print(f"\nCongratulations! You've guessed the word! score: {self.score}")
                play_again = input("Do you want to play again? (y/n): ").lower().strip()
                return play_again == "y"

            elif len(self.stack) == 6:
                self.score -= 5
                self.spec_print(f"\n{self.colours['red']}Game over! The word was '{word_to_guess}'. score: {self.score}" + self.colours["RESET"])
                play_again = input("Do you want to play again? (y/n): ").lower().strip()
                return play_again == "y" # returns true if the answer is yes, otherwise breaks back out into initialize where the player can exit, change modes or play again

# i used a __name__ gaurd so if for whatever reason you want this file as a module, you can have it
if __name__ == "__main__":
    wordle = WordleGame()
    if wordle.debug_mode:
        wordle.spec_print(f"Stack: {wordle.stack}, Score: {wordle.score}")
    wordle.initialize() # the initialize function leads into all of the other functions so its the only thing we have to call


