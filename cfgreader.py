from config import CONFIG
import sys

section=sys.argv[1]
key=sys.argv[2]
print(CONFIG['default'][section][key])
