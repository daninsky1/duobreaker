from database import TransPair, TransList, TransDatabase


# TODO: use a xlsx database to test methods

def construct_tl():
    my_tl = TransList()
    translations = [["car", "carro"], ["water", "água"]]
    for phrases in translations:
        my_tl.append(TransPair.fromlist(phrases))
    return my_tl

def tl_init():

    pass

def tl_insert():
    pass

def tl_extend():
    my_tl = TransList()
    my_tl2 = TransList()
    car = TransPair("car", "carro")
    water = TransPair("water", "água")
    cup = TransPair("cup", "xícara")
    water = TransPair("water", "água")
    my_tl.append(car)
    my_tl.append(water)
    my_tl2.append(car)
    my_tl2.append(water)


def tl_remove():
    print("* TransList.remove(): ", sep="", end="")
    my_tl = TransList()
    car = TransPair("car", "carro")
    water = TransPair("water", "água")
    my_tl.append(car)
    my_tl.append(water)
    my_tl.remove(car)
    if car not in my_tl:
        print("Passed!")
    else:
        print("Failed!")

def tl_pop():
    passed = True
    print("* TransList.__pop__(): ", sep="", end="")
    my_tl = TransList()
    car = TransPair("car", "carro")
    water = TransPair("water", "água")
    fan = TransPair("fan", "ventilador")
    my_tl.append(car)
    my_tl.append(water)
    my_tl.pop()
    my_tl.pop(0)
    try:
        my_tl.pop(water)
    except TypeError:
        pass
    else:
        passed = False
    if water in my_tl:
        passed = False
    if passed:
        print("Passed!")
    else:
        print("Failed!")

def tl_iter():
    print("* TransList.__iter__(): ", sep="", end="")
    passed = True
    my_tl = TransList()
    tp_list = []
    car = TransPair("car", "carro")
    water = TransPair("water", "água")
    my_tl.append(car)
    my_tl.append(water)
    tp_list.append(car)
    tp_list.append(water)
    for tp_tl, tp_lst in zip(my_tl, tp_list):
        if tp_tl != tp_lst:
            passed = False
    if passed:
        print("Passed!")
    else:
        print("Failed!")

def tl_len():
    print("* TransList.len__(): ", sep="", end="")
    my_tl = construct_tl()
    if len(my_tl) == 2:
        print("Passed!")
    else:
        print("Failed!")

def tl_getitem():
    print("* TransList.__getitem__(): ", sep="", end="")
    my_tl = TransList()
    car = TransPair("car", "carro")
    water = TransPair("water", "água")
    my_tl.append(car)
    my_tl.append(water)
    if (my_tl[0] == car) and (my_tl[1] == water):
        print("Passed!")
    else:
        print("Failed!")

def tl_append():
    passed = True
    print("* TransList.append(): ", sep="", end="")
    my_tl = TransList()
    car = TransPair("car", "carro")
    water = TransPair("water", "água")
    my_tl.append(car)
    my_tl.append(water)
    if (car in my_tl) and (water in my_tl):
        pass
    else:
        passed = False
    try:
        my_tl.append(["hi", "oi"])
        my_tl.append(("hi", "oi"))
        my_tl.append(3.0)
        my_tl.append(2)
    except (TypeError, KeyError):
        pass
    else:
        passed = False
    if passed:
        print("Passed!")
    else:
        print("Failed!")

def tl__contains():
    print("* TransList.__contains__(): ", sep="", end="")
    car = TransPair("car", "carro")
    water = TransPair("water", "água")
    my_tl = TransList(car)
    my_tl.append(water)
    if (car in my_tl) and (water in my_tl):
        print("Passed!")
    else:
        print("Failed!")

def tl_str():
    my_tl = construct_tl()
    print(my_tl)

def tl_eq():
    print("* TransList.__eq__(): ", sep="", end="")
    my_tl = TransList()
    my_tl2 = TransList()
    my_tl3 = TransList()
    car = TransPair("car", "carro")
    water = TransPair("water", "água")
    my_tl.append(car)
    my_tl.append(water)
    my_tl2.append(car)
    my_tl2.append(water)
    my_tl3.append(car)
    if my_tl == my_tl2 and my_tl != my_tl3:
        print("Passed!")
    else:
        print("Failed")

def test_trans_list():
    tl_init()
    tl_insert()
    tl_extend()
    tl_remove()
    tl_pop()
    tl_len()
    tl_iter()
    tl_getitem()
    tl_append()
    tl__contains()
    tl_eq()

def tp_init():
    mytp = TransPair("hi", "oi")
    print(mytp)

def tp_iter():
    mytp = TransPair("hi", "oi")
    for item in mytp:
        print(item)

def tp_switch():
    mytp = TransPair("hi", "oi")
    mytp.switch()
    print(mytp)

def tp_append():
    mytp = TransPair("hi", "oi")
    mytp.append("hello")
    print(mytp)


def test_db2():
    my_translist = TransList(("hi", "oi"))
    my_translist2 = TransList(["car", "carro"])
    new_translist = TransList()
    my_trans_pair = TransPair("olá", "hello")
    new_translist.extend(my_translist)
    new_translist.extend(my_translist2)

    print(my_translist, my_translist2, sep="\n")


def tl_contains_test():
    hi = TransPair("hi", "oi")
    my_trans_list = TransList(hi)
    my_trans_list.append(hi)

def td_test():
    my_tl = TransList()
    translations = [["car", "carro"], ["water", "água"]]
    for phrases in translations:
        my_tl.append(TransPair(phrases[0], phrases[1]))

    my_database = TransDatabase("en", "pt")
    my_database.add("saudações", my_tl)
    my_database.add("phrases")
    my_database["daniel"] = my_tl

    my_tl_back = my_database["saudações"]

    print(len(my_tl))
    print(len(my_database["daniel"]))
    print(type(my_database["daniel"]))
    print(my_tl)
    print(my_database)

def tdb_load_save_test():
    my_tdb = TransDatabase.fromfile(r"../database/Acidentes/Acidentes_en_to_pt_dictionary.xlsx")
    my_tdb.save(r"../test_noascii.json")
    my_tdb2 = TransDatabase.fromfile(r"../test_noascii.json")
    my_tdb2.save(r"../test.xlsx")


if __name__ == "__main__":
    import json
    print(dir(tuple))
    # tp_append()