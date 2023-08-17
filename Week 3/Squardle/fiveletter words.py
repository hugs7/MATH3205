from gurobipy import Model, quicksum, GRB

# Goal: Make a 3x3 squaredle, with 9 distinct letters
#       Maximise the number of 4+ letter words
Alphabet = 'abcdefghijklmnopqrstuvwxyz'
# Most common letters to reduce to for a simpler problem
LimA = 16

S = range(9)

f = open("enable1.txt", "r")
WordList = [w[:-1] for w in f]
# Limit to words with 4 to 9 letters and no repeats (len(w) = len(set(w)))
WordList = [w for w in WordList if len(w) == 5 and w[0] == 'e']

nextWord = False
for word in WordList:
    if 't' not in word:
        continue
    for letter in word:
        if letter in ['a', 's', 'r', 'f', 'c', 'g', 'n', 'i', 'o', 'l']:
            nextWord = True
            break
    if nextWord:
        nextWord = False
        continue
    print(word)
