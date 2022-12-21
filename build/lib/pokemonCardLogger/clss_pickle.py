"""
Description:
    The alternate library version of Pokémon Card Logger using sqlite
    FYI this module is pre alpha and experimental
Usage:
    from pokemonCardLogger import clss_pickle as pcl
"""
import pickle
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
        for i in [card for card, qnty in self.logdict["log"].items() if qnty == 0]:
            _ = self.logdict["log"].pop(i)
        if self.logfile == ":memory:":
            return None
        with open(self.logfile, "wb") as f:
            pickle.dump(self.logdict, f)
        self.encrypt()

    def read(self):
        """
        Description:
            reads the data from pickle and returns the log dictionary
        Parameters:
            :return: dictionary consisting of the log data
        """
        self.decrypt()
        if self.logfile == ":memory:":
            return None
        with open(self.logfile, "rb") as f:
            try:
                ld = pickle.load(f)
            except pickle.PickleError:
                if self.has_encryption:
                    self.encrypt()
                    raise PermissionError
                raise pickle.PickleError
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
