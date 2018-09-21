import pymongo
import time


db = pymongo.MongoClient("mongodb://localhost:27017/")['movie-trailer']
class Movie(object):
	def __init__(self, doubanId):
		self.doubanId = doubanId

	def get_all_attr(self):
		for name, value in vars(self).items():
			print('%s=%s' % (name,value))

	def insertMongo(self):
		"""
		插入数据库，打印日志
		"""
		collection = db["movies"]
		movie_dict = dict(vars(self).items())
		result = collection.insert_one(movie_dict)
		self.insertMovieType(result.inserted_id)

	def insertMovieType(self, object_id):
		"""
		将电影类别插入数据库
		"""
		collection = db["categories"]
		for type in self.movieTypes:
			ret = collection.find_one({'name': type })
			if not ret:
				collection.insert_one({
					'name': type,
					'movies': [object_id]
				})
			else:
				ret['movies'].append(object_id)
				collection.update({'name': type }, ret)
