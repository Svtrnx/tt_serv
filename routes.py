from fastapi import Depends, APIRouter, Request, Body, Response, HTTPException, status, Form, Cookie
from connection import session, query_tiktok_table, update_is_active, get_docs_list_bot, create_doc, delete_doc, get_docs_list, check_user, get_db, get_proxy_list, create_media_task, get_cluster, create_proxy_list, query_tiktok_table_check_auth, query_tiktok_media, create_user_reg, delete_media, check_key, create_warming_link, query_tiktok_warming_links
from schema import Token
from sqlalchemy.orm import Session
import model
import userController
from datetime import timedelta, datetime
from authSecurity import create_access_token, get_current_user
from starlette.responses import RedirectResponse
from dotenv import load_dotenv
from config import ACCESS_TOKEN_EXPIRE_MINUTES, COOKIE_NAME
from typing import List

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
def check_auth(username: str, data_select: str, db: Session = Depends(get_db)):
	user_media = query_tiktok_media(session=session, username=username, data_select=data_select)
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


@userRouter.post('/create_warming_link')
async def create_warming_link_func(
		db: Session = Depends(get_db), 
		current_user: model.TikTokTableWarming = Depends(get_current_user),
		form_data: model.TikTokMediaWarmingForm = Depends(),
):
	if current_user.username == form_data.username:
		new_warming = model.TikTokTableWarming(
			link=form_data.link,
			username=form_data.username,
			unique_id=form_data.unique_id,
			completed=False,
		)
		warming_response = create_warming_link(db=db, warming=new_warming)
		return {'warming': warming_response}
	else:
		raise HTTPException(status_code=310, detail="Authentication failed")

@userRouter.post('/create_task')
async def create_task(db: Session = Depends(get_db), 
					  current_user: model.MediaRequestForm = Depends(get_current_user), 
					  form_data: model.MediaRequestForm = Depends()):
	if current_user.username == form_data.username:
		new_media = model.TikTokTableMedia(
			content=form_data.content,
			cluster_name_media=form_data.cluster_name_media,
			completed=form_data.completed,
			content_type=form_data.content_type,
			sound=form_data.sound,
			time_content=datetime.now() + timedelta(hours=2),
			username=form_data.username,
			unique_id=form_data.unique_id,
			media_name=form_data.media_name,
			tags=form_data.tags,
		)
		media = create_media_task(db=db, media=new_media)
		return {'media': media}
	else:
		raise HTTPException(status_code=310, detail="Authentication failed")

@userRouter.post('/create_reg_account')
async def create_task2(db: Session = Depends(get_db), form_data: model.TikTokRegUserRequestForm = Depends()):
	current_time = datetime.now() + timedelta(hours=2)
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
		work_time=datetime.now() + timedelta(hours=5),
		reg_time=datetime.now() + timedelta(hours=2),
		user_reg=form_data.user_reg,
		is_warmed=False
	)
	user_reg = create_user_reg(db=db, user_reg=new_user_reg)
	return {'user_reg': user_reg}
	

@userRouter.patch('/update_reg_account')
async def update_reg_account_func(
		username: str = Body(embed=True),
		email: str = Body(embed=True, default=None),
		password: str = Body(embed=True),
		user_reg: str = Body(embed=True),
		proxy_address: str = Body(embed=True),
		proxy_port: int = Body(embed=True),
		proxy_username: str = Body(embed=True),
		proxy_password: str = Body(embed=True),
		work_time: datetime = Body(embed=True, default=None),
		is_warmed: bool = Body(embed=True, default=None),
		db: Session = Depends(get_db),
		form_data: model.TikTokRegAccountUpdateForm = Depends()
):
	form_data.username 			= username
	form_data.email 			= email
	form_data.password 			= password
	form_data.user_reg 			= user_reg
	form_data.proxy_address 	= proxy_address
	form_data.proxy_port 		= proxy_port
	form_data.proxy_username 	= proxy_username
	form_data.proxy_password 	= proxy_password
	
	db_account = db.query(model.TikTokTableRegAccounts).filter_by(
		username=form_data.username,
		email=form_data.email,
		password=form_data.password,
		user_reg=form_data.user_reg,
	).first()

	if db_account:
		db_account.proxy_address = form_data.proxy_address
		db_account.proxy_port = form_data.proxy_port
		db_account.proxy_username = form_data.proxy_username
		db_account.proxy_password = form_data.proxy_password
		db_account.work_time = work_time
		db_account.is_warmed = is_warmed
		db.commit()
		db.refresh(db_account)
		return {"reg_account": db_account}
	else:
		return {"error": "Account dont found"}
 

