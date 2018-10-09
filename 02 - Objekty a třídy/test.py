import sys
import scorelib
from sys import argv

if len(argv) != 2:
    thisScript = sys.argv[0].split('\\')[-1]
    message = "The program expects to be called with one command-line argument:\n" + \
              f"\t./{thisScript} ./(SCORE_LIB_FILE)\n" + \
              "with SCORE_LIB_FILE being the path to the score library file cointaining the records.\n"
    sys.exit(message)

filename = argv[1]
prints = scorelib.load(filename)

# for p in prints:
#     print(str(p))
