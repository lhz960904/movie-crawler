import re
import os
import json
import logging
import requests
import pymongo
from bs4 import BeautifulSoup

from movie import Movie
from proxy import IProxy

# 正在热映url
NOWPLAYING_URL= 'https://movie.douban.com/cinema/nowplaying/'

# 即将上映url
COMING_URL = 'https://movie.douban.com/coming'

# 豆瓣api_url
API_URL = 'http://api.douban.com/v2/movie/'

# 豆瓣电影详情url
DETAIL_URL = 'https://movie.douban.com/subject/'

# 模拟请求头
HEADERS = {
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Referer': 'https://www.douban.com/'
}

# 电影实例list
movies = []

# 存入数据库总数
count = 0

# 代理ip类实例
proxyIps = ''


def get_trailer_data(movie):
	"""
	爬取电影详情页获取预告片
	"""
	url = DETAIL_URL + movie.doubanId
	for i in range(100):
		proxies = proxyIps.get_ip()
		try:
			r = requests.get(url, headers=HEADERS, timeout=10, proxies=proxies).text
		except Exception as e:
			# Todo: 存入文件中、待重新爬取
			logging.info('超时或被禁: %s' %  movie.doubanId)
			proxyIps.del_ip()
			continue
		poster_dom = BeautifulSoup(r, 'lxml').select('div#mainpic img')
		if (len(poster_dom) > 0):
			poster = poster_dom[0]['src']
			movie.poster = poster
		lists = BeautifulSoup(r, 'lxml').select('ul.celebrities-list .celebrity')
		casts = []
		for i in range(1, len(lists)):
			try:
				backgroud = lists[i].find('div', class_='avatar')['style']
			except Exception as e:
				logging.info('无效图片块儿')
				continue
			avatar = re.findall(r'http[s]?://[\w./]+', backgroud)[0]
			name = lists[i].find('a', class_='name').text
			casts.append({
				'name': name,
				'avatar': avatar
			})
		movie.casts = casts
		trailer = BeautifulSoup(r, 'lxml').find('li', class_="label-trailer")
		if trailer:
			movie.cover = re.findall(r'http[s]?://[\w./]+', trailer.find('a')['style'])[0]
			r2 = requests.get(trailer.find('a')['href'], headers=HEADERS, timeout=10).text
			movie.video = BeautifulSoup(r2, 'lxml').find('source')['src']
		break	


def get_api_data(movie):
	"""
	利用豆瓣api获取数据
	"""
	url = API_URL + movie.doubanId
	for i in range(100):
		proxies = proxyIps.get_ip()
		try:
			r = requests.get(url, headers=HEADERS, timeout=10, proxies=proxies).text
			data = json.loads(r)
		except Exception as e:
			logging.info('请求api失败, 重试第%s次' % i)
			proxyIps.del_ip()
			continue
		if data.get('code') == 112:
			logging.info('IP次数达到上限, 切换IP')
			proxyIps.del_ip()
		else:
			break
	logging.info('爬取ID: %s, Title: %s' % (movie.doubanId, movie.title))
	author = data.get('author')
	movie.author = author[0]['name'] if author else '无'
	movie.summary = data.get('summary')
	rate = data['rating'].get('average')
	movie.rate = float(rate) if rate else 0
	if data.get('attrs'):
		attrs = data.get('attrs')
		duration = attrs.get('movie_duration')
		movie.duration = duration[0] if duration else '无'
		movie.movieTypes = attrs.get('movie_type')
		movie.pubdate = attrs.get('pubdate')[-1]


def crawl_attr():
	"""
	遍历待爬取电影数组，获取所有属性，存入数据库
	"""
	global count
	for idx, movie in enumerate(movies):
		logging.info('----------------------------------------------------------')
		logging.info('爬取序号: %s' % (idx))
		get_api_data(movie)
		get_trailer_data(movie)
		if hasattr(movie, 'cover') and hasattr(movie, 'video'):
			object_id = movie.insertMongo()
			logging.info('ObjectId: %s, 存入数据库' % object_id)
			count += 1
		# movie.print_all_attr()
	logging.info('----------------------------------------------------------')
	logging.info('存入数据库总数为: %s' % count)


def main():
	"""
	爬虫入口，获取要爬取的电影doubanID
	"""
	global proxyIps
	proxyIps = IProxy()
	logging.info('***************已获取代理ip池, 开始爬取豆瓣***************')
	# 获取正在热映的电影列表
	r = requests.get(NOWPLAYING_URL, headers=HEADERS, timeout=10).text
	lists = BeautifulSoup(r, 'lxml').select('div#nowplaying li.list-item')
	movies.extend([Movie(it['id'],it['data-title'], 1) for it in lists])
	# 获取即将上映的电影列表
	r = requests.get(COMING_URL, headers=HEADERS, timeout=10).text
	movie_row = BeautifulSoup(r, 'lxml').select('table.coming_list tbody tr')
	for it in movie_row:
		href = it.select('td:nth-of-type(2) > a')[0]['href']
		title = it.select('td:nth-of-type(2) > a')[0].text
		movie = Movie(re.findall(r'\d+\.?', href)[0], title, 0)
		movies.append(movie)
	logging.info('***************已获取待爬取电影数组:  %s个***************' % len(movies))
	crawl_attr()



if __name__ == '__main__':
	# log日志配置
	path = os.path.join(os.path.dirname(__file__), 'crawler_log')
	logging.basicConfig(
        level = logging.INFO,
        format = '%(asctime)s (%(levelname)s) : %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
        filename = path,
        filemode = 'a'
    )
	logging.getLogger("requests").setLevel(logging.WARNING)
	# 删除movie、category表，重新爬取
	db = pymongo.MongoClient("mongodb://localhost:27017/")['movie-trailer']
	db["movies"].drop()
	db["categories"].drop()
	main()