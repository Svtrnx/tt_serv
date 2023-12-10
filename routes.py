from fastapi import Depends, APIRouter, Request, Body, Response, HTTPException, status, Form
from connection import session, query_tiktok_table, update_is_active, check_user, get_db, create_media_task, get_cluster, query_tiktok_table_check_auth, query_tiktok_media, create_user_reg
from schema import Token
from sqlalchemy.orm import Session
import model
import userController
from datetime import timedelta, datetime
from authSecurity import create_access_token, get_current_user
from starlette.responses import RedirectResponse
from dotenv import load_dotenv
from config import ACCESS_TOKEN_EXPIRE_MINUTES, COOKIE_NAME

load_dotenv()
userRouter = APIRouter()

@userRouter.get("/index")
def get_index(request: Request):
	return {"request": request.url}

@userRouter.get('/clusters')
def get_clusters(user: str, db: Session = Depends(get_db), current_user: model.TikTokTableUser = Depends(get_current_user)):
	if user == current_user.username:
		clusters = query_tiktok_table(user)
	else:
		raise HTTPException(status_code=309, detail="Not found user clusters")
	return {"clusters": clusters}

@userRouter.post('/check_auth_bot')
def check_auth(db: Session = Depends(get_db), current_user: model.TikTokClusterHwidCheckRequestForm = Depends()):
	user_hwid = query_tiktok_table_check_auth(current_user.hwid)
	if user_hwid is None:
		raise HTTPException(status_code=311, detail="Autentication failed")
	else:
		clusters = query_tiktok_table(user_hwid.username)
		return {"clusters": clusters}
	
@userRouter.get('/get_tiktok_media')
def check_auth(username: str, db: Session = Depends(get_db)):
	user_media = query_tiktok_media(username=username)
	return {"media": user_media}

@userRouter.post('/update_active')
def update_cluster_active(cluster_id: int = Body(embed=True), is_active: bool = Body(embed=True)):
	active = update_is_active(session=session, cluster_id=cluster_id, new_is_active=is_active)
	return {"active": active}

@userRouter.post('/signin', response_model=Token)
async def signin_auth(response:Response, db: Session = Depends(get_db), form_data: model.OAuth2PasswordRequestFormSignin = Depends()):
	user = userController.authenticate_user(
		db=db,
		username=form_data.username,
		user_key=form_data.user_key
	)
	if not user:
		raise HTTPException(status_code=301, detail="Incorrect account information")
	
	access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	access_token = create_access_token(
		data={"sub": user.username}, expires_delta=access_token_expires
	)
	response = RedirectResponse(url='/index',status_code=status.HTTP_302_FOUND)
	response.set_cookie(key="access_token",value=f"Bearer {access_token}", samesite='none', httponly=True,
					secure=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60) 
	return response

@userRouter.get("/check-auth")
async def check_auth(db: Session = Depends(get_db), current_user: model.TikTokTableUser = Depends(get_current_user)):
	user = current_user.username
	return user


@userRouter.patch('/update_cluster_proxy')
async def create_task(
		cluster: str = Body(embed=True),
		db: Session = Depends(get_db),
		form_data: model.TikTokClusterRequestForm = Depends()
):
	cluster_obj = get_cluster(db=db, cluster=cluster)

	if form_data.proxy_address and cluster_obj.cluster_name == cluster:
		cluster_obj.proxy_address 	= form_data.proxy_address
		cluster_obj.proxy_port 		= form_data.proxy_port
		cluster_obj.proxy_username 	= form_data.proxy_username
		cluster_obj.proxy_password 	= form_data.proxy_password
		db.commit()
		db.refresh(cluster_obj)
		return {"cluster": cluster_obj}
	else:
		return {"error": "Proxy address not provided or cluster_name does not match"}

@userRouter.post('/create_task')
async def create_task(db: Session = Depends(get_db), current_user: model.MediaRequestForm = Depends(get_current_user), form_data: model.MediaRequestForm = Depends()):
	if current_user.username == form_data.username:
		new_media = model.TikTokTableMedia(
			content=form_data.content,
			cluster_name_media=form_data.cluster_name_media,
			completed=form_data.completed,
			content_type=form_data.content_type,
			sound=form_data.sound,
			time_content=datetime.now(),
			username=form_data.username,
			unique_id=form_data.unique_id,
			media_name=form_data.media_name,
		)
		media = create_media_task(db=db, media=new_media)
		return {'media': media}
	else:
		raise HTTPException(status_code=310, detail="Authentication failed")

@userRouter.post('/create_reg_account')
async def create_task2(db: Session = Depends(get_db), form_data: model.TikTokRegUserRequestForm = Depends()):
	current_time = datetime.now()
	new_time = current_time + timedelta(hours=12)
	print(new_time)
	new_user_reg = model.TikTokTableRegAccounts(
		username=form_data.username,
		email=form_data.email,
		password=form_data.password,
		is_loginning_now=form_data.is_loginning_now,
		is_uploaded_content=form_data.is_uploaded_content,
		proxy_address=form_data.proxy_address,
		proxy_port=form_data.proxy_port,
		proxy_username=form_data.proxy_username,
		proxy_password=form_data.proxy_password,
		work_time=new_time,
		reg_time=datetime.now()
	)
	user_reg = create_user_reg(db=db, user_reg=new_user_reg)
	return {'user_reg': user_reg}
	
 

@userRouter.patch('/update_used_proxy')
async def create_task(
		proxy_address: str = Body(embed=True),
		proxy_port: int = Body(embed=True),
		proxy_username: str = Body(embed=True),
		proxy_password: str = Body(embed=True),
		used: bool = Body(embed=True),
        db: Session = Depends(get_db),
        form_data: model.TikTokProxyUpdateForm = Depends()
):
	form_data.proxy_address 	= proxy_address
	form_data.proxy_port 		= proxy_port
	form_data.proxy_username 	= proxy_username
	form_data.proxy_password 	= proxy_password
	form_data.used 				= used
	
	db_proxy = db.query(model.TikTokTableProxy).filter_by(
		proxy_address=form_data.proxy_address,
		proxy_port=form_data.proxy_port,
		proxy_username=form_data.proxy_username,
		proxy_password=form_data.proxy_password
	).first()

	if db_proxy:
		db_proxy.used = form_data.used
		db.commit()
		db.refresh(db_proxy)
		return {"cluster": db_proxy}
	else:
		return {"error": "Proxy dont found"}


@userRouter.get("/get_proxy")
async def check_auth(db: Session = Depends(get_db)):
    proxy = db.query(model.TikTokTableProxy).filter(model.TikTokTableProxy.used == False).first()
    
    if proxy:
        return {
            "proxy_address": proxy.proxy_address,
            "proxy_port": proxy.proxy_port,
            "proxy_username": proxy.proxy_username,
            "proxy_password": proxy.proxy_password
        }
    else:
        return {"message": "Proxy not found, all proxies are used!"}
	
 
 