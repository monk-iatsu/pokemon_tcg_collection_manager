import time
from clss_base import RqHandle

try:
    from config import *
except ImportError:
    API_KEY = ""
    if __name__ != "__main__":

        def init(api_key: str):
            global API_KEY
            API_KEY = api_key
    else:
        print("Please enter you pokemontcgapi key: ")
        API_KEY = input(">>> ")


def main():
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


if __name__ == "__main__":
    main()
    quit()