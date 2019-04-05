from goban import run_game, GtpEngine

# gnugo = GtpEngine(['gnugo-3.8/gnugo.exe', '--mode', 'gtp'])
leela1 = GtpEngine(['leela-zero-0.17-win64/leelaz.exe', '-g', '--noponder', '-w',
                   'networks/57499cb9d2f90d5a0c2b1fbd2905a77093a02006bc3620cc69af78a9c3ac4b61.gz',
                   '-b', '0'])
leela2 = GtpEngine(['leela-zero-0.17-win64/leelaz.exe', '-g', '--noponder', '-w',
                   'networks/e6779c9becc10a7e147d3cb9c5177a45d3659f95856cd7199d98d0f9ecaf156e.gz',
                   '--precision', 'single', '-b', '0'])

run_game(leela1, leela2)