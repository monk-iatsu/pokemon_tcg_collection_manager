import os
import sys
import json
import datetime as dt
import sqlite3

import pokemontcgsdk

import config

def init(api_key: str = None):
    """
    Initializes the module
    
    Args:
    -----
        api_key: (str, optional) a string used by the module pokemotcgsdk for the rest api. only enter if you have your own api key.
    """
    if api_key == None:
        api_key = config.API_KEY
    pokemontcgsdk.RestClient.configure(api_key)


class PackCardHandle:
    """
    PackCardHandle:
    ---------------
        handles api communiations with pokemontcg api
        
    """

    def __init__(self):
        """
        PackCardHandle.__init__:
        ------------------------
            constructor method
        """
        self.sets = {}
        for i in pokemontcgsdk.Set.all():
            self.sets.update({i.id: {"pack-name": i.name, "printed-total": i.printedTotal, "real-total": i.total}})

    def verify_card(self, pack_id: str, card_num: str):
        """
        PackCardHandle.verify_card:
        ---------------------------
            verifies the existance of a card
            Args:
            -----
                pack_id: (str), the id for the cards pack
                card_id: (str), the cards collectors number
            Returns:
            --------
                bool: if card is valid True otherwise False
        """
        try:
            _ = pokemontcgsdk.Set.find(pack_id)
        except Exception:
            return False
        card = f"{pack_id}-{card_num}"
        try:
            _ = pokemontcgsdk.Card.find(card)
            return True
        except Exception:
            return False

    def get_pack_name(self, pack_id: str):
        """
        PackCardHandle.get_pack_name:
        -----------------------------
            gets pack name from pack id
            Args:
            -----
                pack_id: (str), the id of the pack
            Returns:
            --------
                bool: False if cant find pack
                str: the name of the pack if found
        """
        if str(num) in self.sets.keys():
            return self.sets[str(num)]["pack-name"]
        else:
            return False

    def get_pack_count(self, pack_id: str):
        """
        PackCardHandle.get_pack_count:
        ------------------------------
            gets a given pack card count
            Args:
            -----
                pack_id: (str), the id of the pack
            Returns:
            --------
                tuple: either two Falses if pack is not found ot two ints for printed size and
                actual size
        """
        if str(num) in self.sets.keys():
            return self.sets[str(num)]["printed-total"], self.sets[str(num)]["total"]
        else:
            return False

    def get_card_info(self, pack_id: str, card_id: str):
        """
        PackCardHandle.get_card_info:
        -----------------------------
            gets the data for a given card
            Args:
            -----
                pack_id: (str), the id for the cards pack
                card_id: (str), the cards collectors number
            Returns:
            --------
                bool: False if the card is not found
                pokemontcgsdk.Card: the dataclass of the card if found
        """
        card = f"{pack_id}-{card_id}"
        try:
            return pokemontcgsdk.Card.find(card)
        except Exception:
            print("can't find card. try again.")
            return False

    def get_pack_info(self, pack_id: str):
        """
        PackCardHandle.get_pack_info:
        -----------------------------
            gets the data for a given pack
            Args:
            -----
                pack_id: (str), the id of the pack
            Returns:
            --------
                bool: False if pack is not found
                pokemontcgsdk.Set: the dataclass of the pack if found
        """
        try:
            return pokemontcgsdk.Set.find(pack_id)
        except Exception:
            print("can't find pack. try again.")
            return False

    def get_card_price_data(self, pack_id: str, card_id: str, print_type: str):
        """
        PackCardHandle.get_card_price_data:
        -----------------------------------
            gets the market price on tcgplayer of a given card
            Args:
            -----
                pack_id: (str), the id for the cards pack
                card_id: (str), the cards collectors number
                print_type: (str), the print type of a given card*
            Returns:
            --------
                float: the value of tcgplayer market price
            Notes:
            ------
                * print_type accepts the following strings:
                    'feh': first edition holo
                    'fen': first edition normal
                    'h': holo
                    'n': normal
                    'rh': revers holo
        """
        data = self.get_card_info(pack_id, card_id)
        if print_type == "feh":
            return data.tcgplayer.prices.firstEditionHolofoil.market
        elif print_type == "fen":
            return data.tcgplayer.prices.firstEditionNormal.market
        elif print_type == "h":
            return data.tcgplayer.prices.holofoil.market
        elif print_type == "n":
            return data.tcgplayer.prices.normal.market
        elif print_type == "rh":
            return data.tcgplayer.prices.reverseHolofoil.market
        else:
            return 0.00

    def get_all_packs(self):
        """
        PackCardHandle.get_all_packs:
        -----------------------------
        generator for list of all pack ids, and pack names
            Yields:
            --------
                k: (str) pack id of current pack
                v: (str) name of current pack
        """
        for k, v in self.sets.items():
            yield k, v["pack-name"]


