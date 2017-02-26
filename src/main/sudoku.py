'''
Created on Feb 25, 2017

@author: safdar
'''

class Sudoku(object):
    rows = 'ABCDEFGHI'
    cols = '123456789'
    digits = '123456789'

    '''
    classdocs
    '''
    def __init__(self, inputstring, unitnames, verbose):
        '''
        Constructor
        '''
        self.__inputstring__ = inputstring
        self.__boxes__ = Sudoku.__cross__(Sudoku.rows, Sudoku.cols)
        
        # Create the constrained 'units':
        self.__unitlist__ = []
        for name in unitnames:
            if name == 'Row':
                self.__unitlist__.extend([Sudoku.__cross__(r, Sudoku.cols) for r in Sudoku.rows])
            elif name == 'Column':
                self.__unitlist__.extend([Sudoku.__cross__(Sudoku.rows, c) for c in Sudoku.cols])
            elif name == 'Square':
                self.__unitlist__.extend([Sudoku.__cross__(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')])
            elif name == 'Diagonal':
                pass
#                 self.__unitlist__.extend(None)
    
        # Encapsulate all units into a general list:    
        self.__units__ = dict((s, [u for u in self.__unitlist__ if s in u]) for s in self.__boxes__)
        self.__peers__ = dict((s, set(sum(self.__units__[s],[]))-set([s])) for s in self.__boxes__)

        self.__verbose__ = verbose
        self.__raw__, self.__values__ = Sudoku.__extract_grid__(inputstring, self.__boxes__)
        
        print ("Constructed sudoku (Raw):")
        Sudoku.__display__(self.__raw__, self.__boxes__)

        print ("Constructed sudoku (Possibilities):")
        Sudoku.__display__(self.__values__, self.__boxes__)
        
    def solve(self):
        print ("Solving...")
        values = self.__values__.copy()
        result = Sudoku.__search__(values, self.__boxes__, self.__peers__, self.__unitlist__, self.__verbose__)
        if result:
            print ("SOLVED! Sudoku is:")
            Sudoku.__display__(result, self.__boxes__)
        else:
            print ("Could not find solution :(")
            
    @staticmethod  
    def __display__(values, boxes):
        """
        Display the values as a 2-D grid.
        Input: The sudoku in dictionary form
        Output: None
        """
        width = 1+max(len(values[s]) for s in boxes)
        line = '+'.join(['-'*(width*3)]*3)
        for r in Sudoku.rows:
            print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                          for c in Sudoku.cols))
            if r in 'CF': print(line)
        return

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
                Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
        """
        chars = []
        raw = []
        digits = Sudoku.digits
        for c in inputstring:
            raw.append(c)
            if c in digits:
                chars.append(c)
            if c == '.':
                chars.append(digits)
        assert len(chars) == 81
        return dict(zip(boxes, raw)), dict(zip(boxes, chars))

    @staticmethod
    def __eliminate__(values, peers):
        """
        Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
        Input: A sudoku in dictionary form.
        Output: The resulting sudoku in dictionary form.
        """
        solved_values = [box for box in values.keys() if len(values[box]) == 1]
        for box in solved_values:
            digit = values[box]
            for peer in peers[box]:
                values[peer] = values[peer].replace(digit,'')
        return values

    @staticmethod
    def __only_choice__(values, unitlist):
        """
        Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
        Input: A sudoku in dictionary form.
        Output: The resulting sudoku in dictionary form.
        """
        for unit in unitlist:
            for digit in Sudoku.digits:
                dplaces = [box for box in unit if digit in values[box]]
                if len(dplaces) == 1:
                    values[dplaces[0]] = digit
        return values

    @staticmethod
    def __constraint_propagation__(values, peers, unitlist, verbose):
        """
        Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
        If the sudoku is solved, return the sudoku.
        If after an iteration of both functions, the sudoku remains the same, return the sudoku.
        Input: A sudoku in dictionary form.
        Output: The resulting sudoku in dictionary form.
        """
#         solved_values = [box for box in values.keys() if len(values[box]) == 1]
        stalled = False
        while not stalled:
            solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
            values = Sudoku.__eliminate__(values, peers)
            values = Sudoku.__only_choice__(values, unitlist)
            solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
            stalled = solved_values_before == solved_values_after
            if len([box for box in values.keys() if len(values[box]) == 0]):
                return False
        return values

    @staticmethod
    def __search__(values, boxes, peers, unitlist, verbose):
        "Using depth-first search and propagation, try all possible values."
        # First, reduce the puzzle using the previous function
        values = Sudoku.__constraint_propagation__(values, peers, unitlist, verbose)
        if values is False:
            return False ## Failed earlier
        
        if verbose:
            print ("Propagated constraints to get reduced Sudoku:")
            Sudoku.__display__(values, boxes)
        
        if all(len(values[s]) == 1 for s in boxes): 
            return values ## Solved!
        
        # Choose one of the unfilled squares with the fewest possibilities
        n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)

        # Now use recurrence to solve each one of the resulting sudokus
        print ("Performing search on box: {} (n={})".format(s, n))
#         oldvalue = values[s]
        for value in values[s]:
            new_sudoku = values.copy()
            new_sudoku[s] = value
            if verbose:
                print ("Setting {} = {}".format(s, value))
            attempt = Sudoku.__search__(new_sudoku, boxes, peers, unitlist, verbose)
            if attempt:
                return attempt
#         values[s] = oldvalue
            