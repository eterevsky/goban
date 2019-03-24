from typing import Union

from .gtp import GtpError

KNOWN_COMMANDS = ['protocol_version', 'name', 'version', 'known_command', 'list_commands', 'quit',
                  'boardsize', 'clear_board', 'komi', 'play', 'genmove', 'final_score']


def parse_color(color: Union[int, str]) -> int:
    if type(color) == int:
        if color not in (1, 2):
            raise GtpError('Unknown color: {}'.format(color))
        return color
    if color.lower() in ('b', 'black'):
        return 1
    elif color.lower() in ('w', 'white'):
        return 2
    raise GtpError('Unknown color: {}'.format(color))


def parse_point(point: Union[int, str], size: int) -> int:
    if type(point) == int:
        if not 0 <= point < size * size:
            raise GtpError('Incorrect point: {}', point)
        return point

    point = point.strip()
    col = point[0].lower()
    if col < 'i':
        col = ord(col) - ord('a')
    elif col > 'i':
        col = ord(col) - ord('b')
    else:
        raise GtpError('There is no `i` column')

    if col < 0 or col >= size:
        raise GtpError('Incorrect column for point {}'.format(point))
    try:
        row = int(point[1:]) - 1
    except ValueError:
        raise GtpError('Can\'t parse the row for point {}'.format(point))
    if row < 0 or row >= size:
        raise GtpError('Incorrect row for point {}'.format(point))
    return col * size + row


def unpack_point(point: int, size: int) -> (int, int):
    return divmov(point, size)


def print_point(point: Union[int, str], size: int) -> str:
    if type(point) == str: return point
    col, row = unpack_point(point, size)
    if col < ord('i'):
        col = chr(col + ord('a'))
    else:
        col = chr(col + ord('b'))
    return '{}{}'.format(col, row)


class Board(object):
    """Simple Go engine with GTP-like interface, used for judging.
    
    Tromp-Taylor Rules are used for scoring.
    """

    def __init__(self):
        self._size = 19
        self._komi = 7.5
        self._init_board()
    
    def _init_board(self):
        # Number of subsequent passes
        self._passes = 0
        self._resign = 0
        self._next_to_move = 1
        self._board = bytes([0])  * (self._size * self._size)
        self._previous_positions = set()

    def protocol_version(self):
        return 2
    
    def name(self):
        return 'goban'
    
    def version(self):
        return '0.1'
    
    def known_command(self, command: str):
        return command in KNOWN_COMMANDS
    
    def list_commands(self):
        return KNOWN_COMMANDS
    
    def quit(self):
        pass
    
    def boardsize(self, size: int):
        self._size = size
        self._init_board()
    
    def clear_board(self):
        self._init_board()
    
    def komi(self, value: float):
        self._komi = value
    
    def play(self, color: Union[int, str], move: Union[int, str]):
        color = parse_color(color)

        if move.lower() == 'pass':
            self._passes += 1
            return
        if move.lower() == 'resign':
            self._resign = color
            return
        
        move = parse_point(move, self._size)
        
        assert 0 <= move < len(self._board)

        if self._board[move] != 0:
            raise GtpError('Point {} is taken'.format(move))
        board = bytearray(self._board)
        board[move] = color
        other_color = 3 - color
        
        for neighbor in self._neighbors(move):
            self._try_to_clear(board, neighbor, other_color)
        self._try_to_clear(board, move, color)

        board = bytes(board)
        if board in self._previous_positions:
            raise GtpError('The move leads to a repeated position')
        
        self._previous_positions.add(self._board)
        self._board = board
        self._passes = 0
        self._resign = 0
        self._next_to_move = other_color

    def genmove(self, color: str):
        return 'pass'

    def finished(self) -> bool:
        return self._resign != 0 or self._passes >= 2

    def color_to_move(self) -> int:
        if self.finished():
            return 0
        else:
            return self._next_to_move

    def final_score(self):
        """Black score - white score. +1/-1 if one of the sides has resigned."""
        if self._resign != 0:
            return 

        territory = [None, set(), set()]
        resolved = set()
        for point in range(len(self._board)):
            if self._board[point] != 0:
                territory[self._board[point]].add(point)
                resolved.add(point)

            can_reach = [None, False, False]
            visited = set()
            to_visit = [point]
            while to_visit:
                current = to_visit.pop()
                color = self._board[current]
                if color == 0:
                    if current in visited: continue
                    visited.add(current)
                    for neighbor in self._neighbors(current):
                        to_visit.append(neighbor)
                else:
                    can_reach[color] = True
            
            if can_reach[1] and not can_reach[2]:
                territory[1] |= visited
            elif not can_reach[1] and can_reach[2]:
                territory[2] |= visited
            resolved |= visited
           
        return len(territory[1]) - len(territory[2]) - self._komi
    
    def _neighbors(self, point):
        size = self._size
        size2 = size * size
        row = point % size
        if point >= size: yield point - size
        if point + size < size2: yield point + size
        if row != 0: yield point - 1
        if row != size - 1: yield point + 1

    def _try_to_clear(self, board: bytearray, point: int, color: int):
        if board[point] != color: return
        visited = set()
        to_visit = [point]
        while to_visit:
            current = to_visit.pop()
            if board[current] == 0:
                return
            if board[current] != color or current in visited:
                continue
            visited.add(current)
            for neighbor in self._neighbors(current):
                to_visit.append(neighbor)
        
        # Since we haven't exited, there are not empty neighbor, so we have to clear the group.
        for current in visited:
            board[current] = 0

        