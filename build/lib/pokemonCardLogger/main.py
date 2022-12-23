"""
Description:
    the main program for Pokémon card logger
Usage:
    To run as a program "python3 main.py"
    Fill out the prompts to use.
"""
import cliTextTools as ctt
import contextlib
import os
import sys
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
with contextlib.suppress(FileExistsError):
    os.makedirs(prog_data)


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
        pack_name = rq.get_pack(pack_id)["data"]["name"]
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
        card_data = rq.get_card(card_id)
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


def get_mode():
    """
    Description:
        Asks the user what they wish to do
    Parameters:
        :return: a string stating the option chose by the user
    """
    info = """
please select one of the following:
0:  quit
1:  add card
2:  remove a card from count
3:  delete card from database
4:  list packs
5:  get card count
6:  list log
7:  log size
8:  collection value
9:  card value
10: list login
11: test card validity
12: export to csv
13: import from csv
14: get a cards full price data
15: get full price data on all cards in collection
16: trade with another user
17: get full price data on all cards in collection and giving a total value for each
18: list all the names and ids of energy cards
19: add energy card to the log
20: remove energy card from the log
21: deletes energy card entry from the log
22: gets the count of a given energy card
23: gets the counts of the entire energy log
24: gets the length of the energy card log
"""
    mode = ctt.get_user_input(info, ctt.INT_TYPE)
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
        24: "len energy"
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
        data = rq.get_card(card_id)["data"]
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
    card_name = rq.get_card(card_id)["data"]["name"]
    msg = "Would you like to use print type as well?('y' or 'n')"
    if not ctt.get_user_input(msg, ctt.BOOL_TYPE, can_cancel=False):
        total_qnty = 0
        for print_type, qnty in db.get_card_by_id_only(card_id):
            print(f"\tfor {print_type}, you have {qnty}")
            total_qnty += qnty
        print(f"for all of {card_name}, card id: {card_id}, you have {total_qnty}")
        return
    qnty = db.get_card_qnty(card_id, print_type)
    data = rq.get_card(card_id)["data"]
    name = data["name"]
    pack = data["set"]["name"]
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
        pack_name = rq.get_pack(pack_id)["data"]["name"]
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
        card_data = rq.get_card(card_id)
    except ConnectionError:
        print("Either the card is invalid, or your connection to the api has failed. Try again.")
        return
    print(f"That is a valid card. the card name is {card_data['data']['name']}")


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
        card_name = rq.get_card(card_id)["data"]["name"]
    except ConnectionError:
        print("Your connection to the api has failed. Try again.")
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
    print(f"The size of your logged collection is {len(db)}")


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
        data = rq.get_card(card_id)
        price = data["data"]["tcgplayer"]["prices"][print_type]["market"]
        value = round((value + price), 2)
        card_name = data["data"]["name"]
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
    data = rq.get_card(card_id)
    card_name = data["data"]["name"]
    price = data["data"]["tcgplayer"]["prices"][print_type]["market"]
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
        data = rq.get_card(card_id)["data"]
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
    _, lf = os.path.split(db.logfile)
    user, _ = lf.split(".")
    csv_file = f"pcllog-{user}.csv"
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
    card_id, print_type = get_card_id_and_print_type(rq)
    cd = rq.get_card(card_id)["data"]
    card_name = cd["name"]
    print("")
    for key, price in db.get_full_price_data(card_id, print_type):
        msg = f"The card with card id {card_id} with the card name {card_name}, the price data for {key} is ${price}."
        print(msg)


def get_full_price_in_collection(db: clss_pickle.DbHandle,
                                 rq: (clss_pickle.RqHandle, clss_base.RqHandle),
                                 *args, **kwargs):
    print("")
    for row in db.get_log():
        card_id = row[0]
        print_type = row[1]
        qnty = row[2]
        card_data = rq.get_card(card_id)["data"]
        card_name = card_data["name"]
        msg = f"The card id of the card is {card_id} card name is {card_name}, the current print type is {print_type}:"
        print(msg)
        for key, price in db.get_full_price_data(card_id, print_type):
            msg = f"\tThe price data is {key} has a price of ${price} with a quantity of {qnty} the value of this card is ${round((price * qnty), 2)}"
            print(msg)


def get_full_price_in_collection_and_collection_value(db: clss_pickle.DbHandle,
                                                      rq: (clss_pickle.RqHandle, clss_base.RqHandle),
                                                      *args, **kwargs):
    print("")
    full_collection = {}
    print("The full collection:")
    for row in db.get_log():
        card_id = row[0]
        print_type = row[1]
        qnty = row[2]
        card_data = rq.get_card(card_id)["data"]
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
    other_card_data = rq.get_card(other_card_id)["data"]
    card_data = rq.get_card(card_id)["data"]
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
    for card_id, print_type, qnty in db.get_energy_log():
        energy_name = rq.get_basic_energy(card_id)
        msg = f"the energy card {energy_name} with print type {print_type} has a quantity of {qnty}"
        print(msg)


def energy_log_len(db: clss_pickle.DbHandle, *args, **kwargs):
    qnty = 0
    for _, _, q in db.get_energy_log():
        qnty += q

    msg = f"The length of the energy log is {qnty}"
    print(msg)


def add_energy(db: clss_pickle.DbHandle, rq: (clss_pickle.RqHandle, clss_base.RqHandle), *args, **kwargs):
    card_id, print_type = get_energy_id_and_print_type(rq)
    msg = "How many energy do you wish to add?"
    qnty = ctt.get_user_input(msg, ctt.INT_TYPE, can_cancel=False)
    f"The process was successful: {db.add_energy_card(card_id, print_type, qnty)}"


def get_energy_ids(rq: (clss_pickle.RqHandle, clss_base.RqHandle), *args, **kwargs):
    for card_id, name in rq.get_basic_energy_list():
        print(f"the card id {card_id} is {name} energy")


def remove_energy(db: clss_pickle.DbHandle, rq: (clss_pickle.RqHandle, clss_base.RqHandle), *args, **kwargs):
    card_id, print_type = get_energy_id_and_print_type(rq)
    msg = "How many energy do you wish to remove?"
    qnty = ctt.get_user_input(msg, ctt.INT_TYPE, can_cancel=False)
    f"The process was successful: {db.remove_energy_card(card_id, print_type, qnty)}"


def delete_energy(db: clss_pickle.DbHandle, rq: (clss_pickle.RqHandle, clss_base.RqHandle), *args, **kwargs):
    card_id, print_type = get_energy_id_and_print_type(rq)
    msg = "this is permanent. do yuo wish to continue? ('y' or 'n')"
    if not ctt.get_user_input(msg, ctt.BOOL_TYPE):
        return
    f"The process was successful: {db.delete_energy_card(card_id, print_type)}"


def get_energy(db: clss_pickle.DbHandle, rq: (clss_pickle.RqHandle, clss_base.RqHandle), *args, **kwargs):
    card_id, print_type = get_energy_id_and_print_type(rq)
    qnty = db.get_energy_card(card_id, print_type)
    print(f"the count of energy card {rq.get_basic_energy(card_id)} with print type {print_type} is {qnty}")


def main():
    """
    Description:
        Main Loop
    Parameters:
        :return: None
    """
    print("waiting for api connection")
    test_api_status.init(API_KEY)
    test_api_status.without_output()
    db, rq = get_user()
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
        "len energy": energy_log_len
    }
    while True:
        mode = get_mode()
        func = switch[mode]
        func(db=db, rq=rq)


if __name__ == "__main__":
    main()
