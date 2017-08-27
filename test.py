import argparse
from functools import partial

import dsnes


parser = argparse.ArgumentParser()
parser.add_argument("--address", default=0xff9c, type=partial(int, base=0))
parser.add_argument("--state", default=None)
parser.add_argument("--stop-before", default=None, type=partial(int, base=0))
args = parser.parse_args()

project = dsnes.project.load("starfox")
analyser = dsnes.Analyser(project)
try:
    analyser.analyse_function(args.address, args.state, args.stop_before)
except:
    analyser.display()
    print("Processed {} instructions".format(len(analyser.visited)))
    raise
