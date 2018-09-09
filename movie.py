import pymongo
import time

class Movie(object):
	def __init__(self, doubanId):
		self.doubanId = doubanId

	def get_all_attr(self):
		for name, value in vars(self).items():
			print('%s=%s' % (name,value))

	def insertMongo(self):
		"""
		插入数据库，打印日志
		待完善
		"""
		db = pymongo.MongoClient("mongodb://localhost:27017/")['moviedb']
		collection = db["movies"]
		movie_dict = dict(vars(self).items()) 
		collection.insert_one(movie_dict)
