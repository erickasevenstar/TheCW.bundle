RE_SEASON_EP = Regex('Season (?P<season>\d+), Ep. (?P<episode>\d+)')

CW_ROOT = 'http://www.cwtv.com'
CW_SHOWS_LIST = 'http://www.cwtv.com/shows'
EP_URL = 'http://www.cwtv.com/cw-video'

THUMB_PROXY = 'http://www.uswebproxy.com/?q=%s'

####################################################################################################
def Start():

	ObjectContainer.title1 = 'The CW'

####################################################################################################
@handler('/video/thecw', 'The CW')
def MainMenu():

	oc = ObjectContainer()
	html = HTML.ElementFromURL(CW_SHOWS_LIST)

	for item in html.xpath('//div[@class="shows-current"]//a[@class="hublink"]'):
		show = item.get('href').split('/')[-1]
		url = '%s/%s' % (EP_URL, show)
		title = String.CapitalizeWords(show.replace('-', ' '))
		thumb = item.xpath('.//img/@src')[0]
		thumb_alt = THUMB_PROXY % String.Base64Encode(thumb)

		oc.add(DirectoryObject(
			key = Callback(Episodes, url=url, title=title),
			title = title,
			thumb = Resource.ContentsOfURLWithFallback([thumb, thumb_alt])
		))

	return oc

####################################################################################################
@route('/video/thecw/episodes')
def Episodes(url, title):

	oc = ObjectContainer(title2=title)
	html = HTML.ElementFromURL(url)

	for item in html.xpath('//ul[@id="list_1"]/li/div/a[@class="thumbLink"]'):
		url = item.xpath('./@href')[0]
		if not url.startswith('http://'):
			url = '%s%s' % (CW_ROOT, url)

		thumb = item.xpath('.//img/@src')[0]
		if not thumb.startswith('http://'):
			thumb = '%s%s' % (CW_ROOT, thumb)
		thumb_alt = THUMB_PROXY % String.Base64Encode(thumb)

		episode_title = item.xpath('.//div[@class="videodetails1"]/p/text()')[0]
		summary = item.xpath('.//p[@class="d3"]/text()')[0].split(' Watch free')[0]

		try:
			season_and_episode = episode_title.split('Ep.')[1].split(')')[0]
			if len(season_and_episode) >3:
				season = season_and_episode[0] + season_and_episode[1]
			else:
				season = season_and_episode[0]
			try: season = int(season)
			except: season = None
			try: ep_index = int(season_and_episode)
			except: ep_index = None
		except:
			season = None
			ep_index = None

		try:
			date = item.xpath('.//p[@class="videodate"]//text()')[0]
			date = Datetime.ParseDate(date.split('Original Air Date: ')[1]).date()
		except:
			date = None

		if date:
			oc.add(EpisodeObject(
				url = url,
				title = episode_title,
				show = title,
				index = ep_index,
				season = season,
				summary = summary,
				originally_available_at = date,
				thumb = Resource.ContentsOfURLWithFallback([thumb, thumb_alt])
			))
		else:
			oc.add(VideoClipObject(
				url = url,
				title = episode_title,
				summary = summary,
				thumb = Resource.ContentsOfURLWithFallback([thumb, thumb_alt])
			))

	return oc
