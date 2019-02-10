#!/bin/bash

replace_str="put your public wishlist URL here"

cat steam_wishlist_extractor.py | sed "s/steam_wishlist_url.*\".*\"/steam_wishlist_url = \"$replace_str\"/g" > steam-wishlist-extractor/steam_wishlist_extractor.py

echo "cleaned file pushed to repo dir."
