import subprocess


class GtpError(Exception):
    pass


class EngineError(Exception):
    pass


class GtpEngine(object):
    def __init__(self, args):
        self._args = args
        self._process = None

    def __del__(self):
        if self._process is not None:
            self.quit()

    def run(self):
        assert self._process is None
        self._process = subprocess.Popen(
            self._args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            bufsize=0)
        self.check_protocol_version()

    def full_name(self):
        return self.name() + ' ' + self.version()

    def init_game(self, size=19, komi=7.5, handicap=0):
        self.boardsize(size)
        self.clear_board()
        self.komi(komi)
        if handicap:
            assert 0 < handicap <= 9
            self.fixed_handicap(handicap)

    def command(self, command, *args):
        assert self._process is not None
        command = command
        command_parts = [command]
        command_parts.extend(args)

        command_str = ' '.join(command_parts)
        command_bytes = bytes(command_str + '\n', 'utf-8')

        print('> {}\n'.format(command_str))
        self._process.stdin.write(command_bytes)
        lines = []
        while True:
            line = self._process.stdout.readline()
            line = line.strip().decode('utf-8')
            if not line:
                break
            print(line)
            lines.append(line)
        print()
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

    def list_commands(self):
        return self.command('list_commands')

    def name(self):
        lines = self.command('name')
        assert len(lines) == 1
        return lines[0]

    def version(self):
        lines = self.command('version')
        assert len(lines) == 1
        return lines[0]
