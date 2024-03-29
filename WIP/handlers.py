# todo write docstring for handlers
import base64
import csv
import random
import secrets
import time
import cliTextTools as ctt
import cryptography
import pandas as pd
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from delayedKeyInt import DelayedKeyboardInterrupt
from pokemontcgsdk import Set, Card, RestClient
from tqdm import tqdm

from assets import *

API_KEY = ""


def init(api_key: str, iterations: int = 1000000, lru: int = 15):
    """
    Description:
        sets the module global variables, so it can be used
    :param api_key: string containing the api key for Pokémon tcg api
    :param iterations: iterations used for the password encryption
    :param lru: the new lru cache expo
    :return: None
    """
    global API_KEY, ITERATIONS, LRU_CACHE_EXPO
    API_KEY = api_key
    ITERATIONS = iterations
    LRU_CACHE_EXPO = lru


try:
    from config import *
except ImportError:

    if __name__ == "__main__":
        msg = "Please enter you pokemontcgapi key. if you do not have one you can get one for free at " \
              "'https://dev.pokemontcg.io/':"
        API_KEY = ctt.get_user_input(msg, ctt.STR_TYPE, can_cancel=False)


class RqHandle:
    # todo write docstring for handlers.RqHandle

    API_KEY = False
    CARD_ENERGY = "energy"
    CARD_REGULAR = "regular"

    def __repr__(self):
        return f"RqHandle({self.API_KEY})"

    def __init__(self, api_key: str = API_KEY):
        # todo write docstring for handlers.RqHandle.__init__
        self.API_KEY = api_key
        RestClient.configure(self.API_KEY)

    def get_card(self, card_id: str, *args, **kwargs):
        # todo write docstring for handlers.RqHandle.get_card
        if not self.API_KEY:
            raise NotImplementedError
        try:
            return Card.find(card_id)
        except Exception:
            return None

    def wait_for_con(self, *args, **kwargs):
        # todo write docstring for handlers.RqHandle.wait_for_con
        if not self.API_KEY:
            raise NotImplementedError
        while True:
            try:
                _ = Card.find("swsh1-1")
                break
            except Exception:
                time.sleep(1)

    def get_pack(self, pack_id: str, *args, **kwargs):
        # todo write docstring for handlers.RqHandle.get_pack
        if not self.API_KEY:
            raise NotImplementedError
        try:
            return Set.find(pack_id)
        except Exception:
            return None

    def get_all_sets(self, *args, **kwargs):
        # todo write docstring for handlers.RqHandle.get_all_sets
        if not self.API_KEY:
            raise NotImplementedError
        try:
            set_list = list(Set.all())
        except Exception:
            raise ConnectionError
        yield from set_list

    def get_energy(self, energy_id: str, *args, **kwargs):
        # todo write docstring for handlers.RqHandle.get_energy
        if not self.API_KEY:
            raise NotImplementedError
        rv = None
        for index, data in enumerate(BASIC_ENERGY.items()):
            k, v = data
            if energy_id == v["id"]:
                rv = {k: v}
                break
        return rv, k

    def validate_card(self, card_id: str, *args, **kwargs):
        # todo write docstring for handlers.RqHandle.validate_card
        if not self.API_KEY:
            raise NotImplementedError
        try:
            _ = Card.find(card_id)
            return True
        except Exception:
            return False

    def validate_print_type(self, card_type: str, card_data: Card, print_type: str, *args, **kwargs):
        # todo write docstring for handlers.RqHandle.validate_print_type
        if card_type == self.CARD_ENERGY:
            return print_type in ENERGY_PRINT_TYPES
        elif card_type != self.CARD_REGULAR:
            raise NotImplementedError
        return card_data.tcgplayer.prices.__getattribute__(print_type) is not None

    @staticmethod
    def get_valid_print_types(card_data: Card, *args, **kwargs):
        # todo write docstring for handlers.RqHandle.get_valid_print_types
        valid_print_types = []
        for index, pt_dict in VALID_PRINT_TYPES.items():
            print_type = pt_dict["attr"]
            try:
                d = card_data.tcgplayer.prices.__getattribute__(print_type)
            except AttributeError:
                continue
            if d is None:
                continue
            valid_print_types.append({"index": index, "data": pt_dict})
        return valid_print_types


