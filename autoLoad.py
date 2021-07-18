from .getData import room_info_load
import time
import pandas as pd
from sqlalchemy import create_engine
import schedule

engine = create_engine("postgresql://postgres:Password@localhost/web_scrapping", pool_pre_ping=True)

schedule.every().day.at("10:00").do(room_info_load, engine)

while True:
    schedule.run_pending()