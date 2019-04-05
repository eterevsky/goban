from . import GtpEngine, Board

def run_game(player1: GtpEngine, player2: GtpEngine) -> int:
    """Runs one game between two engines.

    Return 1 if player1 (black) wins, 0 otherwize.
    """
    board = Board()
    player1.run()
    player2.run()
    for player in (player1, player2, board):
        player.boardsize(19)
        player.clear_board()
        player.komi(7.5)
        # One second per move
        player.time_settings(0, 1, 1)
    
    while not board.finished():
        color_to_move = board.color_to_move()
        player, other_player = (player1, player2) if color_to_move == 'b' else (player2, player1)

        move = player.genmove(color_to_move)
        # print(move, end=' ', flush=True)
        other_player.play(color_to_move, move)
        board.play(color_to_move, move)
    
    print()
    print("Player 1 score:", player1.final_score())
    print("Player 2 score:", player2.final_score())
    print("Board score:", board.final_score())
