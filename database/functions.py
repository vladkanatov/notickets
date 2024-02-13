from datetime import datetime
from models.main_models import AllEvents

def add_event(event_name: str, url: str, date: datetime, venue: str = None):
    
    event_name = event_name.replace('\n', ' ')
    if venue is not None:
        venue = venue.replace('\n', ' ')
        
    