import base64
import csv
import datetime
import io
import os
import re
import time
from threading import Thread
from time import sleep

import logging
from dotenv import load_dotenv
# from pymouse import PyMouse
from pynput.keyboard import Key, Controller

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium import webdriver
from selenium.webdriver.common.by import By

try:
    from PIL import Image, ImageFilter
except ImportError:
    import Image

import pytesseract

base = os.path.dirname(os.path.realpath(__file__))
load_dotenv(os.path.join(base, '.env'))
USERNAME = os.environ.get("TRADINGVIEW_USERNAME")
PASSWORD = os.environ.get("TRADINGVIEW_PASSWORD")

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

# input("anykey to continue")

huOpenSelector = 'return document.querySelectorAll("body > div.js-rootresizer__contents > div.layout__area--center > div > div.chart-container-border > div.chart-widget > table > tbody > tr:nth-child(1) > td.chart-markup-table.pane > div > div.pane-legend > div.pane-legend-line.pane-legend-wrap.main > div > span:nth-child(1) > span.pane-legend-item-value.pane-legend-line.pane-legend-item-value__main")[0].textContent'
huHighSelector = 'return document.querySelectorAll("body > div.js-rootresizer__contents > div.layout__area--center > div > div.chart-container-border > div.chart-widget > table > tbody > tr:nth-child(1) > td.chart-markup-table.pane > div > div.pane-legend > div.pane-legend-line.pane-legend-wrap.main > div > span:nth-child(2) > span.pane-legend-item-value.pane-legend-line.pane-legend-item-value__main")[0].textContent'
huLowSelector = 'return document.querySelectorAll("body > div.js-rootresizer__contents > div.layout__area--center > div > div.chart-container-border > div.chart-widget > table > tbody > tr:nth-child(1) > td.chart-markup-table.pane > div > div.pane-legend > div.pane-legend-line.pane-legend-wrap.main > div > span:nth-child(3) > span.pane-legend-item-value.pane-legend-line.pane-legend-item-value__main")[0].textContent'
huCloseSelector = 'return document.querySelectorAll("body > div.js-rootresizer__contents > div.layout__area--center > div > div.chart-container-border > div.chart-widget > table > tbody > tr:nth-child(1) > td.chart-markup-table.pane > div > div.pane-legend > div.pane-legend-line.pane-legend-wrap.main > div > span:nth-child(4) > span.pane-legend-item-value.pane-legend-line.pane-legend-item-value__main")[0].textContent'

huVol1Selector = 'return document.querySelectorAll("body > div.js-rootresizer__contents > div.layout__area--center > div > div.chart-container-border > div.chart-widget > table > tbody > tr:nth-child(1) > td.chart-markup-table.pane > div > div.pane-legend > div.pane-legend-line.pane-legend-wrap.study > div > span:nth-child(1) > span")[0].textContent'
huVol2Selector = 'return document.querySelectorAll("body > div.js-rootresizer__contents > div.layout__area--center > div > div.chart-container-border > div.chart-widget > table > tbody > tr:nth-child(1) > td.chart-markup-table.pane > div > div.pane-legend > div.pane-legend-line.pane-legend-wrap.study > div > span:nth-child(2) > span")[0].textContent'

done = set()

if os.path.isfile("data.csv"):
    with open("data.csv", "r") as file:
        reader = csv.reader(file)

        for row in reader:
            done.add(row[0])


def mover(start_x):
    sleep(4)
    m = PyMouse()
    m.move(start_x, 500)
    keyboard = Controller()

    while True:
        keyboard.press(Key.left)
        sleep(100)


def parse_time(text):
    text = text.split("\n")
    if len(text) == 2:
        text = text[1]
    else:
        text = text[0]

    text = text.replace("'", "").replace("`", "").replace("-", "").replace("‘", "")
    text = re.sub("\\s+", " ", text)
    return time.mktime(datetime.datetime.strptime(text, "%d %b %y %H:%M").timetuple())


