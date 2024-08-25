from sqlmodel import SQLModel, Field
from sqlalchemy import BigInteger, Column
from typing import Optional
from datetime import datetime, time

class StoreStatus(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    store_id: int = Field(sa_column=Column(BigInteger))
    timestamp_utc: datetime
    status: str
    
class OriginalBuisnessHours(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    store_id: int = Field(sa_column=Column(BigInteger))
    startTime: datetime
    endTime: datetime

class StoreBusinessHours(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    store_id: int = Field(sa_column=Column(BigInteger))
    day_of_week: int  # 0 = Monday, 6 = Sunday
    start_time_local: time
    end_time_local: time

class StoreTimezone(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    store_id: int = Field(sa_column=Column(BigInteger))
    timezone_str: str
