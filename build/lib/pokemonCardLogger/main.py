"""
Description:
    the main program for Pokémon card logger
Usage:
    To run as a program "python3 main.py"
    Fill out the prompts to use.
"""
import cliTextTools as ctt
import os
# noinspection PyUnresolvedReferences
import datetime as dt
from getpass import getpass
import clss_base
import clss_pickle
import test_api_status
import cryptography
from assets import *

API_KEY = ""
NO_RESPONSE = ("n", "0", "no", "")


# noinspection PyGlobalUndefined
def init(api_key: str):
    global API_KEY
    API_KEY = api_key


try:
    from config import *
except ImportError:

    if __name__ == "__main__":
        msg = "Please enter you pokemontcgapi key. if you do not have one you can get one for free at 'https://dev.pokemontcg.io/':"
        API_KEY = ctt.get_user_input(msg, ctt.STR_TYPE, can_cancel=False)


def get_card_id_and_print_type(rq: (clss_pickle.RqHandle, clss_base.RqHandle), *args, **kwargs):
    """
    Description:
        Asks the user for a card id and returns the data received from the pokemonTcgApi
    Parameters:
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: the card id from pokemonTcgApi or False if it errors out
    """
    msg = "Please type the pack id of the card. If you dont know what that is run the 5th option from the main menu:"
    pack_id = ctt.get_user_input(msg, ctt.STR_TYPE)
    if pack_id is None:
        return False, False
    try:
        pack_name = rq.get_pack(pack_id, select=("name", ))["data"]["name"]
    except ConnectionError:
        print("Either the pack is invalid, or your connection to the api has failed. Try again.")
        return False, False
    msg = f"Is the pack name {pack_name}? ('n' or 'y')"
    if not ctt.get_user_input(msg, ctt.BOOL_TYPE, can_cancel=False):
        print("Then try again.")
        try:
            return get_card_id_and_print_type(rq)
        except RecursionError:
            print("Too many retries. Try again.")
            return False, False
    msg = "Please enter the cards collectors number"
    card_num = ctt.get_user_input(msg, ctt.STR_TYPE, can_cancel=False)
    card_id = f"{pack_id}-{card_num}"
    try:
        card_data = rq.get_card(card_id, select=("name", "tcgplayer"))
    except ConnectionError:
        print("Either the card is invalid, or your connection to the api has failed. Try again.")
        return False, False
    card_name = card_data["data"]["name"]
    msg = f"Is {card_name} the name of the card?('y' or 'n')"
    if not ctt.get_user_input(msg, ctt.BOOL_TYPE, can_cancel=False):
        print("Then try again.")
        return False, False
    try:
        card_print_types = list(card_data["data"]["tcgplayer"]["prices"].keys())
    except KeyError:
        print("Sorry but that card cannot be logged.")
        return False, False
    msg = "Select one of the following for valid print types"
    for index, print_type in enumerate(card_print_types):
        msg = f"{msg}\n{index} = {print_type}"
    index = ctt.get_user_input(msg, ctt.INT_TYPE, can_cancel=False)
    try:
        print_type = card_print_types[index]
    except IndexError:
        print("Invalid entry. Enter a number in the given range. Try again.")
        try:
            return get_card_id_and_print_type(rq)
        except RecursionError:
            print("Too many retries. Try again.")
            return False, False
    return card_id, print_type


def list_packs(rq: (clss_pickle.RqHandle, clss_base.RqHandle), *args, **kwargs):
    """
    Description:
        Prints out to console, the list of packs and their pack ids
    Parameters:
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    for pack_id, name in rq.get_all_sets():
        print(f"the pack {name}'s id is: {pack_id}")


def switch_mode(mode: int = 0):
    """
    Description:
        Asks the user what they wish to do
    Parameters:
        :return: a string stating the option chose by the user
    """
    switch = {
        0: "end prog",
        1: "add card",
        2: "remove card",
        3: "delete entry",
        4: "list packs",
        5: "get card",
        6: "list log",
        7: "log len",
        8: "collection value",
        9: "card value",
        10: "list login",
        11: "test card",
        12: "to csv",
        13: "from csv",
        14: "full price",
        15: "full collection",
        16: "csv trade",
        17: "total collection",
        18: "list energy",
        19: "add energy",
        20: "remove energy",
        21: "delete energy",
        22: "get energy",
        23: "energy log",
        24: "len energy",
        25: "len max",
        26: "init load",
        27: "avg price",
        28: "avg full",
        29: "go back",
        30: "backup put",
        31: "backup get"
    }
    mode = switch.get(mode, "invalid entry")
    if mode == "invalid entry":
        print("Invalid entry try again")
        try:
            return get_mode()
        except RecursionError:
            print("Too many invalid entries. Quitting.")
            return "end"
    return mode


def io_menu():
    menu = """
