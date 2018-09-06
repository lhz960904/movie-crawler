class Movie(object):
	def __init__(self, doubanId):
		self.doubanId = doubanId

	def get_all_attr(self):
		for name, value in vars(self).items():
			print('%s=%s' % (name,value))