@userRouter.patch('/update_used_proxy')
async def create_task(
		proxy_address: str = Body(embed=True),
		proxy_port: int = Body(embed=True),
		proxy_username: str = Body(embed=True),
		proxy_password: str = Body(embed=True),
		proxy_type: str = Body(embed=True),
		used: bool = Body(embed=True),
		db: Session = Depends(get_db),
		form_data: model.TikTokProxyUpdateForm = Depends()
):
	
	form_data.proxy_address 	= proxy_address
	form_data.proxy_port 		= proxy_port
	form_data.proxy_username 	= proxy_username
	form_data.proxy_password 	= proxy_password
	form_data.used 				= used
	form_data.proxy_type 		= proxy_type
	
	db_proxy = db.query(model.TikTokTableProxy).filter_by(
		proxy_address=form_data.proxy_address,
		proxy_port=form_data.proxy_port,
		proxy_username=form_data.proxy_username,
		proxy_password=form_data.proxy_password,
		proxy_type=form_data.proxy_type
	).first()
 
	
	if db_proxy:
		updated_rows = db.query(model.TikTokTableProxy).filter_by(
			proxy_address=form_data.proxy_address,
			proxy_port=form_data.proxy_port,
			proxy_username=form_data.proxy_username,
			proxy_password=form_data.proxy_password,
			proxy_type=form_data.proxy_type
		).update({"used": form_data.used})
		if updated_rows > 0:
			print('find_rows')
			db.commit()

			# Fetch the rows after the update
			rows_after_update = db.query(model.TikTokTableProxy).filter_by(
				proxy_address=form_data.proxy_address,
				proxy_port=form_data.proxy_port,
				proxy_username=form_data.proxy_username,
				proxy_password=form_data.proxy_password,
				proxy_type=form_data.proxy_type
			).all()

			updated_columns = [key for key in form_data.__dict__.keys() if key in model.TikTokTableProxy.__table__.columns.keys()]

			rows_after_update_dict = [row.__dict__ for row in rows_after_update]

			return {
				"message": f"{updated_rows} rows updated successfully.",
				"rows_after_update": rows_after_update_dict
			}
		else:
			return {"message": "No matching rows found for update"}
	else:
		return {"error": "Proxy dont found"}


@userRouter.get("/get_proxy")
async def check_auth(proxy_type: str, db: Session = Depends(get_db)):
	proxy = db.query(model.TikTokTableProxy).filter((model.TikTokTableProxy.used == False) &
												(model.TikTokTableProxy.proxy_type == proxy_type)).first()
	
	if proxy:
		return {
			"proxy_address": 	proxy.proxy_address,
			"proxy_port": 		proxy.proxy_port,
			"proxy_username": 	proxy.proxy_username,
			"proxy_password": 	proxy.proxy_password,
			"proxy_type": 		proxy.proxy_type
		}
	else:
		return {"message": "Proxy not found!"}
	
@userRouter.delete("/delete_media")
async def delete_media_func(unique_id: str = Body(embed=True), db: Session = Depends(get_db), current_user: model.TikTokTableUser = Depends(get_current_user)):
	try:
		delete_media(db=db, unique_id=unique_id)
  
		return {'status': 'successfully deleted'}
	except Exception as e:
		print("Error deleting media")
		return "Error deleting media"
     
 
 
