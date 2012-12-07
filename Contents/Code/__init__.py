RE_SEASON_EP = Regex('Season (?P<season>\d+), Ep. (?P<episode>\d+)')

CW_ROOT = 'http://www.cwtv.com'
CW_SHOWS_LIST = 'http://www.cwtv.com/shows'
EP_URL = 'http://www.cwtv.com/cw-video/'

####################################################################################################
def Start():

	Plugin.AddPrefixHandler("/video/thecw", MainMenu, "The CW", "icon-default.png", "art-default.jpg")
	Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')
	ObjectContainer.art = R('art-default.jpg')
	ObjectContainer.title1 = 'The CW'
	DirectoryObject.thumb = R('icon-default.png')

####################################################################################################
def MainMenu():

	oc = ObjectContainer()
	content = HTML.ElementFromURL(CW_SHOWS_LIST)

	for item in content.xpath('//div[@class="shows-current"]//a[@class="hublink"]'):
		link = item.get('href').replace('/shows', '')
		link = EP_URL + link
		link = link.replace('video//', 'video/')
		title = item.xpath('.//img')[0].get('title')
		title = title.replace('-', ' ').title()

		thumb = item.xpath('.//img')[0].get('src')
		if not thumb.startswith('http://'):
			thumb = CW_ROOT + thumb

		oc.add(DirectoryObject(key=Callback(EpList, url=link, title=title), title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback='icon-default.png')))

	return oc

####################################################################################################
def EpList(url, title):

	oc = ObjectContainer(title2=title)
	content = HTML.ElementFromURL(url)

	for item in content.xpath('//div[contains(@class, "videowrapped slide full-episodes")]'):
		link = item.xpath('.//a[@class="thumbLink"]')[0].get('href')
		if not link.startswith('http://'):
			link = CW_ROOT + link

		thumb = item.xpath('.//img')[0].get('src')
		if not thumb.startswith('http://'):
			thumb = CW_ROOT + thumb

		video_title = item.xpath('.//p[@class="et"]')[0].text.title().replace("'S", "'s")
		details = item.xpath('.//p[@class="d2"]//text()')
		summary = item.xpath('.//p[@class="d3"]')[0].text.split(' Watch free')[0]

		try:
			season_and_episode = RE_SEASON_EP.search(details[0]).groupdict()
			season = int(season_and_episode['season'])
			epIndex = int(season_and_episode['episode'])
		except:
			season = None
			epIndex = None

		try:
			date = Datetime.ParseDate(details[1].split('Original Air Date: ')[1]).date()
		except:
			date = None

		if date:
			oc.add(EpisodeObject(url=link, title=video_title, show=title, index=epIndex, season=season, summary=summary,
			originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback='icon-default.png')))
		else:
			oc.add(VideoClipObject(url=link, title=video_title, summary=summary, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback='icon-default.png')))

	return oc
