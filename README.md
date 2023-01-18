# proxy-scraper
Easy proxies from GitHub!


The scraper uses github search query "filename:proxies.txt", and saves all links to sources/http.txt. After that checks all founded proxies and saves them in folder in config.ini parameter SavePath


install requierments with pip

pip install -r requirements.txt

and run!

python main.py

all parsed and checked proxies will save in proxies/parsed.txt. You can change folder if you want in config.ini


WARNING!!! The parser runs in infinite mode, which means that it will collect and check proxies every timelimit which specified in config.ini MainTimeout

