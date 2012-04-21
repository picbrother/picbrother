

from urllib import request, parse
import json

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
import sched, time
s = sched.scheduler(time.time, time.sleep)

from threading import Thread

class myWebClient(Thread):
	def __init__(self, fbapi):
		super(myWebClient, self).__init__()
		self.fbapi = fbapi
		self.url = QUrl("https://www.facebook.com/dialog/oauth?client_id=309558635776311&redirect_uri=http://89.88.36.152/test.html?p=1&scope=offline_access,user_birthday,friends_birthday,user_photos,friends_photos,user_relationships,friends_relationships,user_relationship_details,friends_relationship_details,read_friendlists&response_type=token")
		self.timer = ""

	def run(self):
		app = QApplication(sys.argv)
		web = QWebView()
		web.resize(1100, 700)
		self.timer = QTimer()
		QObject.connect(self.timer, SIGNAL("timeout()"), self.reload_token)
		QObject.connect(web,SIGNAL("urlChanged (const QUrl&)"), self.link_clicked)
		web.load(self.url)
		web.show()
		app.exec_()

	def link_clicked(self, url):
		"""
		url of the page had changed
		"""
		if url.host() == "89.88.36.152":
			fragment=url.fragment().split("&")
			token=fragment[0].split("=")
			expire=fragment[1].split("=")
			self.fbapi.access_token=token[1]
			if self.fbapi.verbose:
				print(token[1])
				print(expire[1])
			self.timer.start(int(expire[1])*1000/2)


	def reload_token(self):
		"""
		reload the token
		"""
		self.web.load(url)

	
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
	def __init__(self, *, access_token="", verbose=False):
		self.access_token = access_token
		self.verbose = verbose
		if self.access_token == "":
			w = myWebClient(self)
			w.start()
		while self.access_token == "":
			time.sleep(1)

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

	api = FacebookAPI(verbose=True)

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