Import/Export Menu:
    0: Go back
    1: Export
    2: Import
    3: Backup
    4: Restore 
            """
    switch = {
        0: 29,
        1: 12,
        2: 13,
        3: 30,
        4: 31
    }
    mode = switch.get(ctt.get_user_input(menu, ctt.INT_TYPE), 29)
    return switch_mode(mode)


def r_menu():
    menu = """
Resource Menu:
    0: Go back
    1: List packs
    2: List energies
    3: Preload card and pack data (Takes a while, but saves internet usage)
        """
    switch = {
        0: 29,
        1: 4,
        2: 18,
        3: 26
    }
    mode = switch.get(ctt.get_user_input(menu, ctt.INT_TYPE), 29)
    return switch_mode(mode)


def ci_menu():
    menu = """
Collection Info Menu:
    0:  Go Back
    1:  List the log
    2:  Regular card log length
    3:  Collection value using market value
    4:  Collection list using all price data
    5:  Collection value using all price data
    6:  List energy log
    7:  Length of the energy log
    8:  Length of both logs combined
    9:  Average price of the log using market price
    10: Average price of the log using all price data
    """
    switch = {
        0: 29,
        1: 6,
        2: 7,
        3: 8,
        4: 15,
        5: 17,
        6: 23,
        7: 24,
        8: 25,
        9: 27,
        10: 28
    }
    mode = switch.get(ctt.get_user_input(menu, ctt.INT_TYPE), 29)
    return switch_mode(mode)


def gd_menu():
    menu = """
Get Data Menu:
    0: Go back
    1: Get card count
    2: Get energy count
    3: Get card value
    4: Get the full price data of a card
    """
    switch = {
        0: 29,
        1: 5,
        2: 22,
        3: 9,
        4: 14
    }
    mode = switch.get(ctt.get_user_input(menu, ctt.INT_TYPE), 29)
    return switch_mode(mode)


def ard_menu():
    menu = """
Edit Menu:
    0: Go Back
    1: Add card
    2: Remove card
    3: Delete card
    4: Add Energy
    5: Remove Energy
    6: Delete Energy
    7: Trade
    """
    switch = {
        1: 1,
        2: 2,
        3: 3,
        4: 19,
        5: 20,
        6: 21,
        7: 16,
        0: 29
    }
    mode = switch.get(ctt.get_user_input(menu, ctt.INT_TYPE), 29)
    return switch_mode(mode)


def menu_mode():
    menu = """
MAIN MENU:
    0: Quit
    1: Edit Cards.
    2: Get Data.
    3: Collection Info.
    4: Import Export.
    5: Resources.
    """
    main_menu = {
        0: switch_mode,
        1: ard_menu,
        2: gd_menu,
        3: ci_menu,
        4: io_menu,
        5: r_menu
    }
    func = main_menu.get(ctt.get_user_input(menu, ctt.INT_TYPE), 0)
    return func()


def get_card_log(db: clss_pickle.DbHandle,
                 rq: (clss_pickle.RqHandle, clss_base.RqHandle),
                 *args, **kwargs):
    """
    Description:
        Prints to console the list of the log data
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    print("This may take some time")
    for card_id, print_type, qnty in db.get_log():
        try:
            data = rq.get_card(card_id, select=("name", "set"))["data"]
        except ConnectionError:
            print("Connection Error. Try again.")
            return
        name = data["name"]
        pack = data["set"]["name"]
        print(f"card name: {name} with print type: {print_type}; the pack of the card is: {pack}; count: {qnty}")


