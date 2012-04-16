

from urllib import request, parse
import json





class ResponsePages:
	def __init__(self, url):
		self.url = None
		self.raw_page = None
		self.page = {'paging': {'next': url}}

	def init(self, url):
		print(url)
		self.url = url
		self.raw_page = request.urlopen(url).read().decode()
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
	def __init__(self, url):
		ResponsePages.__init__(self, url)
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
	def __init__(self, access_token):
		self.access_token = access_token

	def get_albums(self, subject):
		return DataResponse("https://graph.facebook.com/%s/albums?limit=100&access_token=%s" % (subject, self.access_token))

	def get_photos(self, subject):
		return DataResponse("https://graph.facebook.com/%s/photos?limit=100&access_token=%s" % (subject, self.access_token))


if __name__ == "__main__":
	ACCESS_TOKEN = "AAAAAAITEghMBAE72EK4Hsu3a8OvwWCLVsvokQnx3tFlZCyN3zqonZBmMXtc8625RhHPYC3FVm23sNOIx73INDjWb3oU3Iv4HFKWOL0ctAS0xQrbn2E"

	api = FacebookAPI(ACCESS_TOKEN)

	nb_albums = 0
	nb_photos = 0


	for album in api.get_albums("me"):
		print("ALBUM {name} (#{id})".format(**album))
		nb_albums += 1
		for photo in api.get_photos(album['id']):
			print("\tPHOTO #%s" % photo['id'])
			print("\t\t* %s" % photo['source'])
			nb_photos += 1

	print("nb_albums=%s" % nb_albums)



