import time
from clss_base import RqHandle


def init(api_key: str):
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
            time.sleep(10)
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
            time.sleep(5)
            continue
        break


if __name__ == "__main__":
    main_with_output()
    quit()
