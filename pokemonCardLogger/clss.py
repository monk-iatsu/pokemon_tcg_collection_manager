"""
Description:
    The library version of Pokémon Card Logger
Usage:
    from pokemonCardLogger import clss as pcl
"""
import sqlite3
import os
import requests
import hashlib
import datetime as dt


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

    @property
    def __repr__(self):
        return f"RqHandle({self.api_key}"


class DbHandle:
    """
    Description:
        stores and organizes the log data in a sqlite database
    """
    def __init__(self, db_file: str, psswrd: str, rq: RqHandle):
        """
        Description:
            Constructor method
        Parameters
            :param db_file: the path to the database file
            :param psswrd: the password for the database
            :param rq: an instance of RqHandle
        """
        self.db_file = db_file
        self.psswrd = psswrd
        self.rq = rq
        self.psswrd_hash = hashlib.sha512(self.psswrd.encode("utf-8")).hexdigest()
        if os.path.exists(self.db_file):
            self.db = sqlite3.connect(self.db_file)
            self.c = self.db.cursor()
            self.validate()
        else:
            self.db = sqlite3.connect(self.db_file)
            self.c = self.db.cursor()
            self.first_run()
        self.login_setup()

    def first_run(self):
        """
        Description:
            Sets up the database if it was freshly created
        Parameters:
            :return: None
        """
        self.c.execute("CREATE TABLE params(key TEXT, value TEXT)")
        self.c.execute("CREATE TABLE card_log(card TEXT, qnty INTEGER)")
        self.c.execute("CREATE TABLE login_log(datetime TEXT)")
        self.c.execute("INSERT INTO params(key, value) VALUES(?,?)", ("password", self.psswrd_hash))
        self.db.commit()

    def validate(self):
        """
        Description:
            Validates the database and password combo. if the password doesn't match, raises ValueError
        Parameters:
            :return: None
        """
        self.c.execute("SELECT value FROM params WHERE key='password'")
        if not self.psswrd_hash == self.c.fetchone()[0]:
            raise PermissionError

    def login_setup(self):
        """
        Description:
            Logs the current login to the database
        Parameters:
            :return: None
        """
        login_time = dt.datetime.now().isoformat()
        self.c.execute("INSERT INTO login_log VALUES(?)", (login_time,))
        self.db.commit()

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
            print("card does not exist")
            return None
        current_qnty = self.get_card_qnty(card_id)
        if not current_qnty:
            new_qnty = qnty
            self.c.execute("INSERT INTO card_log VALUES(?,?)", (new_qnty, card_id))
        else:
            new_qnty = qnty + current_qnty
            self.c.execute("UPDATE card_log SET qnty = ? WHERE card = ?", (new_qnty, card_id))
        self.db.commit()

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
            print("card does not exist")
            return False
        current_qnty = self.get_card_qnty(card_id)
        if not current_qnty:
            return False
        new_qnty = current_qnty - qnty
        if new_qnty < 0:
            new_qnty = 0
        self.c.execute("UPDATE card_log SET qnty = ? WHERE card = ?", (new_qnty, card_id))
        self.db.commit()
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
            print("card does not exist")
            return None
        self.c.execute("DELETE FROM card_log WHERE card = ?", (card_id,))
        self.db.commit()

    def get_card_qnty(self, card_id: str):
        """
        Description:
            Gets and returns the quantity of a given card in the log
        Parameters
            :param card_id: the id of the card according to pokemonTcgApi
            :return: The quantity of the card
        """
        if not self.test_card(card_id):
            print("card does not exist")
            return None
        self.c.execute("SELECT qnty FROM card_log WHERE card = ?", (card_id,))
        return self.c.fetchone()

    def get_log(self):
        """
        Description:
            A generator consisting of the log
        Parameters:
            :return: a generator of the rows in the log
        """
        self.c.execute("SELECT * FROM card_log")
        for row in self.c.fetchall():
            yield row

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

    def __del__(self):
        """
        Description:
            Destructor method
        Parameters:
            :return: None
        """
        self.db.commit()
        self.c.close()
        self.db.close()

    @property
    def __repr__(self):
        return f"DbHandle({self.db_file}, psswrd, {self.rq.__repr__})"

    def __len__(self):
        return len(list(self.get_log()))
