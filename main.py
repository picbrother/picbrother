#!/usr/bin/python3

from facebookAPI import *
from facecomAPI import *
from mysqlAPI import *
from gephiAPI import *

# facebook
FB_ACCESS_TOKEN = "AAAEZAiryFyTcBAMjxztgJGaEAFpwXidNZAt03pfSS6cJUXFGrCgome0Bs41HDm5nvsVZCByxGsV6iLxv3l9ESayTZCp5kZBTRf2aehYsuhgY6L0s1y9ZBo"
FB_USER_ID		= "100002945999274"

# facecom
FC_API_KEY		= "da444b9c09b0c03a7355a3b37a56c1e0"
FC_APP_SECRET	= "8138a4afa7d5bb82fc167f0a594dfccf"

# mysql
DB_HOST		= "localhost"
DB_USER		= "root"
DB_PSWD		= "root"
DB_NAME		= "picbrother"

#GEPHI
GEPHI_HOST	= "localhost"
GEPHI_PORT	= 8080

# instanciation des apis
fbapi = FacebookAPI()
fcapi = FacecomAPI(FC_API_KEY, FC_APP_SECRET)
dbapi = MysqlAPI(DB_HOST, DB_USER, DB_PSWD, DB_NAME, verbose=False)
graphapi = GephiAPI(GEPHI_HOST, GEPHI_PORT)

def add_users(tags):
	results = []
	for tag in tags:
		if tag['recognizable']:
			user = tag['uids'][0]
			fb_id = int(user['uid'].split("@",1)[0])
			confidence = user['confidence']
			user_exists = dbapi.get_fb_user(fb_id)
			if user_exists:
				db_user = user_exists
			else:
				for i in range(10):
					try: 
						profile = fbapi.get_profile(fb_id)
						new_user = User(
							fb_id=fb_id,
							first_name=profile['first_name'],
							last_name=profile['last_name'],
						)
						r = dbapi.add_object(new_user)
					except Exception as ex:
						print(ex)
					else:
						break

				if isinstance(r,str):
					print("\t\t"+r)
					ful_name = "db error"
					db_user = None
				else:
					db_user = r
			if db_user:
				results.append(db_user)
				graphapi.add_node(db_user.fb_id)
				ful_name = db_user.first_name+" "+db_user.last_name
			print("\t\t* %s #%s (%s percents)" % (ful_name, fb_id, confidence))
		else:
			print("\t\t* not recognizable")
	return results


def add_photo(album, fb_id, photo):
	fb_id = int(fb_id)
	url = photo['url']
	tags = photo['tags']
	users = add_users(tags)
	photo_exists = dbapi.get_fb_photo(fb_id)
	if photo_exists:
		photo_exists.users = users
		dbapi.update()
	else:
		for u1 in users:
			for u2 in users:
				graphapi.add_edge(str(u1.fb_id), str(u2.fb_id))
		photo = Photo(
			fb_id = fb_id,
			url = url,
			users = users,
			album = album,
		)
		dbapi.add_object(photo)
	
stop = False
# parcourt des photos facebook
for album in fbapi.get_albums("me"):
	if stop:
		break
	try:
		title = "ALBUM {name} (#{id})".format(**album)
		print("*"*100)
		print("{: ^100}".format(title))
		print("*"*100)
		album_fb_id = album['id']
		db_album = dbapi.get_fb_album(album_fb_id)
		if not db_album:
			db_album = Album(
				fb_id=album_fb_id,
				name=album['name']
			)
			r = dbapi.add_object(db_album)
			if isinstance(r, str):
				print("\tERROR: ",r)
				continue
		for photo in fbapi.get_photos(album['id']):
			photo_fb_id = photo['id']
			print("\tPHOTO #%s" % photo_fb_id)
			print("\turl = %s" % photo['source'])
			photo_exists = dbapi.get_fb_photo(photo_fb_id)
			if photo_exists:
				print("\tphoto déjà visitée")
			else:
				result = fcapi.recognize(
					photo["source"],
					"friends@facebook.com",
					namespace="facebook.com",
					detector="Aggressive",
					#attributes="all",
					user_auth="fb_user:%s,fb_oauth_token:%s" % (FB_USER_ID, fbapi.get_access_token())
				)
				if result and 'photos' in result:
					for photo in result['photos']:
						add_photo(db_album, photo_fb_id, photo)
				else:
					print("\t\tno result")
			#input("appuyez sur une touche...")
	except KeyboardInterrupt:
		stop = True


