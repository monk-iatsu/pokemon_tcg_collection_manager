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
from clss_base import *

print("depreciated use clss_json")


class DbHandle(DbHandleBase):
    """
    Description:
        stores and organizes the log data in a pickle file
    """

    def save(self):
        """
        Description:
            saves the log to a file
        Parameters:
            :return: None
        """
        pop_items = [card for card, qnty in self.logdict["log"].items() if qnty == 0]
        for i in pop_items:
            _ = self.logdict["log"].pop(i)
        if self.logfile == ":memory:":
            return None
        with open(self.logfile, "w") as f:
            json.dump(self.logdict, f, indent=True)

    def read(self):
        """
        Description:
            reads the data from json and returns the log dictionary
        Parameters:
            :return: dictionary consisting of the log
        """
        if self.logfile == ":memory:":
            return None
        with open(self.logfile, "r") as f:
            ld = json.load(f)
        return ld

    def close(self):
        self.close()


if __name__ == "__main__":
    print("this is for testing purposes")
    import config
    _file = ":memory:"
    _psswrd = "default"
    _rq = RqHandle(config.API_KEY)
    db = DbHandle(_file, _psswrd, _rq)
    print(db.__repr__())
