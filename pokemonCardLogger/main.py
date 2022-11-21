"""
Description:
    the main program for Pokémon card logger
Usage:
    To run as a program "python3 main.py"
    Fill out the prompts to use.
"""
import sys
# noinspection PyUnresolvedReferences
from getpass import getpass
import os
import clss
import clss_alt

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

pltfrm = sys.platform
home = os.environ["HOME"]
if pltfrm == "linux":
    prog_data = os.path.join(os.path.join(home, ".config"), "POKEMON_TCG_LOG")
elif pltfrm == "win32" or pltfrm == "cygwin":
    prog_data = os.path.join(os.path.join(home, "Documents"), "POKEMON_TCG_LOG")
elif pltfrm == "darwin":
    prog_data = os.path.join(os.path.join(home, "Documents"), "POKEMON_TCG_LOG")
else:
    print("your system is not supported. quitting")
    quit(1)
try:
    os.makedirs(prog_data)
except FileExistsError:
    pass


def get_card_id(rq: (clss.RqHandle, clss_alt.RqHandle)):
    """
    Description:
        Asks the user for a card id and returns the data received from the pokemonTcgApi
    Parameters:
        :param rq: an instance of pokemonCardLogger.clss.RqHandle or pokemonCardLogger.clss_alt.RqHandle
        :return: the card id from pokemonTcgApi or False if it errors out
    """
    print(
        "please type the pack id of the card. if you dont know what that is run the 5th option from the main menu:"
    )
    pack = input(">>> ")
    try:
        _ = rq.get_pack(pack)
    except ConnectionError:
        print("invalid pack id. try main menu item 5")
        return False
    print("please enter the cards collectors number")
    num = input(">>> ")
    card_id = f"{pack}-{num}"
    try:
        _ = rq.get_card(card_id)
    except ConnectionError:
        print("Error. try again")
        return False
    return card_id


def list_packs(rq: (clss.RqHandle, clss_alt.RqHandle)):
    """
        Description:
            Prints out to console, the list of packs and their pack ids
        Parameters:
            :param rq: an instance of pokemonCardLogger.clss.RqHandle or pokemonCardLogger.clss_alt.RqHandle
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
0: quit
1: get card count
2: add card
3: remove a card from count
4: delete card from database
5: list packs
6: list log
7: log size
"""
    print(info)
    mode = input(">>> ")
    if mode == "0":
        return "end"
    elif mode == "1":
        return "card"
    elif mode == "2":
        return "add"
    elif mode == "3":
        return "remove"
    elif mode == "4":
        return "delete"
    elif mode == "5":
        return "packs"
    elif mode == "6":
        return "log"
    elif mode == "7":
        return "len"
    else:
        print("invalid entry try again")
        return get_mode()


def get_card_log(db: (clss.DbHandle, clss_alt.DbHandle), rq: (clss.RqHandle, clss_alt.RqHandle)):
    """
    Description:
        Prints to console the list of the log data
    Parameters:
        :param db: an instance of pokemonCardLogger.clss.DbHandle
        :param rq: an instance of pokemonCardLogger.clss.RqHandle or pokemonCardLogger.clss_alt.RqHandle
        :return: None
    """
    for qnty, card_id in db.get_log():
        data = rq.get_card(card_id)["data"]
        name = data["name"]
        pack = data["set"]["name"]
        print(f"card name: {name}; the pack of the card is: {pack}; count: {qnty}")


def get_card(db: (clss.DbHandle, clss_alt.DbHandle), rq: (clss.RqHandle, clss_alt.RqHandle)):
    """
    Description:
        Prints out to the console the data in the log of a specific card
    Parameters:
        :param db: an instance of pokemonCardLogger.clss.DbHandle
        :param rq: an instance of pokemonCardLogger.clss.RqHandle or pokemonCardLogger.clss_alt.RqHandle
        :return: None
    """
    card_id = get_card_id(rq)
    if not card_id:
        print("canceled")
        return
    card_name = rq.get_card(card_id)["data"]["name"]
    print(f"is {card_name} the name of the card?('y' or 'n')")
    truth = input(">>> ")
    if truth.lower() == "n":
        print("then try again.")
        return
    qnty = db.get_card_qnty(card_id)
    data = rq.get_card(card_id)["data"]
    name = data["name"]
    pack = data["set"]["name"]
    print(f"the card {name} in pack {pack} quantity is: {qnty}")


