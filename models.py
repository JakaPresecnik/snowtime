from datetime import date, datetime, time
from pydantic import BaseModel
from typing import Optional
from fastapi.encoders import jsonable_encoder

class Working_hours(BaseModel):
    working: Optional[bool] = False
    open: Optional[str] = "00:00"
    close: Optional[str] = "00:00"

class Working_plan(BaseModel): 
    mon: Working_hours
    tue: Working_hours
    wed: Working_hours
    thu: Working_hours
    fri: Working_hours
    sat: Working_hours
    sun: Working_hours

class Lift(BaseModel):
    name: str
    id: int
    capacity: int
    notes: Optional[list[str]] = []
    notes_count: Optional[int] = 0
    working: Optional[bool] = False
    working_hours: Working_plan

    def to_json(self):
        return jsonable_encoder(self)

class Slope(BaseModel):
    name: str
    id: int
    difficulty: int
    working: Optional[bool] = False
    snowmaking: Optional[bool] = False
    notes: Optional[list[str]] = []
    notes_count: Optional[int] = 0
    def to_json(self):
        return jsonable_encoder(self)

class Temp_closed(BaseModel):
    closed: bool = False
    reason: Optional[str]
    new_info: Optional[time]

class Resort(BaseModel):
    user: str
    name: str
    country: str
    last_update: Optional[datetime]
    closed_until: Optional[date]
    opened_until: Optional[date]
    temporarily_closed: Temp_closed
    working: Optional[bool] = False
    working_hours: Working_plan
    notes: Optional[list[str]] = []
    notes_count: Optional[int] = 0
    lifts: Optional[list[Lift]] = []
    slopes: Optional[list[Slope]] = []

    def to_json(self):
        return jsonable_encoder(self)

    def to_bson(self):
        data = self.dict(by_alias=True)
        if data.get("_id") is None:
            data.pop("_id", None)
        return data
