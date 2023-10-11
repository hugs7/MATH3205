# %%
import gurobipy as gp
from toyinstance import ToyInstance
from largeinstance import LargeInstance
from shortestpaths import ShortestPaths
from plotpaths import PlotPaths
EPS = 1e-6

# Small instance
if True:
    pos, arcs, length = ToyInstance()
    ignition = 0
    delay = 50
    target = 28
    resources = {10:2, 15:3}

else:
    pos, arcs, length = LargeInstance()
    ignition = 23
    delay = 50
    target = 90
    resources = {10:3, 20:3, 30: 3}

nodes = range(len(pos))
times = list(resources.keys())
ignitions = [ignition]

# Get in and out arcs
inarcs = {n: [] for n in nodes}
outarcs = {n: [] for n in nodes}
for a in arcs:
    outarcs[a[0]].append((a[0], a[1]))
    inarcs[a[1]].append((a[0], a[1]))









solution = set([])
# solution = set([2, 8, 14])
arrival_time, fire_path, pred = ShortestPaths(
    nodes, length, inarcs, outarcs, solution, ignitions, delay)
PlotPaths(pos, arrival_time, pred, solution, ignitions, target, round(0.5*len(nodes)**0.5))







# %%