def add_card(db: (clss.DbHandle, clss_alt.DbHandle), rq: (clss.RqHandle, clss_alt.RqHandle)):
    """
    Description:
        Adds more to the value of a specific card count to the log
    Parameters:
        :param db: an instance of pokemonCardLogger.clss.DbHandle
        :param rq: an instance of pokemonCardLogger.clss.RqHandle or pokemonCardLogger.clss_alt.RqHandle
        :return: None
    """
    card_id = get_card_id(rq)
    if not card_id:
        print("canceled")
        return None
    card_name = rq.get_card(card_id)["data"]["name"]
    print(f"is {card_name} the name of the card?('y' or 'n')")
    truth = input(">>> ")
    if truth.lower() == "n":
        print("then try again.")
        return
    print("how many would you like to add")
    new_count = input(">>> ")
    try:
        new_count = int(new_count)
    except ValueError:
        print("invalid entry. please try again and enter a number")
        return add_card(db, rq)
    success = db.add_card(card_id=card_id, qnty=new_count)
    print(f"the process was successful: {success}")


def remove_card(db: (clss.DbHandle, clss_alt.DbHandle), rq: (clss.RqHandle, clss_alt.RqHandle)):
    """
    Description:
        Remove from the value of a specific card count to the log
    Parameters:
        :param db: an instance of pokemonCardLogger.clss.DbHandle
        :param rq: an instance of pokemonCardLogger.clss.RqHandle or pokemonCardLogger.clss_alt.RqHandle
        :return: None
    """
    card_id = get_card_id(rq)
    if not card_id:
        print("canceled")
        return None
    card_name = rq.get_card(card_id)["data"]["name"]
    print(f"is {card_name} the name of the card?('y' or 'n')")
    truth = input(">>> ")
    if truth.lower() == "n":
        print("then try again.")
        return
    print("how many would you like to remove")
    new_count = input(">>> ")
    try:
        new_count = int(new_count)
    except ValueError:
        print("invalid entry. please try again and enter a number")
        return remove_card(db, rq)
    success = db.remove_card(card_id, new_count)
    print(f"the process was successful: {success}")


def delete_card(db: (clss.DbHandle, clss_alt.DbHandle), rq: (clss.RqHandle, clss_alt.RqHandle)):
    """
    Description:
        Deletes all data from a card in the log
    Parameters:
        :param db: an instance of pokemonCardLogger.clss.DbHandle
        :param rq: an instance of pokemonCardLogger.clss.RqHandle or pokemonCardLogger.clss_alt.RqHandle
        :return: None
    """
    card_id = get_card_id(rq)
    if not card_id:
        print("canceled")
        return
    card_name = rq.get_card(card_id)["data"]["name"]
    print(f"is {card_name} the name of the card?('y' or 'n')")
    truth = input(">>> ")
    if truth.lower() == "n":
        print("then try again.")
        return
    print(" are you sure you want to do this? it cannot be undone.")
    truth = input("(yes/no)>>> ")
    if truth == "yes":
        success = db.delete_card(card_id)
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
    print("please enter 1 for json or 2 for pickle (pickle is still pre alpha and experimental)")
    mode = input(">>> ")
    if mode == "1":
        rq = clss.RqHandle(API_KEY)
    elif mode == "2":
        rq = clss_alt.RqHandle(API_KEY)
    else:
        print("invalid input. please enter 1 or 2")
        return get_user()
    print("please enter the name of the user, 'default' for the default insecure login")
    user = input(">>> ")
    if mode == "1":
        ext = ".json"
    elif mode == "2":
        ext = ".pcllog"
    user = f"{user}{ext}"
    user_file = os.path.join(prog_data, user)
    if user == "default.json" or user == "default.pcllog":
        psswrd = "default"
    else:
        print("Please enter password for said user.")
        psswrd = getpass(">>> ")
    try:
        if mode == "1":
            db = clss.DbHandle(user_file, psswrd, rq)
        elif mode == "2":
            db = clss_alt.DbHandle(user_file, psswrd, rq)
    except PermissionError:
        print("Invalid password, try again.")
        return get_user()
    return db, rq


def len_of_log(db: (clss.DbHandle, clss_alt.DbHandle)):
    print(f"the size of your logged collection is {len(db)}")


def main():
    """
    Description
        Main Loop
    Parameters:
        :return: None
    """
    db, rq = get_user()
    while True:
        mode = get_mode()
        if mode == "add":
            add_card(db, rq)
        elif mode == "remove":
            remove_card(db, rq)
        elif mode == "card":
            get_card(db, rq)
        elif mode == "delete":
            delete_card(db, rq)
        elif mode == "packs":
            list_packs(rq)
        elif mode == "log":
            get_card_log(db, rq)
        elif mode == "len":
            len_of_log(db)
        elif mode == "end":
            break
    db.close()


if __name__ == "__main__":
    main()