@userRouter.get("/get_reg_accounts")
async def check_auth(db: Session = Depends(get_db), 
					 current_user: model.TikTokTableUser = Depends(get_current_user)):
	
	reg_accounts = db.query(model.TikTokTableRegAccounts).all()
	
	if reg_accounts:
	   
		reg_accounts_data = [
			{
				"username": account.username,
				"email": account.email,
				"password": account.password,
				"is_loginning_now": account.is_loginning_now,
				"is_uploaded_content": account.is_uploaded_content,
				"proxy_address": account.proxy_address,
				"proxy_port": account.proxy_port,
				"proxy_username": account.proxy_username,
				"proxy_password": account.proxy_password,
				"work_time": account.work_time,
				"reg_time": account.reg_time,
				"user_reg": account.user_reg,
				"is_warmed": account.is_warmed
			}
			for account in reg_accounts
		]
		return reg_accounts_data
	else:
		return {"message": "No available reg accounts!"}
	
@userRouter.post("/get_reg_accounts_bot")
async def check_auth(db: Session = Depends(get_db), current_user: model.TikTokClusterHwidCheckRequestForm = Depends(), username: str = Body(embed=True)):
	user_hwid = query_tiktok_table_check_auth(current_user.hwid)
	user_key_taken = check_key(session=session, username=username, hwid=current_user.hwid)
	print(user_key_taken)
	if user_key_taken == False:
		raise HTTPException(status_code=311, detail="Autentication failed")
	else:
		user_info = check_user(session=session, username=username, user_key=user_key_taken)
		if user_hwid is None or user_info == False:
			raise HTTPException(status_code=311, detail="Autentication failed")
		else:
			reg_accounts = db.query(model.TikTokTableRegAccounts).all()
			
			if reg_accounts:
			
				reg_accounts_data = [
					{
						"username": account.username,
						"email": account.email,
						"password": account.password,
						"is_loginning_now": account.is_loginning_now,
						"is_uploaded_content": account.is_uploaded_content,
						"proxy_address": account.proxy_address,
						"proxy_port": account.proxy_port,
						"proxy_username": account.proxy_username,
						"proxy_password": account.proxy_password,
						"work_time": account.work_time,
						"reg_time": account.reg_time,
						"user_reg": account.user_reg,
						"is_warmed": account.is_warmed,
					}
					for account in reg_accounts
				]
				return reg_accounts_data
			else:
				return {"message": "No available reg accounts!"}

@userRouter.patch('/update_account_activity_login')
def update_is_loginning_now(
	username: str = Body(embed=True), 
	email: str = Body(embed=True, default=None), 
	password: str = Body(embed=True), 
	is_loginning_now: bool = Body(embed=True), 
	db: Session = Depends(get_db), 
	current_user: model.TikTokClusterHwidCheckRequestForm = Depends(), 
 	form_data: model.TikTokAccountIsActiveUpdateForm = Depends()
  	):
	user_hwid = query_tiktok_table_check_auth(current_user.hwid)
	if user_hwid is None:
		raise HTTPException(status_code=311, detail="Autentication failed")
	else:
		form_data.username = username
		form_data.email = email
		form_data.password = password
		form_data.is_loginning_now = is_loginning_now
		db_account = db.query(model.TikTokTableRegAccounts).filter_by(
		username=form_data.username,
		email=form_data.email,
		password=form_data.password
  		).first()
		if db_account:
			db_account.is_loginning_now = form_data.is_loginning_now
			db.commit()
			db.refresh(db_account)
			return {"db_account": db_account}
		else:
			return {"error": "Account dont found"}


