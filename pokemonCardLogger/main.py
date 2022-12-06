"""
Description:
    the main program for Pokémon card logger
Usage:
    To run as a program "python3 main.py"
    Fill out the prompts to use.
"""
import contextlib
import os
import sys
# noinspection PyUnresolvedReferences
import datetime as dt
from getpass import getpass
import clss_base
import clss_json
import clss_pickle
import test_api_status

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
        print("Please enter you pokemontcgapi key: ")
        API_KEY = input(">>> ")

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


def get_card_id_and_print_type(rq: (clss_json.RqHandle, clss_pickle.RqHandle, clss_base.RqHandle)):
    """
    Description:
        Asks the user for a card id and returns the data received from the pokemonTcgApi
    Parameters:
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: the card id from pokemonTcgApi or False if it errors out
    """
    print(
        "please type the pack id of the card. if you dont know what that is run the 5th option from the main menu:"
    )
    pack = input(">>> ")
    try:
        pack_name = rq.get_pack(pack)["data"]["name"]
    except ConnectionError:
        print("invalid pack id. try main menu item 5")
        return False, False
    except TypeError:
        print("canceled.")
        return False, False
    print(f"is the pack name {pack_name}? ('n' or 'y')")
    truth = input(">>> ")
    if truth.lower() in NO_RESPONSE:
        print("then try again")
        try:
            return get_card_id_and_print_type(rq)
        except RecursionError:
            print("too many invalid entries, try again")
            return False, False
    print("please enter the cards collectors number")
    num = input(">>> ")
    card_id = f"{pack}-{num}"
    try:
        card_data = rq.get_card(card_id)
    except ConnectionError:
        print("Error. try again")
        return False, False
    try:
        card_print_types = list(card_data["data"]["tcgplayer"]["prices"].keys())
    except KeyError:
        print("sorry, but that card cannot be logged.")
        return False, False
    card_name = card_data["data"]["name"]
    print("select one of the following for valid print types")
    for index, print_type in enumerate(card_print_types):
        print(f"{index} = {print_type}")
    index = input(">>> ")
    try:
        index = int(index)
    except ValueError:
        print("invalid entry. enter a number. try again")
        try:
            return get_card_id_and_print_type(rq)
        except RecursionError:
            print("too many invalid entries, try again")
            return False, False
    try:
        print_type = card_print_types[index]
    except IndexError:
        print("invalid entry. enter a number in the given range. try again")
        try:
            return get_card_id_and_print_type(rq)
        except RecursionError:
            print("too many invalid entries, try again")
            return False, False
    print(f"is {card_name} the name of the card?('y' or 'n')")
    truth = input(">>> ")
    if truth.lower() in NO_RESPONSE:
        print("then try again.")
        return False, False
    return card_id, print_type


def list_packs(
        db: (clss_json.DbHandle, clss_pickle.DbHandle),
        rq: (clss_json.RqHandle, clss_pickle.RqHandle, clss_base.RqHandle)):
    """
    Description:
        Prints out to console, the list of packs and their pack ids
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle
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
1:  get card count
2:  add card
3:  remove a card from count
4:  delete card from database
5:  list packs
6:  list log
7:  log size
8:  collection value
9:  card value
10: list login
11: test card validity
12: export to csv
"""
    print(info)
    mode = input(">>> ")
    switch = {
        "0": "end prog",
        "1": "get card",
        "2": "add card",
        "3": "remove card",
        "4": "delete entry",
        "5": "list packs",
        "6": "list log",
        "7": "log len",
        "8": "collection value",
        "9": "card value",
        "10": "list login",
        "11": "test card",
        "12": "export csv"
    }
    mode = switch.get(mode, "invalid entry")
    if mode == "invalid entry":
        print("invalid entry try again")
        try:
            return get_mode()
        except RecursionError:
            print("too many invalid entries, quitting")
            return "end"
    return mode


def get_card_log(db: (clss_json.DbHandle, clss_pickle.DbHandle),
                 rq: (clss_json.RqHandle, clss_pickle.RqHandle, clss_base.RqHandle)):
    """
    Description:
        Prints to console the list of the log data
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    print("this may take some time")
    for card_id, print_type, qnty in db.get_log():
        data = rq.get_card(card_id)["data"]
        name = data["name"]
        pack = data["set"]["name"]
        print(f"card name: {name} with print type: {print_type}; the pack of the card is: {pack}; count: {qnty}")


def get_card(db: (clss_json.DbHandle, clss_pickle.DbHandle),
             rq: (clss_json.RqHandle, clss_pickle.RqHandle, clss_base.RqHandle)):
    """
    Description:
        Prints out to the console the data in the log of a specific card
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    print("if you wish to get a card by card id only, enter '0' for print type")
    card_id, print_type = get_card_id_and_print_type(rq)
    if not card_id:
        print("canceled")
        return
    card_name = rq.get_card(card_id)["data"]["name"]
    print("would you like to use print type as well?('y' or 'n')")
    truth = input(">>> ")
    if truth.lower() in NO_RESPONSE:
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


