from gurobipy import *

# Goal: Make a 3x3 squaredle, with 9 distinct letters
#       Maximise the number of 4+ letter words
Alphabet = 'abcdefghijklmnopqrstuvwxyz'
# Most common letters to reduce to for a simpler problem
LimA = 16

S = range(9)

f = open("enable1.txt","r")
WordList = [ w[:-1] for w in f]
# Limit to words with 4 to 9 letters and no repeats
WordList = [w for w in WordList if len(w)>=4 and len(w)<=len(S) and len(w)==len(set(w))]
print(len(WordList), "words between 4 and", len(S), "letters, no repeats")
# Count the frequency of letters
Freq = {a: 0 for a in Alphabet}
for w in WordList:
    for a in w:
        Freq[a] += 1
FList = sorted([(Freq[a],a) for a in Freq],reverse=True)
# Limited alphabet
FSet = set(a[1] for a in FList[:LimA])
# Reduced alphabet
WordList = [w for w in WordList if len(set(w)&FSet)==len(w)]
print(len(WordList), "words using reduced alphabet")
# Put a weight of 2 on palindromes and remove them
wDict = {}
for w in WordList:
    s = w[::-1]
    if s in wDict:
        wDict[s]+=1
    else:
        wDict[w] = 1
WordList = [w for w in WordList if w in wDict]
W = range(len(WordList))
print(len(WordList), "words after palindromes removed")

print('Alphabet:', FSet)