@userRouter.patch('/update_account_upload_content')
def update_is_uploaded_content(
	username: str = Body(embed=True), 
	email: str = Body(embed=True, default=None), 
	password: str = Body(embed=True), 
	is_uploaded_content: bool = Body(embed=True), 
	db: Session = Depends(get_db), 
	current_user: model.TikTokClusterHwidCheckRequestForm = Depends(), 
 	form_data: model.TikTokAccountIsActiveUpdateForm = Depends()
  	):
	user_hwid = query_tiktok_table_check_auth(current_user.hwid)
	if user_hwid is None:
		raise HTTPException(status_code=311, detail="Autentication failed")
	else:
		form_data.username = username
		form_data.email = email
		form_data.password = password
		form_data.is_uploaded_content = is_uploaded_content
		db_account = db.query(model.TikTokTableRegAccounts).filter_by(
		username=form_data.username,
		email=form_data.email,
		password=form_data.password
  ).first()
		if db_account:
			db_account.is_uploaded_content = form_data.is_uploaded_content
			db.commit()
			db.refresh(db_account)
			return {"db_account": db_account}
		else:
			return {"error": "Account dont found"}


@userRouter.patch('/update_tt_media')
def update_tt_media_to_completed(
	media_name: str = Body(embed=True), 
	unique_id: str = Body(embed=True),
	completed: bool = Body(embed=True), 
	db: Session = Depends(get_db), 
	current_user: model.TikTokClusterHwidCheckRequestForm = Depends(), 
 	form_data: model.TikTokMediaCompletedUpdateForm = Depends()
  	):
	user_hwid = query_tiktok_table_check_auth(current_user.hwid)
	if user_hwid is None:
		raise HTTPException(status_code=311, detail="Autentication failed")
	else:
		form_data.media_name = media_name
		form_data.unique_id = unique_id
		form_data.completed = completed
		db_tt_media = db.query(model.TikTokTableMedia).filter_by(
		cluster_name_media=form_data.media_name,
		unique_id=form_data.unique_id).first()
		if db_tt_media:
			updated_rows = db.query(model.TikTokTableMedia).filter_by(
				cluster_name_media=form_data.media_name,
				unique_id=form_data.unique_id
			).update({"completed": form_data.completed})
			if updated_rows > 0:
				db.commit()
				return {"message": f"{updated_rows} rows updated successfully"}
			else:
				return {"message": "No matching rows found for update"}
		else:
			return {"error": "Media dont found"}
	
 

@userRouter.get('/get_warming_links')
def get_warming_links_function(current_user_hwid: str, unique_id: str, username: str, db: Session = Depends(get_db)):
	user_hwid = query_tiktok_table_check_auth(current_user_hwid)
	if user_hwid is None:
		raise HTTPException(status_code=311, detail="Autentication failed")
	else:
		warming_links = query_tiktok_warming_links(username=username, unique_id=unique_id)
		return {"warming_links": warming_links}	

@userRouter.patch('/update_warming_links')
def update_warming_links_function(current_user_hwid: str = Body(embed=True), unique_id: str = Body(embed=True), username: str = Body(embed=True), completed: bool = Body(embed=True), db: Session = Depends(get_db)):
	user_hwid = query_tiktok_table_check_auth(current_user_hwid)
	if user_hwid is None:
		raise HTTPException(status_code=311, detail="Autentication failed")
	else:
		# Используйте filter вместо filter_by
		db_accounts = db.query(model.TikTokTableWarming).filter(
			model.TikTokTableWarming.username == username,
			model.TikTokTableWarming.unique_id == unique_id,
		).all()

		if db_accounts:
			# Обновление всех записей
			response = db.query(model.TikTokTableWarming).filter(
				model.TikTokTableWarming.username == username,
				model.TikTokTableWarming.unique_id == unique_id,
			).update({model.TikTokTableWarming.completed: completed}, synchronize_session=False)

			# Подтверждение изменений в базе данных
			db.commit()

			# Возвращаем обновленные записи
			return {"warming_links_updated": response}

		else:
			return {"error": "warming link dont found"}
			
		# return {"warming_links": warming_links}	


