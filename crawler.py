import requests
import re
from bs4 import BeautifulSoup

from movie import Movie

# 正在热映url
NOWPLAYING_URL= 'https://movie.douban.com/cinema/nowplaying/'
# 即将上映url
COMING_URL = 'https://movie.douban.com/coming'
# 电影
movies = []


def get_data():
	for movie in movies:
		print(movie.get_doubanId())

def main():
	"""
	爬虫入口，获取要爬取的电影ID
	"""
	r = requests.get(NOWPLAYING_URL, timeout=10).text
	lists = BeautifulSoup(r, 'lxml').select('div#nowplaying li.list-item')
	for it in lists:
		movie = Movie(it['id'])
		movies.append(movie)
	r = requests.get(COMING_URL, timeout=10).text
	movie_row = BeautifulSoup(r, 'lxml').select('table.coming_list tbody tr')
	for it in movie_row:
		href = it.select('td:nth-of-type(2) > a')[0]['href']
		movie = Movie(re.findall(r'\d+\.?', href)[0])
		movies.append(movie)
	get_data()


if __name__ == '__main__':
	main()