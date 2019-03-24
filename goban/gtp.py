import re
import subprocess
from typing import List


class GtpError(Exception):
    pass


class EngineError(Exception):
    pass


RE_WHITESPACE = re.compile(b'\\s')


def strip_gtp_line(s: bytes) -> str:
    """Convert bytes, returned by a GTP engine to a string."""
    if b'#' in s:
        s = s[:s.index(b'#')]
    s = RE_WHITESPACE.sub(b' ', s)
    return s.rstrip().decode('utf-8')


class GtpEngine(object):
    def __init__(self, args):
        self._args = args
        self._process = None

    def __del__(self):
        if self._process is not None:
            self.quit()

    def is_running(self):
        return self._process is not None

    def run(self):
        assert self._process is None
        self._process = subprocess.Popen(
            self._args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0)
        self.check_protocol_version()

    def command(self, command, *args):
        assert self._process is not None
        command = command
        command_parts = [command]
        command_parts.extend(args)

        command_str = ' '.join(command_parts)
        command_bytes = bytes(command_str + '\n', 'utf-8')

        self._process.stdin.write(command_bytes)
        lines = []
        while True:
            line = strip_gtp_line(self._process.stdout.readline())
            if not line:
                break
            lines.append(line)
        assert len(lines) > 0
        status = lines[0][0]
        if status == '=':
            lines[0] = lines[0][2:]
            return lines
        elif status == '?':
            lines[0] = lines[0][2:]
            raise EngineError('\n'.join(lines))
        else:
            raise GtpError('Incorrect GTP response:\n', '\n'.join(lines))

    def full_name(self) -> str:
        return self.name() + ' ' + self.version()

    def init_game(self, size=19, komi=7.5, handicap=0, time=(0, 1, 1)):
        self.boardsize(size)
        self.clear_board()
        self.komi(komi)
        self.time_settings(*time)
        if handicap:
            assert 0 < handicap <= 9
            self.fixed_handicap(handicap)

    def check_protocol_version(self):
        response = self.command('protocol_version')
        assert len(response) == 1
        assert int(response[0]) == 2

    def quit(self):
        self.command('quit')
        try:
            self._process.wait(1)
        except subprocess.TimeoutExpired:
            self._process.terminate()

        self._process = None

    def list_commands(self) -> List[str]:
        return self.command('list_commands')

    def name(self) -> str:
        lines = self.command('name')
        assert len(lines) == 1
        return lines[0]

    def version(self):
        lines = self.command('version')
        assert len(lines) == 1
        return lines[0]

    def boardsize(self, size: int):
        assert 5 <= size <= 25
        self.command('boardsize', str(size))

    def clear_board(self):
        self.command('clear_board')

    def komi(self, value: float):
        self.command('komi', str(value))

    def fixed_handicap(self, handicap: int):
        self.command('fixed_handicap', str(handicap))

    def play(self, color: str, move: str):
        self.command('play', color, move)

    def undo(self):
        self.command('undo')

    def time_settings(self,
                      main_time: int,
                      byo_yomi_time: int,
                      byo_yomi_stones: int):
        self.command('time_settings',
                     str(main_time), str(byo_yomi_time), str(byo_yomi_stones))

    # TODO: parse the result
    def final_score(self) -> str:
        lines = self.command('final_score')
        assert len(lines) == 1
        return lines[0]

    def genmove(self, player) -> str:
        lines = self.command('genmove', player)
        assert len(lines) == 1
        return lines[0]

    def showboard(self) -> str:
        lines = self.command('showboard')
        return '\n'.join(lines)