def add_card(db: (clss_json.DbHandle, clss_pickle.DbHandle),
             rq: (clss_json.RqHandle, clss_pickle.RqHandle, clss_base.RqHandle)):
    """
    Description:
        Adds more to the value of a specific card count to the log
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    card_id, print_type = get_card_id_and_print_type(rq)
    if not card_id:
        print("canceled")
        return None
    print("how many would you like to add")
    new_count = input(">>> ")
    try:
        new_count = int(new_count)
    except ValueError:
        print("invalid entry. please try again and enter a number")
        try:
            return add_card(db, rq)
        except RecursionError:
            print("too many invalid entries, try again")
            return None
    success = db.add_card(card_id, new_count, print_type)
    print(f"the process was successful: {success}")


def test_card_validity(
        db: (clss_json.DbHandle, clss_pickle.DbHandle),
        rq: (clss_json.RqHandle, clss_pickle.RqHandle, clss_base.RqHandle)):
    """
    Description:
        asks user for a suspected card id and tests if it is valid
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    print(
        "please type the pack id of the card. if you dont know what that is run the 5th option from the main menu:"
    )
    pack = input(">>> ")
    try:
        pack_name = rq.get_pack(pack)["data"]["name"]
    except ConnectionError:
        print("invalid pack id. try main menu item 5")
        return
    except TypeError:
        print("canceled.")
        return
    print(f"is the pack name {pack_name}? ('n' or 'y')")
    truth = input(">>> ")
    if truth.lower() in NO_RESPONSE:
        print("then try again")
        try:
            return test_card_validity(rq)
        except RecursionError:
            print("too many invalid entries, try again")
            return
    print("please enter the cards collectors number")
    num = input(">>> ")
    card_id = f"{pack}-{num}"
    card_data = {}
    try:
        card_data = rq.get_card(card_id)
    except ConnectionError:
        print("that is not a valid card.")
        return
    print(f"that is a valid card. the card name is {card_data['data']['name']}")


def remove_card(db: (clss_json.DbHandle, clss_pickle.DbHandle),
                rq: (clss_json.RqHandle, clss_pickle.RqHandle, clss_base.RqHandle)):
    """
    Description:
        Remove from the value of a specific card count to the log
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    card_id, print_type = get_card_id_and_print_type(rq)
    if not card_id:
        print("canceled")
        return None
    print("how many would you like to remove")
    new_count = input(">>> ")
    try:
        new_count = int(new_count)
    except ValueError:
        print("invalid entry. please try again and enter a number")
        try:
            return remove_card(db, rq)
        except RecursionError:
            print("too many invalid entries, try again")
            return None
    success = db.remove_card(card_id, new_count, print_type)
    print(f"the process was successful: {success}")


def delete_card(db: (clss_json.DbHandle, clss_pickle.DbHandle),
                rq: (clss_json.RqHandle, clss_pickle.RqHandle, clss_base.RqHandle)):
    """
    Description:
        Deletes all data from a card in the log
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    card_id, print_type = get_card_id_and_print_type(rq)
    if not card_id:
        print("canceled")
        return
    card_name = rq.get_card(card_id)["data"]["name"]
    print(f"is {card_name} the name of the card?('y' or 'n')")
    truth = input(">>> ")
    if truth.lower() in NO_RESPONSE:
        print("then try again.")
        return
    print(" are you sure you want to do this? it cannot be undone.")
    truth = input("(yes/no)>>> ")
    if truth.lower() not in NO_RESPONSE:
        success = db.delete_card(card_id, print_type)
        print(f"the process was successful: {success}")
    else:
        print("canceled")
        return


def get_user():
    """
    Description:
        Gets user data from user, and gives instances of the RqHandle and DbHandle objects
    Parameters
        :return: a tuple of two items consisting of instances of RqHandle and DbHandle
    """
    if clss_json.API_KEY == "":
        clss_json.init(API_KEY)
    if clss_pickle.API_KEY == "":
        clss_pickle.init(API_KEY)
    msg1 = "please enter 1 for json or 2 for pickle (pickle is binary and unreadable outside the program, while json "
    msg2 = "is not)"
    msg = f"{msg1}{msg2}"
    print(msg)
    mode = input(">>> ")
    rq = None
    db = None
    if mode == "1":
        rq = clss_json.RqHandle(API_KEY)
    elif mode == "2":
        rq = clss_pickle.RqHandle(API_KEY)
    else:
        print("invalid input. please enter 1 or 2")
        try:
            return get_user()
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
    user_file = os.path.join(prog_data, user)
    if user in ["default.json", "default.pcllog"]:
        psswrd = "default"
    else:
        print("Please enter password for said user.")
        psswrd = getpass(">>> ")
    print("is this an encrypted user? ('y' or 'n')")
    enc = input(">>> ")
    enc = enc not in NO_RESPONSE
    try:
        if mode == "1":
            db = clss_json.DbHandle(user_file, psswrd, rq, has_encryption=enc)
        elif mode == "2":
            db = clss_pickle.DbHandle(user_file, psswrd, rq, has_encryption=enc)
    except PermissionError:
        print("Invalid password, try again.")
        try:
            return get_user()
        except RecursionError:
            print("too many invalid entries, quitting")
            quit()
    return db, rq


