from config import CONFIG
import sys

section=sys.argv[1]
key=sys.argv[2]

if len(sys.argv)>3:
    print(CONFIG['default'].get(section,{}).get(key,sys.argv[3]))
else:
    print(CONFIG['default'][section][key])