def get_card(db: clss_pickle.DbHandle,
             rq: (clss_pickle.RqHandle, clss_base.RqHandle),
             *args, **kwargs):
    """
    Description:
        Prints out to the console the data in the log of a specific card
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    print("If you wish to get a card by card id only, enter '0' for print type, otherwise enter the correct print type")
    card_id, print_type = get_card_id_and_print_type(rq)
    if not card_id:
        return
    try:
        data = rq.get_card(card_id, select=("name", "set"))["data"]
        name = data["name"]
        pack = data["set"]["name"]
    except ConnectionError:
        print("Connection Error. Try again.")
        return
    msg = "Would you like to use print type as well?('y' or 'n')"
    if not ctt.get_user_input(msg, ctt.BOOL_TYPE, can_cancel=False):
        total_qnty = 0
        for print_type, qnty in db.get_card_by_id_only(card_id):
            print(f"\tfor {print_type}, you have {qnty}")
            total_qnty += qnty
        print(f"for all of {card_name}, card id: {card_id}, you have {total_qnty}")
        return
    qnty = db.get_card_qnty(card_id, print_type)
    print(f"the card {name} in pack {pack} quantity is: {qnty}")


def add_card(db: clss_pickle.DbHandle,
             rq: (clss_pickle.RqHandle, clss_base.RqHandle),
             *args, **kwargs):
    """
    Description:
        Adds more to the value of a specific card count to the log
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    card_id, print_type = get_card_id_and_print_type(rq)
    if not card_id:
        return None
    msg = "how many would you like to add."
    new_count = ctt.get_user_input(msg, ctt.INT_TYPE, can_cancel=False)
    print(f"the process was successful: {db.add_card(card_id, new_count, print_type)}")


def test_card_validity(rq: (clss_pickle.RqHandle, clss_base.RqHandle), *args, **kwargs):
    """
    Description:
        asks user for a suspected card id and tests if it is valid
    Parameters:
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    msg = "Please type the pack id of the card. If you dont know what that is run the 5th option from the main menu:"
    pack_id = ctt.get_user_input(msg, ctt.STR_TYPE)
    if pack_id is None:
        print("Canceled.")
        return
    try:
        pack_name = rq.get_pack(pack_id, select=("name", ))["data"]["name"]
    except ConnectionError:
        print("Either the pack is invalid, or your connection to the api has failed. Try again.")
        return
    msg = f"Is the pack name {pack_name}? ('n' or 'y')"
    if not ctt.get_user_input(msg, ctt.BOOL_TYPE, can_cancel=False):
        print("Then try again")
        try:
            return test_card_validity(rq, args, kwargs)
        except RecursionError:
            print("too many invalid entries, try again")
            return
    msg = "Please enter the cards collectors number"
    num = ctt.get_user_input(msg, ctt.STR_TYPE)
    if num is None:
        print("Canceled.")
        return
    card_id = f"{pack_id}-{num}"
    card_data = {}
    try:
        card_data = rq.get_card(card_id, select=("name", ))["data"]
    except ConnectionError:
        print("Either the card is invalid, or your connection to the api has failed. Try again.")
        return
    print(f"That is a valid card. the card name is {card_data['name']}")


def remove_card(db: clss_pickle.DbHandle,
                rq: (clss_pickle.RqHandle, clss_base.RqHandle),
                *args, **kwargs):
    """
    Description:
        Remove from the value of a specific card count to the log
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    card_id, print_type = get_card_id_and_print_type(rq)
    if not card_id:
        print("Canceled.")
        return
    msg = "How many would you like to remove"
    new_count = ctt.get_user_input(msg, ctt.INT_TYPE, can_cancel=False)
    print(f"the process was successful: {db.remove_card(card_id, new_count, print_type)}")