def len_of_log(
        db: (clss_json.DbHandle, clss_pickle.DbHandle),
        rq: (clss_json.RqHandle, clss_pickle.RqHandle, clss_base.RqHandle)):
    """
    Description:
        prints the length of the log
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    print(f"the size of your logged collection is {len(db)}")


def get_collection_value(
        db: (clss_json.DbHandle, clss_pickle.DbHandle),
        rq: (clss_json.RqHandle, clss_pickle.RqHandle, clss_base.RqHandle)):
    """
    Description:
        prints the log and value of each card as well as the value of the entire collection
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    print("this may take some time")
    value = 0.00
    for card_id, print_type, qnty in db.get_log():
        data = rq.get_card(card_id)
        price = data["data"]["tcgplayer"]["prices"][print_type]["market"]
        value = round((value + price), 2)
        card_name = data["data"]["name"]
        msg1 = f"the value of {card_id} who's name is {card_name} with print type of {print_type} is ${price} times the"
        msg2 = f"quantity of {qnty} the value is {round((price * qnty), 2)}"
        msg = f"{msg1} {msg2}"
        print(msg)
    print(f"the value of your collection is ${value}")


def get_card_value(
        db: (clss_json.DbHandle, clss_pickle.DbHandle),
        rq: (clss_json.RqHandle, clss_pickle.RqHandle, clss_base.RqHandle)):
    """
    Description:
        prints the value of a card
    Parameter:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    card_id, print_type = get_card_id_and_print_type(rq)
    if not card_id and not print_type:
        print("canceled")
        return None
    # noinspection PyUnreachableCode
    data = rq.get_card(card_id)
    card_name = data["data"]["name"]
    price = data["data"]["tcgplayer"]["prices"][print_type]["market"]
    print(f"the value of {card_id} who's name is {card_name} with print type of {print_type} is ${price}")


def list_login(
        db: (clss_json.DbHandle, clss_pickle.DbHandle),
        rq: (clss_json.RqHandle, clss_pickle.RqHandle, clss_base.RqHandle)):
    """
    Description:
        prints out to the user all prior login attempts
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    for day, month, year, hour, minute, second in db.list_failed_logins():
        print(f"an unsuccessful login on {month} / {day} / {year} at {hour} : {minute} : {second}")
    for day, month, year, hour, minute, second in db.list_login():
        print(f"a successful login on {month} / {day} / {year} at {hour} : {minute} : {second}")


def get_log_by_price(
        db: (clss_json.DbHandle, clss_pickle.DbHandle),
        rq: (clss_json.RqHandle, clss_pickle.RqHandle, clss_base.RqHandle)):
    """
    Description:
        gets and prints the log by price. not fully implemented.
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    print("this may take a while. please be patient")
    for card_id, print_type, qnty in db.get_log_by_total_value():
        data = rq.get_card(card_id)["data"]
        name = data["name"]
        pack = data["set"]["name"]
        print(f"card name: {name} with print type: {print_type}; the pack of the card is: {pack}; count: {qnty}")


def to_csv(
        db: (clss_json.DbHandle, clss_pickle.DbHandle),
        rq: (clss_json.RqHandle, clss_pickle.RqHandle, clss_base.RqHandle)):
    """
    Description:
        exports log to csv.
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    print("this may take a while. please wait.")
    _, lf = os.path.split(db.logfile)
    user, _ = lf.split(".")
    csv_file = f"{dt.datetime.now().isoformat()}-{user}.csv"
    db.export_csv(os.path.join(documents_dir, csv_file))
    print(f"the location for the output file is in Documents. it is called: {csv_file}")


def end(
        db: (clss_json.DbHandle, clss_pickle.DbHandle),
        rq: (clss_json.RqHandle, clss_pickle.RqHandle, clss_base.RqHandle)):
    """
    Description:
        cleanly ends the program
    Parameters:
        :param db: an instance of pokemonCardLogger.clss_json.DbHandle
        :param rq: an instance of pokemonCardLogger.clss_json.RqHandle or pokemonCardLogger.clss_pickle.RqHandle
        :return: None
    """
    db.close()
    quit()


def main():
    """
    Description
        Main Loop
    Parameters:
        :return: None
    """
    print("waiting for api connection")
    test_api_status.init(API_KEY)
    test_api_status.main_without_output()
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
        "export csv": to_csv
    }
    while True:
        mode = get_mode()
        func = switch[mode]
        func(db, rq)


if __name__ == "__main__":
    main()
