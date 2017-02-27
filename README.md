# Artificial Intelligence Nanodegree
## Introductory Project: Diagonal Sudoku Solver

# Question 1 (Naked Twins)
Q: How do we use constraint propagation to solve the naked twins problem?  
A: I have added a new method Sudoku.__naked_twins__() that iterates over each unit of the game (row units, column units, square units and diagonal units) and checks whether any two boxes have the same 2-digit values (possibility values). If so, it eliminates those possibility-values from all other boxes in that unit that are peers of the 2 boxes above.

```
for unit in units:
    tuples = [box for box in unit if len(valuemap[box])==2]
    if len(tuples) > 1:
        combinations = combinations_with_replacement(tuples, 2)
        nakedtwins = [[s,t] for [s,t] in combinations if not s == t and valuemap[s] == valuemap[t]]
        for twins in nakedtwins:
            digits = valuemap[twins[0]] # Get the 2-digit string
            peerlist = [box for box in unit if box not in twins]
            for peer in peerlist:
                for digit in digits:
                    self.__assign__(valuemap, peer, valuemap[peer].replace(digit, ''))
return valuemap

```
# Question 2 (Diagonal Sudoku)
Q: How do we use constraint propagation to solve the diagonal sudoku problem?  
A: This was a rather straightforward. I only had to add 2 new 'units' to the list of existing 'units' for the sudoku game. I created those two units as below, and added them to the 'units' instance.

```
units.extend([[r+c for (r,c) in zip(Sudoku.rows, Sudoku.cols)]])
units.extend([[r+c for (r,c) in zip(Sudoku.rows, Sudoku.cols[::-1])]])
```
