import urllib.request
from bs4 import BeautifulSoup

#Returns the webpage HTML parsed as a BeautifulSoup object
def getSoup(url):
	req = urllib.request.Request(url)
	with urllib.request.urlopen(req) as response:
		soup = BeautifulSoup(response.read(), 'html.parser')
	return soup

def getStoriesInfo():
	stories = []
	soup = getSoup('https://www.publicsource.org/')
	main_div = soup.find('div',{'class':'entry-content'})
	for article in main_div.find_all('article'):
		meta = article.find('div',{'class':'entry-meta'})
		try:
			link = article.find(True,{'class':'entry-title'}).a
			title = link.string
			url = link['href']
			desc = getDesc(url)
		except AttributeError:
			title = ''
			url = ''
		try:
			author = meta.find('a',{'class':'url'}).string
		except AttributeError:
			author = ''
		try:
			published = meta.time.string
		except AttributeError:
			published = ''
		story = ['',title, author, published, desc, url]
		stories.append(story)
	return stories

def getDesc(url):
	soup = getSoup(url)
	return soup.find('meta',{'property':'og:title'})['content']
		