def delete_card(db: clss_pickle.DbHandle,
                rq: (clss_pickle.RqHandle, clss_base.RqHandle),
                *args, **kwargs):
    """
    Description:
        Deletes all data from a card in the log
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    card_id, print_type = get_card_id_and_print_type(rq)
    if not card_id:
        print("Canceled")
        return
    try:
        card_name = rq.get_card(card_id, select=("name", ))["data"]["name"]
    except ConnectionError:
        print("Your connection to the api has failed. Try again.")
        return
    msg = f"is {card_name} the name of the card?('y' or 'n')"
    if not ctt.get_user_input(msg, ctt.BOOL_TYPE, can_cancel=False):
        print("Then try again.")
        return
    msg = "are you sure you want to do this? it cannot be undone. ('y' or 'n')"
    if ctt.get_user_input(msg, ctt.BOOL_TYPE, can_cancel=False):
        print(f"the process was successful: {db.delete_card(card_id, print_type)}")
    else:
        print("Canceled.")
        return


def get_user():
    """
    Description:
        Gets user data from user, and gives instances of the RqHandle and DbHandle objects
    Parameters
        :return: a tuple of two items consisting of instances of RqHandle and DbHandle
    """
    if clss_pickle.API_KEY == "":
        clss_pickle.init(API_KEY)
    db = None
    rq = clss_pickle.RqHandle(API_KEY)
    msg = "Please enter the name of the user. Enter 'default' for the default insecure no password login"
    user = ctt.get_user_input(msg, ctt.STR_TYPE, can_cancel=False)
    user = f"{user}.pcllog"
    user_file = os.path.join(prog_data, user)
    if user in ["default.json", "default.pcllog"]:
        psswrd = "default"
    print("Please enter password for said user.")
    psswrd = getpass(">>> ")
    if not os.path.exists(user_file):
        db = clss_pickle.DbHandle(user_file, psswrd, rq)
        return db, rq
    try:
        db = clss_pickle.DbHandle(user_file, psswrd, rq)
    except cryptography.fernet.InvalidToken:
        print("Invalid password. Try again.")
        try:
            return get_user()
        except RecursionError:
            print("Too many invalid entries. Quitting")
            quit()
    return db, rq


def len_of_log(db: clss_pickle.DbHandle, *args, **kwargs):
    """
    Description:
        prints the length of the log
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :return: None
    """
    print(f"The size of your logged collection is {db.reg_log_size}")


def get_collection_value(db: clss_pickle.DbHandle,
                         rq: (clss_pickle.RqHandle, clss_base.RqHandle),
                         *args, **kwargs):
    """
    Description:
        prints the log and value of each card as well as the value of the entire collection
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    print("This may take some time. Please wait.")
    value = 0.00
    for card_id, print_type, qnty in db.get_log():
        try:
            data = rq.get_card(card_id, select=("name", "tcgplayer"))["data"]
        except ConnectionError:
            print("Connection Error. Try again.")
            return
        price = data["tcgplayer"]["prices"][print_type]["market"]
        value = round((value + price), 2)
        card_name = data["name"]
        msg1 = f"The value of {card_id} who's name is {card_name} with print type of {print_type} is ${price} times the"
        temp = 0
        for _ in range(qnty):
            temp = temp + price
        msg2 = f"Quantity of {qnty} the value is ${round(temp, 2)}"
        msg = f"{msg1} {msg2}"
        print(msg)
    print(f"\nThe value of your collection is ${value}")


def get_card_value(rq: (clss_pickle.RqHandle, clss_base.RqHandle), *args, **kwargs):
    """
    Description:
        prints the value of a card
    Parameter:
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    card_id, print_type = get_card_id_and_print_type(rq)
    if not card_id and not print_type:
        print("Canceled.")
        return None
    # noinspection PyUnreachableCode
    try:
        data = rq.get_card(card_id, select=("name", "tcgplayer"))["data"]
    except ConnectionError:
        print("Connection Error. Try again.")
        return
    card_name = data["name"]
    price = data["tcgplayer"]["prices"][print_type]["market"]
    print(f"The value of {card_id} who's name is {card_name} with print type of {print_type} is ${price}")


def list_login(db: clss_pickle.DbHandle,
               *args, **kwargs):
    """
    Description:
        prints out to the user all prior login attempts
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :return: None
    """
    for day, month, year, hour, minute, second in db.list_login():
        print(f"A successful login on {month} / {day} / {year} at {hour} : {minute} : {second}")


def get_log_by_price(db: clss_pickle.DbHandle,
                     rq: (clss_pickle.RqHandle, clss_base.RqHandle),
                     *args, **kwargs):
    """
    Description:
        gets and prints the log by price. not fully implemented.
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    print("This may take a while. Please be patient")
    for card_id, print_type, qnty in db.get_log_by_total_value():
        try:
            data = rq.get_card(card_id, select=("name", "set"))["data"]
        except ConnectionError:
            print("Connection Error. Try again.")
            return
        name = data["name"]
        pack = data["set"]["name"]
        print(f"card name: {name} with print type: {print_type}; the pack of the card is: {pack}; count: {qnty}")


def to_csv(db: clss_pickle.DbHandle, *args, **kwargs):
    """
    Description:
        exports log to csv.
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :return: None
    """
    print("This may take a while. Please wait.")
    csv_file = f"pcllog-{db.user}.csv"
    db.export_csv(os.path.join(documents_dir, csv_file))
    print(f"\nThe location for the output file is in Documents. it is called: {csv_file}")


