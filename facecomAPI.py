
from urllib import parse
from urllib import request
import json

class FacecomAPI:
	def __init__(self, api_key, api_secret, *, verbose=False):
		self.verbose = verbose
		self.api_key = api_key
		self.api_secret = api_secret
		self.opener = request.FancyURLopener()

	def recognize(self, urls, uids, **kwargs):
		"""
		@param urls a comma separated list of JPG photos
		@param uids a comma separated list of user IDs to search for in the photos passed in the request
		@param namespace a default user namespace to be used for all users
			specified in the short-hand syntax (just the user ID, without
			the '@namespace')
		@param detector Set the face detector work mode: Normal (default)
			or Aggressive. Aggressive mode may find a bit more faces, and
			is also slower. Usage of this detector counts as two Normal
			detections
		@param attributes Can be all, none or a list of specific comma-separated
			attributes (see list of available attributes on the return values
			page. Unless specified, it returns the default 3 attributes of
			gender, glasses and smiling. The face attribute, marking whether
			there's a face present is always returned.
		@param format 'json' (default) or 'xml'
		@param user_auth signed-in facebook or twitter user credentials.
			Required only when specifying UIDsin these namespaces. Use name:value pairs, separated by comma:
				* fb_user:[facebook user id]
				* [Deprecated] fb_session:[facebook session id]
				* fb_oauth_token [facebook oauth 2.0 access token]
				and/or:
				* twitter_username:[twitter screen name]
				* twitter_password:[twitter password]
				or:
				* twitter_oauth_user:[twitter OAuth user]
				* twitter_oauth_secret:[twitter OAuth secret]
				* twitter_oauth_token:[twitter OAuth token]
		"""
		kwargs['urls'] = urls
		kwargs['uids'] = uids
		return self.send("recognize", **kwargs)


	def send(self, cmd, **kwargs):
		url = "http://api.face.com/faces/%s.json?" % cmd
		data = dict(
			api_key		= self.api_key,
			api_secret	= self.api_secret,
		)
		data.update(kwargs)
		url += parse.urlencode(data)
		"""
		for k,v in data.items():
			url += "%s=%s&" % (k,v)"""

		if self.verbose:
			print(url)
		r = self.opener.open(url)
		s = r.read().decode()
		return json.loads(s)


if __name__ == "__main__":
	API_KEY		= "da444b9c09b0c03a7355a3b37a56c1e0"
	APP_SECRET	= "8138a4afa7d5bb82fc167f0a594dfccf"
	api = FacecomAPI(API_KEY, APP_SECRET, verbose=True)

	result = api.recognize(
		"https://fbcdn-sphotos-a.akamaihd.net/hphotos-ak-ash3/528598_226102264164638_100002945999274_426143_744451539_n.jpg",
		"friends@facebook.com",
		namespace="facebook.com",
		detector="Aggressive",
		#attributes="all",
		user_auth="fb_user:100002945999274,fb_oauth_token:AAAAAAITEghMBAE72EK4Hsu3a8OvwWCLVsvokQnx3tFlZCyN3zqonZBmMXtc8625RhHPYC3FVm23sNOIx73INDjWb3oU3Iv4HFKWOL0ctAS0xQrbn2E"
	)

	
	print(json.dumps(result, indent=4))
