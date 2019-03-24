import unittest

from goban.board import Board, parse_color, parse_point, print_point
from goban.gtp import GtpError

class TestBoard(unittest.TestCase):

    def test_basic(self):
        board = Board()
        self.assertEqual(board.protocol_version(), 2)
        self.assertEqual(board.name(), 'goban')
        self.assertTrue(board.known_command('name'))
    
    def test_play(self):
        board = Board()
        board.play('b', 'd4')
        board.play('w', 'q15')

    def test_taken_point(self):
        board = Board()
        board.play('b', 'd4')
        with self.assertRaises(GtpError):
            board.play('w', 'd4')
    
    def test_positions(self):
        board = Board()
        board.play('b', 'a1')
        board.play('w', 'a19')
        board.play('b', 't19')
        board.play('w', 't1')
        with self.assertRaises(GtpError):
            board.play('b', 'a0')
        with self.assertRaises(GtpError):
            board.play('b', 'i10')
        with self.assertRaises(GtpError):
            board.play('b', 'a20')
        with self.assertRaises(GtpError):
            board.play('b', 'u8')
        
    def test_ko(self):
        board = Board()
        board.play('b', 'a1')
        board.play('w', 'd1')
        board.play('b', 'b2')
        board.play('w', 'c2')
        board.play('b', 'c1')
        board.play('w', 'b1')
        with self.assertRaises(GtpError):
            board.play('b', 'c1')

    def test_score_empty(self):
        board = Board()
        self.assertEqual(board.final_score(), -7.5)
        board.komi(6.5)
        self.assertEqual(board.final_score(), -6.5)

    def test_score_one_stone(self):
        board = Board()
        board.play('b', 'd4')
        self.assertEqual(board.final_score(), 19 * 19 - 7.5)

    def test_score_two_stones(self):
        board = Board()
        board.play('b', 'd4')
        board.play('w', 'q16')
        self.assertEqual(board.final_score(), -7.5)

    def test_score_corner_territory(self):
        board = Board()
        board.play('b', 'a2')
        board.play('w', 'q16')
        board.play('b', 'b1')
        self.assertEqual(board.final_score(), 3 - 1 - 7.5)

    def test_score_capture_corner_stone(self):
        board = Board()
        board.play('b', 'a2')
        board.play('w', 'a1')
        board.play('b', 'b1')
        self.assertEqual(board.final_score(), 19*19 - 7.5)
    
    def test_capture_line(self):
        board = Board()
        for i in range(1, 20):
            board.play('b', 'a{}'.format(i))
            board.play('w', 'b{}'.format(i))
        self.assertEqual(board.final_score(), -19*19 - 7.5)

    def test_split_line(self):
        board = Board()
        for i in range(1, 20):
            board.play('b', 'b{}'.format(i))
            board.play('w', 'c{}'.format(i))
        self.assertEqual(board.final_score(), 2 * 19 - 17 * 19 - 7.5)

if __name__ == '__main__':
    unittest.main()