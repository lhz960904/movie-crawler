import requests
import re
import time
import json
from bs4 import BeautifulSoup

from movie import Movie

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

# 电影
movies = []
# 代理IP
proxy_ips = []


def get_proxies():
	"""
	获取代理IP池
	"""
	url = 'http://www.xicidaili.com/wt/'
	r = requests.get(url, headers=HEADERS, timeout=10).text
	trs = BeautifulSoup(r, 'lxml').select('#ip_list tr')
	for i in range(1, 101):
		ip = trs[i].select('td:nth-of-type(2)')[0].text
		port = trs[i].select('td:nth-of-type(3)')[0].text
		res = 'http://%s:%s' % (ip, port)
		proxy_ips.append({
			'http': res
		})
	print('------------已获取代理ip池，开始爬取------------')


def insertMongoDB():
	"""
	插入mongoDB数据库
	"""
	movie_list = [x for x in movies if not x.get('video')]
	print('*******************有效电影数: %s******************' % len(movie_list))
	for movie in movie_list:
		movie.insertMongo()

def get_page_data():
	"""
	爬取电影详情页获取预告片
	"""
	for idx, movie in enumerate(movies):
		proxies = proxy_ips[0]
		print('------------开始请求doubanID: %s------------' % movie.doubanId)
		time.sleep(3)
		url = DETAIL_URL + movie.doubanId
		r = requests.get(url, headers=HEADERS, timeout=10).text
		poster = BeautifulSoup(r, 'lxml').select('div#mainpic img')[0]['src']
		movie.poster = poster.replace('s_ratio_poster', 'l_ratio_poster')
		lists = BeautifulSoup(r, 'lxml').select('ul.celebrities-list .celebrity')
		casts = []
		for i in range(1, len(lists)):
			try:
				backgroud = lists[i].find('div', class_='avatar')['style']
			except Exception as e:
				print('------------无效图片块儿------------')
				continue
			avatar = re.findall(r'http[s]?://[\w./]+', backgroud)[0]
			name = lists[i].find('a', class_='name').text
			casts.append({
				'name': name,
				'avatar': avatar
			})
		movie.casts = casts
		trailer = BeautifulSoup(r, 'lxml').find('li', class_="label-trailer")
		if (trailer):
			movie.cover = re.findall(r'http[s]?://[\w./]+', trailer.find('a')['style'])[0]
			r2 = requests.get(trailer.find('a')['href'], headers=HEADERS, timeout=10).text
			movie.video = BeautifulSoup(r2, 'lxml').find('source')['src']
		else:
			print('------------没有预告片------------')
	insertMongoDB()

def get_api_data():
	"""
	利用豆瓣api获取数据
	"""
	for idx, movie in enumerate(movies):
		url = API_URL + movie.doubanId
		for i in range(100):
			proxies = proxy_ips[0]
			print(proxies)
			try:
				r = requests.get(url, headers=HEADERS, timeout=10, proxies=proxies).text
				data = json.loads(r)
			except Exception as e:
				print('------------请求失败, 重试------------')
				proxy_ips.pop(0)
				continue
			if data.get('code') == 112:
				print('------------IP次数达到上限，切换IP------------')
				proxy_ips.pop(0)
			else:
				break
		print('%s: %s-%s' % (idx, movie.doubanId, data.get('title')))
		movie.author = data.get('author')
		movie.title = data.get('alt_title')
		movie.enTitle = data.get('title')
		movie.summary = data.get('summary')
		if data.get('attrs'):
			attrs = data.get('attrs')
			movie.duration = attrs.get('movie_duration')
			movie.movieType = attrs.get('movie_type')
			movie.pubdate = attrs.get('pubdate')
	get_page_data()


def main():
	"""
	爬虫入口，获取要爬取的电影ID
	"""
	get_proxies()
	r = requests.get(NOWPLAYING_URL, headers=HEADERS, timeout=10).text
	lists = BeautifulSoup(r, 'lxml').select('div#nowplaying li.list-item')
	for it in lists:
		movie = Movie(it['id'])
		movies.append(movie)
	r = requests.get(COMING_URL, headers=HEADERS, timeout=10).text
	movie_row = BeautifulSoup(r, 'lxml').select('table.coming_list tbody tr')
	for it in movie_row:
		href = it.select('td:nth-of-type(2) > a')[0]['href']
		movie = Movie(re.findall(r'\d+\.?', href)[0])
		movies.append(movie)	
	get_api_data()


if __name__ == '__main__':
	main()