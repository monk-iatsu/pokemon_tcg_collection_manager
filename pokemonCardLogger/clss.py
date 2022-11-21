"""
Description:
    The library version of Pokémon Card Logger using json
Usage:
    from pokemonCardLogger import clss as pcl
"""
import os
import requests
import hashlib
import datetime as dt
import json


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

    def get_card(self, card_id: str):
        """
        Description:
            Requests from pokemonTcgApi the data for a specific card and returns that data as a dictionary
            If the data is bad raises ValueError
        Parameters:
            :param card_id: a string that represents the card according to pokemonTcgApi
            :return: dict of the data from pokemonTcgApi
        """
        data = requests.get(f"{self.card_url}/{card_id}", headers=self.headers)
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
        data = requests.get(f"{self.pack_url}/{pack_id}", headers=self.headers)
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
        data = requests.get(self.pack_url, headers=self.headers)
        if data.ok:
            pass
        else:
            raise ConnectionError
        for i in data.json()["data"]:
            yield i["id"], i["name"]

    def __repr__(self):
        return f"RqHandle('{self.api_key}')"


class DbHandle:
    """
    Description:
        stores and organizes the log data in a sqlite database
    """

    def __init__(self, file: str, psswrd: str, rq: RqHandle):
        """
        Description:
            Constructor method
        Parameters
            :param db_file: the path to the database file
            :param psswrd: the password for the database
            :param rq: an instance of RqHandle
        """
        self.logfile = file
        self.psswrd = psswrd
        self.rq = rq
        self.psswrd_hash = hashlib.sha512(self.psswrd.encode("utf-8")).hexdigest()
        if self.logfile == ":memory:":
            self.logdict = {}
            self.first_run()
        elif os.path.exists(self.logfile):
            with open(self.logfile) as f:
                self.logdict = json.load(f)
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
        self.logdict = {"psswrd": self.psswrd_hash, "login_times": [], "log": {}}
        self.save()

    def validate(self):
        """
        Description:
            Validates the database and password combo. if the password doesn't match, raises ValueError
        Parameters:
            :return: None
        """
        if not self.psswrd_hash == self.logdict["psswrd"]:
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

    def add_card(self, card_id: str, qnty: int):
        """
        Description:
            Adds quantity to the card as well as adds a new card to the database
        Parameters:
            :param card_id: the id of the card according to pokemonTcgApi
            :param qnty: the quantity of cards to add. if there is already quantity, it adds to that
            :return: None
        """
        if not self.test_card(card_id):
            return False
        current_qnty = self.get_card_qnty(card_id)
        if not current_qnty:
            self.logdict["log"].update({card_id: qnty})
        else:
            qnty = qnty + current_qnty
            self.logdict["log"].update({card_id: qnty})
        self.save()
        return True

    def remove_card(self, card_id: str, qnty: int):
        """
        Description:
            Removes quantity from a card in the log
        Parameters:
            :param card_id: the id of the card according to pokemonTcgApi
            :param qnty: the quantity of cards to remove. if there is already quantity, it subtracts from that
            :return: a bool based on if the operation was successful or not
        """
        if not self.test_card(card_id):
            return False
        current_qnty = self.get_card_qnty(card_id)
        if not current_qnty:
            return False
        qnty = current_qnty - qnty
        if qnty < 0:
            qnty = 0
        self.logdict["log"].update({card_id: qnty})
        self.save()
        return True

    def delete_card(self, card_id: str):
        """
        Description:
            Deletes a card from the log
        Parameters:
            :param card_id: the id of the card according to pokemonTcgApi
            :return: None
        """
        if not self.test_card(card_id):
            return False
        _ = self.logdict["log"].pop(card_id)
        self.save()
        return True

    def get_card_qnty(self, card_id: str):
        """
        Description:
            Gets and returns the quantity of a given card in the log
        Parameters
            :param card_id: the id of the card according to pokemonTcgApi
            :return: The quantity of the card
        """
        if not self.test_card(card_id):
            return 0
        try:
            return self.logdict["log"][card_id]
        except KeyError:
            return 0

    def get_log(self):
        """
        Description:
            A generator consisting of the log
        Parameters:
            :return: a generator of the rows in the log
        """
        for card_id, qnty in self.logdict["log"].items():
            yield qnty, card_id

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

    def close(self):
        self.save()
        quit()

    def save(self):
        """
        Description:
            cleanly closes the log by saving the log to a file
        Parameters:
            :return: None
        """
        pop_items = []
        for card, qnty in self.logdict["log"].items():
            if qnty == 0:
                pop_items.append(card)
        for i in pop_items:
            _ = self.logdict["log"].pop(i)
        if self.logfile == ":memory:":
            return None
        with open(self.logfile, "w") as f:
            json.dump(self.logdict, f, indent=True)

    def __repr__(self):
        return f"DbHandle('{self.logfile}', 'redacted', {self.rq.__repr__()})"

    def __len__(self):
        return len(list(self.get_log()))


if __name__ == "__main__":
    import config
    print("this is for testing purposes")
    _file = ":memory:"
    _psswrd = "default"
    _rq = RqHandle(config.API_KEY)
    db = DbHandle(_file, _psswrd, _rq)
    print(db.__repr__())
