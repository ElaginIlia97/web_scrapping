from selenium import webdriver

from .getData import *

import time

import pandas as pd

from sqlalchemy import create_engine

import logging
import datetime

year = datetime.datetime.today().year
month = datetime.datetime.today().month
day = datetime.datetime.today().day
hour = datetime.datetime.today().hour

logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = '.\Logs\Initial_load_{0}_{1}_{2}_{3}.log'.format(year, month, day, hour))

logging.info('Process started')

try:

    # Chrome driver path
    driver_path = 'C:\Program Files (x86)\chromedriver.exe'
    driver = webdriver.Chrome(driver_path)
    driver.maximize_window()

    driver.get("https://novosibirsk.n1.ru/")

    logging.info('Load main page')

    # Button for room size selection
    button = driver.find_element_by_xpath('''//button[@class="search-2gen-module-select-base__button _default _placeholder"]''')
    button.click()

    # Get list of room size selectors
    room_dropdown = driver.find_elements_by_xpath('''//div[@class="rooms-filter__dropdown"]/div[2]/div/label''')

    driver.implicitly_wait(5)

    # Выбор типа квартиры
    room_size = ['1-комнатные', '2-комнатные']

    for index, room_type in enumerate(room_dropdown):

        # Click suitable room size selector
        span = room_type.find_element_by_xpath('''span/span[@class="ui-kit-checkbox__text"]''')
        if span.text in room_size:
            span.click()

    # Search button click
    search = driver.find_element_by_xpath('''//button[@class="ui-kit-button search-2gen-short-controls__btn-search _color-terracotta _size-default"]''')
    search.click()

    logging.info('Got to filtered page')
    time.sleep(5)

    # Get list of filtered rooms
    rooms = driver.find_elements_by_xpath('''//div[@class="living-search-item offers-search__item"]''')
    rooms_dict = {
        'address': [],
        'type': [],
        'link': [],
        'created': []
    }

    # Load room info to rooms_dict
    room_list(rooms, rooms_dict, driver)

    driver.quit()

    data = pd.DataFrame.from_dict(rooms_dict, orient='index')
    data = data.transpose()

    data.columns = ['address', 'layout_type', 'link', 'created_on']
    engine = create_engine("postgresql://postgres:Password@localhost/web_scrapping", pool_pre_ping=True)
    data.to_sql('n1_ad', con=engine, if_exists='append', index=False)

    logging.info('Load data to SQL')

except Exception:
    logging.exception("Fatal error in main loop")