import sys
import os
import contextlib

BASIC_ENERGY = {
    "fy": "Fairy",
    "fg": "Fighting",
    "fr": "Fire",
    "gs": "Grass",
    "lg": "Lightning",
    "ml": "Metal",
    "pc": "Psychic",
    "wr": "Water",
    "ds": "Darkness"
}
ENERGY_TYPES = BASIC_ENERGY
ENERGY_TYPES["dn"] = "Dragon"
ENERGY_TYPES["cs"] = "Colorless"
ENERGY_PRINT_TYPES = ("normal", "reverseHolofoil")
ITERATIONS = 1000000
LRU_CACHE_EXPO = 18

pltfrm = sys.platform
home = os.environ["HOME"]
documents_dir = os.path.join(home, "Documents")
prog_data = ""
if pltfrm == "linux":
    prog_data = os.path.join(os.path.join(home, ".config"), "POKEMON_TCG_LOG")
elif pltfrm in ["win32", "cygwin", "darwin"]:
    prog_data = os.path.join(documents_dir, "POKEMON_TCG_LOG")
else:
    print("your system is not supported. quitting")
    quit(1)
with contextlib.suppress(FileExistsError):
    os.makedirs(prog_data)
main_backup_dir = os.path.join(prog_data, "pcllog.bkp")
main_backup_key = os.path.join(prog_data, "pcllog.txt")
