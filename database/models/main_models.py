from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

Base = declarative_base(metadata=MetaData())

# engine = create_engine('mysql://lon8:132465-Cs@localhost/eventservice')

class AllEvents(Base):
    __tablename__ = 'all_events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))  # Размер 255 (замените на нужный)
    link = Column(String(255))  # Размер 255 (замените на нужный)
    parser = Column(String(255))  # Размер 255 (замените на нужный)
    venue = Column(String(255))
    date = Column(DateTime)
    average_price = Column(Integer)

class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(255))  # Размер 255 (замените на нужный)

class EventCategories(Base):
    __tablename__ = 'event_categories'

    event_id = Column(Integer, ForeignKey('all_events.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), primary_key=True)

class Venues(Base):
    __tablename__ = 'venues'

    id = Column(Integer, primary_key=True, autoincrement=True)
    venue_name = Column(String(255))  # Размер 255 (замените на нужный)
    description = Column(Text)

class Cities(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    city_name = Column(String(255))  # Размер 255 (замените на нужный)

class CityVenues(Base):
    __tablename__ = 'city_venues'

    city_id = Column(Integer, ForeignKey('cities.id'), primary_key=True)
    venue_id = Column(Integer, ForeignKey('venues.id'), primary_key=True)

class GroupedEvents(Base):
    __tablename__ = 'grouped_events'

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('all_events.id'))
    description = Column(Text)
    venue_id = Column(Integer, ForeignKey('venues.id'))

class Sites(Base):
    __tablename__ = 'sites'

    id = Column(Integer, primary_key=True, autoincrement=True)
    site = Column(String(255))  # Размер 255 (замените на нужный)

class EventSites(Base):
    __tablename__ = 'event_sites'

    event_id = Column(Integer, ForeignKey('all_events.id'), primary_key=True)
    site_id = Column(Integer, ForeignKey('sites.id'), primary_key=True)

# Session = sessionmaker(bind=engine)

# session = Session()

# metadata = Base.metadata.create_all(bind=engine)