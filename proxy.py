import requests
from bs4 import BeautifulSoup

# 模拟请求头
HEADERS = {
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Referer': 'https://www.douban.com/'
}

class IProxy(object):
	def __init__(self):
		"""
		构造函数
		"""
		self.page = 1
		self.proxy_ips = [] # 代理IP池
		self.get_proxies()

	def get_proxies(self):
		"""
		通过爬取西刺代理获取100条IP
		"""
		url = 'http://www.xicidaili.com/wt/' + str(self.page)
		r = requests.get(url, headers=HEADERS, timeout=10).text
		trs = BeautifulSoup(r, 'lxml').select('#ip_list tr')
		for i in range(1, 101):
			ip = trs[i].select('td:nth-of-type(2)')[0].text
			port = trs[i].select('td:nth-of-type(3)')[0].text
			res = 'http://%s:%s' % (ip, port)
			self.proxy_ips.append({
				'http': res
			})

	
	def get_ip(self):
		if len(self.proxy_ips) == 0:
			self.page += 1
			self.get_proxies()
		return self.proxy_ips[0]

	def del_ip(self):
		self.proxy_ips.pop(0)
