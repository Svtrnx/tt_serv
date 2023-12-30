from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from fastapi import Form

Base = declarative_base()

class TikTokTable(Base):
    __tablename__ = 'tiktokTable'

    id = Column(Integer, primary_key=True)
    cluster_name = Column(String)
    cluster_id = Column(Integer)
    tiktok_username = Column(String)
    tiktok_password = Column(String)
    step = Column(Integer)
    sleep_datetime = Column(DateTime)
    adb_address = Column(String)
    is_active = Column(Boolean)
    proxy_address = Column(String)
    proxy_port = Column(String)
    proxy_username = Column(String)
    proxy_password = Column(String)
    user_id = Column(String)
    
class TikTokTableMedia(Base):
    __tablename__ = 'tt_media'

    id = Column(Integer, primary_key=True)
    content = Column(String)
    cluster_name_media = Column(String)
    tiktok_username = Column(String)
    completed = Column(Boolean)
    content_type = Column(String)
    sound = Column(String)
    time_content = Column(DateTime)
    username = Column(String)
    unique_id = Column(String)
    media_name = Column(String)
    tags = Column(String)
    
class TikTokTableUser(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    user_key = Column(String)
    have_subscription = Column(Boolean)
    subscription_time_starts = Column(DateTime)
    subscription_time_ends = Column(DateTime)
    hwid = Column(String)
    
    
class TikTokTableProxy(Base):
    __tablename__ = 'proxy'

    id = Column(Integer, primary_key=True)
    proxy_address = Column(String)
    proxy_port = Column(Integer)
    proxy_username = Column(String)
    proxy_password = Column(String)
    used = Column(Boolean)
    proxy_type = Column(String)
    
class TikTokTableRegAccounts(Base):
    __tablename__ = 'reg_accounts'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    is_loginning_now = Column(Boolean)
    is_uploaded_content = Column(Boolean)
    proxy_address = Column(String)
    proxy_port = Column(Integer)
    proxy_username = Column(String)
    proxy_password = Column(String)
    work_time = Column(DateTime)
    reg_time = Column(DateTime)
    user_reg = Column(String)
    
class TikTokTableWarming(Base):
    __tablename__ = 'warming'

    id = Column(Integer, primary_key=True)
    link = Column(String)
    username = Column(String)
    unique_id = Column(String)
    completed = Column(Boolean)


class OAuth2PasswordRequestFormSignin:
	
    def __init__(
        self,
        username: str = Form(),
        user_key: str = Form(),
    ):
        self.username = username
        self.user_key = user_key

class MediaRequestForm:
	
    def __init__(
        self,
        content: str = Form(),
        cluster_name_media: str = Form(),
        completed: bool = Form(),
        content_type: str = Form(),
        sound: str = Form(),
        username: str = Form(),
        unique_id: str = Form(),
        media_name: str = Form(),
        tags: str = Form(None),
    ):
        self.content = content
        self.cluster_name_media = cluster_name_media
        self.completed = completed
        self.content_type = content_type
        self.sound = sound
        self.username = username
        self.unique_id = unique_id
        self.media_name = media_name
        self.tags = tags
     
class TikTokClusterRequestForm:
	
    def __init__(
        self,
        proxy_address: str = Form(),
        proxy_port: str = Form(),
        proxy_username: str = Form(),
        proxy_password: str = Form(),
        proxy_type: str = Form()
    ):
        self.proxy_address = proxy_address
        self.proxy_port = proxy_port
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self.proxy_type = proxy_type

class TikTokRegUserRequestForm:
	
    def __init__(
        self,
        username: str = Form(),
        email: str = Form(),
        password: str = Form(),
        is_loginning_now: bool = Form(),
        is_uploaded_content: bool = Form(),
        proxy_address: str = Form(),
        proxy_port: int = Form(),
        proxy_username: str = Form(),
        proxy_password: str = Form(),
        user_reg: str = Form()
    ):
        self.username = username
        self.email = email
        self.password = password
        self.is_loginning_now = is_loginning_now
        self.is_uploaded_content = is_uploaded_content
        self.proxy_address = proxy_address
        self.proxy_port = proxy_port
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password,
        self.user_reg = user_reg
        
class TikTokClusterHwidCheckRequestForm:
	
    def __init__(
        self,
        hwid: str = Form()
    ):
        self.hwid = hwid

class TikTokClusterGetClustersBotRequestForm:
	
    def __init__(
        self,
        hwid: str = Form(),
        username: str = Form()
        
    ):
        self.hwid = hwid
        self.username = username

class TikTokProxyUpdateForm:
	
    def __init__(
        self,
        proxy_address: str = Form(),
        proxy_port: int = Form(),
        proxy_password: str = Form(),
        used: bool = Form(),
        proxy_type: str = Form()
        
    ):
        self.proxy_address = proxy_address
        self.proxy_port = proxy_port
        self.proxy_password = proxy_password
        self.used = used
        self.proxy_type = proxy_type
            
class TikTokAccountIsActiveUpdateForm:
	
    def __init__(
        self,
        username: str = Form(),
        email: str = Form(),
        password: str = Form(),
        is_loginning_now: bool = Form(),
        is_uploaded_content: bool = Form()
        
    ):
        self.username = username
        self.email = email
        self.password = password
        self.is_loginning_now = is_loginning_now
        self.is_uploaded_content = is_uploaded_content
        
class TikTokMediaCompletedUpdateForm:
	
    def __init__(
        self,
        media_name: str = Form(),
        unique_id: str = Form(),
        completed: bool = Form(),
        
    ):
        self.media_name = media_name
        self.unique_id = unique_id
        self.completed = completed

class TikTokMediaWarmingForm:
	
    def __init__(
        self,
        link: str = Form(None),
        username: str = Form(None),
        unique_id: str = Form(None),
        
    ):
        self.link = link
        self.username = username
        self.unique_id = unique_id




