"""
Description:
    a module to test if pokemontcg api can be accessed
Usage:
    as module: "from pokemonCardLogger import test_api_status as pcl_test"
    as program: "python3 test_api_status.py"
"""
import time
from clss_base import RqHandle

SLEEP_TIME = 1


def init(api_key: str):
    # noinspection PyGlobalUndefined
    global API_KEY
    API_KEY = api_key


try:
    from config import *
except ImportError:
    API_KEY = ""
    if __name__ == "__main__":
        print("Please enter you pokemontcgapi key: ")
        API_KEY = input(">>> ")


def main_with_output():
    rq = RqHandle(API_KEY)
    while True:
        try:
            _ = rq.get_card("swsh1-1")
        except ConnectionError:
            time.sleep(SLEEP_TIME)
            print("connection is down")
            continue
        print("connection is up")
        break


def main_without_output():
    rq = RqHandle(API_KEY)
    while True:
        try:
            _ = rq.get_card("swsh1-1")
        except ConnectionError:
            time.sleep(SLEEP_TIME)
            continue
        break


if __name__ == "__main__":
    # main_without_output()
    main_with_output()
    quit()
