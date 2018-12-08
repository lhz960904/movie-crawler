import pymongo
import time


DB = pymongo.MongoClient("mongodb://localhost:27017/")['movie-trailer']
class Movie(object):
	def __init__(self, doubanId, isPlay = 0):
		"""
		构造函数，传入doubanID
		"""
		self.doubanId = doubanId
		self.isPlay = isPlay


	def print_all_attr(self):
		"""
		打印实例所有属性
		"""
		for name, value in vars(self).items():
			print('%s=%s' % (name,value))


	def insertMongo(self):
		"""
		插入数据库，打印日志
		"""
		collection = DB["movies"]
		movie_dict = dict(vars(self).items())
		# 检查数据库是否存在
		ret = collection.find_one({'doubanId': movie_dict['doubanId'] })
		if ret:
			return ret['_id']
		result = collection.insert_one(movie_dict)
		self.insertMovieType(result.inserted_id)
		return result.inserted_id


	def insertMovieType(self, object_id):
		"""
		将电影类别插入数据库
		"""
		collection = DB["categories"]
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



