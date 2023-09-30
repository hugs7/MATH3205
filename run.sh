python3 Project/NaiveImplementation.py | tee out
echo "\n---------- Solution Checker ----------" >> out
examtt_toolbox validate-solution Project/data/toy.json Project/toy_sol.json 2>&1 | tee -a out
