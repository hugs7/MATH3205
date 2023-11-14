import os
from typing import Dict, Set
import time
import sys

startTime = time.time()

# Constants
min_word_len = 4
max_word_len = 20

# Functions


def GetNeigh(squares: set[tuple[int, int]], i, j):
    """
    Given a set of squares and a position, return the neighbours of that position
    Includes orthogonal and diagonal neighbours
    """

    neighbourPositions = squares.intersection(
        {
            (i - 1, j),  # up
            (i + 1, j),  # down
            (i, j - 1),  # left
            (i, j + 1),  # right
            (i - 1, j - 1),  # up left
            (i - 1, j + 1),  # up right
            (i + 1, j - 1),  # down left
            (i + 1, j + 1),  # down right
        }
    )
    return neighbourPositions


# Read Game Grid
grid = []  # 2D Game grid
grid_letters = set()  # Set of letters used in the game grid

# Read the text file
with open(
    os.path.join(".", "Practical Revision", "Squardle", "gamegrid.txt"), "r"
) as file:
    # Iterate through each line in the file
    for line in file:
        # Create a list of individual characters in the line
        line_list = list(line.lower().strip())
        for char in line_list:
            if char not in grid_letters:
                grid_letters.add(char.lower())

        # Append the line_list to the 2D list
        grid.append(line_list)

N = range(len(grid))
M = range(len(grid[0]))
# Set of square positions
S = {(i, j) for i in N for j in M}

for line in grid:
    print(line)

print("Grid Letters", grid_letters)

### Read words from file

f = open(os.path.join(".", "Practical Revision", "Squardle", "wordsbig.txt"), "r")

# :-1 removes the new line
AllWords = [w[:-1] for w in f]

# Limit to words with min_word_length to max_word_len letters
# All letters from each word must also be within grid_letters
AllWords = [
    w.lower()
    for w in AllWords
    if len(w) >= min_word_len
    and len(w) <= max_word_len
    and all(c in grid_letters for c in w)
]
print(
    "There are",
    len(AllWords),
    "words between",
    min_word_len,
    "and",
    max_word_len,
    "letters with each of these words containing all of their letters in the grid",
)
WordsOfLen = {
    l: [w for w in AllWords if len(w) == l]
    for l in range(min_word_len, max_word_len + 1)
}

print("Generating all possible combinations of grid patterns...")

neighbours = {(i, j): GetNeigh(S, i, j) for i in N for j in M}
printNeighbours = False
if printNeighbours:
    for square, n in neighbours.items():
        print(
            "square",
            grid[square[0]][square[1]],
            square,
            "has neighbours",
            [grid[n[0]][n[1]] for n in n],
        )


def positionsToWord(positions, grid):
    """
    Given a list of positions, return the word that they make up
    """
    return "".join(grid[i][j] for (i, j) in positions)


generatedWords = set()

# open file to write to
squardleWordsFileName = "squardlewords.txt"
squardleWordsFile = open(
    os.path.join(".", "Practical Revision", "Squardle", squardleWordsFileName), "w"
)


def growWord(partWordPositions, endPosition, lengthRemaining, grid, neighbours):
    """
    PartWordPositions is a list of positions that the word has already taken
    """
    # print(word, endPosition, lengthRemaining)
    if lengthRemaining == 0:
        # Convert list of positions to string
        # Add to list of generated words
        newWord = positionsToWord(partWordPositions, grid)
        if newWord in AllWords:
            if newWord not in generatedWords:
                squardleWordsFile.write(newWord + "\n")
                if len(generatedWords) % 100 == 0:
                    # flush stdout
                    squardleWordsFile.flush()

            generatedWords.add(newWord)
    else:
        if len(partWordPositions) == 0 or endPosition is None:
            # loop over the starting squares
            for startingSquare in S:
                # Add position to list
                newPartWordPositions = partWordPositions + [startingSquare]
                # Recurse
                growWord(
                    newPartWordPositions,
                    startingSquare,
                    lengthRemaining - 1,
                    grid,
                    neighbours,
                )
        else:
            for childPosition in neighbours[endPosition]:
                if childPosition in partWordPositions:
                    # can't use this neighbour as position is already used
                    continue

                # Add the neighbour to the list of positions
                newPartWordPositions = partWordPositions + [childPosition]
                newPartWord = positionsToWord(newPartWordPositions, grid)
                # Check to see if there exist words that begin with this part word
                existsWord = False
                for word in WordsOfLen[lengthRemaining + len(partWordPositions)]:
                    if word.startswith(newPartWord):
                        existsWord = True
                        break

                if not existsWord:
                    continue

                # can use this neighbour
                # Recurse
                growWord(
                    newPartWordPositions,
                    childPosition,
                    lengthRemaining - 1,
                    grid,
                    neighbours,
                )


wordLengthTime = time.time()
# Generate all possible combinations of grid patterns
for wordLength in range(min_word_len, max_word_len + 1):
    print("Computed words of length", wordLength, "in...", end=" ")
    # flush stdout
    sys.stdout.flush()
    growWord([], None, wordLength, grid, neighbours)
    print(
        f"{time.time() - wordLengthTime:.3f} seconds - cumulative: {time.time() - startTime:.3f} seconds - {len(generatedWords)} words"
    )
    wordLengthTime = time.time()


generatedByLength = {
    l: [word for word in generatedWords if len(word) == l]
    for l in range(min_word_len, max_word_len + 1)
}

for length, words in generatedByLength.items():
    print("\nWords of length", length)
    for word in words:
        print(word)

endTime = time.time()
runTime = endTime - startTime
runTimeDisplay = f"{runTime:.3f}"

print("Generated", len(generatedWords), "words in", runTimeDisplay, "seconds")
