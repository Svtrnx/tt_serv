from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from model import Base, TikTokTable, TikTokTableUser, TikTokTableMedia, TikTokTableRegAccounts, TikTokTableWarming
from config import DB_NAME, DB_HOST, DB_PORT, DB_USER, DB_PASS
import datetime
from sqlalchemy.orm import Session
import schema

db_url = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(db_url)

Base.metadata.create_all(engine)



def query_tiktok_table(current_user):
    Session = sessionmaker(bind=engine)
    session = Session()

    results = session.query(TikTokTable).filter(TikTokTable.user_id == current_user).all()

    session.close()

    return results

def query_tiktok_warming_links(username, unique_id):
    Session = sessionmaker(bind=engine)
    session = Session()

    results = session.query(TikTokTableWarming).filter((TikTokTableWarming.username == username)
                            & (TikTokTableWarming.unique_id == unique_id)).all()

    session.close()

    return results

def update_tiktok_warming_links(username, unique_id):
    Session = sessionmaker(bind=engine)
    session = Session()

    results = session.query(TikTokTableWarming).filter((TikTokTableWarming.username == username)
                            & (TikTokTableWarming.unique_id == unique_id)).all()

    session.close()

    return results

def query_tiktok_media(session, username, data_select):

    if data_select == 'workable':
        results = session.query(TikTokTableMedia).filter(
            and_(TikTokTableMedia.username == username, TikTokTableMedia.completed == False)
        ).all()
    elif data_select == 'all':
        results = session.query(TikTokTableMedia).filter(TikTokTableMedia.username == username).all()
    
    session.close()

    return results


def query_tiktok_table_check_auth(hwid):
    Session = sessionmaker(bind=engine)
    session = Session()

    results = session.query(TikTokTableUser).filter(TikTokTableUser.hwid == hwid).first()

    session.close()

    return results

def update_sleep_datetime(session, cluster_id, new_sleep_datetime):
    try:
        record = session.query(TikTokTable).filter(TikTokTable.cluster_id == cluster_id).one()

        record.sleep_datetime = new_sleep_datetime
        session.commit()
        return "Successfully updated sleep_datetime"

    except Exception as e:
        session.rollback()
        return f"Error updating sleep_datetime: {e}"

def update_is_active(session, cluster_id, new_is_active):
    try:
        record = session.query(TikTokTable).filter(TikTokTable.cluster_id == cluster_id).one()

        record.is_active = new_is_active
        session.commit()
        return "Successfully updated is_active"

    except Exception as e:
        session.rollback()
        return (f"Error updating is_active: {e}")

def check_user(session, username, user_key):
    try:
        record = session.query(TikTokTableUser).filter(
            (TikTokTableUser.username == username) & (TikTokTableUser.user_key == user_key)).first()

        if record:
            return True
        else:
            return False

    except Exception as e:
        session.rollback()
        return f"Error checking user: {e}"
    
def check_key(session, username, hwid):
    try:
        print('session', session)
        print('username', username)
        print('hwid', hwid)
        user_current_key = session.query(TikTokTableUser).filter(
            (TikTokTableUser.username == username) & (TikTokTableUser.hwid == hwid)
        ).first()

        if user_current_key:
            return user_current_key
        else:
            return False

    except Exception as e:
        session.rollback()
        return f"Error checking user: {e}"

def get_user_by_username(db: Session, username: str, user_key: str):
    try:
        record = db.query(TikTokTableUser).filter(
            (TikTokTableUser.username == username) & (TikTokTableUser.user_key == user_key)
        ).first()
        
        print(record)

        return record

    except Exception as e:
        db.rollback()
        return f"Error getting user by username: {e}"
    
def get_user_only_by_username(db: Session, username: str):
    try:
        record = db.query(TikTokTableUser).filter((TikTokTableUser.username == username)).first()
        
        return record

    except Exception as e:
        db.rollback()
        return f"Error getting user by username: {e}"
    
def get_cluster(db: Session, cluster: str):
    try:
        record = db.query(TikTokTable).filter((TikTokTable.cluster_name_media == cluster)).first()
        
        return record

    except Exception as e:
        db.rollback()
        return f"Error getting user by username: {e}"
    
def create_media_task(db: Session, media: schema.TikTokMediaSchema):
    new_media = TikTokTableMedia(
        content                     = media.content,
        cluster_name_media          = media.cluster_name_media,
        completed                   = media.completed,
        content_type                = media.content_type,
        sound                       = media.sound,
        time_content                = media.time_content,
        username                    = media.username,
        unique_id                   = media.unique_id,
        media_name                  = media.media_name,
        tags                        = media.tags,
    )
    db.add(new_media)
    db.commit()
    db.refresh(new_media)
    return new_media

def create_warming_link(db: Session, warming: schema.TikTokWarmingSchema):
    new_warming = TikTokTableWarming(
        link                        = warming.link,
        username                    = warming.username,
        unique_id                   = warming.unique_id,
        completed                   = warming.completed,
    )
    db.add(new_warming)
    db.commit()
    db.refresh(new_warming)
    return new_warming

def delete_media(db: Session, unique_id):
    try:
        db.query(TikTokTableMedia).filter(TikTokTableMedia.unique_id == unique_id).delete()

        db.commit()

    except Exception as e:
        db.rollback()
        return f"Error deleting media: {e}"



def create_user_reg(db: Session, user_reg: schema.TikTokSchemaRegAccount):
    new_user_reg = TikTokTableRegAccounts(
        username                    = user_reg.username,
        email                       = user_reg.email,
        password                    = user_reg.password,
        is_loginning_now            = user_reg.is_loginning_now,
        is_uploaded_content         = user_reg.is_uploaded_content,
        proxy_address               = user_reg.proxy_address,
        proxy_port                  = user_reg.proxy_port,
        proxy_username              = user_reg.proxy_username,
        proxy_password              = user_reg.proxy_password,
        work_time                   = user_reg.work_time,
        reg_time                    = user_reg.reg_time,
        user_reg                    = user_reg.user_reg,
        is_warmed                   = user_reg.is_warmed,
    )
    db.add(new_user_reg)
    db.commit()
    db.refresh(new_user_reg)
    return new_user_reg


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



new_sleep_datetime = datetime.datetime.now().replace(microsecond=0)
new_timestamp = new_sleep_datetime + datetime.timedelta(minutes=300)

# update_sleep_datetime(session, 3, new_sleep_datetime)


session.close()