def end(db: clss_pickle.DbHandle, *args, **kwargs):
    """
    Description:
        cleanly ends the program
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :return: None
    """
    db.close()
    quit()


def from_csv(db: clss_pickle.DbHandle, *args, **kwargs):
    """
    Description:
        imports data to the log from csv
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :return: None
    """
    print(
        "Importing data from csv overwrites existing data. if there is a card that you already have in the log, it will be deleted.")
    msg = "please enter the full path to the csv file containing the data."
    path = ctt.get_user_input(msg, ctt.STR_TYPE)
    if path is None:
        print("Canceled.")
        return
    if not os.path.exists(path):
        print("Invalid path. Try again.")
        try:
            return from_csv(db, args, kwargs)
        except RecursionError:
            print("To many retries. Try again.")
            return
    print("This may take a while. Please wait.")
    print(f"The process was successful: {db.import_csv(path, output=True)}")


def get_card_full_price(db: clss_pickle.DbHandle,
                        rq: (clss_pickle.RqHandle, clss_base.RqHandle),
                        *args, **kwargs):
    """
    Description:
        gets the full price data of a card and prints it out to the user
    Parameters:
        :param db: instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :param rq: instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    card_id, print_type = get_card_id_and_print_type(rq)
    if not card_id:
        print("Canceled")
        return
    try:
        cd = rq.get_card(card_id, select=("name", ))["data"]
    except ConnectionError:
        print("Connection Error. Try again.")
        return
    card_name = cd["name"]
    print("")
    for key, price in db.get_full_price_data(card_id, print_type):
        msg = f"The card with card id {card_id} with the card name {card_name}, the price data for {key} is ${price}."
        print(msg)


def get_full_price_in_collection(db: clss_pickle.DbHandle,
                                 rq: (clss_pickle.RqHandle, clss_base.RqHandle),
                                 *args, **kwargs):
    """
    Description:
        gets the full price data of the full collection and prints it out to the user
    Parameters:
        :param db: instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :param rq: instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    print("")
    for row in db.get_log():
        card_id = row[0]
        print_type = row[1]
        qnty = row[2]
        try:
            card_data = rq.get_card(card_id, select=("name", ))["data"]
        except ConnectionError:
            print("Connection Error. Try again.")
            return
        card_name = card_data["name"]
        msg = f"The card id of the card is {card_id} card name is {card_name}, the current print type is {print_type}:"
        print(msg)
        for key, price in db.get_full_price_data(card_id, print_type):
            msg = f"\tThe price data is {key} has a price of ${price} with a quantity of {qnty} the value of this card is ${round((price * qnty), 2)}"
            print(msg)


