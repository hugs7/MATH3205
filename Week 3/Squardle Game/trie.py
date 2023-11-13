from gurobipy import Model, quicksum, GRB
from typing import Dict, Set, List
import os
import itertools

Alphabet = "abcdefghijklmnopqrstuvwxyz"

min_word_length = 4
max_word_len = 12


def generate_combinations(grid, min_length, max_length):
    N1 = len(grid)
    N2 = len(grid[0])

    grid_positions = list(itertools.product(range(N1), range(N2)))

    def is_adjacent(pos1, pos2):
        return abs(pos1[0] - pos2[0]) <= 1 and abs(pos1[1] - pos2[1]) <= 1

    base_combs: Dict[int, Set[List[tuple]]] = dict()

    for length in range(2, (max_word_len // 3) + 2):
        base_combs[length] = set()
        print("Computing permutations of length", length, "...")
        len_comb = set(itertools.permutations(grid_positions, length))
        print("permutation complete")
        print(length, len(len_comb))
        # Use combinations directly without creating a list
        for index, comb in enumerate(len_comb):
            if index % 100000 == 0:
                print(index, round(index / len(len_comb) * 100, 3), "%")
            # Check if all positions in the combination are adjacent
            if all(is_adjacent(comb[i], comb[i + 1]) for i in range(len(comb) - 1)):
                base_combs[length].add(comb)

        print("number of base", length, len(base_combs[length]))
    print("number of base", len(base_combs))

    # mapping to get longer combinations
    mapping: Dict[int, tuple[int]] = {
        6: (4, 3),
        7: (4, 4),
        8: (5, 4),
        9: (5, 5),
        10: (4, 4, 4),
        11: (5, 4, 4),
        12: (5, 5, 4),
    }

    joined_combs = set()
    for length, bases in mapping.items():
        print("joining", length, "with bases", bases)
        if len(bases) == 2:
            for i, comb1 in enumerate(base_combs[bases[0]]):
                if i % 1000 == 0:
                    print(i, "of", len(base_combs[bases[0]]))
                for comb2 in base_combs[bases[1]]:
                    if comb1[-1] == comb2[0]:
                        # Check if any duplicates in combined list
                        combined = comb1 + comb2[1:]
                        if len(combined) == len(set(combined)):
                            joined_combs.add(combined)
        elif len(bases) == 3:
            for i, comb1 in enumerate(base_combs[bases[0]]):
                if i % 100 == 0:
                    print(i, "of", len(base_combs[bases[0]]))
                for comb2 in base_combs[bases[1]]:
                    # check if comb1 and comb2 are adjacent
                    if comb1[-1] == comb2[0]:
                        # Check if any duplicates in combined list
                        for comb3 in base_combs[bases[2]]:
                            if comb2[-1] == comb3[0]:
                                combined = comb1 + comb2[1:] + comb3[1:]
                                if len(combined) == len(set(combined)):
                                    joined_combs.add(combined)

    print("number of joined", len(joined_combs))
    final_combs = base_combs + joined_combs
    print("number of final", len(final_combs))
    return final_combs


def to_words(combs, grid):
    words = set()
    spaces = 0
    for comb in combs:
        word = ""
        for pos in comb:
            if grid[pos[0]][pos[1]] == " ":
                spaces += 1
                break
            word += grid[pos[0]][pos[1]]

        words.add(word)
    print("spaces", spaces)
    return list(words)


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

all_pos_combs = generate_combinations(grid, min_word_length, max_word_len)
print("Number of combinations", len(all_pos_combs))

# Convert lists of positions to words
all_word_combs = to_words(all_pos_combs, grid)
print("Number of words", len(all_word_combs))

gridwordsLenDict: Dict[str, list[str]] = {}
for l in range(min_word_length, max_word_len + 1):
    gridwordsLenDict[l] = []

print("splitting words")

for word in all_word_combs:
    if len(word) < min_word_length:
        continue
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
