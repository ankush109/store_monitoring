import time
import uuid
from fastapi import FastAPI, BackgroundTasks
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, Session, create_engine
import pandas as pd
from models import StoreStatus, StoreBusinessHours, StoreTimezone
from dateutil import parser
from datetime import datetime, timedelta
from pytz import timezone

DATABASE_URL = "postgresql://postgres:root@localhost:5432/store_monitoring"
engine = create_engine(DATABASE_URL)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session