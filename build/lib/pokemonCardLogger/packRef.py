"""
Description:
    A script to display the Pokémon packs and their pack ids according to the logger.
Usage:
    Run with "python3 packRef.py" in a shell to get a list of packs and their pack ids
"""
import clss_base
import test_api_status
import cliTextTools as ctt
try:
    # noinspection PyUnresolvedReferences
    import config
    key = config.API_KEY
except ImportError:
    msg = "Please enter you pokemontcgapi key. if you do not have one you can get one for free at 'https://dev.pokemontcg.io/': "
    API_KEY = ctt.get_user_input(msg, ctt.STR_TYPE, can_cancel=False)


if __name__ == "__main__":
    print("waiting for api connection")
    test_api_status.without_output()
    rq = clss_base.RqHandle(key)
    for pack_id, pack_name in rq.get_all_sets():
        print(f"the pack {pack_name}'s id is {pack_id}")
else:
    print("Not importable, quitting")
    raise NotImplementedError
