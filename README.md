Free proxies from GitHub!


The scraper uses github search query "filename:proxies.txt", and saves all links to sources/http.txt. After that checks all founded proxies and saves them in folder in config.ini parameter SavePath


install requierments with pip

~~~bash
pip install -r requirements.txt
~~~

and run!
~~~bash
python proxy_parser
~~~

all parsed and checked proxies will save in proxies/parsed.txt. You can change folder if you want in config.ini


WARNING!!! The parser runs in infinite mode, which means that it will collect and check proxies every timelimit which specified in config.ini MainTimeout

replaced main lib requests with aiohttp which increased speed of parsing
