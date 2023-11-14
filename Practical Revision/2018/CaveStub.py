from gurobipy import *

Data = [
    "6   6    4",
    "     6    ",
    "  3    5  ",
    "   7  9   ",
    " 5  3    5",
    "5    5  2 ",
    "   2  4   ",
    "  7    4  ",
    "    2     ",
    "5    6   6"]

n = len(Data)
N = range(n)

Seeds = {(i,j): int(Data[i][j]) for i in N for j in N if Data[i][j]!=' '}

m = Model('Cave')

