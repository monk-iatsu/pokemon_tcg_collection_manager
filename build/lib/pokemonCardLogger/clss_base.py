import contextlib
import os
import requests
import datetime as dt
import csv
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import sys
import hashlib

TRADE_SUCCESS = 0
TRADE_CODE_CARD_NOT_IN_LOG = 1
TRADE_CODE_CARD_DOES_NOT_EXIST = 2
TRADE_CODE_CARD_NOT_IN_LOG_QNTY = 3

API_KEY = ""
ITERATIONS = 1000000


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


class RqHandle:
    """
    Description:
        Handles the pokemonTcgApi data transmission
    """
    card_url = "https://api.pokemontcg.io/v2/cards"
    pack_url = "https://api.pokemontcg.io/v2/sets"

    def __init__(self, api_key: str):
        """
        Description:
            Constructor method
        Parameters:
            :param api_key: the pokemonTcgApi api key
        """
        self.api_key = api_key
        self.headers = {"X-Api-Key": self.api_key}

    def get_card(self, card_id: str):  # sourcery skip: raise-from-previous-error
        """
        Description:
            Requests from pokemonTcgApi the data for a specific card and returns that data as a dictionary
            If the data is bad raises ValueError
        Parameters:
            :param card_id: a string that represents the card according to pokemonTcgApi
            :return: dict of the data from pokemonTcgApi
        """
        try:
            data = requests.get(f"{self.card_url}/{card_id}", headers=self.headers)
        except requests.exceptions.ConnectionError:
            raise ConnectionError
        if data.ok:
            return data.json()
        else:
            raise ConnectionError

    def get_pack(self, pack_id: str):
        """
        Description:
            Requests from pokemonTcgApi the data for a specific pack and returns that data as a dictionary
            If the data is bad raises ValueError
        Parameters:
            :param pack_id: a string that represents the pack according to pokemonTcgApi
            :return: dict of the data from pokemonTcgApi
        """
        try:
            data = requests.get(f"{self.pack_url}/{pack_id}", headers=self.headers)
        except requests.exceptions.ConnectionError:
            raise ConnectionError
        if data.ok:
            return data.json()
        else:
            raise ConnectionError

    def get_all_sets(self):
        """
        Description:
            Requests a list of packs from pokemonTcgApi and returns a generator
            The generator yields a tuple with the id of the pack and the packs name
        Parameters:
            :return: generator consisting of a tuple of pack id and pack name
        """
        try:
            data = requests.get(self.pack_url, headers=self.headers)
        except requests.exceptions.ConnectionError:
            raise ConnectionError
        if not data.ok:
            raise ConnectionError
        for i in data.json()["data"]:
            yield i["id"], i["name"]

    def __repr__(self):
        return f"RqHandle({self.api_key}"


