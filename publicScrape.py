import requests
from bs4 import BeautifulSoup
import json

STORY_NUM = 400

param_dict = {
	"className":"is-style-borders",
	"moreButton":0,
	"moreButtonText":"LOAD MORE STORIES",
	"showAvatar":0,
	"showCategory":1,
	"postsToShow":STORY_NUM,
	"mediaPosition":"right",
	"":"","":"","":"","":"","":"","":"",
	"typeScale":3,
	"imageScale":1,
	"postType[0]":"post",
	"showExcerpt":1,
	"excerptLength":55,
	"showReadMore":0,
	"readMoreLabel":"Keep reading",
	"showDate":1,
	"showImage":0,
	"showCaption":0,
	"disableImageLazyLoad":0,
	"imageShape":"landscape",
	"minHeight":0,
	"showAuthor":1,
	"postLayout":"list",
	"columns":3,
	"mobileStack":0,
	"sectionHeader":"",
	"specificMode":0,
	"textColor":"",
	"customTextColor":"",
	"singleMode":0,
	"showSubtitle":"0",
	"textAlign":"left",
	"page":1,
	"amp":1,
	"exlude_ids":""
}

def getStoriesInfo():
	stories_info = []
	with requests.get("https://www.publicsource.org/wp-json/newspack-blocks/v1/articles", params = param_dict) as r:
		stories_json = json.loads(r.text)['items']
	for story in stories_json:
		soup = BeautifulSoup(story['html'], 'html.parser')
		link = soup.find(True, {'class':'entry-title'}).a
		title = link.string;
		url = link['href']
		meta = soup.find('div',{'class':'entry-meta'})
		author = meta.find('a',{'class':'url'}).string
		published = meta.time.string
		try:
			desc = soup.p.string
		except AttributeError:
			desc=""
		story_info = ['', title, author, published, desc, url]
		stories_info.append(story_info)
	return stories_info