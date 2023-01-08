# proxy-scraper
Scrapes proxies for github


The parser uses links to github files named proxies.txt and checks them in multithreading


install requierments with pip


pip install -r requirements.txt

and run!

python main.py

all parsed and checked proxies will save in proxies/parsed.txt. You can change folder if you want in config.ini


WARNING!!! The parser runs in infinite mode, which means that it will collect and check proxies every 2 minutes.

