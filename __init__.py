import clss
import config
import os
import datetime as dt

def init(api_key: str = None, file: str = None):
    if file == None:
        file = config.DEFAULT_FILE
    clss.init(api_key)
    pcm = clss.PackCardHandle()
    if not os.path.exists(config.DEFAULT_FILE):
        app = clss.StorageHandle(file, pcm)
        app.new_db_setup()
    else:
        app = clss.StorageHandle(file, pcm)
    return app, pcm

def get_input(dt: str, msg: str):
    print(msg)
    data = input(">>>_")
    if data == "":
        return None
    if dt == "str":
        return data
    elif dt == "bool":
        if data.lower() in ("y", "yes", "t", "true"):
            return True
        elif data.lower() in ("n", "no", "f", "false"):
            return False
        elif data.lower() in ("c", "cancel"):
            print("operation canceled. please try again")
            return None
        else:
            print("invalid input. please try again")
            return get_input(dt, msg)
    elif dt == "int":
        try:
            return int(data)
        except ValueError:
            print("invalid input. try again")
            return get_input(dt, msg)
    elif dt == "float":
        try:
            return float(data)
        except ValueError:
            print("invalid input. please try again")
            return get_input(dt, msg)
    else:
        print("invalid data type. please try again")
        return None

def get_pack_ids(pcm: clss.PackCardHandle):
    rc = []
    for i in pcm.get_all_packs():
        print(f"pack name: {i[1]}; pack id: {i[0]}")
        rc.append(i)
    return rc
        
def get_pack_by_id(pcm: clss.PackCardHandle):
    msg = "please enter a pack id. if you dont know it run print packs. cancel with no input."
    pid = get_input("str", msg)
    if pid == "":
        return None
    else:
        data = pcm.get_pack_info(pid)
        if data == False:
            print("invalid pack id. try again")
            return None
        
        else:
            return pid

def get_card_by_collector_num(pcm: clss.PackCardHandle, pid: str = None):
    if pid == None:
        pid = get_pack_by_id(pcm)
        if pid == None:
            return None, None
    msg = """please enter collectors number of your specific card letters and numbers. ignore the slash and extra number. enter nothing to cancel"""
    cid = get_input("str", msg)
    if cid == "":
        return None, None
    try:
        cid = cid.upper()
    except Exception:
        pass
    data = pcm.get_card_info(pid, cid)
    if not data:
        print(data)
        print("card not found. try again")
        return None, None
    return pid, cid


def get_condition():
    msg = """enter a number between 1 and 10 on what condition the card is where 1 is very bad and 10 is mint"""
    con = get_input("int", msg)
    if con == None:
        print("operation canceled.")
        return None
    elif 1 <= con >= 10:
        return con
    else:
        print("please enter a number between 1 and ten")
        return get_condition()
    
def get_print_type(pcm: clss.PackCardHandle, pid: str, cid: str):
    msg = """
enter the number of one of the following
1: unlimited
2: first edition
3: first edition holofoil
4: holofoil
5: reverse holofoil
"""
    pt = get_input("int", msg)
    rc_dict = {1: "n", 2: "fen", 3: "feh", 4: "h", 5: "rh"}
    if pt == None:
        print("operation canceled")
        return None
    elif pt in rc_dict.keys():
        pt = rc_dict[pt]
        try:
            data = pcm.get_card_price_data(pid, cid, pt)
        except AttributeError:
            print("card dosen't support print type. tray again")
            return get_print_type(pcm, pid, cid)
        return pt
    else:
        print("invalidn entry. try again.")
        return get_print_type(pcm, pid, cid)

def add_card(pcm: clss.PackCardHandle, app: clss.StorageHandle, pid: str = None, cid: str = None):
    pid, cid = get_card_by_collector_num(pcm)
    if pid == None or cid == None:
        return
    con = get_condition()
    if con == None:
        return
    pt = get_print_type(pcm, pid, cid)
    if pt == None:
        return
    sid = app.add_card(pid, cid, con, pt, dt.datetime.now().isoformat())
    print(f"the id of this card is {sid}")
    
