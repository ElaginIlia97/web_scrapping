from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import re
import time
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd
import numpy as np

import logging


def rid_of_first_zero(today, type):
    if today.strftime(f'%{type}').startswith('0'):
        return(today.strftime(f'%{type}').replace('0', ''))
    else:
        return(today.strftime(f'%{type}'))

def room_list(rooms, rooms_dict, driver):
    for index, room in enumerate(rooms):
        title_div = room.find_element_by_css_selector("div.card-title.living-list-card__inner-block")
        room_type = title_div.find_element_by_class_name("link-text").text.split(' ', 1)[0].replace(',', '')
        title = title_div.find_element_by_class_name("link-text").text.split(' ', 1)[1:]
        title = ''.join(title)
        if title.endswith(' стр.'):
            title = ' '.join(title.split(' ')[:-1])
        link = room.find_element_by_css_selector("a.link").get_attribute('href')

        # Check for unique title
        if ''.join(title) not in rooms_dict['address']:
            rooms_dict['address'].append(''.join(title))
            rooms_dict['link'].append(link)
            rooms_dict['type'].append(room_type)
            rooms_dict['created'].append(datetime.now().strftime(r"%Y-%m-%d %H:%M:%S"))

        # No more then 10 buildings are needed
        if len(rooms_dict['address']) == 10 :
            break
        # Check if there enough data in opened page
        if index+1 == len(rooms) and len(rooms_dict['address']) < 10:
            ele = driver.find_element_by_tag_name('body')
            ele.send_keys(Keys.END)
            div = driver.find_element_by_css_selector("div.paginator")
            next_link = div.find_element_by_css_selector("a.paginator-pages__link[data-test='offers-list-next-page']")
            next_link.click()
            rooms = driver.find_elements_by_xpath('''//div[@class="living-search-item offers-search__item"]''')
            room_list(rooms)

def room_info(link_url, ad_id):
    scrap_result = {
       # 'address': f'{address}',
        #'room_type': f'{room_type}',
        'ad_id': ad_id,
        'total_area': '',
        'floor': '',
        'max_floor': '',
        'constr_year': '',
        'price': '',
        'average_price_current': '',
        'average_price_last_month': '',
        'build_material': '',
        'request_datetime': ''
    } 
    
    # Chrome driver path
    driver_path = 'C:\Program Files (x86)\chromedriver.exe'
    driver = webdriver.Chrome(driver_path)
    driver.maximize_window()

    driver.get(link_url)

    # Waiting for full page load
    driver.implicitly_wait(5)

    # Gather some information 
    #page_link = driver.current_url
    total_area = driver.find_element_by_css_selector("span[data-test='offer-card-param-total-area']").text.split(' ')[0].replace(',', '.')
    floor = driver.find_element_by_css_selector("span[data-test='offer-card-param-floor']").text.split(' ')[0]
    max_floor = driver.find_element_by_css_selector("span[data-test='offer-card-param-floor']").text.split(' ')[2]
    #year_constr_div = driver.find_element_by_css_selector("div.card-living-content__info")
    price = driver.find_element_by_css_selector("header.offer-card-header").find_element_by_css_selector("span.price").text
    price = price.encode('ascii', 'ignore').decode("utf-8").replace(',', '.')
    building_material = driver.find_element_by_css_selector("span[data-test='offer-card-param-house-material-type']").text

    # Try catch for build year
    try:
        year_constr = driver.find_element_by_xpath("//li[@class='card-living-content-params-list__item'][span/text()='Год постройки']/span[2]").text.split(' ')[0]
    except:
        year_constr = driver.find_element_by_xpath("//li[@class='card-living-content-params-list__item'][span/text()='Срок сдачи']/span[2]").text
        year_constr = re.findall("\d{4}", year_constr)[0]

    # DOM of price graph
    graphs = driver.find_element_by_css_selector("div.similar-prices-chart__main")

    rus_month = ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня', 'Июля', 'Августа', 'Сентября', 'Ноября', 'Декабря']
    
    today = date.today()
    today_str = f"{today.strftime(f'%d')} {rus_month[int(rid_of_first_zero(today, 'm'))-1]} {today.strftime('%Y')}"

    monthBack = today - relativedelta(months=1)
    monthBack_str = f"01 {rus_month[int(rid_of_first_zero(monthBack, 'm'))-1]} {monthBack.strftime('%Y')}"

    # Go to graph element
    actions = ActionChains(driver)
    actions.move_to_element_with_offset(graphs, 0, 0)
    actions.perform()
    actions.move_by_offset(700, 100).perform()

    time.sleep(2)

    today_price_chart_district = ''
    month_back_price_chart_district = ''

    # Iterate through graph in order to get price in different time period
    for i in range(30):
        actions = ActionChains(driver)
        actions.move_to_element_with_offset(graphs, 0, 0)
        actions.move_by_offset(700+10*i, 100).perform()
        price_list = driver.find_element_by_css_selector("ul.prices-chart-tooltip__list")
        if driver.find_element_by_css_selector("div.prices-chart-tooltip__title").text == today_str:
            today_price_chart_district = price_list.find_element_by_xpath("li[1]").find_element_by_css_selector("strong.prices-chart-tooltip__price").text.encode('ascii', 'ignore').decode("utf-8").replace(',', '.')
            break

        if driver.find_element_by_css_selector("div.prices-chart-tooltip__title").text == monthBack_str:
            month_back_price_chart_district = price_list.find_element_by_xpath("li[1]").find_element_by_css_selector("strong.prices-chart-tooltip__price").text.encode('ascii', 'ignore').decode("utf-8").replace(',', '.')

    # Close browser
    driver.quit()

    # Collect all data into final dictionary
    #scrap_result['link'] = page_link
    scrap_result['total_area'] = total_area
    scrap_result['floor'] = floor
    scrap_result['max_floor'] = max_floor
    scrap_result['constr_year'] = year_constr
    scrap_result['price'] = price
    scrap_result['average_price_current'] = today_price_chart_district
    scrap_result['average_price_last_month'] = month_back_price_chart_district
    scrap_result['build_material'] = building_material
    scrap_result['request_datetime'] = datetime.now().strftime(r"%Y-%m-%d %H:%M:%S")

    return scrap_result

import multiprocessing
from joblib import Parallel, delayed

def room_info_load(engine):

    try:
        year = datetime.today().year
        month = datetime.today().month
        day = datetime.today().day
        hour = datetime.today().hour
        logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = '.\Logs\Rooms_info_Update_{0}_{1}_{2}_{3}.log'.format(year, month, day, hour))
        
        # Load data from database with links
        df1 = pd.read_sql_table('n1_ad', con=engine)

        logging.info('Load data from SQL')

        rooms_link = df1['link'].to_list()
        rooms_id   = df1['id'].to_list()

        # Number of processors
        num_cores = multiprocessing.cpu_count()

        # Got data from each link
        room_list = Parallel(n_jobs=num_cores)(delayed(room_info)(rooms_link[i], rooms_id[i]) for i in range(len(rooms_link)))

        df = pd.DataFrame(room_list)

        logging.info('Get each room info')

        # Load to temp

        df = df.replace(r'^\s*$', np.NaN, regex=True)
        
        df.to_sql("n1_ad_info", con=engine, if_exists='append', index=False)

        logging.info('Load info to database')
    except Exception:
        logging.exception("Fatal error in main loop")