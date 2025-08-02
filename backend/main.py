from datetime import datetime, timedelta, timezone
from typing import List, Optional
from enum import Enum
import asyncio
import random
import os
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Session, SQLModel, create_engine, select, func
from pydantic import BaseModel
import uvicorn

load_dotenv()
# Database URL - adjust credentials as needed
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Enums
class BinStatus(str, Enum):
    EMPTY = "empty"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    FULL = "full"
    NEEDS_MAINTENANCE = "needs_maintenance"

class BinType(str, Enum):
    GENERAL = "general"
    RECYCLING = "recycling"
    ORGANIC = "organic"
    HAZARDOUS = "hazardous"

# SQLModel tables
class TrashBin(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    location: str = Field(index=True)
    district: str = Field(index=True)
    bin_type: BinType = Field(default=BinType.GENERAL)
    capacity_liters: int = Field(default=120)
    current_fill_percentage: int = Field(default=0, ge=0, le=100)
    status: BinStatus = Field(default=BinStatus.EMPTY)
    last_emptied: datetime = Field(default_factory=datetime.utcnow)
    last_sensor_update: datetime = Field(default_factory=datetime.utcnow)
    maintenance_required: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CollectionSchedule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bin_id: int = Field(foreign_key="trashbin.id", index=True)
    scheduled_at: datetime
    completed: bool = Field(default=False)
    completed_at: Optional[datetime] = None
    truck_id: Optional[str] = None
    notes: Optional[str] = None

# Pydantic models for API
class BinCreate(BaseModel):
    location: str
    district: str
    bin_type: BinType = BinType.GENERAL
    capacity_liters: int = 120

class BinUpdate(BaseModel):
    current_fill_percentage: Optional[int] = None
    status: Optional[BinStatus] = None
    maintenance_required: Optional[bool] = None

class ScheduleCreate(BaseModel):
    bin_id: int
    scheduled_at: datetime

class BinStats(BaseModel):
    total_bins: int
    full_bins: int
    needs_maintenance: int
    avg_fill_percentage: float
    bins_by_type: dict
    bins_by_district: dict

# Create engine and app
engine = create_engine(DATABASE_URL, echo=True)
app = FastAPI(title="Smart Trash Collection API", version="1.0.0", debug=True)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_session():
    with Session(engine) as session:
        yield session

# Create tables on startup
@app.on_event("startup")
async def on_startup():
    SQLModel.metadata.create_all(engine)
    # Seed some demo data if tables are empty
    with Session(engine) as session:
        count = session.exec(select(func.count(TrashBin.id))).one()
        if count == 0:
            await seed_demo_data()

# Background task to simulate sensor updates
async def update_sensor_data():
    while True:
        await asyncio.sleep(30)  # Update every 30 seconds
        with Session(engine) as session:
            bins = session.exec(select(TrashBin)).all()
            for bin in bins:
                # Simulate fill level changes
                if random.random() > 0.7:
                    bin.current_fill_percentage = min(100, bin.current_fill_percentage + random.randint(1, 5))
                    bin.last_sensor_update = datetime.utcnow()
                    
                    # Update status based on fill percentage
                    if bin.current_fill_percentage >= 90:
                        bin.status = BinStatus.FULL
                    elif bin.current_fill_percentage >= 70:
                        bin.status = BinStatus.HIGH
                    elif bin.current_fill_percentage >= 40:
                        bin.status = BinStatus.MEDIUM
                    elif bin.current_fill_percentage >= 20:
                        bin.status = BinStatus.LOW
                    else:
                        bin.status = BinStatus.EMPTY
                    
                    session.add(bin)
            session.commit()

@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(update_sensor_data())

# Routes
@app.get("/api/bins", response_model=List[TrashBin])
async def get_bins(
    district: Optional[str] = None,
    bin_type: Optional[BinType] = None,
    status: Optional[BinStatus] = None,
    min_fill: Optional[int] = None,
    session: Session = Depends(get_session)
):
    query = select(TrashBin)
    
    if district:
        query = query.where(TrashBin.district == district)
    if bin_type:
        query = query.where(TrashBin.bin_type == bin_type)
    if status:
        query = query.where(TrashBin.status == status)
    if min_fill is not None:
        query = query.where(TrashBin.current_fill_percentage >= min_fill)
    
    bins = session.exec(query.order_by(TrashBin.current_fill_percentage.desc())).all()
    return bins

@app.get("/api/bins/{bin_id}", response_model=TrashBin)
async def get_bin(bin_id: int, session: Session = Depends(get_session)):
    bin = session.get(TrashBin, bin_id)
    if not bin:
        raise HTTPException(status_code=404, detail="Bin not found")
    return bin

@app.post("/api/bins")
def create_bin(bin: BinCreate, session: Session = Depends(get_session)):
    db_bin = TrashBin(
        location=bin.location,
        district=bin.district,
        bin_type=bin.bin_type.upper(),  # Convert to uppercase for DB
        capacity_liters=bin.capacity_liters,
    )
    session.add(db_bin)
    session.commit()
    session.refresh(db_bin)
    return db_bin

@app.patch("/api/bins/{bin_id}", response_model=TrashBin)
async def update_bin(bin_id: int, bin_update: BinUpdate, session: Session = Depends(get_session)):
    bin = session.get(TrashBin, bin_id)
    if not bin:
        raise HTTPException(status_code=404, detail="Bin not found")
    
    update_data = bin_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(bin, key, value)
    
    bin.last_sensor_update = datetime.utcnow()
    session.add(bin)
    session.commit()
    session.refresh(bin)
    return bin

@app.post("/api/bins/{bin_id}/empty", response_model=TrashBin)
async def empty_bin(bin_id: int, session: Session = Depends(get_session)):
    bin = session.get(TrashBin, bin_id)
    if not bin:
        raise HTTPException(status_code=404, detail="Bin not found")
    
    bin.current_fill_percentage = 0
    bin.status = BinStatus.EMPTY
    bin.last_emptied = datetime.now(timezone.utc)
    session.add(bin)
    session.commit()
    session.refresh(bin)
    return bin

@app.get("/api/schedules", response_model=List[CollectionSchedule])
async def get_schedules(
    upcoming_only: bool = True,
    bin_id: Optional[int] = None,
    session: Session = Depends(get_session)
):
    query = select(CollectionSchedule)
    
    if upcoming_only:
        query = query.where(CollectionSchedule.completed == False)
    if bin_id:
        query = query.where(CollectionSchedule.bin_id == bin_id)
    
    schedules = session.exec(query.order_by(CollectionSchedule.scheduled_at)).all()
    return schedules

@app.post("/api/schedules", response_model=CollectionSchedule)
async def create_schedule(schedule: ScheduleCreate, session: Session = Depends(get_session)):
    # Verify bin exists
    bin = session.get(TrashBin, schedule.bin_id)
    if not bin:
        raise HTTPException(status_code=404, detail="Bin not found")
    
    db_schedule = CollectionSchedule(**schedule.dict())
    session.add(db_schedule)
    session.commit()
    session.refresh(db_schedule)
    return db_schedule

@app.patch("/api/schedules/{schedule_id}/complete")
async def complete_schedule(
    schedule_id: int,
    truck_id: Optional[str] = None,
    session: Session = Depends(get_session)
):
    schedule = session.get(CollectionSchedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    schedule.completed = True
    schedule.completed_at = datetime.utcnow()
    schedule.truck_id = truck_id
    
    # Empty the bin
    bin = session.get(TrashBin, schedule.bin_id)
    if bin:
        bin.current_fill_percentage = 0
        bin.status = BinStatus.EMPTY
        bin.last_emptied = datetime.utcnow()
        session.add(bin)
    
    session.add(schedule)
    session.commit()
    return {"message": "Schedule completed successfully"}

@app.get("/api/stats", response_model=BinStats)
async def get_stats(session: Session = Depends(get_session)):
    total_bins = session.exec(select(func.count(TrashBin.id))).one()
    full_bins = session.exec(
        select(func.count(TrashBin.id)).where(TrashBin.status == BinStatus.FULL)
    ).one()
    needs_maintenance = session.exec(
        select(func.count(TrashBin.id)).where(TrashBin.maintenance_required == True)
    ).one()
    avg_fill = session.exec(select(func.avg(TrashBin.current_fill_percentage))).one() or 0
    
    # Bins by type
    bins_by_type = {}
    for bin_type in BinType:
        count = session.exec(
            select(func.count(TrashBin.id)).where(TrashBin.bin_type == bin_type)
        ).one()
        bins_by_type[bin_type] = count
    
    # Bins by district
    districts = session.exec(select(TrashBin.district).distinct()).all()
    bins_by_district = {}
    for district in districts:
        count = session.exec(
            select(func.count(TrashBin.id)).where(TrashBin.district == district)
        ).one()
        bins_by_district[district] = count
    
    return BinStats(
        total_bins=total_bins,
        full_bins=full_bins,
        needs_maintenance=needs_maintenance,
        avg_fill_percentage=round(avg_fill, 1),
        bins_by_type=bins_by_type,
        bins_by_district=bins_by_district
    )

# Demo data seeding
async def seed_demo_data():
    locations = [
        ("Main Street & 1st Ave", "Downtown"),
        ("Central Park North", "Downtown"),
        ("City Hall Plaza", "Downtown"),
        ("Market Square", "Commercial"),
        ("Shopping Mall Entrance", "Commercial"),
        ("Office Complex A", "Commercial"),
        ("Residential Block 1", "Residential"),
        ("Apartment Complex B", "Residential"),
        ("Community Center", "Residential"),
        ("Industrial Park Gate", "Industrial"),
        ("Factory Road", "Industrial"),
        ("Warehouse District", "Industrial"),
    ]
    
    with Session(engine) as session:
        for location, district in locations:
            for bin_type in [BinType.GENERAL, BinType.RECYCLING]:
                bin = TrashBin(
                    location=location,
                    district=district,
                    bin_type=bin_type,
                    capacity_liters=random.choice([120, 240, 360]),
                    current_fill_percentage=random.randint(0, 100)
                )
                
                # Set status based on fill
                if bin.current_fill_percentage >= 90:
                    bin.status = BinStatus.FULL
                elif bin.current_fill_percentage >= 70:
                    bin.status = BinStatus.HIGH
                elif bin.current_fill_percentage >= 40:
                    bin.status = BinStatus.MEDIUM
                elif bin.current_fill_percentage >= 20:
                    bin.status = BinStatus.LOW
                else:
                    bin.status = BinStatus.EMPTY
                
                # Random maintenance needed
                if random.random() > 0.9:
                    bin.maintenance_required = True
                    bin.status = BinStatus.NEEDS_MAINTENANCE
                
                session.add(bin)
        
        session.commit()
        
        # Create some schedules
        bins = session.exec(select(TrashBin).where(TrashBin.current_fill_percentage >= 70)).all()
        for bin in bins[:5]:  # Schedule first 5 high-fill bins
            schedule = CollectionSchedule(
                bin_id=bin.id,
                scheduled_at=datetime.utcnow() + timedelta(hours=random.randint(1, 48))
            )
            session.add(schedule)
        
        session.commit()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)