def get_full_price_in_collection_and_collection_value(db: clss_pickle.DbHandle,
                                                      rq: (clss_pickle.RqHandle, clss_base.RqHandle),
                                                      *args, **kwargs):
    """
    Description:
        Gets the full log, and gets full price of each card, while adding them all up and prints it out to the user.
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :param rq: instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    print("")
    full_collection = {}
    print("The full collection:")
    for card_id, print_type, qnty in db.get_log():
        try:
            card_data = rq.get_card(card_id, select=("name", ))["data"]
        except ConnectionError:
            print("Connection Error. Try again.")
            return
        card_name = card_data["name"]
        msg = f"\tThe card id of the card is {card_id} card name is {card_name}, the current print type is {print_type}:"
        print(msg)
        for key, price in db.get_full_price_data(card_id, print_type):
            msg = f"\t\tThe price data is {key} has a price of ${price} with a quantity of {qnty} the value of this card is ${round((price * qnty), 2)}"
            print(msg)
            fc = full_collection.get(key, {"fc": 0})["fc"]
            fc = round(((price * qnty) + fc), 2)
            count = full_collection.get(key, {"count": 0})["count"]
            full_collection[key] = {"fc": fc, "count": count+qnty}
    print("All prices put together: ")
    for key, value in full_collection.items():
        count = value["count"]
        price = value["fc"]
        print(f"\tAll {key} prices added up = ${round((price * qnty), 2)}. There are {count} cards with this price category")


def trade(db: clss_pickle.DbHandle,
          rq: (clss_pickle.RqHandle, clss_base.RqHandle),
          *args, **kwargs):
    """
    Description:
        trades a card with another user using a csv file for user two
    Parameters:
        :param db: instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :param rq:  instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    print("")
    other_db = clss_pickle.DbHandle(":memory:", "default", rq)
    msg = "Please enter the path to the user two's csv file. Enter nothing to try again later."
    csv_path = ctt.get_user_input(msg, ctt.STR_TYPE)
    if csv_path is None:
        print("Canceled.")
        return
    if not os.path.exists(csv_path) or os.path.isdir(csv_path):
        print("Invalid path. Try using full path. Try again.")
        return
    print("Adding csv to memory. This may take a while. Please wait")
    other_db.import_csv(csv_path)
    print("Select a card for user one")
    card_id, print_type = get_card_id_and_print_type(rq)
    msg = "How many?"
    qnty = ctt.get_user_input(msg, ctt.INT_TYPE)
    print("Select a card for user two")
    other_card_id, other_print_type = get_card_id_and_print_type(rq)
    other_qnty = ctt.get_user_input(msg, ctt.INT_TYPE)
    other_card_data = rq.get_card(other_card_id, select=("tcgplayer", ))["data"]
    card_data = rq.get_card(card_id, select=("tcgplayer", ))["data"]
    other_price_data = other_card_data["tcgplayer"]["prices"][print_type]["market"]
    price_data = card_data["tcgplayer"]["prices"][print_type]["market"]
    trade_value = round((price_data - other_price_data), 2)
    if trade_value < 0:
        trade_value = round((other_price_data - price_data), 2)
        print(f"the trade value is tipped in favor of user two by ${trade_value}")
    else:
        print(f"the trade value is tipped in favor of user one by ${trade_value}")
    msg = "do you wish to continue?"

    if not ctt.get_user_input(msg, ctt.BOOL_TYPE):
        print("Canceled.")
        return
    trade_code = db.trade(other_db, other_card_id, other_print_type, other_qnty, card_id, print_type, qnty)
    if trade_code != clss_base.TRADE_SUCCESS:
        print(f"Process failed. Fail code {trade_code}")
    else:
        print("Process successful. Saving user two's updated csv.")
        other_db.export_csv(csv_path)


def get_energy_id_and_print_type(rq: (clss_pickle.RqHandle, clss_base.RqHandle), *args, **kwargs):
    """
    Description:
        gets an energy and print type from the user
    Parameters:
        :param rq: instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    print("")
    msg = "please enter the card id of the energy card. please use option 18 from the main menu. enter nothing to cancel"
    card_id = ctt.get_user_input(msg, ctt.STR_TYPE)
    if card_id is None:
        print("Canceled")
        return None
    if not rq.validate_basic_energy(card_id):
        print("Invalid card id. Try again. See option 18 from the main menu")
        try:
            return get_energy_id_and_print_type(rq)
        except RecursionError:
            print("Too many invalid entries. Try again.")
    msg = "please select a print type from one of the following options: "
    for i, print_type in enumerate(ENERGY_PRINT_TYPES):
        msg = f"{msg}\n{i} = {print_type}"
    index = ctt.get_user_input(msg, ctt.INT_TYPE, can_cancel=False)
    print_type = ENERGY_PRINT_TYPES[index]
    return card_id, print_type


def get_energy_log(db: clss_pickle.DbHandle, rq: (clss_pickle.RqHandle, clss_base.RqHandle), *args, **kwargs):
    """
    Description:
        prints out to the user the logged energy cards
    Parameters:
        :param db: instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :param rq: instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    print("")
    for card_id, print_type, qnty in db.get_energy_log():
        energy_name = rq.get_basic_energy(card_id)
        msg = f"the energy card {energy_name} with print type {print_type} has a quantity of {qnty}"
        print(msg)


def energy_log_len(db: clss_pickle.DbHandle, *args, **kwargs):
    """
    Description:
        prints out the size of the energy log
    Parameters:
        :param db: instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :return: None
    """
    print(f"\nThe length of the energy log is {db.energy_log_size}")


