from gurobipy import Model, quicksum, GRB
from typing import Set
import os

Alphabet = "abcdefghijklmnopqrstuvwxyz"


def position_in_alphabet(letter):
    return Alphabet.index(letter.lower())


def get_letter_pairs_indices(letters: Set[str]):
    """
    Gets pairs of letters from set of letters
    """
    # Assuming Alphabet is "abcdefghijklmnopqrstuvwxyz"

    letter_indices = {letter: Alphabet.index(letter.lower()) for letter in letters}

    pairs_indices = []

    for letter1 in letters:
        for letter2 in letters:
            index1 = letter_indices[letter1]
            index2 = letter_indices[letter2]
            pairs_indices.append((index1, index2))

    return pairs_indices


def get_letter_pairs(grid):
    """
    Gets every pair of letters in the grid
    """

    rows = len(grid)
    cols = len(grid[0])
    alphabet_indices_pairs = []

    # Horizontal pairs
    for row in grid:
        for i in range(cols - 1):
            index1 = position_in_alphabet(row[i])
            index2 = position_in_alphabet(row[i + 1])
            alphabet_indices_pairs.append((index1, index2))

    # Vertical pairs
    for col in range(cols):
        for i in range(rows - 1):
            index1 = position_in_alphabet(grid[i][col])
            index2 = position_in_alphabet(grid[i + 1][col])
            alphabet_indices_pairs.append((index1, index2))

    # Diagonal pairs (top-left to bottom-right)
    for row in range(rows - 1):
        for col in range(cols - 1):
            index1 = position_in_alphabet(grid[row][col])
            index2 = position_in_alphabet(grid[row + 1][col + 1])
            alphabet_indices_pairs.append((index1, index2))

    # Diagonal pairs (top-right to bottom-left)
    for row in range(rows - 1):
        for col in range(1, cols):
            index1 = position_in_alphabet(grid[row][col])
            index2 = position_in_alphabet(grid[row + 1][col - 1])
            alphabet_indices_pairs.append((index1, index2))

    return alphabet_indices_pairs


# Maximise the number of 4+ letter words
# Most common letters to reduce to for a simpler problem
S = range(9)

f = open(os.path.join(".", "Week 3", "Squardle Game", "enable1.txt"), "r")

# :-1 removes the new line
AllWords = [w[:-1] for w in f]

# Limit to words with 4 to 9 letters

AllWords = [w for w in AllWords if len(w) >= 4 and len(w) <= len(S)]
print(len(AllWords), "words between 4 and", len(S), "letters, no repeats")

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


# Define model
m = Model()

# Sets

WL = range(len(WordList))
A = Alphabet

# Set of pairs of indices for each word in WordList
# Indexed by position in alphabet
P = {}
for w_index, word in enumerate(WordList):
    tuples = []
    for i in range(len(word) - 1):
        letter1 = word[i]
        letter2 = word[i + 1]
        position1 = position_in_alphabet(letter1)
        position2 = position_in_alphabet(letter2)
        tuples.append((position1, position2))
    P[w_index] = tuples


# Data
AllLetterPairs = get_letter_pairs_indices(grid_letters)
print(AllLetterPairs)

GridPairs = get_letter_pairs(grid)
GP = {}
for pair in AllLetterPairs:
    # Determine if pair exists on the grid or not 1 or 0
    if pair in GridPairs:
        GP[pair] = 1
    else:
        GP[pair] = 0


# Variables

# Each word has a binary variable if it's possible to make
X = {w: m.addVar(vtype=GRB.BINARY) for w in WL}

# Z_wp = 1 if letter pair p from word w exists on grid
Z = {(w, p): m.addVar(vtype=GRB.BINARY) for w in WL for p in P[w]}

# Objective

# Maximise words that can be formed
m.setObjective(quicksum(X[w] for w in WL), GRB.MAXIMIZE)

# Constraints

PairsExist = {
    (w, p): m.addConstr(Z[w, p] <= quicksum(GP[pp] for pp in GridPairs))
    for w in WL
    for p in P[w]
}

WordPossible = {w: m.addConstr(X[w] <= Z[w, p]) for w in WL for p in P[w]}

m.setParam("BranchDir", 1)
m.setParam("Heuristics", 0)
m.setParam("Cuts", 0)
m.setParam("MIPGap", 0)
m.setParam("MIPFocus", 2)
m.optimize()

for w in WL:
    if X[w].x > 0.9:
        print(WordList[w])
