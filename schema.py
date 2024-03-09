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
    tags: Optional[str]=None
    
class TikTokProxySchema(BaseModel):
    id: int
    proxy_address: Optional[str]=None
    proxy_port: Optional[int]=None
    proxy_username: Optional[str]=None
    proxy_password: Optional[bool]=None
    used: Optional[bool]=None
    proxy_type: Optional[str]=None  
    
class TikTokDocSchema(BaseModel):
    id: int
    business_name: Optional[str]=None
    country: Optional[str]=None
    address: Optional[str]=None
    province: Optional[str]=None
    city: Optional[str]=None
    zip_code: Optional[str]=None
    license: Optional[str]=None
    doc_img_1: Optional[str]=None
    doc_img_2: Optional[str]=None
    cluster: Optional[str]=None
    username: Optional[str]=None
    

class TikTokWarmingSchema(BaseModel):
    id: int
    link: Optional[str]=None
    unique_id: Optional[str]=None
    username: Optional[str]=None
    
    
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
    user_reg: Optional[str]=None

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
