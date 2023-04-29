from string import digits, ascii_letters
import sys
import os
import contextlib

PROGRAM_NAME = "POKEMON_TCG_LOG"
PLTFRM = sys.platform
HOME = os.environ["HOME"]
DOCUMENTS_DIR = os.path.join(HOME, "Documents")
if PLTFRM == "linux":
    PROG_DATA = os.path.join(os.path.join(HOME, ".config"), PROGRAM_NAME)
elif PLTFRM in ["win32", "cygwin", "darwin"]:
    PROG_DATA = os.path.join(DOCUMENTS_DIR, f".{PROGRAM_NAME}")
else:
    print("your system is not supported. quitting")
    quit(1)
with contextlib.suppress(FileExistsError):
    os.makedirs(PROG_DATA)

API_KEY = os.environ.get("API_KEY", None)

LOADING_STRING = "This may take a while, please wait."
CNCL = "Canceled."

VALID_PRINT_TYPES = {
    0: {
        "attr": "normal",
        "hr": "normal"
    },
    1: {
        "attr": "holofoil",
        "hr": "holofoil"
    },
    2: {
        "attr": "reverseHolofoil",
        "hr": "reverse holofoil"
    },
    3: {
        "attr": "firstEditionNormal",
        "hr": "1st edition normal"
    },
    4: {
        "attr": "firstEditionHolofoil",
        "hr": "1st edition holofoil"
    }
}
BASIC_ENERGY = {
    0: {
        "name": "grass",
        "id": "grs"
    },
    1: {
        "name": "fire",
        "id": "fir"
    },
    2: {
        "name": "water",
        "id": "wtr"
    },
    3: {
        "name": "lightning",
        "id": "ltn"
    },
    4: {
        "name": "psychic",
        "id": "psy"
    },
    5: {
        "name": "fighting",
        "id": "fgt"
    },
    6: {
        "name": "darkness",
        "id": "drk"
    },
    7: {
        "name": "metal",
        "id": "mtl"
    },
    8: {
        "name": "fairy",
        "id": "fry"
    }
}
ENERGY_PRINT_TYPES = (0, 2)

ITERATIONS = 1000000

LRU_CACHE_EXPO = 18
API_KEY_SITE = "'https://dev.pokemontcg.io/'"
CANCEL_WAIT = 10
SALT_LIST = (i for i in f"{digits}{ascii_letters}")
MIN_SEED = 16
MAX_SEED = 32