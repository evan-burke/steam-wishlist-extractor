setup:
1. edit steam_wishlist_extractor.py with your public steam wishlist URL and the local path of the sqlite wrapper lib.
2. add to task scheduler. run daily. 


todo:
* add reporting for price drops and/or price increases
* move steam wishlist link to config file
* add logging
* put sqlite wrapper in relative path
* add requirements.txt and/or package this up more like a module
* detect/warn if/when steam wishlist page format changes
* add retries to http request
