"""
Description:
    The alternate library version of Pokémon Card Logger using sqlite
    FYI this module is pre alpha and experimental
Usage:
    from pokemonCardLogger import clssalt as pcl
"""
import pickle
import os
import requests
import hashlib
import datetime as dt
from clss_base import *


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
        pop_items = []
        for card, qnty in self.logdict["log"].items():
            if qnty == 0:
                pop_items.append(card)
        for i in pop_items:
            _ = self.logdict["log"].pop(i)
        if self.logfile == ":memory:":
            return None
        with open(self.logfile, "wb") as f:
            pickle.dump(self.logdict, f)

    def read(self):
        """
        Description:
            reads the data from pickle and returns the log dictionary
        Parameters:
            :return: dictionary consisting of the log
        """
        if self.logfile == ":memory:":
            return None
        with open(self.logfile, "rb") as f:
            ld = pickle.load(f)
        return ld

    def close(self):
        self.save()


if __name__ == "__main__":
    print("this is for testing purposes")
    import config
    _file = ":memory:"
    _psswrd = "default"
    _rq = RqHandle(config.API_KEY)
    db = DbHandle(_file, _psswrd, _rq)
    print(db.__repr__())
