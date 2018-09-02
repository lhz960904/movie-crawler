class Movie(object):
	def __init__(self, doubanId):
		self.doubanId = doubanId

	def get_doubanId(self):
		return self.doubanId