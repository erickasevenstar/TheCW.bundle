RE_SEASON_EP = Regex("Season (?P<season>[0-9]+), EP. (?P<episode>[0-9]+)")

CW_ROOT = "http://www.cwtv.com"
CW_SHOWS_LIST = "http://www.cwtv.com/shows"
EP_URL = "http://www.cwtv.com/cw-video/%s"

####################################################################################################
def Start():

	Plugin.AddPrefixHandler("/video/thecw", MainMenu, "The CW", "icon-default.png", "art-default.jpg")
	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
	ObjectContainer.art = R('art-default.jpg')
	ObjectContainer.title1 = 'The CW'
	DirectoryObject.thumb = R("icon-default.png")

####################################################################################################
def MainMenu():

	oc = ObjectContainer()
	content = HTML.ElementFromURL(CW_SHOWS_LIST)

	for item in content.xpath('//ul[@id="shows-all-list"]/li/div'):
		link = item.xpath('./a')[0].get('href').split('/')[2]
		link = EP_URL % link
		title = item.xpath('./following-sibling::text()')[0].strip()
		thumb = item.xpath('./a/img')[0].get('src')

		if not thumb.startswith('http://'):
			thumb = CW_ROOT + thumb

		oc.add(DirectoryObject(
			key=Callback(EpList, url=link, title=title),
			title=title,
			thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback='icon-default.png'))
		)

	return oc

####################################################################################################
def EpList(url, title):

	oc = ObjectContainer(title2=title)
	content = HTML.ElementFromURL(url)
	urls = []

	for item in content.xpath('//div[contains(@class, "videotabrows_")]'):
		link = item.xpath(".//a")[0].get('href')

		if link in urls:
			continue
		else:
			urls.append(link)

		if not link.startswith('http://'):
			link = CW_ROOT + link

		thumb = item.xpath(".//img")[0].get('src').rsplit('_',1)[0] + '_640x360.jpg'

		if not thumb.startswith('http://'):
			thumb = CW_ROOT + thumb

		video_title = item.xpath('.//p[@class="header"]')[0].text.title().replace("'S", "'s").replace("'M", "'m").replace("Cw", "CW")
		details = item.xpath('.//div[@class="hoverinfo-lower"]/p//text()')
		runtime = details[-2].strip().split(':')
		duration = (int(runtime[0])*60 + int(runtime[1]))*1000
		summary = details[-1].strip()

		try:
			season_and_episode = RE_SEASON_EP.search(details[0]).groupdict()
			season = int(season_and_episode['season'])
			epIndex = int(season_and_episode['episode'])
		except:
			season = None
			epIndex = None

		try:
			date = Datetime.ParseDate(details[1].split('Original Air Date:')[1]).date()
		except:
			date = None

		if date:
			oc.add(EpisodeObject(url=link, title=video_title, show=title, index=epIndex, season=season, summary=summary, duration=duration,
			originally_available_at=date, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback='icon-default.png')))
		else:
			oc.add(VideoClipObject(url=link, title=video_title, summary=summary, duration=duration,
			thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback='icon-default.png')))

	return oc
