"""
Description:
    The library version of Pokémon Card Logger using json
Usage:
    from pokemonCardLogger import clss_json as pcl
"""
import json
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
        if self.has_encryption:
            self.encrypt()
        for i in [card for card, qnty in self.logdict["log"].items() if qnty == 0]:
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
            :return: dictionary consisting of the log data
        """
        if self.has_encryption:
            self.decrypt()
        if self.logfile == ":memory:":
            return None
        with open(self.logfile, "r") as f:
            ld = json.load(f)
        return ld


if __name__ == "__main__":
    print("this is for testing purposes")
    try:
        import config
    except ImportError:
        print("no api key found quitting.")
        quit()
    _file = ":memory:"
    _psswrd = "default"
    _rq = RqHandle(config.API_KEY)
    db = DbHandle(_file, _psswrd, _rq)
    print(db.__repr__())