@userRouter.post('/create-proxy')
def create_proxy_func(prxy_list: List[str] = Body(...), db: Session = Depends(get_db), current_user: model.TikTokTableUser = Depends(get_current_user)):
    try:
        new_proxies = [
            model.TikTokTableProxy(
                proxy_address=proxy.split(':')[0],
                proxy_port=proxy.split(':')[1],
                proxy_username=proxy.split(':')[2],
                proxy_password=proxy.split(':')[3],
                used=False,
                proxy_type='bad',
            )
            for proxy in prxy_list
        ]
        create_proxy_list(db=db, media=new_proxies)
        return {'status': 'success'}
    except Exception as e:
        raise HTTPException(status_code=511, detail=f"Error: {e}")


@userRouter.get('/get_proxy_list')
def get_proxy_list_func(current_user: model.TikTokTableUser = Depends(get_current_user)):
	proxy = get_proxy_list()
	return proxy
# current_user: model.TikTokTableUser = Depends(get_current_user)


@userRouter.post('/create_doc')
async def create_doc_func(db: Session = Depends(get_db), form_data: model.TikTokCreateDocRequestForm = Depends(), current_user: model.TikTokTableUser = Depends(get_current_user)):
	# current_time = datetime.now() + timedelta(hours=2)
	# new_time = current_time + timedelta(hours=12)
	# print(new_time)
	new_doc = model.TikTokCreateDocRequestForm(
		business_name=form_data.business_name,
		country=form_data.country,
		address=form_data.address,
		province=form_data.province,
		city=form_data.city,
		zip_code=form_data.zip_code,
		license=form_data.license,
		doc_img_1=form_data.doc_img_1,
		doc_img_2=form_data.doc_img_2,
		cluster=form_data.cluster,
		username=current_user.username
	)
	doc = create_doc(db=db, doc=new_doc)
	return {'doc': doc}


@userRouter.get('/get_docs_list')
def get_docs_list_func(current_user: model.TikTokTableUser = Depends(get_current_user)):
	docs = get_docs_list(user = current_user.username)
	return docs

@userRouter.post('/get_docs_list_bot')
def check_auth(cluster: str = Body(embed=True), current_user: model.TikTokClusterHwidCheckRequestForm = Depends()):
	user_hwid = query_tiktok_table_check_auth(current_user.hwid)
	if user_hwid is None:
		raise HTTPException(status_code=311, detail="Autentication failed")
	else:
		docs = get_docs_list_bot(user=user_hwid.username, cluster=cluster)
		return docs

@userRouter.delete("/delete_doc")
async def delete_doc_func(doc_id: str = Body(embed=True), db: Session = Depends(get_db), current_user: model.TikTokTableUser = Depends(get_current_user)):
	try:
		delete_doc(db=db, doc_id=doc_id, user=current_user.username)
  
		return {'status': 'successfully deleted'}
	except Exception as e:
		print("Error deleting media")
		return f"Error deleting media: {e}"

# def check_user_bot_info(username: str = Body(embed=True, default=None), user_key: str = Body(embed=True, default=None), hwid: str = Body(embed=True, default=None)):
#     user_hwid = query_tiktok_table_check_auth(hwid)
#     if user_hwid is None:
#         raise HTTPException(status_code=311, detail="Autentication failed")
#     else:
#      	return True

# def check_access_token(request: Request):
#     access_token_cookie = request.cookies.get("access_token")
#     if access_token_cookie is not None:
#         current_user: model.TikTokTableUser = Depends(get_current_user)
#         return True
#     else:
#         # raise HTTPException(status_code=401, detail="Cookies do not found")
#         return False

# @userRouter.get("/secure-endpoint")
# async def secure_endpoint(username: str = Body(embed=True),cookie_present: bool = Depends(check_access_token), user: bool = Depends(check_user_bot_info)):
	
#     return {"message": "Доступ разрешен", "user": user}
 