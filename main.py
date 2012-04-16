#!/usr/bin/python3

from facebookAPI import *
from facecomAPI import *
from mysqlAPI import *

# facebook
FB_ACCESS_TOKEN = "AAAAAAITEghMBAE72EK4Hsu3a8OvwWCLVsvokQnx3tFlZCyN3zqonZBmMXtc8625RhHPYC3FVm23sNOIx73INDjWb3oU3Iv4HFKWOL0ctAS0xQrbn2E"
FB_USER_ID		= ""

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
dbapi = MysqlAPI(DB_HOST, DB_USER, DB_PSWD, DB_NAME, verbose=True)

# parcourt des photos facebook
for album in fbapi.get_albums("me"):
	print("ALBUM {name} (#{id})".format(**album))
	for photo in api.get_photos(album['id']):
		print("\tPHOTO #%s" % photo['id'])
		print("\t\t* %s" % photo['source'])
		result = fcapi.recognize(
			photo["source"],
			"friends@facebook.com",
			namespace="facebook.com",
			detector="Aggressive",
			#attributes="all",
			user_auth="fb_user:%s,fb_oauth_token:%s" % (FB_USER_ID, FB_ACCESS_TOKEN)
		)
		if result:
			for tag in tags:
				if tag['recognizable']:
					uid = tag['uids']
					print("\t\t\t* %s (%s%)" % (uid['uid'], uid['confidence']))




