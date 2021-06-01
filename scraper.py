import os
import glob
import time
import random
import pandas as pd
import requests
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm


_BASE_URL = "https://coinmarketcap.com"


class Scraper:
    """
    scrapes data from coinmarketcap.com and stores historical data
    for each cryptocurrency in a csv file
    """

    def __init__(self, load_time, geckodriver_path, 
                 out_dir = 'coin_data', months_back = 38,
                 reload=False):
        """
        takes all the cryptocurrency names with a get request,
        opens a browser and for each cryptocurrency scrapes the data
        
        Args:
            load_time (int): time to wait for loading a page
            geckodriver_path (str): path to the GECKODRIVER 
                                    (executable file) compatible with your browser
            out_dir (str, optional): directory where to save historical data.
                                    if it does not exist, it will create it.
                                    Defaults to 'coin_data'.
            months_back (int, optional): number of months to collect in the past 
                                        Defaults to 38.
            reload (bool, optional): if false, first it checks in out_dir if there are
                                     already saved data. If so, it downloads data only 
                                     for the missing cryptocurrencies. 
                                     Defaults to False.
        """
        self.base_url = _BASE_URL
        self.load_time = load_time
        self.out_dir = out_dir
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)    
        self.months_back = months_back
        self.driver = webdriver.Firefox(
            executable_path = geckodriver_path)
        self.reload = reload
        
    def get_currencies(self, selected_coin = 'all'):
        """
        stores historical data for each cryptocurrency in a csv file
        Args:
            selected_coin (str, optional): which cryptocurrency scrape.
            Defaults to 'all'.
        """
        if selected_coin == 'all':
            self.get_all_historical_data()
        else:
            self.accept_cookies()
            self.save_historical_data(selected_coin)


    def get_all_coin_links(self):
        """takes all the crypto currency from coinmarketcap.com
        with a get request to the site
        Returns:
            set: all the crypto currency links
        """
        url = self.base_url + "/all/views/all/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('tbody')
        links = []
        for tr in table.findAll("tr"):
            trs = tr.findAll("td")
            for each in trs:
                a = each.find('a')
                if each.find('a'):
                    link = a['href']
                    links.append(link)
        return set([l.split('/')[2]
                for l in links])

    def get_all_historical_data(self):
        """if reload:
               gets historical data for all the cryptocurrency and saves them
           else:
               gets historical data for the missing cryptocurrency 
               (first it checks in out_dir wether there are already data)
        """
        coins = self.get_all_coin_links()

        if self.reload:
            coins_to_do = coins
        else:
            # check which currencies have already been downloaded
            done = [file_name[len(self.out_dir)+1:-4]
                for file_name in glob.glob(self.out_dir+"/*")]
            
            coins_to_do = [c for c in coins
                        if c not in done]
            
            print("    {} cryptocurrencies already done.".format(len(done)))
            print("    {} cryptocurrencies missing.".format(len(coins_to_do)))

        if coins_to_do:
            self.accept_cookies()
                
        for coin in tqdm(coins_to_do):
            self.save_historical_data(coin)
        return            
            
    
    def accept_cookies(self):
        """
        The first time the browser loads the site, 
        one needs to accept the cookies,
        otherwise the cookies panel will obscure 
        the button to load more data
        """  
        self.driver.get(self.base_url)
        time.sleep(self.load_time)    
        try:
            panel_close_path = "/html/body/div/div/div[3]/div[2]/div[2]"
            self.driver.find_element_by_xpath(panel_close_path).click()
        except:
            print("\n\n Press x to the botton right of the open page " +
                "to accept cookies and continue scraping. \n\n")
            time.sleep(5)
        return
            
    def save_historical_data(self, coin):
        """saves historical data of coin
        """
        print("Reading data for", coin)
        table = self.get_historical_data(coin)
        df = self.format_table(table)
        print("Number of points", len(df))
        if df is None:
            return
        out_file = self.out_dir + "/{}.csv".format(coin)
        df.to_csv(out_file)
        print("{} printed.\n".format(out_file))        
        return        

    def scroll_and_sleep(self):
        """uses down arrow to scroll down and sleeps"""
        time.sleep(self.load_time + (random.randint(10, 100) / 1500))
        self.driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
        return
    
    def scroll_and_load_more(self):
        """scrolls down 3 times and clicks on button 'load more'
        """
        for j in range(3):
            self.scroll_and_sleep()
        time.sleep(random.randint(50, 100) / 1500)       
        button_path = "/html/body/div/div/div[1]/div[2]/div/div[3]/div/div/p[1]/button"
        self.driver.find_element_by_xpath(button_path).click()
        return

    def get_historical_data(self, coin):
        """loads data for coin back in time

        Args:
            coin (string): a certain cryptocurrency

        Returns:
            string: table with historical data
        """
        url = self.base_url + "/currencies/{}/historical-data/".format(coin)
        self.driver.get(url)
        time.sleep(self.load_time+(random.randint(500,1000)/500))
        
        ## go down
        Y = random.randint(1200, 1900) 
        self.driver.execute_script("window.scrollTo(0, {})".format(Y)) 
        
        table_path = "/html/body/div/div/div[1]/div[2]/div/div[3]/div/div/div[2]/table"
        table = ""
        for i in range(self.months_back-2):
            self.scroll_and_load_more()
            
            # check if there are new data
            previous_last_row = table.split('\n')[-1]
            table = self.driver.find_element_by_xpath(table_path).text
            if table.split('\n')[-1] == previous_last_row:
                print(" Loaded data for {} months.\n".format(i+2) +
                    " No more data to load.")
                return table           
        return table


    @staticmethod
    def format_table(table):
        """transforms the string table in a pandas dataframe"""
        def format_row(row):
            return [w.replace('<','').strip() 
                    for w in row.split('$')]

        def to_num(string):
            string = string.replace(',','')
            return pd.to_numeric(string)


        rows = table.split('\n')
        columns_names = rows[0].split(' ')
        rows = rows[1:]
        rows = [format_row(r) for r in rows]
        columns_names = columns_names[:-2]+['Market_Cap']
        try:
            df = pd.DataFrame(rows, columns = columns_names)
            df['Date'] = df.Date.map(pd.to_datetime)
        except Exception as e:
            print(e)
            return
        for c in df.columns[1:]:
            df[c] = df[c].map(to_num)
        return df