class DbHandle:
    # Todo write handlers.DbHandle
    # Todo write handlers.DbHandle docstring

    _DATA_FRAME_GEN_DICT = {
        "card-id": pd.Series(dtype="str"),
        "print-type": pd.Series(dtype="int"),
        "is-energy": pd.Series(dtype="bool"),
        "qnty": pd.Series(dtype="int")
    }

    def __init__(self, rq: RqHandle, uname: str, file: str, psswrd: str, salt_list: (str, list, tuple)):
        # TODO write handlers.DbHandle.__init__ docstring
        self.logfile = file
        self.user = uname
        self.rq = rq
        if os.path.isfile(self.logfile):
            for i in salt_list:
                i = i.encode("utf-8")
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256,
                    length=32,
                    salt=i,
                    iterations=ITERATIONS,
                    backend=default_backend()
                )
                self.key = base64.urlsafe_b64encode(kdf.derive(psswrd.encode("utf-8")))
                self.fernet = Fernet(self.key)
                try:
                    self.data = self._read_file()
                except cryptography.fernet.InvalidToken:
                    continue
                break
        else:
            token = secrets.token_urlsafe(256)
            random.seed(token)
            gen = random.randrange(MIN_SEED, MAX_SEED)
            gen = 2 ** gen
            for _ in range(gen):
                byte_count = random.randrange(MIN_SEED, MAX_SEED)
                _ = [random.randint(2 ** MIN_SEED, 2 ** +MAX_SEED) for i in range(byte_count)]
            salt = random.choice(salt_list)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256,
                length=32,
                salt=salt.encode("utf-8"),
                iterations=ITERATIONS,
                backend=default_backend()
            )
            self.key = base64.urlsafe_b64encode(kdf.derive(psswrd.encode("utf-8")))
            self.fernet = Fernet(self.key)
            self.data = pd.DataFrame(self._DATA_FRAME_GEN_DICT)
            self._save_file()

    def __len__(self):
        if not self.data_has_data:
            return 0
        count = [int(data["qnty"]) for data in self.list_log_all()]
        return sum(count)

    def __repr__(self):
        return f"DbHandle({self.rq.__repr__()}, {self.user}, {self.logfile}, REDACTED)"

    def _encrypt(self):
        # todo write handlers.DbHandle._encrypt docstring
        with DelayedKeyboardInterrupt():
            with open(self.logfile, "rb") as f:
                contents = f.read()
            contents = self.fernet.encrypt(contents)
            with open(self.logfile, "wb") as f:
                f.write(contents)

    def _decrypt(self):
        with DelayedKeyboardInterrupt():
            with open(self.logfile, "rb") as f:
                contents = f.read()
            contents = self.fernet.decrypt(contents)
            with open(self.logfile, "wb") as f:
                f.write(contents)

    @property
    def data_has_data(self):
        try:
            _ = self.data.iterrows()
        except AttributeError:
            return False
        return True

    def _read_file(self):
        with DelayedKeyboardInterrupt():
            self._decrypt()
            data = pd.read_parquet(self.logfile)
            self._encrypt()
            return data

    def _save_file(self):
        with DelayedKeyboardInterrupt():
            self.data.to_parquet(self.logfile)
            self._encrypt()

    def unique_len(self):
        if not self.data_has_data:
            return 0
        s = len(self.data.index)
        return s

    def _edit_card(self, cid: str, pt: str, ie: bool, qnty: int):
        current = self.get_card(cid, pt, ie)
        edit_index = self.data.loc[
                     self.data[
                         (self.data["card-id"] == cid) &
                         (self.data["print-type"] == pt) &
                         (self.data["is-energy"] == ie)
                         ]:
                     self.data,
                     ["qnty"]
                     ] = current + qnty

    def add_card(self, card_id: str, print_type: str, is_energy: bool, qnty: int):
        cq = self.get_card(card_id, print_type, is_energy)
        if cq == -1 or not self.data_has_data:
            new_data = {
                "card-id": card_id,
                "print-type": print_type,
                "is-energy": is_energy,
                "qnty": qnty
            }
            new_data = pd.Series(new_data)
            pd.concat([new_data, self.data], ignore_index=True)
        else:
            self._edit_card(card_id, print_type, is_energy, qnty)
        self._save_file()

    def remove_card(self, card_id: str, print_type: str, is_energy: bool, qnty: int):
        cq = self.get_card(card_id, print_type, is_energy)
        if cq == -1 or not self.data_has_data:
            new_data = {
                "card-id": card_id,
                "print-type": print_type,
                "is-energy": is_energy,
                "qnty": 0
            }
            new_data = pd.Series(new_data)
            pd.concat([new_data, self.data], ignore_index=True)
        else:
            self._edit_card(card_id, print_type, is_energy, qnty * -1)
        self._save_file()

    def delete_card(self, card_id: str, print_type: str, is_energy: bool):
        c = self.get_card(card_id, print_type, is_energy)
        if c != -1 or not self.data_has_data:
            index = self.data.query(f"card-id == {card_id} & print-type == {print_type} & is-energy == {is_energy}")
            self.data.drop(index=index)
        self._save_file()

    def list_log_reg(self):
        yield from (row for row in self.data.iterrows() if row["is-energy"])

    def list_log_energy(self):
        yield from (row for row in self.data.iterrows() if not row["is-energy"])

    def list_log_all(self):
        yield from self.data.iterrows()

    def len_log_reg(self):
        if not self.data_has_data:
            return 0
        count = [int(data["qnty"]) for data in self.list_log_reg()]
        return sum(count)

    def len_log_energy(self):
        if not self.data_has_data:
            return 0
        count = [int(data["qnty"]) for data in self.list_log_energy()]
        return sum(count)

    def get_card(self, card_id: str, print_type: str, is_energy: bool):
        if not self.data_has_data:
            return 0
        data = self.data[
            (self.data["card-id"] == card_id) &
            (self.data["print-type"] == print_type) &
            (self.data["is-energy"] == is_energy)
            ]
        lngth = len(data.index)
        if lngth > 1:
            raise ValueError
        if lngth == 0:
            return -1
        return int(data["qnty"])

    def trade(self, other, user_1_trade: list, user_2_trade: list, user_2_file: str):
        # TODO write handlers.DbHandle.trade docstring
        undo_list_remove = []
        undo_list_add = []
        undo_bool = False
        print("stage 1 of 3")
        for row in tqdm(user_1_trade):
            card_id = row["card-id"]
            print_type = row["print-type"]
            qnty = row["quantity"]
            is_energy = row["is-energy"]
            if not qnty < self.get_card(card_id, print_type, is_energy):
                undo_bool = True
                break
            self.remove_card(card_id, print_type, is_energy, qnty)
            other.add_card(card_id, print_type, is_energy, qnty)
            undo_list_remove.append((card_id, print_type, is_energy, qnty))
        print("stage 2 of 3")
        for row in tqdm(user_2_trade):
            if undo_bool:
                break
            card_id = row["card-id"]
            print_type = row["print-type"]
            qnty = row["quantity"]
            is_energy = row["is-energy"]
            if not qnty < other.get_card_qnty():
                undo_bool = True
                break
            other.remove_card(card_id, print_type, is_energy, qnty)
            self.add_card(card_id, print_type, is_energy, qnty)
            undo_list_add.append((card_id, print_type, is_energy, qnty))
        if not undo_bool:
            for row in undo_list_remove:
                self.add_card(*row)
            for row in undo_list_add:
                self.remove_card(*row)
            return False
        print("stage 3 of 3")
        other.export_csv()
        self._save_file()
        return True

    def import_csv(self, loc: str):
        with DelayedKeyboardInterrupt():
            if not os.path.exists(file):
                return
            with open(file, "r") as f:
                csv_reader = csv.DictReader(f)
                for row in tqdm(csv_reader):
                    card_id = row["card-id"]
                    print_type = row["print-type"]
                    qnty = int(row["quantity"])
                    is_energy = row["is-energy"]
                    card_data = self.rq.get_card(card_id)
                    if card_data is None:
                        try:
                            return self.import_csv(file)
                        except RecursionError:
                            continue
                    self.delete_card(card_data, print_type, is_energy)
                    self.add_card(card_id, qnty, print_type, is_energy)
            self._save_file()

    def export_csv(self, loc: str):
        self.data.to_csv(loc)

    def export_prices_csv(self, loc: str):
        data = pd.DataFrame(
            {
                "card-id": pd.Series(dtype="str"),
                "print-type": pd.Series(dtype="str"),
                "is-energy": pd.Series(dtype="bool"),
                "qnty": pd.Series(dtype="int"),
                "price-low-base": pd.Series(dtype="float"),
                "price-mid-base": pd.Series(dtype="float"),
                "price-high-base": pd.Series(dtype="float"),
                "price-direct-base": pd.Series(dtype="float"),
                "price-market-base": pd.Series(dtype="float"),
                "price-low-calc": pd.Series(dtype="float"),
                "price-mid-calc": pd.Series(dtype="float"),
                "price-high-calc": pd.Series(dtype="float"),
                "price-direct-calc": pd.Series(dtype="float"),
                "price-market-calc": pd.Series(dtype="float")
            }
        )
        for index, row in enumerate(self.data.iterrows()):
            card_id = row["card-id"]
            print_type = row["print-type"]
            is_energy = row["is-energy"]
            qnty = row["qnty"]
            new_data = {
                "card-id": card_id,
                "print-type": print_type,
                "is-energy": True,
                "qnty": qnty
            }
            if is_energy:
                p = {
                    "price-low-base": None, "price-mid-base": None, "price-high-base": None,
                    "price-direct-base": None, "price-market-base": None, "price-low-calc": None,
                    "price-mid-calc": None, "price-high-calc": None, "price-direct-calc": None,
                    "price-market-calc": None
                }
                new_data.update(p)
            else:
                card_data = self.rq.get_card(card_id)
                if card_data is None:
                    return False
                price_data = card_data.tcgplayer.prices.__getattribute__(print_type)
                p = {
                    "price-low-base": price_data.low, "price-mid-base": price_data.mid,
                    "price-high-base": price_data.high, "price-direct-base": price_data.directLow,
                    "price-market-base": price_data.market, "price-low-calc": round(price_data.low * qnty, 2),
                    "price-mid-calc": round(price_data.mid * qnty, ),
                    "price-high-calc": round(price_data.high * qnty, 2),
                    "price-direct-calc": round(price_data.directLow * qnty, 2),
                    "price-market-calc": round(price_data.market * qnty, 2)
                }
                new_data.update(p)
            data = pd.concat([data, new_data], ignore_index=True)
        data.to_csv(loc)
        self._save_file()
        return True


if __name__ == "__main__":
    name = "test"
    file = os.path.join(PROG_DATA, f"{name}.pcldata")
    psswrd = "test1234"
    rq = RqHandle(API_KEY)
    db = DbHandle(rq, name, file, psswrd, BASIC_SALT_LIST)
    db.add_card("swsh1-1", "holofoil", False, 10)