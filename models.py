from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, DateTime, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

engine = create_engine("postgresql://postgres:Password@localhost/web_scrapping", pool_pre_ping=True)

Base = declarative_base()
Session = sessionmaker()
Session.configure(bind=engine)

class RoomAd(Base):
    __tablename__ = 'n1_ad'

    id =            Column(Integer, primary_key=True)
    link =          Column(Text)
    layout_type =   Column(String(50))
    address =       Column(String(200))
    created_on =    Column(DateTime)    
    room_info =     relationship("RoomInfo", backref='ad', lazy=True)

class RoomInfo(Base):
    __tablename__ = 'n1_ad_info'

    id =                        Column(Integer, primary_key=True)
    ad_id =                     Column(Integer, ForeignKey('n1_ad.id'), nullable=False)
    total_area =	            Column(Numeric(10, 2))
    floor =			            Column(Integer)
    max_floor =		            Column(Integer)
    constr_year	=	            Column(Integer)
    price =			            Column(Numeric(20, 2))
    average_price_current =		Column(Numeric(20, 2))
    average_price_last_month =	Column(Numeric(20, 2))
    build_material =			Column(String(200))
    request_datetime =          Column(DateTime())