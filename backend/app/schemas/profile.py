from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime


class ProfileBase(BaseModel):
    """Base profile schema"""
    display_name: str = Field(..., min_length=2, max_length=100)
    date_of_birth: date
    gender: str = Field(..., pattern="^(male|female|non_binary|other)$")
    bio: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    country: str = Field(default="USA", max_length=100)
    height_cm: Optional[int] = Field(None, ge=100, le=250)
    looking_for_gender: str = Field(..., max_length=200)
    min_age: int = Field(default=18, ge=18, le=100)
    max_age: int = Field(default=99, ge=18, le=100)
    max_distance_km: int = Field(default=50, ge=1, le=500)


class ProfileCreate(ProfileBase):
    """Create profile request"""
    pass


class ProfileUpdate(BaseModel):
    """Update profile request (all fields optional)"""
    display_name: Optional[str] = Field(None, min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = None
    state: Optional[str] = None
    height_cm: Optional[int] = Field(None, ge=100, le=250)
    looking_for_gender: Optional[str] = None
    min_age: Optional[int] = Field(None, ge=18, le=100)
    max_age: Optional[int] = Field(None, ge=18, le=100)
    max_distance_km: Optional[int] = Field(None, ge=1, le=500)
    is_active: Optional[bool] = None
    is_paused: Optional[bool] = None


class PhotoSchema(BaseModel):
    """Photo response schema"""
    id: int
    url: str
    thumbnail_url: Optional[str]
    is_primary: bool
    order_index: int
    is_approved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileResponse(ProfileBase):
    """Profile response schema"""
    id: int
    user_id: int
    latitude: Optional[float]
    longitude: Optional[float]
    is_complete: bool
    is_active: bool
    is_paused: bool
    is_verified: bool
    is_flagged: bool
    is_banned: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_active_at: Optional[datetime]
    photos: List[PhotoSchema] = []

    class Config:
        from_attributes = True


class DiscoveryProfileResponse(BaseModel):
    """Simplified profile for discovery feed"""
    id: int
    display_name: str
    age: int
    bio: Optional[str]
    city: Optional[str]
    state: Optional[str]
    distance_km: Optional[float]
    photos: List[PhotoSchema]
    compatibility_score: Optional[int]
    is_verified: bool

    class Config:
        from_attributes = True


class PhotoUpload(BaseModel):
    """Photo upload request"""
    url: str
    is_primary: bool = False
    order_index: int = 0


class PhotoUpdate(BaseModel):
    """Photo update request"""
    is_primary: Optional[bool] = None
    order_index: Optional[int] = None
