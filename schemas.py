from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from models import RequestStatus, DataType, PrivacyLevel, UserRole

# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str

class ClientBase(UserBase):
    organization: Optional[str] = None

class AdminBase(UserBase):
    pass

# Request/Response schemas
class ClientCreate(ClientBase):
    password: str

class ClientResponse(ClientBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class AdminCreate(AdminBase):
    password: str

class AdminResponse(AdminBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class RequestCreate(BaseModel):
    data_type: DataType
    size: int
    privacy_level: PrivacyLevel
    params: Optional[str] = None

class RequestResponse(BaseModel):
    id: int
    client_id: int
    data_type: DataType
    size: int
    privacy_level: PrivacyLevel
    params: Optional[str]
    status: RequestStatus
    output_path: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class RequestUpdate(BaseModel):
    status: Optional[RequestStatus] = None
    output_path: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    user_role: Optional[UserRole] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class DownloadResponse(BaseModel):
    download_url: str
    expires_at: Optional[datetime] = None
