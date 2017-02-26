from sudoku import Sudoku

assignments = []
counter = 0

def assign_value(values):
    global counter, assignments
    assignments.append(values.copy())
    counter = counter + 1

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    verbose = False
    units = ['Row', 'Column', 'Square', 'Diagonal']
    game = Sudoku.fromString(diag_sudoku_grid, callback=assign_value)
    game.display()
    game.solve()
    game.display()
    
    print ("Completed in {} assignments".format(counter)) 
    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
