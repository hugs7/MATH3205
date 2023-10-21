from gurobipy import Model, quicksum, GRB
from typing import Dict, Set
import os

Alphabet = "abcdefghijklmnopqrstuvwxyz"

min_word_length = 4
max_word_len = 12


def generate_words(grid):
    def is_valid(x, y):
        return 0 <= x < len(grid[0]) and 0 <= y < len(grid)

    def backtrack(word, x, y):
        if min_word_length <= len(word) <= max_word_len:
            found_words.add(word)

        if len(word) > max_word_len:
            return

        for dx, dy in [
            (1, 0),
            (0, 1),
            (1, 1),
            (-1, 0),
            (0, -1),
            (-1, -1),
            (1, -1),
            (-1, 1),
        ]:
            new_x, new_y = x + dx, y + dy
            if is_valid(new_x, new_y) and (new_x, new_y) not in visited:
                visited.add((new_x, new_y))
                backtrack(word + grid[new_y][new_x], new_x, new_y)
                visited.remove((new_x, new_y))

    found_words = set()
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            print(x, y)
            visited = set()
            visited.add((x, y))
            backtrack(grid[y][x], x, y)

    return found_words


# Maximise the number of min_word_length+ letter words
# Most common letters to reduce to for a simpler problem
S = range(max_word_len)

f = open(os.path.join(".", "Week 3", "Squardle Game", "enable1.txt"), "r")

# :-1 removes the new line
AllWords = [w[:-1] for w in f]

# Limit to words with min_word_length to 9 letters

AllWords = [w for w in AllWords if len(w) >= min_word_length and len(w) <= len(S)]
print(len(AllWords), "words between min_word_length and", len(S), "letters, no repeats")

# Define game grid

grid = []  # 2D Game grid
grid_letters = set()  # Set of letters used in the game grid
# Read the text file
with open(os.path.join(".", "Week 3", "Squardle Game", "gamegrid.txt"), "r") as file:
    # Iterate through each line in the file
    for line in file:
        # Create a list of individual characters in the line
        line_list = list(line.lower().strip())
        for char in line_list:
            if char not in grid_letters:
                grid_letters.add(char.lower())

        # Append the line_list to the 2D list
        grid.append(line_list)

# Limit Word List to words where all letters are in the game grid
WordList = []
for word in AllWords:
    # print(word)
    word_valid = True
    for char in range(len(word)):
        if word[char] not in grid_letters:
            word_valid = False
            break  # Inner Loop

    if word_valid is True:
        # Add word to LimitedWordList
        WordList.append(word)

gridWords = generate_words(grid)

gridwordsLenDict: Dict[str, list[str]] = {}
for l in range(min_word_length, max_word_len + 1):
    gridwordsLenDict[l] = []

print("splitting words")

for word in gridWords:
    gridwordsLenDict[len(word)].append(word)
print([len(w) for w in gridwordsLenDict.values()])

print("----")
# _, _, next_x, next_y = GridPairsLookup[(x1, y1)]
count = 0
for wordLen in range(min_word_length, max_word_len + 1):
    print(f"{wordLen} letter words")
    for word in gridwordsLenDict[wordLen]:
        if word in WordList and len(word) == wordLen:
            print(word)
            count += 1
    print()

print(count)
# Variables
exit()
