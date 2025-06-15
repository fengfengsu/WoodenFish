from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    avatar: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_vip: bool
    vip_expire_date: Optional[datetime]
    merit_points: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserStatOut(BaseModel):
    total_taps: int
    today_taps: int
    consecutive_days: int
    last_tap_date: Optional[datetime]

    class Config:
        from_attributes = True

class MeditationSessionCreate(BaseModel):
    duration: int
    tap_count: int

class MeditationSessionOut(MeditationSessionCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AchievementOut(BaseModel):
    id: int
    name: str
    description: str
    icon: str

    class Config:
        from_attributes = True

class UserAchievementOut(BaseModel):
    achievement: AchievementOut
    unlocked_at: datetime

    class Config:
        from_attributes = True

class LeaderboardOut(BaseModel):
    user_id: int
    period: str
    rank: int
    tap_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class ShareTaskOut(BaseModel):
    id: int
    title: str
    description: str
    merit: int
    icon: str

    class Config:
        from_attributes = True

class UserShareTaskOut(BaseModel):
    task: ShareTaskOut
    completed: bool
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True 