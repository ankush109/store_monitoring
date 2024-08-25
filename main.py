import time
import uuid
from fastapi import FastAPI, BackgroundTasks ,Depends
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, Session, create_engine ,select
import pandas as pd
from models import StoreStatus, StoreBusinessHours, StoreTimezone, OriginalBuisnessHours
from dateutil import parser
from datetime import datetime, timedelta
from pytz import timezone
from db import init_db ,get_session
# PostgreSQL connection string format: "postgresql://user:password@host/dbname"

def load_store_status_csv(limit=10000):
    df = pd.read_csv("store_status.csv")
    df = df.head(limit)  # Limit to the first limit records
    print("Loading store status data...")
    with next(get_session()) as session:
        statuses = [
            StoreStatus(
                store_id=row["store_id"],
                timestamp_utc=parser.parse(row["timestamp_utc"]),
                status=row["status"]
            )
            for _, row in df.iterrows()
        ]
        session.bulk_save_objects(statuses)
        session.commit()

def load_store_business_hours_csv(limit=10000):
    df = pd.read_csv("store_hours.csv")
    df = df.head(limit)  # Limit to the first limit records
    with next(get_session()) as session:
        business_hours = [
            StoreBusinessHours(
                store_id=row["store_id"],
                day_of_week=row["day"],
                start_time_local=parser.parse(row["start_time_local"]).time(),
                end_time_local=parser.parse(row["end_time_local"]).time()
            )
            for _, row in df.iterrows()
        ]
        session.bulk_save_objects(business_hours)
        session.commit()

def load_store_timezone_csv(limit=10000):
    df = pd.read_csv("store_timezone.csv")
    df = df.head(limit)  # Limit to the first limit records
    with next(get_session()) as session:
        timezones = [
            StoreTimezone(
                store_id=row["store_id"],
                timezone_str=row["timezone_str"]
            )
            for _, row in df.iterrows()
        ]
        session.bulk_save_objects(timezones)
        session.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application setup...")
    init_db()
    load_store_status_csv()
    load_store_business_hours_csv()
    load_store_timezone_csv()
    print("Application setup complete.")
    yield
    print("Application is shutting down...")

app = FastAPI(lifespan=lifespan)

reports = {}


@app.get("/")
def home(session: Session = Depends(get_session)):
    Convert(session)


def Convert(session: Session = Depends(get_session)):
    # Query all StoreBusinessHours
    print("Conversion from localtime zone to utc started...")
    business_hours_statement = select(StoreBusinessHours)
    business_hours_results = session.exec(business_hours_statement).all()
    
    # Query all StoreTimezones
    timezone_statement = select(StoreTimezone)
    timezone_results = session.exec(timezone_statement).all()
    
    # Create a dictionary for quick timezone lookups
    timezone_dict = {result.store_id: result.timezone_str for result in timezone_results}
    
    for record in business_hours_results:
        # Get the store's timezone
        timezone = timezone_dict.get(record.store_id, "America/Chicago")
        
        # Convert local times to UTC
        start_time_utc = convert_local_to_utc(record.start_time_local, timezone)
        end_time_utc = convert_local_to_utc(record.end_time_local, timezone)
        
        # Create a new OriginalBuisnessHours record
        new_record = OriginalBuisnessHours(
            store_id=record.store_id,
            startTime=start_time_utc,
            endTime=end_time_utc
        )
        
        # Add the new record to the session
        session.add(new_record)
    
    # Commit changes
    session.commit()
    print("All business hours converted and stored successfully.")
from datetime import datetime
import pytz

def convert_local_to_utc(local_time_str: str, timezone_str: str, date_str: str = '2024-08-25', time_format: str = '%H:%M:%S') -> datetime:
    """
    Converts a local time (given as a string) to UTC time.
    """
    # Combine the provided date with the local time string
    local_time_str_combined = f'{date_str} {local_time_str}'
    
    # Define the time zone
    local_tz = pytz.timezone(timezone_str)
    
    # Parse the local time string
    local_time_dt = datetime.strptime(local_time_str_combined, f'%Y-%m-%d {time_format}')
    
    # Localize the local time (attach the timezone)
    localized_time = local_tz.localize(local_time_dt)
    
    # Convert to UTC
    utc_time = localized_time.astimezone(pytz.UTC)
    
    return utc_time

