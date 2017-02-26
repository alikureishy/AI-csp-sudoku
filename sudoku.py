'''
Created on Feb 25, 2017

@author: safdar
'''
from itertools import combinations_with_replacement

class Sudoku(object):
    rows = 'ABCDEFGHI'
    cols = '123456789'
    digits = '123456789'

    @staticmethod
    def fromString(inputstring, callback=None, verbose=False):
        boxes, units, unitmap, peermap = Sudoku.__get_configuration__()
        valuemap = Sudoku.__extract_grid__(inputstring, boxes)
        sudoku = Sudoku(valuemap, boxes, units, unitmap, peermap, verbose=verbose, callback=callback)
        return sudoku
    
    @staticmethod
    def fromValueMap(valuemap, callback=None, verbose=False):
        boxes, units, unitmap, peermap = Sudoku.__get_configuration__()
        sudoku = Sudoku(valuemap, boxes, units, unitmap, peermap, verbose=verbose, callback=callback)
        return sudoku

    @staticmethod
    def __get_configuration__():
        # Generate box names:
        boxes = Sudoku.__cross__(Sudoku.rows, Sudoku.cols)
        
        units = []
        # Row units:
        units.extend([Sudoku.__cross__(r, Sudoku.cols) for r in Sudoku.rows])
        
        # Column units:
        units.extend([Sudoku.__cross__(Sudoku.rows, c) for c in Sudoku.cols])
        
        # Square units:
        units.extend([Sudoku.__cross__(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')])
        
        # Diagonal units:
        units.extend([[r+c for (r,c) in zip(Sudoku.rows, Sudoku.cols)]])
        units.extend([[r+c for (r,c) in zip(Sudoku.rows, Sudoku.cols[::-1])]])

        # Box -> Units mapping        
        unitmap = dict((s, [u for u in units if s in u]) for s in boxes)
        
        # Box -> Peers mapping (across all units)
        peermap = dict((s, set(sum(unitmap[s],[]))-set([s])) for s in boxes)
        
        return boxes, units, unitmap, peermap

    '''
    classdocs
    '''
    def __init__(self, valuemap, boxes, units, unitmap, peermap, verbose=False, callback=None):
        '''
        Constructor
        '''
        self.__valuemap__ = valuemap
        self.__boxes__ = boxes
        self.__units__ = units
        self.__unitmap__ = unitmap
        self.__peermap__ = peermap
        self.__verbose__ = verbose
        self.__callback__ = callback
        
    def display(self):
        Sudoku.__print__(self.__valuemap__, self.__boxes__)
        
    def solve(self, callback=None):
        print ("Solving...")
        valuemap = self.__valuemap__.copy()
        result = self.__search__(valuemap)
        if result:
            self.__valuemap__ = result
        else:
            print ("Could not find a solution :(")
        return result
            
    @staticmethod  
    def __print__(valuemap, boxes):
        """
        Display the valuemap as a 2-D grid.
        Input: The sudoku in dictionary form
        Output: None
        """
        width = 1+max(len(valuemap[s]) for s in boxes)
        line = '+'.join(['-'*(width*3)]*3)
        for r in Sudoku.rows:
            print(''.join(valuemap[r+c].center(width)+('|' if c in '36' else '')
                          for c in Sudoku.cols))
            if r in 'CF': print(line)
        return

    def __assign__(self, valuemap, box, value):
        if not valuemap[box] == value:
            valuemap[box] = value
            if self.__callback__:
                self.__callback__(valuemap)
        
    @staticmethod
    def __cross__(a, b):
        return [s+t for s in a for t in b]

    @staticmethod
    def __extract_grid__(inputstring, boxes):
        """
        Convert grid into a dict of {square: char} with '123456789' for empties.
        Input: A grid in string form.
        Output: A grid in dictionary form
                Keys: The boxes, e.g., 'A1'
                valuemap: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
        """
        chars = []
        digits = Sudoku.digits
        for c in inputstring:
            if c in digits:
                chars.append(c)
            if c == '.':
                chars.append(digits)
        return dict(zip(boxes, chars))

    def __eliminate__(self, valuemap):
        """
        Go through all the boxes, and whenever there is a box with a value, eliminate this value from the valuemap of all its peermap.
        Input: A sudoku in dictionary form.
        Output: The resulting sudoku in dictionary form.
        """
        peermap = self.__peermap__
        solved_valuemap = [box for box in valuemap.keys() if len(valuemap[box]) == 1]
        for box in solved_valuemap:
            digit = valuemap[box]
            for peer in peermap[box]:
                self.__assign__(valuemap, peer, valuemap[peer].replace(digit,''))
        return valuemap

    def __only_choice__(self, valuemap):
        """
        Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
        Input: A sudoku in dictionary form.
        Output: The resulting sudoku in dictionary form.
        """
        units = self.__units__
        for unit in units:
            for digit in Sudoku.digits:
                dplaces = [box for box in unit if digit in valuemap[box]]
                if len(dplaces) == 1:
                    self.__assign__(valuemap, dplaces[0], digit)
        return valuemap

    def __naked_twins__(self, valuemap):
        """
        Go through all the units, and whenever there is a unit with 2 boxes possessing the same 2-digit possibilities, remove those
        2 digits from the remaining boxes in that unit. This is an optimization that reduces the branching factor of the subsequent
        search operation.
        Input: A sudoku in dictionary form.
        Output: The resulting sudoku in dictionary form.
        """
        units = self.__units__
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

    def __constraint_propagation__(self, valuemap):
        """
        Iterate eliminate() and only_choice(). If at some point, there is a box with no available valuemap, return False.
        If the sudoku is solved, return the sudoku.
        If after an iteration of both functions, the sudoku remains the same, return the sudoku.
        Input: A sudoku in dictionary form.
        Output: The resulting sudoku in dictionary form.
        """
#         solved_valuemap = [box for box in valuemap.keys() if len(valuemap[box]) == 1]
        stalled = False
        while not stalled:
            solved_valuemap_before = len([box for box in valuemap.keys() if len(valuemap[box]) == 1])
            valuemap = self.__eliminate__(valuemap)

            # Invoke pruning strategies:
            valuemap = self.__only_choice__(valuemap)
            valuemap = self.__naked_twins__(valuemap)
            
            solved_valuemap_after = len([box for box in valuemap.keys() if len(valuemap[box]) == 1])
            stalled = solved_valuemap_before == solved_valuemap_after
            if len([box for box in valuemap.keys() if len(valuemap[box]) == 0]):
                return False
        return valuemap

    def __search__(self, valuemap):
        "Using depth-first search and propagation, try all possible valuemap."
        boxes = self.__boxes__
        # First, reduce the puzzle using the previous function
        valuemap = self.__constraint_propagation__(valuemap)
        if valuemap is False:
            return False ## Failed earlier
        
        if self.__verbose__:
            print ("Propagated constraints to get reduced Sudoku:")
            Sudoku.__print__(valuemap, boxes)
        
        if all(len(valuemap[s]) == 1 for s in boxes): 
            return valuemap ## Solved!
        
        # Choose one of the unfilled squares with the fewest possibilities
        n,s = min((len(valuemap[s]), s) for s in boxes if len(valuemap[s]) > 1)

        # Now use recurrence to solve each one of the resulting sudokus
        print ("Performing search on box: {} (n={})".format(s, n))
#         oldvalue = valuemap[s]
        for value in valuemap[s]:
            new_sudoku = valuemap.copy()
            self.__assign__(new_sudoku, s, value)
            if self.__verbose__:
                print ("Trying with {} = {}".format(s, value))
            attempt = self.__search__(new_sudoku)
            if attempt:
                return attempt
#         valuemap[s] = oldvalue
            