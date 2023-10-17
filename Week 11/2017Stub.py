from gurobipy import Model, quicksum, GRB
import random
from itertools import combinations

Values = range(1, 14)
Suits = ["Red", "Green", "Blue", "Yellow"]
Deck = [(v, s) for v in Values for s in Suits]

Decks = range(10)

HandSize = 100
random.seed(3)
Hand = random.sample([k for k in Deck for d in Decks], HandSize)

# generate all 3 of a kind
combinations_of_suits_3 = list(combinations(Suits, 3))
G = set()
for v in Values:
    for s in combinations_of_suits_3:
        a, b, c = s
        G.add(frozenset([(v, a), (v, b), (v, c)]))

# Generate all 4 of a kind
combinations_of_suits_4 = list(combinations(Suits, 3))
for v in Values:
    for s in combinations_of_suits_4:
        a, b, c = s
        G.add(frozenset([(v, a), (v, b), (v, c)]))

# Sequences of 3 or more
for v in Values:
    if v <= 12:
        for s in Suits:
            for j in range(3, 14 - v + 1):
                tmp_set = set()
                for i in range(j):
                    tmp_set.add((v + i, s))
                G.add(frozenset(tmp_set))
print(len(G))

N = {t: 0 for t in Deck}
for t in Hand:
    N[t] += 1

m = Model("Rummikub")

# 1 if ungrouped, 0 if grouped
Z = {g: m.addVar(vtype=GRB.INTEGER) for g in G}
U = {t: m.addVar(vtype=GRB.INTEGER) for t in Deck}
# Discarded
X = {t: m.addVar(vtype=GRB.INTEGER) for t in Deck}
# Picked up
Y = {t: m.addVar(vtype=GRB.INTEGER) for t in Deck}


XYEq = m.addConstr(quicksum(X[t] for t in Deck) == quicksum(Y[t] for t in Deck))
# 3 of a kind – 3 tiles with the same number and three different colours

# • 4 of a kind – 4 tiles with the same number and all different colours

# • Sequences of length 3 or more. The tiles in a sequence must all have
# the same colour and the numbers must be consecutive. For example, 7
# Red, 8 Red and 9 Red make up a sequence.

Cal = {
    t: m.addConstr(quicksum(Z[g] for g in G if t in g) + U[t] == N[t] + Y[t] - X[t])
    for t in Deck
}

m.setObjective(
    quicksum(t[0] * U[t] for t in Deck) + 10 * quicksum(X[t] for t in Deck),
    GRB.MINIMIZE,
)

m.optimize()


# for g in G:
#     if Z[g].x > 0.0:
#         print(round(Z[g].x), g)


# for t in Deck:
#     if U[t].x > 0.9:
#         print(round(U[t].x), t)


print("Discarded")
for t in Deck:
    if X[t].x > 0.9:
        print(round(X[t].x), t)

print("Picked up")
for t in Deck:
    if Y[t].x > 0.9:
        print(round(Y[t].x), t)