def extract_text(b64_encoded):
    image = Image.open(io.BytesIO(base64.b64decode(b64_encoded)))
    image = image.crop(image.getbbox())
    image = image.filter(ImageFilter.SHARPEN)
    image = image.filter(ImageFilter.DETAIL)
    width = 300
    wpercent = (width / float(image.size[0]))
    hsize = int((float(image.size[1]) * float(wpercent)))
    image = image.resize((width, hsize), Image.ANTIALIAS)
    return pytesseract.image_to_string(image)


def collect():
    keyboard = Controller()
    f = open("{}_{}_{}.csv".format(EXCHANGE, SYMBOL, int(time.time())), "a")
    writer = csv.writer(f)

    while True:
        # for i, canvas in enumerate(driver.find_elements_by_tag_name("canvas")):

        try:
            canvas = driver.find_elements_by_tag_name("canvas")[8]
            canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);",
                                                  canvas)
            time_text = extract_text(canvas_base64)
            timestamp = int(parse_time(time_text))
            huOpen = driver.execute_script(huOpenSelector)
            huHigh = driver.execute_script(huHighSelector)
            huLow = driver.execute_script(huLowSelector)
            huClose = driver.execute_script(huCloseSelector)
            huVolume1 = driver.execute_script(huVol1Selector)
            huVolume2 = driver.execute_script(huVol2Selector)
        except Exception as e:
            print(e)
            continue

        if timestamp not in done:
            writer.writerow([
                timestamp,
                huOpen,
                huHigh,
                huLow,
                huClose,
                huVolume1,
                huVolume2,
            ])
            done.add(timestamp)

            print(len(done), timestamp, huOpen, huHigh, huLow, huClose, huVolume1, huVolume2)
        keyboard.press(Key.left)
        keyboard.release(Key.left)


if __name__ == '__main__':
    EXCHANGE = "NASDAQ"
    SYMBOL = "GOOG"
    driver.get("https://uk.tradingview.com/#signin")
    print(">> Loading home page")

    username = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.NAME, 'username')))
    password = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.NAME, 'password')))

    username.send_keys(USERNAME)
    password.send_keys(PASSWORD)
    print(">> Logging in")

    login = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                             "//button[@type='submit']")))

    login.submit()
    print(">> Logged in")

    print(">> Loading Stock Page")
    driver.get("https://uk.tradingview.com/chart?symbol={}:{}".format(EXCHANGE, SYMBOL))

    sleep(2)
    driver.execute_script(
        'document.querySelectorAll("body > div.js-rootresizer__contents > div.layout__area--center > div > div.chart-container-border > div.chart-controls-bar > div > div:nth-child(2) > div > div.sliderRow-Tv1W7hM5-.tabs-1LGqoVz6- > div.item-3cgIlGYO-.isFirst-2kfAV5tf- > div.apply-common-tooltip")[0].click()'
    )
    sleep(1)
    driver.execute_script(
        'document.querySelectorAll("body > div.js-rootresizer__contents > div.layout__area--center > div > div.chart-container-border > div.chart-widget > table > tbody > tr:nth-child(1) > td.chart-markup-table.pane > div > div.pane-legend > div.pane-legend-line.pane-legend-wrap.study > span.pane-legend-icon-container > a.pane-legend-icon.apply-common-tooltip.format")[0].click()'
    )
    sleep(1)
    driver.execute_script(
        'document.querySelectorAll("body > div._tv-dialog._tv-dialog-nonmodal.ui-draggable > div._tv-dialog-content > div:nth-child(2) > table > tbody > tr:nth-child(1) > td:nth-child(2) > input")[0].value = 1'
    )
    sleep(2)
    driver.execute_script(
        'return document.querySelectorAll("body > div._tv-dialog._tv-dialog-nonmodal.ui-draggable > div._tv-dialog-content > div.main-properties.main-properties-aftertabs > div > a._tv-button.ok")[0].click()')
    print(">> Collecting Data")
    sleep(2)

    start_coords = driver.find_element_by_class_name("icon-2Gun4jqH-").location

    print(start_coords)
    # m = PyMouse()
    # m.move(start_coords["x"] - 100, 500)
    # mover_thread = Thread(target=mover, args=(start_coords["x"] - 100,))
    # mover_thread.start()

    input("Anykey to start")
    for i in range(0, 5):
        print("Starting in {}....".format(5 - i))
        sleep(1)
    collect()
