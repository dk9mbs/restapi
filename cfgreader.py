from config import CONFIG
import sys

#
# usage: cfgreader.py <section> <key> [<default>]
# Without default a missing section/key raises an error.
#
section=sys.argv[1]
key=sys.argv[2]

if len(sys.argv)>3:
    print(CONFIG['default'].get(section, {}).get(key, sys.argv[3]))
else:
    print(CONFIG['default'][section][key])
