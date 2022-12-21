"""
Description:
    use to migrate from pickle to json and vise versa
    (Depreciated)
Usage:
    python3 migrate.py
"""
import json
import os
import sys
import pickle
from getpass import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from assets import *
print(" this feature is depreciated. will be removed in the future")

API_KEY = ""
NO_RESPONSE = ("n", "0", "no", "")


# noinspection PyGlobalUndefined
def init(api_key: str, iterations: int = ITERATIONS):
    """
    Description:
        sets the module global variables, so it can be used
    :param api_key: string containing the api key for pokemon tcg api
    :param iterations: iterations used for the password encryption
    :return: None
    """
    global API_KEY, ITERATIONS
    API_KEY = api_key
    ITERATIONS = iterations


try:
    from config import *
except ImportError:

    if __name__ == "__main__":
        print("Please enter you pokemontcgapi key: ")
        API_KEY = input(">>> ")

pltfrm = sys.platform
home = os.environ["HOME"]
if pltfrm == "linux":
    prog_data = os.path.join(os.path.join(home, ".config"), "POKEMON_TCG_LOG")
elif pltfrm in ["win32", "cygwin", "darwin"]:
    prog_data = os.path.join(os.path.join(home, "Documents"), "POKEMON_TCG_LOG")
else:
    print("your system is not supported. quitting")
    quit(1)


def migrate_to_pickle(json_file: str, pickle_file: str):
    """
    Description:
        migrates a log from json format to pickle format
    :param pickle_file: path to the new pickle file
    :param json_file: path to the existing json file
    :return: None
    """
    if not os.path.exists(json_file):
        raise FileNotFoundError
    with open(json_file) as f:
        log_dict = json.load(f)
    with open(pickle_file, "wb") as f:
        pickle.dump(log_dict, f)


def migrate_to_json(pickle_file: str, json_file: str):
    """
    Description:
        migrates a log from pickle format to json format
    :param pickle_file: path to the existing pickle file
    :param json_file: path to the new json file
    :return: None
    """
    if not os.path.exists(pickle_file):
        raise FileNotFoundError
    with open(pickle_file, "rb") as f:
        log_dict = pickle.load(f)
    with open(json_file, "w") as f:
        json.dump(log_dict, f)


def main():
    print("will you migrate from pickle or json, 1 for pickle 2 for json")
    mode = input(">>> ")
    other = ""
    if mode not in ("1", "2"):
        print("invalid input. try again")
        return main()
    if mode == "1":
        mode = ".pcllog"
        other = ".json"
    elif mode == "2":
        mode = ".json"
        other = ".pcllog"
    print("please enter the name of the user you wish to migrate")
    user = input(">>> ")
    print("is the file encrypted? ('y' or 'n')")
    enc = input(">>> ")
    if enc == "y":
        enc = True
        print("please enter the password of the user: ")
        psswrd = getpass(">>> ")
    elif enc == "n":
        enc = False
        psswrd = ""
    else:
        print("invalid entry. try again")
        return main()
    active_file_user = f"{user}{mode}"
    new_file_user = f"{user}{other}"
    new_file_user = os.path.join(prog_data, new_file_user)
    active_file_user = os.path.join(prog_data, active_file_user)
    if not os.path.exists(active_file_user):
        print("file not found. try again")
        return main()
    if enc:
        psswrd = psswrd.encode("utf-8")
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256,
            length=32,
            salt="a".encode("utf-8"),
            iterations=ITERATIONS,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(psswrd))
        with open(active_file_user, "rb") as f:
            content = f.read()
        content = Fernet(key).decrypt(content)
        if mode == ".pcllog":
            try:
                _ = pickle.loads(content)
            except Exception:
                print("password was invalid. try again.")
                return main()
        elif mode == ".json":
            with open("temp.json", "wb") as f:
                f.write(content)
            with open("temp.json") as f:
                try:
                    _ = json.load(f)
                except Exception:
                    print("invalid password. try again.")
                    return main()
        with open(active_file_user, "wb") as f:
            f.write(content)
    if mode == ".pcllog":
        migrate_to_json(active_file_user, new_file_user)
    else:
        migrate_to_pickle(active_file_user, new_file_user)
    if enc:
        with open(new_file_user, "rb") as f:
            content = f.read()
        content = Fernet(key).encrypt(content)
        with open(new_file_user, "wb") as f:
            f.write(content)


if __name__ == "__main__":
    main()