def add_energy(db: clss_pickle.DbHandle, rq: (clss_pickle.RqHandle, clss_base.RqHandle), *args, **kwargs):
    """
    Description:
        adds to the energy log
    Parameters:
        :param db: instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :param rq: instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    print("")
    card_id, print_type = get_energy_id_and_print_type(rq)
    msg = "How many energy do you wish to add?"
    qnty = ctt.get_user_input(msg, ctt.INT_TYPE, can_cancel=False)
    f"The process was successful: {db.add_energy_card(card_id, print_type, qnty)}"


def get_energy_ids(rq: (clss_pickle.RqHandle, clss_base.RqHandle), *args, **kwargs):
    """
    Description:
        prints out the energy cards and their ids
    Parameters:
        :param rq: instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    print("")
    for card_id, name in rq.get_basic_energy_list():
        print(f"the card id {card_id} is {name} energy")


def remove_energy(db: clss_pickle.DbHandle, rq: (clss_pickle.RqHandle, clss_base.RqHandle), *args, **kwargs):
    """
    Description:
        removes cards from the energy log
    Parameters:
        :param db: instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :param rq: instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    print("")
    card_id, print_type = get_energy_id_and_print_type(rq)
    msg = "How many energy do you wish to remove?"
    qnty = ctt.get_user_input(msg, ctt.INT_TYPE, can_cancel=False)
    f"The process was successful: {db.remove_energy_card(card_id, print_type, qnty)}"


def delete_energy(db: clss_pickle.DbHandle, rq: (clss_pickle.RqHandle, clss_base.RqHandle), *args, **kwargs):
    """
    Description:
        deletes an entire entry in the energy log
    Parameters
        :param db: instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :param rq: instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    print("")
    card_id, print_type = get_energy_id_and_print_type(rq)
    msg = "this is permanent. do yuo wish to continue? ('y' or 'n')"
    if not ctt.get_user_input(msg, ctt.BOOL_TYPE):
        return
    f"The process was successful: {db.delete_energy_card(card_id, print_type)}"


