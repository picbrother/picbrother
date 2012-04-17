#!/usr/bin/python3

from facebookAPI import *
from facecomAPI import *
from mysqlAPI import *

# facebook
FB_ACCESS_TOKEN = "AAAEZAiryFyTcBAPPdSJcEt68wob2k0sBqc9SqUAcnnWxT42D3M5pDPzORA9HlSh1ldA9fos9GYQ2HhUdFrbrngCWUF2WIvXhifd70wjwFsC86pCXl"
FB_USER_ID		= "100002945999274"

# facecom
FC_API_KEY		= "da444b9c09b0c03a7355a3b37a56c1e0"
FC_APP_SECRET	= "8138a4afa7d5bb82fc167f0a594dfccf"

# mysql
DB_HOST		= "localhost"
DB_USER		= "root"
DB_PSWD		= "root"
DB_NAME		= "picbrother"

# instanciation des apis
fbapi = FacebookAPI(FB_ACCESS_TOKEN)
fcapi = FacecomAPI(FC_API_KEY, FC_APP_SECRET)
dbapi = MysqlAPI(DB_HOST, DB_USER, DB_PSWD, DB_NAME, verbose=False)


def add_users(tags):
	results = []
	for tag in tags:
		if tag['recognizable']:
			user = tag['uids'][0]
			fb_id = int(user['uid'].split("@",1)[0])
			confidence = user['confidence']
			user_exists = dbapi.get_fb_user(fb_id)
			if user_exists:
				results.append(user_exists)
				ful_name = user_exists.first_name+" "+user_exists.last_name
			else:
				profile = fbapi.get_profile(fb_id)
				new_user = User(
					fb_id=fb_id,
					first_name=profile['first_name'],
					last_name=profile['last_name'],
				)
				error = dbapi.add_user(new_user)
				if error:
					print("\t\t"+error)
					ful_name = "db error"
				else:
					results.append(new_user)
					ful_name = new_user.first_name+" "+new_user.last_name
			print("\t\t* %s #%s (%s percents)" % (ful_name, fb_id, confidence))
		else:
			print("\t\t* not recognizable")
	return results


def add_photo(fb_id, photo):
	fb_id = int(fb_id)
	url = photo['url']
	tags = photo['tags']
	users = add_users(tags)
	photo_exists = dbapi.get_fb_photo(fb_id)
	if photo_exists:
		photo_exists.users = users
		dbapi.update()
	else:
		photo = Photo(
			fb_id = fb_id,
			url = url,
			users = users
		)
		dbapi.add_photo(photo)
	

# parcourt des photos facebook
for album in fbapi.get_albums("me"):
	title = "ALBUM {name} (#{id})".format(**album)
	print("*"*100)
	print("{: ^100}".format(title))
	print("*"*100)
	for photo in fbapi.get_photos(album['id']):
		photo_fb_id = photo['id']
		print("\tPHOTO #%s" % photo_fb_id)
		print("\turl = %s" % photo['source'])
		result = fcapi.recognize(
			photo["source"],
			"friends@facebook.com",
			namespace="facebook.com",
			detector="Aggressive",
			#attributes="all",
			user_auth="fb_user:%s,fb_oauth_token:%s" % (FB_USER_ID, FB_ACCESS_TOKEN)
		)
		if result and 'photos' in result:
			for photo in result['photos']:
				add_photo(photo_fb_id, photo)
		else:
			print("\t\tno result")
		#input("appuyez sur une touche...")



