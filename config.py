import os
import sys

PROG_NAME = "pokemon_card_collection_manager"
USER_HOME = os.environ["HOME"]
PLATFORM = sys.platform
if PLATFORM.startswith("linux"):
    PROG_FILES = os.path.join(os.path.join(USER_HOME, ".config"), PROG_NAME)
elif PLATFORM.endswith("win") and not PLATFORM == "darwin":
    PROG_FILES = os.path.join(os.path.join(os.path.join(USER_HOME, "Appdata"), "Roaming"), PROG_NAME)
else:
    PROG_FILES = os.path.join(os.path.join(os.path.join(USER_HOME, "Documents"), ".config"), PROG_NAME)
if not os.path.exists(PROG_FILES):
    os.makedirs(PROG_FILES)
API_KEY = "12345678-1234-1234-1234-123456789ABC"
DEFAULT_FILE = os.path.join(PROG_FILES, "default.db")