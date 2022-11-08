"""
Description:
    A script to display the Pokémon packs and their pack ids according to the logger.
Usage:
    Run with "python3 packRef.py" in a shell to get a list of packs and their pack ids
"""
import clss
try:
    import config
    key = config.API_KEY
except ImportError:
    print("please enter your api key for pokemonTcgApi")
    key = input(">>> ")


if __name__ == "__main__":
    rq = clss.RqHandle(key)
    for pack_id, pack_name in rq.get_all_sets():
        print(f"the pack {pack_name}'s id is {pack_id}")
else:
    print("Not importable, quitting")
    raise NotImplementedError
