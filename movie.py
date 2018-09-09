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
		格式：插入时间———ObjectId———电影doubanID——电影名字
		"""
		db = pymongo.MongoClient("mongodb://localhost:27017/")['moviedb']
		collection = db["movies"]
		movie_dict = dict(vars(self).items()) 
		result = collection.insert_one(movie_dict) 
		insert_time = time.strftime('%H:%M:%S', time.localtime())
		print('%s——%s——%s——%s' % (insert_time, result.inserted_id, self.doubanId, self.title))