class StorageHandle:
    """
    StorageHandle:
    --------------
        handles the interface for the sqlite database holding the collection
    """

    def __init__(self, file: str, pcm: PackCardHandle):
        """
        StorageHandle.__init__:
        -----------------------
            constructor method
            Args:
            -----
                file: (str) the path to the sqlite database
                pcm: (PackCardHandle) an access to the instance of PackCardHandle
        """
        self.file = file
        self.conn = sqlite3.connect(file)
        self.curs = self.conn.cursor()
        self.pcm = pcm

    def new_db_setup(self):
        """
        StorageHandle.new_db_setup:
        ---------------------------
            sets up a empty sqlite database for use with this module
        """
        self.curs.execute("CREATE TABLE IF NOT EXISTS collection(pack_id TEXT, card_id TEXT, condition INTEGER, print_type TEXT, date_added TEXT, secondary_id INTEGER)")
        self.curs.execute("CREATE TABLE IF NOT EXISTS deleted_ids(did INTEGER)")
        self.curs.execute("CREATE TABLE IF NOT EXISTS stats(data_id TEXT, value TEXT)")
        self.curs.execute("INSERT INTO stats (data_id, value) VALUES(?, ?)", ('next_id', 0))
        self.curs.execute("INSERT INTO stats (data_id, value) VALUES(?, ?)", ('card_count', 0))
        self.curs.execute("INSERT INTO stats (data_id, value) VALUES(?, ?)", ('collection_value', 0))
        self.conn.commit()

    def add_card(self, pid: str, cid: str, con: int, pt: str, date: str):
        """
        StorageHandle.add_card:
        -----------------------
            adds a card to the collection
            Args:
            -----
                pid: (str), pack id for the card to add
                cid: (str), cards collectors number
                con: (int), the condition of the card from 1 to 10 where 10 is mint condition
                pt: (str), print type *
                date: (str), iso datetime stirng
            Returns:
            --------
                int: the collection id of the card
                bool: false if card is not found
            Notes:
            ------
                * print_type accepts the following strings:
                    'feh': first edition holo
                    'fen': first edition normal
                    'h': holo
                    'n': normal
                    'rh': revers holo
        """
        self.curs.execute("SELECT * FROM deleted_ids")
        sid = self.curs.fetchone()
        if sid == None:
            used_del_id = False
            self.curs.execute("SELECT value FROM stats WHERE data_id='next_id'")
            sid = int(self.curs.fetchone()[0])
        else:
            used_del_id = True
        if self.pcm.verify_card(pid, cid):
            self.curs.execute("INSERT INTO collection (pack_id, card_id, condition, print_type, date_added, secondary_id) VALUES (?,?,?,?,?,?)", (pid, cid, con, pt, date, sid))
            self.curs.execute("SELECT value FROM stats WHERE data_id='card_count'")
            cc = int(self.curs.fetchone()[0])
            self.curs.execute("UPDATE OR IGNORE stats SET value=? WHERE data_id='card_count'", (cc+1, ))
            if used_del_id:
                self.curs.execute("DELETE FROM deleted_ids WHERE did=?", (sid, ))
                self.conn.commit()
            else:
                self.curs.execute("UPDATE OR IGNORE stats SET value=? WHERE data_id='next_id'", (sid+1, ))
            return sid
        else:
            print("card not found. try again")
            return False

    def remove_card(self, sid: int):
        """
        StorageHandle.remove_card:
        --------------------------
            removes a card from your collecion
            Args:
            -----
                sid: (int), the collection id of the card to remove
        """
        self.curs.execute("DELETE FROM collection WHERE secondary_id=?", (sid, ))
        self.curs.execute("SELECT value FROM stats WHERE data_id='card_count'")
        count = int(self.curs.fetchone()[0])
        self.curs.execute("UPDATE OR IGNORE stats SET value=? WHERE data_id='card_count'", (count-1, ))

    def get_id_of_card(self, pid: str, cid: str):
        """
        StorageHandle.get_id_of_card:
        -----------------------------
            returns the collection ids of a card in collection
            Args:
            -----
                pid: (str), the pack id of a given card
                cid: (str), the collectors number of a given card
            Returns:
            --------
                tuple: a tuple of tuples of all the cards data e.g. (condition, print_type, date_added, collection_id)
                bool: false if the card is not found
        """
        self.curs.execute("SELECT condition, print_type, date_added, secondary_id FROM collection WHERE pack_id=? AND card_id=?", (pid, cid))
        return self.curs.fetchall()

    def trade_card(self, sid: int, new_pid: str, new_cid: str, new_con: int, new_pt, new_date: str):
        """
        StorageHandle.trade_card:
        -------------------------
            trades a card for another card
            Args:
            -----
                sid: (int), the collection id of the card to trade
                new_pid: (str), the pack id of the new card
                new_cid: (str), the collectors number of the new card
                new_con: (int), the condition of the new card on a scale of 1 to 10 where 10 is mint
                new_pt: (str), the print type of the new card *
                new_date: (str), today and nows iso datetime
            Returns:
            --------
                bool: whether or not the process succeded
            Notes:
            ------
                * print_type accepts the following strings:
                    'feh': first edition holo
                    'fen': first edition normal
                    'h': holo
                    'n': normal
                    'rh': revers holo
        """
        if self.pcm.verify(pid, cid):
            self.curs.execute("UPDATE OR IGNORE collection SET pack_id=?, card_id=?, condition=?, print_type=?, date_added=? WHERE secondary_id=?", (new_pid, new_cid, new_con, new_pt, new_date, sid))
            return True
        else:
            print("card not found. try again")
            return False

    def get_all_collection(self):
        """
        StorageHandle.get_all_collection:
        ---------------------------------
            returns all of the cards in the collection
            Returns:
            --------
                tuple: a tuple of tuples consisting of pack id of the given card, collectors number,
                condition, print type, date added, and collectionm id
                if the collection is empty, all values will be False
        """
        try:
            self.curs.execute("SELECT * FROM collection")
            return self.curs.fetchall()
        except Exception:
            return [[False, False, False, False, False, False],[False, False, False, False, False, False]]

    def save_collection(self):
        """
        StorageHandle.save_colloction:
        ------------------------------
            final save method
        """
        self.conn.commit()
        value = 0.00
        for i in self.get_all_collection():
            pid = i[0]
            cid = i[1]
            pt = i[3]
            con = i[2]
            base_price = self.pcm.get_card_price_data(pid, cid, pt)
            real_price = base_price/10*con
            value += real_price
        self.curs.execute("UPDATE OR IGNORE stats SET value=? WHERE data_id='collection_value'", (value, ))
        self.conn.commit()