

from urllib import request, parse
import json



	
class ResponsePages:
	def __init__(self, url, verbose):
		self.verbose = verbose
		self.url = None
		self.raw_page = None
		self.page = {'paging': {'next': url}}
		#self.opener = request.FancyURLopener(max_tries=10)

	def init(self, url):
		if self.verbose:
			print(url)
		self.url = url
		self.raw_page = "{'paging': {'next': url}}"
		for i in range(10):
			try:
				self.raw_page = request.urlopen(url).read().decode()
			except Exception as ex:
				print(ex)
			else:
				break
		self.page = json.loads(self.raw_page)

	def __iter__(self):
		return self
	
	def __next__(self):
		url = None
		try:
			url = self.page['paging']['next']
		except Exception as ex:
			print(ex)
			raise StopIteration
		else:
			self.init(url)
			return self.page

class DataResponse(ResponsePages):
	def __init__(self, url, verbose):
		self.verbose = verbose
		ResponsePages.__init__(self, url, self.verbose)
		ResponsePages.__next__(self)
		self.iobject = iter(self.page['data'])
	
	def __iter__(self):
		return self

	def __next__(self):
		try:
			return next(self.iobject)
		except StopIteration:
			ResponsePages.__next__(self)
			self.iphotos = iter(self.page['data'])
			return next(self.iobject)

		
	
class FacebookAPI:
	def __init__(self, access_token, *, verbose=False):
		self.access_token = access_token
		self.verbose = verbose

	def get_albums(self, subject):
		return DataResponse("https://graph.facebook.com/%s/albums?limit=100&access_token=%s" % (subject, self.access_token), self.verbose)

	def get_photos(self, subject):
		return DataResponse("https://graph.facebook.com/%s/photos?limit=100&access_token=%s" % (subject, self.access_token), self.verbose)

	def get_profile(self, subject):
		url = "https://graph.facebook.com/%s?&access_token=%s" % (subject, self.access_token)
		if self.verbose:
			print(url)
		#opener = request.FancyURLopener()
		r = "{}"
		for i in range(10):
			try:
				r = request.urlopen(url).read().decode()
			except Exception as ex:
				print(ex)
			else:
				break
		return json.loads(r)

if __name__ == "__main__":
	ACCESS_TOKEN = "AAAEZAiryFyTcBAPPdSJcEt68wob2k0sBqc9SqUAcnnWxT42D3M5pDPzORA9HlSh1ldA9fos9GYQ2HhUdFrbrngCWUF2WIvXhifd70wjwFsC86pCXl"

	api = FacebookAPI(ACCESS_TOKEN, verbose=True)

	nb_albums = 0
	nb_photos = 0

	profile = api.get_profile("me")
	print(profile)
	exit()
	for album in api.get_albums("me"):
		print("ALBUM {name} (#{id})".format(**album))
		nb_albums += 1
		for photo in api.get_photos(album['id']):
			print("\tPHOTO #%s" % photo['id'])
			print("\t\t* %s" % photo['source'])
			nb_photos += 1

	print("nb_albums=%s" % nb_albums)



