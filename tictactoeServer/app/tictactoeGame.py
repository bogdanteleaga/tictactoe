import random


class TicTacToe(object):
    """Class for TicTacToe on server"""

    def __init__(self):
        self.form = '''
            \t| %s | %s | %s |
            \t-------------
            \t| %s | %s | %s |
            \t-------------
            \t| %s | %s | %s |
            '''
        self.cells = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.last_move = 'X' if random.randint(0, 1) else 'O'

    def display(self):
        """Return a string representing the board state"""
        return self.form % tuple(self.cells)

    def _valid(self, cell_no):
        """Checks if a cell isn't already occupied"""
        return (self.cells[cell_no - 1] != 'X'
                and self.cells[cell_no - 1] != 'O'
                and cell_no in range(1, 10))

    def set_cell(self, cell_no, inp):
        """Set cell number cell_no to inp"""
        if self._valid(cell_no) and self.last_move != inp:
            self.cells[cell_no - 1] = inp
            self.last_move = inp
            return 1
        return None

    def _tie(self):
        """Checks for a tie"""
        return all(c in ('X', 'O') for c in self.cells)

    def win(self):
        """Checks for a win/tie"""
        WAYS_TO_WIN = ((0, 1, 2),
                       (3, 4, 5),
                       (6, 7, 8),
                       (0, 3, 6),
                       (1, 4, 7),
                       (2, 5, 8),
                       (0, 4, 8),
                       (2, 4, 6))

        for way in WAYS_TO_WIN:
            if self.cells[way[0]] == self.cells[way[1]] == self.cells[way[2]]:
                return self.cells[way[0]]

        if self._tie():
            return "TIE"

        return None
