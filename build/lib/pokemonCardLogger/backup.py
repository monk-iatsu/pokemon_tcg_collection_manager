import random

from assets import *
import os
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import hashlib
import pickle
import datetime as dt

KEY = None
BACKUP_LIST = {"users": {}, "log": []}
THRESHOLD = None


def _save_():
    with open(main_backup_dir, "wb") as f:
        pickle.dump(BACKUP_LIST, f)


def _read_():
    global BACKUP_LIST
    with open(main_backup_dir, "rb") as f:
        BACKUP_LIST = pickle.load(f, fix_imports=True)


def init():
    if not os.path.exists(main_backup_dir):
        _save_()
    else:
        _read_()
    today = dt.date.today()


def put(file_loc: str, psswrd_hash: str, user: str):
    if not os.path.exists(file_loc):
        return False, False, False, False
    if user not in BACKUP_LIST["users"].keys():
        BACKUP_LIST["users"][user] = psswrd_hash
    user_hash = BACKUP_LIST["users"][user]
    if psswrd_hash != user_hash:
        return False, False, False, False
    with open(file_loc, "rb") as f:
        contents = f.read()
    date = dt.date.today()
    index = 0
    is_updated = False
    for data in BACKUP_LIST["log"]:
        if (
            data["user"] == user
            and data["date"] == date
            and index < data["index"]
        ):
            index = data["index"]
            is_updated = True
    if is_updated or index != 0:
        index = index + 1
    BACKUP_LIST["log"].append({"date": date, "index": index, "user": user, "data": contents})
    _save_()
    return date.month, date.day, date.year, index


def get(file_loc: str, psswrd_hash: str, user: str, day: int, month: int, year: int, index: int):
    if user not in BACKUP_LIST["users"].keys():
        return False
    if psswrd_hash != BACKUP_LIST["users"][user]:
        return False
    date = dt.date(day=day, month=month, year=year)
    if date < THRESHOLD:
        return False
    date = date.isoformat()
    for i in BACKUP_LIST["log"]:
        if i["date"] == date and i["user"] == user and i["index"] == index:
            with open(file_loc, "wb") as f:
                f.write(i["data"])
            return True


def restart_log(psswrd_hash: str, user: str):
    if user not in BACKUP_LIST["users"].keys():
        return False
    if psswrd_hash != BACKUP_LIST["users"][user]:
        return False
    pop_list = [index for index, entry in enumerate(BACKUP_LIST["log"]) if user == entry["user"]]
    for index in pop_list:
        _ = BACKUP_LIST["log"].pop(index)
    return True
