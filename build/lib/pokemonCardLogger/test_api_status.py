"""
Description:
    a module to test if pokemontcg api can be accessed
Usage:
    as module: "from pokemonCardLogger import test_api_status as pcl_test"
    as program: "python3 test_api_status.py"
"""
import time
from clss_base import RqHandle
import cliTextTools as ctt

SLEEP_TIME = 0.1


def init(api_key: str, sleep_time: (int, float) = 0.1):
    """
    Description:
        sets the module global variables, so it can be used
    :param api_key: string containing the api key for pokemon tcg api
    :param sleep_time: the time to sleep between retries
    :return: None
    """
    # noinspection PyGlobalUndefined
    global API_KEY, SLEEP_TIME
    API_KEY = api_key
    SLEEP_TIME = sleep_time


try:
    from config import *
except ImportError:
    API_KEY = ""
    if __name__ == "__main__":
        msg = "Please enter you pokemontcgapi key. if you do not have one you can get one for free at 'https://dev.pokemontcg.io/': "
        API_KEY = ctt.get_user_input(msg, ctt.STR_TYPE, can_cancel=False)


def with_output():
    """
    Description:
        tests whether the api can be accessed, with output to console
    :return: None
    """
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


def without_output():
    """
    Description:
        tests whether the api can be accessed, without output to console
    :return: None
    """
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
    with_output()
    quit()
