import json

from . import gtp

CONFIG_PATH = 'config.json'


def main():
    config = json.load(open(CONFIG_PATH))
    engine = gtp.GtpEngine(args=config['args'])
    engine.run()

    print(engine.full_name())

    # for i in range(5):
    #     engine.command('genmove', 'b')
    #     engine.command('genmove', 'w')


main()
