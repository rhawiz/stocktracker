import csv
import os
from threading import Thread
from time import sleep, time

import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium import webdriver
import sqlite3

"""

conn = sqlite3.connect('data.db', check_same_thread=False)

CREATE_TABLE_QUERY = '''
CREATE TABLE prices (
    isn       REAL,
    bid       TEXT,
    ask       REAL,
    cul_vol   TEXT,
    timestamp DATETIME,

)'''

c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='prices'")

if not len(c.fetchall()) == 1:
    c.execute(CREATE_TABLE_QUERY)



INSERT_QUERY = '''
INSERT INTO prices (
       cul_vol,
       isn,
       ask,
       bid,
       timestamp
   )
   VALUES (
       {cul_vol},
       '{isn}',
       {ask},
       {bid},
       {timestamp}
    );

'''


def insert_worker(connection, **kwargs):
    while True:
        try:
            connection.execute(INSERT_QUERY.format(**kwargs))
            return True
        except Exception as e:
            print(e)
            pass

"""
base = os.path.dirname(os.path.realpath(__file__))
load_dotenv(os.path.join(base, '.env'))
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")

if os.name == 'posix':
    DRIVER_PATH = "drivers/chromedriver"
elif os.name == 'nt':
    DRIVER_PATH = 'drivers/chromedriver.exe'
else:
    logging.error("No chromedriver found for OS")
    exit(1)

options = webdriver.ChromeOptions()
print(DRIVER_PATH)
# options.add_argument('headless')

driver = webdriver.Chrome(os.path.join(base, DRIVER_PATH))
#
# driver.get("https://www.bitstamp.net/market/tradeview/")

driver.maximize_window()

driver.get("https://www.bitstamp.net/account/login/")
username = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.ID, 'id_username')))
password = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.ID, 'id_password')))

username.send_keys(USERNAME)
password.send_keys(PASSWORD)
input("Click")

# input("anykey to continue")
sleep(5)

done = set()

if os.path.isfile("data.csv"):
    with open("data.csv", "r") as file:
        reader = csv.reader(file)

        for row in reader:
            done.add(row[0])


def main():
    with open("data.csv", "a") as f:
        writer = csv.writer(f)

        while True:
            t0 = time()
            try:
                huDate = driver.find_element_by_id('huDate').text
                huDate = huDate.replace("-", "").replace(":", "").replace(" ", "")
                huOpen = driver.find_element_by_id('huOpen').text
                huHigh = driver.find_element_by_id('huHigh').text
                huLow = driver.find_element_by_id('huLow').text
                huClose = driver.find_element_by_id('huClose').text
                huVolume = driver.find_element_by_id('huVolume').text

                if huDate not in done:
                    writer.writerow([
                        huDate,
                        huOpen,
                        huHigh,
                        huLow,
                        huClose,
                        huVolume
                    ])
                    done.add(huDate)

                print(len(done), huDate)
            except Exception:
                pass


main()
