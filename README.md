

2019-02-23: this appears to be broken and I haven't had time to look into why. maybe steam changed their wishlist page structure.

current status: this mostly just dumps your wishlist to a local sqlite db. lots more to build. 


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