class DbHandleBase:
    """
    Description:
        stores and organizes the log data in a pickle file
    """

    def __init__(self, file: str, psswrd: str, rq: RqHandle, has_encryption: bool):
        """
        Description:
            Constructor method
        Parameters
            :param file: the path to the database file
            :param psswrd: the password for the database
            :param rq: an instance of RqHandle
        """
        self.has_encryption = has_encryption
        self.is_encrypted = True
        self.logfile = file
        self.psswrd = psswrd
        self.rq = rq
        self.kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256,
            length=32,
            salt="a".encode("utf-8"),
            iterations=ITERATIONS,
            backend=default_backend()
        )
        self.key = base64.urlsafe_b64encode(self.kdf.derive(self.psswrd.encode("utf-8")))
        self.key_hash = hashlib.sha512(self.key).hexdigest()
        if self.logfile == ":memory:":
            self.logdict = {}
            self.first_run()
        elif os.path.exists(self.logfile):
            self.logdict = self.read()
            self.validate()
        else:
            self.logdict = {}
            self.first_run()
        self.login_setup()

    def first_run(self):
        """
        Description:
            Sets up the database if it was freshly created
        Parameters:
            :return: None
        """
        self.logdict = {"psswrd": self.key_hash, "failed_login": [], "login_times": [], "log": {}}
        self.login_setup()
        self.save()

    def validate(self):
        """
        Description:
            Validates the database and password combo. if the password doesn't match, raises ValueError
        Parameters:
            :return: None
        """
        if self.key_hash != self.logdict["psswrd"]:
            raise PermissionError

    def login_setup(self):
        """
        Description:
            Logs the current login to the database
        Parameters:
            :return: None
        """
        date = dt.datetime.now().isoformat()
        self.logdict["login_times"].append(date)
        self.save()

    def add_card(self, card_id: str, qnty: int, print_type: str):
        """
        Description:
            Adds quantity to the card as well as adds a new card to the database
        Parameters:
            :param card_id: the id of the card according to pokemonTcgApi
            :param qnty: the quantity of cards to add. if there is already quantity, it adds to that
            :param print_type: the print type of the card
            :return: None
        """
        card_id_print_type = f"{card_id}.{print_type}"
        if not self.test_card(card_id):
            return False
        if current_qnty := self.get_card_qnty(card_id, print_type):
            qnty += current_qnty
        self.logdict["log"].update({card_id_print_type: qnty})
        self.save()
        return True

    def remove_card(self, card_id: str, qnty: int, print_type: str):
        """
        Description:
            Removes quantity from a card in the log
        Parameters:
            :param card_id: the id of the card according to pokemonTcgApi
            :param qnty: the quantity of cards to remove. if there is already quantity, it subtracts from that
            :param print_type: the print type of the card
            :return: a bool based on if the operation was successful or not
        """
        card_id_print_type = f"{card_id}.{print_type}"
        if not self.test_card(card_id):
            return False
        current_qnty = self.get_card_qnty(card_id, print_type)
        if not current_qnty:
            return False
        qnty = current_qnty - qnty
        qnty = max(qnty, 0)
        self.logdict["log"].update({card_id_print_type: qnty})
        self.save()
        return True

    def delete_card(self, card_id: str, print_type: str):
        """
        Description:
            Deletes a card from the log
        Parameters:
            :param card_id: the id of the card according to pokemonTcgApi
            :param print_type: the print type of the card
            :return: None
        """
        card_id_print_type = f"{card_id}.{print_type}"
        if not self.test_card(card_id):
            return False
        _ = self.logdict["log"].pop(card_id_print_type)
        self.save()
        return True

    def get_card_qnty(self, card_id: str, print_type: str):
        """
        Description:
            Gets and returns the quantity of a given card in the log
        Parameters
            :param card_id: the id of the card according to pokemonTcgApi
            :param print_type: the print type of the card
            :return: The quantity of the card
        """
        card_id_print_type = f"{card_id}.{print_type}"
        if not self.test_card(card_id):
            return 0
        try:
            return self.logdict["log"][card_id_print_type]
        except KeyError:
            return 0

    def get_log(self):
        """
        Description:
            A generator consisting of the log
        Parameters:
            :return: a generator of the rows in the log
        """
        for card_id_print_type, qnty in self.logdict["log"].items():
            card_id, print_type = card_id_print_type.split(".")
            yield card_id, print_type, qnty

    def get_card_by_id_only(self, card_id: str):
        """
        Description:
            gets all cards in collection that match card_id, and creates a generator for each entry where
            print_type is the print type of the entry, and qnty is the quantity of the card
        Parameters:
            :param card_id: the id of the card according to pokemonTcgApi
            :return: generator of tuple print_type and qnty
        """
        for card_id_print_type in self.logdict["log"].keys():
            cid, print_type = card_id_print_type.split(".")
            if card_id == cid:
                qnty = self.logdict["log"][card_id_print_type]
                yield print_type, qnty

    def test_card(self, card_id: str):
        """
        Description:
            Test if a card id is valid
        Parameters:
            :param card_id: the id of the card according to pokemonTcgApi
            :return: bool if the card is valid or not
        """
        try:
            _ = self.rq.get_card(card_id)
            return True
        except ConnectionError:
            return False

    def __len__(self):
        return len(list(self.get_log()))

    def save(self):
        """
        Description:
            to be overwritten
        Parameters:
            :return: None
        """
        pass

    def list_login(self):
        """
        Description:
            a generator of all successful logins
        Parameters:
            :return: a generator of a tuple consisting of the datetime data (day, month, year, hour, minute, second)
        """
        if not self.logdict["login_times"]:
            return (None, None, None, None, None, None), (None, None, None, None, None, None)
        for i in self.logdict["login_times"]:
            d = dt.datetime.fromisoformat(i)
            date = d.date()
            time = d.time()
            day = date.day
            month = date.month
            year = date.year
            hour = time.hour
            minute = time.minute
            second = time.second
            yield day, month, year, hour, minute, second

    def read(self):
        """
        Description:
            to be overwritten
        Parameters:
            :return: None
        """
        return {"psswrd": self.psswrd_hash, "failed_login": [], "login_times": [], "log": {}}

    @staticmethod
    def sort_log_total(item: iter):
        """
        Description:
            sorting function for the prepared log
        Parameters:
            :param item: the item to organize
            :return: the price for which the sort function can sort the log with
        """
        return item[3]

    def sort_log_total_pre(self, log_list: iter):
        """
        Descriptions:
            sorts the log and presents it in the form of a generator
        Parameters:
            :param log_list: a reference to the log
            :return: generator of a tuple of card_id, print_type, qnty, and price
        """
        for row in log_list:
            card_id, print_type, qnty = row
            price = round((self.rq.get_card(card_id)["data"]["tcgplayer"]["prices"][print_type]["market"] * qnty), 2)
            # print(f"card id = {card_id}, print type = {print_type}, qnty = {qnty}, price = {price}")
            yield card_id, print_type, qnty, price

    def get_log_by_total_value(self):
        """
        Description:
            a generator that yields the log in order of price
        Parameters:
            :return: generator of a tuple of card_id, print_type, qnty, and price
        """
        yield from list(list(self.sort_log_total_pre(self.get_log()))).sort(key=self.sort_log_total)

    def export_csv(self, output_file: str, output: bool = True):
        """
        Description:
            exports log to a csv file.
        Parameters:
            :param output: a boolean true if you want output to console
            :param output_file: a path to the file you wish to write to
            :return: None
        """
        if output:
            print("loading cards from log...")
        data = []
        for card_id, print_type, qnty, price in self.sort_log_total_pre(self.get_log()):
            if output:
                msg = f"loading card id {card_id} with print type {print_type} and quantity of {qnty} with a price of"
                msg2 = f"${price}"
                print(f"{msg} {msg2}")
            data.append({"card_id": card_id, "print_type": print_type, "qnty": qnty, "price": price})
        with open(output_file, "w") as f:
            field_name = ["card_id", "print_type", "qnty", "price"]
            csv_writer = csv.DictWriter(f, field_name)
            csv_writer.writeheader()
            for row in data:
                if output:
                    print(
                        f"adding card with card id {row['card_id']} and print type {row['print_type']}, and quantity of {row['qnty']} to the csv file {output_file}")
                csv_writer.writerow(row)

    def close(self):
        self.save()

    def encrypt(self):
        with open(self.logfile, "rb") as f:
            contents = f.read()
        output = Fernet(self.key).encrypt(contents)
        with open(self.logfile, "wb") as f:
            f.write(output)

    def decrypt(self):
        with open(self.logfile, "rb") as f:
            contents = f.read()
        output = Fernet(self.key).decrypt(contents)
        with open(self.logfile, "wb") as f:
            f.write(output)

    def import_csv(self, input_file: str, output: bool = True):
        if not os.path.exists(input_file):
            return False
        with open(input_file, "r") as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                card_id = row["card_id"]
                print_type = row["print_type"]
                qnty = int(row["qnty"])
                if output:
                    print(f"processing card id {card_id}")
                with contextlib.suppress(KeyError):
                    if output:
                        print("checking for card pre existence")
                    self.delete_card(card_id, print_type)
                if output:
                    print(f"adding card with card id {card_id} and print type {print_type}, and quantity of {qnty}")
                self.add_card(card_id, qnty, print_type)
        return True

    def get_full_price_data(self, card_id: str, print_type: str):
        cd = self.rq.get_card(card_id)["data"]
        price_data = cd["tcgplayer"]["prices"][print_type]
        yield from price_data.items()

    def trade(self, other, other_card_id: str, other_print_type: str, other_qnty: int, card_id: str, print_type: str, qnty: int, export_file: str):
        self.test_card(card_id)
        if not self.test_card(other_card_id) and not self.test_card(card_id):
            return TRADE_CODE_CARD_DOES_NOT_EXIST
        if (o_qnty := other.get_card_qnty(other_card_id, other_print_type)) == 0:
            return TRADE_CODE_CARD_NOT_IN_LOG
        if (self_qnty := self.get_card_qnty(card_id, print_type)) == 0:
            return TRADE_CODE_CARD_NOT_IN_LOG
        if o_qnty < other_qnty:
            return TRADE_CODE_CARD_NOT_IN_LOG_QNTY
        if self_qnty < qnty:
            return TRADE_CODE_CARD_NOT_IN_LOG_QNTY
        other.add_card(card_id, qnty, print_type)
        other.remove_card(other_card_id, other_qnty, other_print_type)
        self.add_card(other_card_id, other_qnty, other_print_type)
        self.remove_card(card_id, qnty, print_type)
        self.save()
        return TRADE_SUCCESS