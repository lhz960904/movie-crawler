import requests
import re
import json
from bs4 import BeautifulSoup

from movie import Movie

# 正在热映url
NOWPLAYING_URL= 'https://movie.douban.com/cinema/nowplaying/'

# 即将上映url
COMING_URL = 'https://movie.douban.com/coming'

# 豆瓣api_url
API_URL = 'http://api.douban.com/v2/movie/'

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


# 获取代理IP池
def get_proxies():
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
	main()


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
		print('%s: %s-%s' % (idx, movie.doubanId, data.get('alt_title')))
		movie.author = data.get('author')
		movie.title = data.get('alt_title')
		movie.enTitle = data.get('title')
		movie.summary = data.get('summary')
		if data.get('attrs'):
			attrs = data.get('attrs')
			movie.duration = attrs.get('movie_duration')
			movie.movieType = attrs.get('movie_type')
			movie.pubdate = attrs.get('pubdate')
		movie.get_all_attr()


def main():
	"""
	爬虫入口，获取要爬取的电影ID
	"""
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
	get_proxies()