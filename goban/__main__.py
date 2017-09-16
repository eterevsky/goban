import json

from . import gtp

CONFIG_PATH = 'config.json'


def run_game(engine1: gtp.GtpEngine, engine2: gtp.GtpEngine):
    if not engine1.is_running():
        engine1.run()
    if not engine2.is_running():
        engine2.run()
    engine1.init_game()
    engine2.init_game()

    player = 0
    last_move_pass = False
    while player is not None:
        move = engine1.genmove('b') if player == 0 else engine2.genmove('w')
        print('\n{} {}'.format(('b' if player == 0 else 'w'), move))

        if move.lower() == 'resign':
            score = 'W+Resign' if player == 0 else 'B+Resign'
            break

        if move.lower() == 'pass':
            if last_move_pass:
                score = engine1.final_score()
                break
            last_move_pass = True
        else:
            last_move_pass = False

        board = engine2.showboard()
        print(board)

        if player == 0:
            engine2.play('b', move)
        else:
            engine1.play('w', move)

        player = 1 - player

    print('final score: ', score)


def main():
    config = json.load(open(CONFIG_PATH))
    engine1 = gtp.GtpEngine(args=config['player1'])
    engine2 = gtp.GtpEngine(args=config['player2'])

    run_game(engine1, engine2)


main()