def get_energy(db: clss_pickle.DbHandle, rq: (clss_pickle.RqHandle, clss_base.RqHandle), *args, **kwargs):
    """
    Description:
        gets an energy count from the energy log
    Parameters:
        :param db: instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :param rq: instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    card_id, print_type = get_energy_id_and_print_type(rq)
    qnty = db.get_energy_card(card_id, print_type)
    print(f"the count of energy card {rq.get_basic_energy(card_id)} with print type {print_type} is {qnty}")


def full_len(db: clss_pickle.DbHandle, *args, **kwargs):
    """
    Description:
        prints out the full length of the log
    Parameters:
        :param db: instance of pokemonCardLogger.clss_json.DbHandle or pokemonCardLogger.clss_pickle.DbHandle
        :return: None
    """
    print(f"\nThe full size of the log including energy log and regular log, is {len(db)}")


def preload_log(db: clss_pickle.DbHandle, rq: (clss_pickle.RqHandle, clss_base.RqHandle), *args, **kwargs):
    print("\nThis may take a while. Please wait.")
    print("Loading packs.")
    try:
        for pid, _ in rq.get_all_sets():
            try:
                _ = rq.get_pack(pid)
                _ = rq.get_pack(pid, select=("name", ))
            except ConnectionError:
                print(f"Failed on pack {pid}. Retrying.")
                try:
                    return preload_log(db, rq)
                except RecursionError:
                    print("Too many retries. Canceled.")
                    return
    except ConnectionError:
        print("Failed to load pack list, trying again.")
        try:
            return preload_log(db, rq)
        except RecursionError:
            print("Too many retries, canceled.")
            return
    print("Loading cards in log.")
    for card_id, _, _ in db.get_log():
        try:
            _ = rq.get_card(card_id)
            _ = rq.get_card(card_id, select=("name", "tcgplayer"))
            _ = rq.get_card(card_id, select=("name", "set"))
            _ = rq.get_card(card_id, select=("name", ))
            _ = rq.get_card(card_id, select=("tcgplayer", ))
        except ConnectionError:
            print(f"Failed on card {card_id}. Retrying.")
            try:
                return preload_log(db, rq)
            except RecursionError:
                print("Too many retries. Canceled.")
                return
    print("Successful log preload.")


def collection_price_average_full(db: clss_pickle.DbHandle, rq: (clss_pickle.RqHandle, clss_base.RqHandle), *args, **kwargs):
    print("")
    full_collection = {}
    print("The full collection:")
    for card_id, print_type, qnty in db.get_log():
        try:
            card_data = rq.get_card(card_id, select=("name", ))["data"]
        except ConnectionError:
            print("Connection Error. Try again.")
            return
        card_name = card_data["name"]
        msg = f"\tThe card id of the card is {card_id} card name is {card_name}, the current print type is {print_type}:"
        print(msg)
        for key, price in db.get_full_price_data(card_id, print_type):
            msg = f"\t\tThe price data is {key} has a price of ${price} with a quantity of {qnty} the value of this card is ${round((price * qnty), 2)}"
            print(msg)
            fc = full_collection.get(key, {"fc": 0})["fc"]
            fc = round(((price * qnty) + fc), 2)
            count = full_collection.get(key, {"count": 0})["count"]
            full_collection[key] = {"fc": fc, "count": count + qnty}
    print("All prices put together: ")
    for key, value in full_collection.items():
        count = value["count"]
        price = value["fc"]
        print(
            f"\tAll {key} prices added up = ${round((price * qnty), 2)}. There are {count} cards with this price category")
        print(f"\tThe average of {key} prices are ${round(((price * qnty) / count), 2)}")


def collection_average_price(db: clss_pickle.DbHandle, rq: (clss_pickle.RqHandle, clss_base.RqHandle), *args, **kwargs):
    print("")
    print("Full collection:")
    t_price = 0
    count = 0
    for card_id, print_type, qnty, price in db.log_with_prices(db.get_log()):
        t_price += price
        count += qnty
        try:
            card_name = rq.get_card(card_id, select=("name", ))["data"]["name"]
        except ConnectionError:
            print("Connection Error. Try again.")
            return
        msg = f"\tThe card {card_id} who's card name is {card_name}, has a price of ${round(price, 2)}, with a quantity of {qnty}, the value is {round((price * qnty), 2)}"
        print(msg)
    print(f"\nThe average market price of your log is ${round((t_price / count), 2)} based on a price of ${round(t_price, 2)} amd a count of {count}")


def dummy(*args, **kwargs):
    pass


def backup(db: clss_pickle.DbHandle, *args, **kwargs):
    print("\nIf you haven't initialized the backup server by backing up or restoring from it, this will take a while to start. Please wait.")
    month, day, year, index = db.save_backup()
    msg = f"the date used is {month}/{day}/{year} at index {index}"
    print(msg)


def restore(db: clss_pickle.DbHandle, *args, **kwargs):
    print("\nIf you haven't initialized the backup server by backing up or restoring from it, this will take a while to start. Please wait.")
    msg = "Enter the month of the restore point:"
    month = ctt.get_user_input(msg, ctt.INT_TYPE, can_cancel=False)
    msg = "Enter what day of the month of the restore point:"
    day = ctt.get_user_input(msg, ctt.INT_TYPE, can_cancel=False)
    msg = "Enter the year of the restore point:"
    year = ctt.get_user_input(msg, ctt.INT_TYPE, can_cancel=False)
    msg = "Enter the index of the restore point:"
    index = ctt.get_user_input(msg, ctt.INT_TYPE, can_cancel=False)
    s = db.reload_backup(index, day, month, year)
    print(f"The process was successful: {s}")


def main():
    """
    Description:
        Main Loop
    Parameters:
        :return: None
    """
    db, rq = get_user()
    print("waiting for api connection")
    rq.wait_for_con()
    switch = {
        "end prog": end,
        "get card": get_card,
        "add card": add_card,
        "remove card": remove_card,
        "delete entry": delete_card,
        "list packs": list_packs,
        "list log": get_card_log,
        "log len": len_of_log,
        "collection value": get_collection_value,
        "card value": get_card_value,
        "list login": list_login,
        "test card": test_card_validity,
        "to csv": to_csv,
        "from csv": from_csv,
        "full price": get_card_full_price,
        "full collection": get_full_price_in_collection,
        "total collection": get_full_price_in_collection_and_collection_value,
        "csv trade": trade,
        "list energy": get_energy_ids,
        "add energy": add_energy,
        "remove energy": remove_energy,
        "delete energy": delete_energy,
        "get energy": get_energy,
        "energy log": get_energy_log,
        "len energy": energy_log_len,
        "len max": full_len,
        "init load": preload_log,
        "avg full": collection_price_average_full,
        "avg price": collection_average_price,
        "go back": dummy,
        "backup put": backup,
        "backup get": restore
    }
    while True:
        mode = menu_mode()
        func = switch[mode]
        func(db=db, rq=rq)


if __name__ == "__main__":
    main()
