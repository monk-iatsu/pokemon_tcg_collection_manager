"""
Description:
    a program to convert a non encrypted log file to an encrypted one
Usage:
    python3 post_encrypt.py
"""
import os
import sys
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from getpass import getpass
import clss_base
import clss_pickle
import contextlib
import pickle
import json
import hashlib
from assets import *
import cliTextTools as ctt

API_KEY = ""
NO_RESPONSE = ("n", "0", "no", "")


# noinspection PyGlobalUndefined
def init(api_key: str, iterations: int = 1000000):
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
        msg = "Please enter you pokemontcgapi key. if you do not have one you can get one for free at 'https://dev.pokemontcg.io/': "
        API_KEY = ctt.get_user_input(msg, ctt.STR_TYPE, can_cancel=False)

pltfrm = sys.platform
home = os.environ["HOME"]
documents_dir = os.path.join(home, "Documents")
prog_data = ""
if pltfrm == "linux":
    prog_data = os.path.join(os.path.join(home, ".config"), "POKEMON_TCG_LOG")
elif pltfrm in ["win32", "cygwin", "darwin"]:
    prog_data = os.path.join(os.path.join(home, "Documents"), "POKEMON_TCG_LOG")
else:
    print("your system is not supported. quitting")
    quit(1)


def main():
    """
    Description:
        Gets user data from user, and gives instances of the RqHandle and DbHandle objects
    Parameters
        :return: a tuple of two items consisting of instances of RqHandle and DbHandle
    """
    print("to convert, you will need to make a new password. however, you can use the same one.")
    msg1 = "please enter 1 for json or 2 for pickle (pickle is binary and unreadable outside the program, while json "
    msg2 = "is not)"
    msg = f"{msg1}{msg2}"
    print(msg)
    mode = input(">>> ")
    if mode not in ("1", "2"):
        print("invalid input. please enter 1 or 2")
        try:
            return main()
        except RecursionError:
            print("too many invalid entries, quitting")
            quit()
    print("please enter the name of the user, 'default' for the default insecure no password login")
    user = input(">>> ")
    ext = ""
    if mode == "1":
        ext = ".json"
    elif mode == "2":
        ext = ".pcllog"
    user = f"{user}{ext}"
    log_file = os.path.join(prog_data, user)
    print("Please enter the new password for said user. you can use the same")
    psswrd = getpass(">>> ")
    psswrd = psswrd.encode("utf-8")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256,
        length=32,
        salt="a".encode("utf-8"),
        iterations=ITERATIONS,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(psswrd))
    if mode == "1":
        with open(log_file) as f:
            data = json.load(f)
    elif mode == "2":
        with open(log_file, "rb") as f:
            data = pickle.load(f)
    key_hash = hashlib.sha512(key).hexdigest()
    data["psswrd"] = key_hash
    if mode == "1":
        with open(log_file, "w") as f:
            json.dump(data, f)
    elif mode == "2":
        with open(log_file, "wb") as f:
            pickle.dump(data, f)
    with open(log_file, "rb") as f:
        contents = f.read()
    output = Fernet(key).encrypt(contents)
    with open(log_file, "wb") as f:
        f.write(output)


if __name__ == "__main__":
    main()
