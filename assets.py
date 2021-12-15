import os
import sys
import json
import datetime as dt
import sqlite3

import pokemontcgsdk

import config

def init(api_key=None):
    if api_key == None:
        api_key = config.API_KEY
    pokemontcgsdk.RestClient.configure(api_key)



class PackCardHandle:

    def __init__(self):
        self.sets = {}
        for i in pokemontcgsdk.Set.all():
            self.sets.update({i.id: {"pack-name": i.name, "printed-total": i.printedTotal, "real-total": i.total}})

    def verify_card(self, pack_id: str, card_num: str):
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
        if str(num) in self.sets.keys():
            return self.sets[str(num)]["pack-name"]

    def get_pack_count(self, pack_id: str):
        if str(num) in self.sets.keys():
            return self.sets[str(num)]["printed-total"], self.sets[str(num)]["total"]

    def get_card_info(self, pack_id: str, card_id: str):
        card = f"{pack_id}-{card_id}"
        try:
            return pokemontcgsdk.Card.find(card)
        except Exception:
            print("can't find card. try again.")
            return False

    def get_pack_info(self, pack_id: str):
        try:
            return pokemontcgsdk.Set.find(pack_id)
        except Exception:
            print("can't find pack. try again.")
            return False

    def get_card_price_data(self, pack_id: str, card_id: str, print_type: str):
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
        for k, v in self.sets.items():
            yield k, v["pack-name"]


class StorageHandle:

    def __init__(self, file: str, pack_card_manager: PackCardHandle):
        self.file = file
        self.conn = sqlite3.connect(file)
        self.curs = self.conn.cursor()
        self.pcm = pack_card_manager

    def new_db_setup(self):
        self.curs.execute("CREATE TABLE IF NOT EXISTS collection(pack_id TEXT, card_id TEXT, condition INTEGER, print_type TEXT, date_added TEXT, secondary_id INTEGER)")
        self.curs.execute("CREATE TABLE IF NOT EXISTS deleted_ids(did INTEGER)")
        self.curs.execute("CREATE TABLE IF NOT EXISTS stats(data_id TEXT, value TEXT)")
        self.curs.execute("INSERT INTO stats (data_id, value) VALUES(?, ?)", ('next_id', 0))
        self.curs.execute("INSERT INTO stats (data_id, value) VALUES(?, ?)", ('card_count', 0))
        self.curs.execute("INSERT INTO stats (data_id, value) VALUES(?, ?)", ('collection_value', 0))
        self.conn.commit()

    def add_card(self, pid: str, cid: str, con: int, pt: str, date: str):
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
                self.conn.commit()
            return sid
        else:
            print("card not found. try again")
            return False

    def remove_card(self, sid: int):
        self.curs.execute("DELETE FROM collection WHERE secondary_id=?", (sid, ))
        self.curs.execute("SELECT value FROM stats WHERE data_id='card_count'")
        count = int(self.curs.fetchone()[0])
        self.curs.execute("UPDATE OR IGNORE stats SET value=? WHERE data_id='card_count'", (count-1, ))
        self.conn.commit()

    def get_id_of_card(self, pid: str, cid: str):
        self.curs.execute("SELECT condition, print_type, date_added, secondary_id FROM collection WHERE pack_id=? AND card_id=?", (pid, cid))
        return self.curs.fetchall()

    def trade_card(self, sid: int, new_pid: str, new_cid: str, new_con: int, new_pt, new_date: str):
        if self.pcm.verify(pid, cid):
            self.curs.execute("UPDATE OR IGNORE collection SET pack_id=?, card_id=?, condition=?, print_type=?, date_added=? WHERE secondary_id=?", (new_pid, new_cid, new_con, new_pt, new_date, sid))
        else:
            print("card not found. try again")
            return False

    def get_all_collection(self):
        try:
            self.curs.execute("SELECT * FROM collection")
            return self.curs.fetchall()
        except Exception:
            return [[False, False, False, False, False, False],[False, False, False, False, False, False]]

    def save_collection(self):
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