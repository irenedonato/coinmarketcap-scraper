# Coinmarketcap scraper

Coinmarketcap scraper allows extracting cryptocurrency historical data. First, it takes all the cryptocurrency from the site with a get request. Then, it opens the web page using selenium and scrolls the data back in time. It saves the data for each cryptocurrency in a scv file named as the underlying cryptocurrency.

### Application



#### How to install

Clone this repository and run

```bash
pip install pathlib
cd coinmarketcap-scraper
pip install ./
```

You will need to download also a version of the GECKODRIVER (executable file) compatible with your browser.

#### Usage

``` bash
usage: main.py [-h] [--load_time [LOAD_TIME]] [--out_dir [OUT_DIR]]
               [--months [MONTHS]] [--reload [RELOAD]]
               [--coin COIN [COIN ...]]
               geckodriver

scrape

positional arguments:
  geckodriver           path to geckodriver executable file

optional arguments:
  -h, --help            show this help message and exit
  --load_time [LOAD_TIME], -load_time [LOAD_TIME]
                        waiting time to load the page
  --out_dir [OUT_DIR], -out_dir [OUT_DIR]
                        the path to list
  --months [MONTHS], -months [MONTHS]
                        months of data to collect
  --reload [RELOAD], -reload [RELOAD]
                        refresh crypto already in out_dir
  --coin COIN [COIN ...], -coin COIN [COIN ...]
                        specific coin to load
```

##### Sample calls

Download all the cryptocurrency:

```bash
python main.py ~/geckodriver  -out_dir historical_data 
```

Download a specific cryptocurrency (i.e. bitcoin) for 4 years:

```bash
python main.py ~/geckodriver  -out_dir historical_data -c bitcoin -months 48
```