def trade_card(pcm: clss.PackCardHandle, app: clss.StorageHandle):
    print("first card is the card to remove")
    old_pid, old_cid = get_card_by_collector_num(pcm)
    if old_pid == None or old_cid == None:
        return
    old_card_data = pcm.get_card_info(old_pid, old_cid)
    name = old_card_data.name
    ft = old_card_data.flavorText
    sid = -1
    pt_dict = {"rh": "rare-holo", "h": "holo", "feh": "first edition holo", "fen": "first edition normal", "n": "unlimited"}
    for i in app.get_id_of_card(old_pid, old_cid):
        pt = pt_dict[i[1]]
        msg = f"""
please verify the card:
is the name {old_name}
is the flavor text '{ft}'
is the id {i[3]}
is the cards condition {i[2]}
enter 'y', 'n' or 'c' to cancel
"""
        verify = get_input("bool", msg)
        if verify == None:
            return
        elif verify:
            sid = i[3]
            break
    if sid == -1:
        print("card not found. try again")
        return remove_card()
    print("now card in its place. it will have the same id")
    new_pid, new_cid = get_card_by_collector_num(pcm)
    if new_pid == None or new_cid == None:
        return
    new_card_data = pcm.get_card_info(new_pid, new_cid)
    name = new_card_data.name
    new_ft = new_card_data.flavorText
    msg = f"""
please verify the card:
is the name {name}
is the flavor text {ft}
enter 'y', 'n' or 'c' to cancel
"""
    verify = get_input("bool", msg)
    if verify == None:
        return
    elif verify:
        new_pt = get_print_type(new_pid, new_cid)
        if new_pt == None:
            return
        
        elif new_pt:
            con = get_condition()
            if con == None:
                return
            app.trade_card(sid, new_pid, new_cid, con, pt, dt.datetime.now().isoformat())
        else:
            print("lets try again.")
            return trade_card()
    else:
        print("lets try again.")
        return trade_card()
            
            
    
def remove_card(pcm: clss.PackCardHandle, app: clss.StorageHandle):
    pid, cid = get_card_by_collector_num(pcm)
    if pid == None or cid == None:
        return
    card_data = pcm.get_card_info(pid, cid)
    name = card_data.name
    flavor = card_data.flavorText
    msg = f"please verify card:\n is the name of your card {name}\n and is the flavor text {flavor}? enter 'y' or 'n' or 'c' to cancel."
    verify = get_input("bool", msg)
    if verify == None:
        return
    elif verify:
        print("thank you")
    elif not verify:
        print("alright lets try again.")
        return remove_card()
    sid = -1
    pt_dict = {"rh": "rare-holo", "h": "holo", "feh": "first edition holo", "fen": "first edition normal", "n": "unlimited"}
    for i in app.get_id_of_card(pid, cid):
        pt = i[1]
        pt = pt_dict[pt]
        msg = f"""please verify the following information with 'y', 'n', or 'c' to cancel:
is the condition of this card {i[0]}
is the print type of this card {pt}
is the date added to the collection possibly {i[2]}
"""
        verify = get_input("bool", msg)
        if verify:
            sid = i[3]
            break
    if sid == -1:
        print("card not found. try again")
        return remove_card()
    app.remove_card(sid)

def list_collection(app: clss.StorageHandle, pcm: clss.PackCardHandle):
    for i in app.get_all_collection():
        pid = i[0]
        cid = i[1]
        con = i[2]
        pt = i[3]
        date = i[4]
        sid =i[5]
        cd = pcm.get_card_info(pid, cid)
        name = cd.name
        msg = f"""
id = {sid}
name = {name}
pack id = {pid}
card collectors number = {cid}
print type = {pt}
date and time added = {date}
condition = {con}
"""
        print(msg)

def list_packs(pcm: clss.PackCardHandle):
    for k, v in pcm.get_all_packs():
        msg = f"""
pack name = {v}
pack id = {k}
"""
        print(msg)
        
def get_card_price(pcm: clss.PackCardHandle):
    pid, cid = get_card_by_collector_num(pcm)
    if pid == None or cid == None:
        print("operation canceled")
        return None
    cd = pcm.get_card_info(pid, cid)
    name = cd.name
    ft = cd.flavorText
    msg = f"""verify the data of your card. if all are correct enter 'y' else 'n'. 'c' to cancel
is the name of your card {name}?
is the flavor text of your card '{ft}'
"""
    b = get_input("bool", msg)
    if b:
        pt = get_print_type(pcm, pid, cid)
        if pt == None:
            print("operation canceled")
            return None
        try:
            data = pcm.get_card_price_data(pid, cid, pt)
        except AttributeError:
            print("invalid print type. try again.")
            return get_card_price()
        print(data)
    elif b == None:
        print("operation canceled")
        return None
    else:
        return get_card_price()
    

def main():
    run = True
    file = config.DEFAULT_FILE
    api = config.API_KEY
    app, pcm = init(api_key=api, file=file)
    while run:
        mode_msg = """select one of the following options and enter the corresponding number
0: quit
1: add card
2: remove card
3: list packs
4: list collection
5: get a cards market price
"""
        mode = get_input("int", mode_msg)
        if mode == None or mode == 0:
            run = False
            continue
        elif mode == 1:
            add_card(pcm, app)
        elif mode == 2:
            remove_card(pcm, app)
        elif mode == 3:
            list_packs(pcm)
        elif mode == 4:
            list_collection(app, pcm)
        elif mode == 5:
            get_card_price(pcm)
        else:
            print("unknown entry try again")
    app.save_collection()
    
if __name__ == "__main__":
    main()