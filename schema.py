from pydantic import BaseModel, Field
from typing import List, Optional, Generic, TypeVar
from pydantic.generics import GenericModel
from datetime import datetime

class TikTokMediaSchema(BaseModel):
    id: int
    content: Optional[str]=None
    cluster_name_media: Optional[str]=None
    tiktok_username: Optional[str]=None
    completed: Optional[bool]=None
    content_type: Optional[str]=None
    sound: Optional[str]=None
    time_content: Optional[datetime]=None
    username: Optional[str]=None
    unique_id: Optional[str]=None
    media_name: Optional[str]=None
    
    
class TikTokSchemaRegAccount(BaseModel):
    id: int
    username: Optional[str]=None
    email: Optional[str]=None
    password: Optional[str]=None
    is_loginning_now: Optional[bool]=None
    is_uploaded_content: Optional[bool]=None
    proxy_address: Optional[str]=None
    proxy_port: Optional[int]=None
    proxy_username: Optional[str]=None
    proxy_password: Optional[str]=None
    work_time: Optional[datetime]=None
    reg_time: Optional[datetime]=None

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
