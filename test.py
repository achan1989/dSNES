import argparse
from functools import partial

import dsnes


parser = argparse.ArgumentParser()
parser.add_argument("--address", default=0xff9c, type=partial(int, base=0))
parser.add_argument("--state", default=None)
parser.add_argument("--stop-before", default=None, type=partial(int, base=0))
parser.add_argument("--profile-load", action="store_true")
args = parser.parse_args()

if args.profile_load:
    import cProfile
    import pstats
    profile = cProfile.Profile()
    profile.runcall(dsnes.project.load, "starfox")
    stats = pstats.Stats(profile).sort_stats("cumtime")

else:
    project = dsnes.project.load("starfox")
    analyser = dsnes.Analyser(project)
    try:
        analyser.analyse_function(args.address, args.state, args.stop_before)
    except:
        analyser.display()
        print("Processed {} instructions".format(len(analyser.visited)))
        raise
