### Grabs prices from the specified steam wishlist and logs them in a db daily.

import requests
from bs4 import BeautifulSoup
import json
import datetime
import sqlite3
import importlib.util

# ------------------------------------------
# CONFIG

steam_wishlist_url = "put your public wishlist URL here"


# used to construct store page links in conjunction with app IDs
store_base_url = "https://store.steampowered.com/app/"

# sqlite db where we'll store this
dbfile = "steam_wishlist.db"

verbose = 0

dblib_location = "C:/pylib/sqlitelib.py"

# ------------------------------------------

# custom path for local library imports

spec = importlib.util.spec_from_file_location("sqlitelib", dblib_location)
dblib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dblib)

db = dblib.sqlitelib(dbfile)


# ------------------------------------------


def extract_wishlist_items(items_json):
    # given wishlist items parsed from json, extract prices etc.

    game_ids = list(items_json.keys())

    if len(game_ids) < 1:
        print("error: no wishlist items returned")
        return None

    else:
        # price extraction logic:
        # skip if free, denoted by 'free' = 1
        # skip if pre-release denoted by 'prerelease' = 1

        wishlist = []

        for i in game_ids:
            row = {}
            wish_item = items_json[i]
            row["id"] = i
            row["name"] = wish_item["name"]
            row["store_link"] = store_base_url + i

            # there's an 'id' field in the subs dict. seems to be an ID of a particular item for the "app",
            # for when there might be multiple.
            # subs: {discount_block(orig & final price), discount_pct, id, price}

            # sometimes there's more than one sub, each with its own id.
            # I'm *assuming* that the first sub is always the base item. this may not be a correct assumption,
            # but I'm not seeing anything that doesn't adhere to this at the moment.
            # also assuming I want the base game, not any add-ons or whatever.

            if "free" in wish_item:
                if wish_item["free"] == 1:
                    continue
            elif "prerelease" in wish_item:
                if wish_item["prerelease"] == 1:
                    continue
            try:
                if "discount_block" in wish_item["subs"][0]:
                    # assumption described above is here
                    discblk = wish_item["subs"][0]["discount_block"]

                    try:
                        bsoup = BeautifulSoup(discblk, "html.parser")
                        if "discount_original_price" in discblk:
                            # item is on sale
                            orig_price = float(
                                bsoup.select_one(
                                    ".discount_original_price"
                                ).text.replace("$", "")
                            )
                            sale_price = float(
                                bsoup.select_one(".discount_final_price").text.replace(
                                    "$", ""
                                )
                            )
                            disc_pct = round(
                                1 - (orig_price - sale_price) / orig_price, 3
                            )
                        else:
                            # not on sale
                            orig_price = float(
                                bsoup.select_one(".discount_final_price").text.replace(
                                    "$", ""
                                )
                            )
                            sale_price = None
                            disc_pct = None

                    except:
                        print("error parsing discount block for row:\n", row)
                        print(discblk, "\n")

                    row["orig_price"] = orig_price
                    row["sale_price"] = sale_price
                    row["disc_pct"] = disc_pct

                else:
                    print("-- NO DISCOUT BLOCK FOUND --\n", row)
                    pprint(wish_item)  # ['subs'])
                    print("")

            except:
                print("err323423")
                print(wish_item)

            # pprint(ws_arr[i]['subs'])
            # print()

            wishlist.append(row)

        return wishlist


def get_wishlist_page():
    # gets wishlist items, names, etc. from the wishlist page.

    wishlist_html = requests.get(steam_wishlist_url)

    soup = BeautifulSoup(wishlist_html.text, "html.parser")

    # items = soup.find_all('div', attrs={'class': 'wishlistRowItem'})  # old
    items_json = soup.find_all("script")

    if len(items_json) > 1:

        # get json array items for wishlist.
        ws_arr = None
        for n, i in enumerate(items_json):
            element = str(i)

            if "g_rgAppInfo" in element:
                e1 = element.split("var ")

                for i in e1:
                    if "g_rgAppInfo" in i:
                        e2 = i.split("g_rgAppInfo = ")[1]
                        e3 = e2.rstrip().rstrip(";")

                        if len(e3) > 0:
                            ws_arr = json.loads(e3)
                            break

        return extract_wishlist_items(ws_arr)


def insert_items(wishlist):
    # Inserts items into the sqlite db.

    # add date to wishlist
    curdate = datetime.date.today()
    for i in range(len(wishlist)):
        wishlist[i]["date"] = curdate

    sqlite_table_ddl = """CREATE TABLE IF NOT EXISTS games (
        date text NOT NULL,
        app_id integer NOT NULL,
        name text NOT NULL,
        orig_price REAL NOT NULL,
        sale_price REAL,
        discount REAL,
        store_link text NOT NULL,
        PRIMARY KEY (date, app_id)
        )"""

    db.execute(sqlite_table_ddl)

    insert_query = """insert or ignore into games(date, app_id, name,
                orig_price, sale_price, discount, store_link)
            values (:date, :id, :name, :orig_price, :sale_price, :disc_pct, :store_link)
            """  # ON CONFLICT IGNORE"""
    db.executemany(insert_query, wishlist)


### MAIN:

wishlist = get_wishlist_page()
insert_items(wishlist)
