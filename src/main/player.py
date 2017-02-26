'''
Created on Feb 25, 2017

@author: safdar
'''

import argparse
from sudoku import Sudoku

'''
Test input:
..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..
Expected output:
483921657967345821251876493548132976729564138136798245372689514814253769695417382
'''

if __name__ == '__main__':
    print ("###############################################")
    print ("#                   SUDOKU                    #")
    print ("###############################################")
    parser = argparse.ArgumentParser(description='Remote Driving')
    parser.add_argument('-i', '--input', dest='input', required=True, type=str, help='Raw input string representing a Sudoku game board')
    parser.add_argument('-u', '--units', dest='units', required=True, nargs='*', type=str, help="List of unit constraints ('Row', 'Column', 'Square', 'Diagonal'...).")
    parser.add_argument('-v', dest='verbose', action='store_true', help='Flag to print out intermediate steps (default: false).')
    args = parser.parse_args()
    
    # Overrides
    args.verbose = True
    args.units = ['Row', 'Column', 'Square', 'Diagonal']
    args.input = "4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......"

    # Create the Sudoku game instance
    sudoku = Sudoku(args.input, args.units, args.verbose)
    sudoku.solve()
    