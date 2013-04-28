RE_SEASON_EP = Regex('Season (?P<season>\d+), Ep. (?P<episode>\d+)')

CW_ROOT = 'http://www.cwtv.com'
CW_SHOWS_LIST = 'http://www.cwtv.com/shows'
EP_URL = 'http://www.cwtv.com/cw-video'

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

		oc.add(DirectoryObject(
			key = Callback(Episodes, url=url, title=title),
			title = title,
			thumb = Resource.ContentsOfURLWithFallback(url=thumb)
		))

	return oc

####################################################################################################
@route('/video/thecw/episodes')
def Episodes(url, title):

	oc = ObjectContainer(title2=title)
	html = HTML.ElementFromURL(url)

	for item in html.xpath('//div[contains(@class, "full-episodes")]'):
		url = item.xpath('./a[@class="thumbLink"]/@href')[0]
		if not url.startswith('http://'):
			url = '%s%s' % (CW_ROOT, url)

		thumb = item.xpath('.//img/@src')[0]
		if not thumb.startswith('http://'):
			thumb = '%s%s' % (CW_ROOT, thumb)

		episode_title = item.xpath('.//p[@class="et"]/text()')[0]
		summary = item.xpath('.//p[@class="d3"]/text()')[0].split(' Watch free')[0]

		details = item.xpath('.//p[@class="d2"]//text()')

		try:
			season_and_episode = RE_SEASON_EP.search(details[0]).groupdict()
			season = int(season_and_episode['season'])
			ep_index = int(season_and_episode['episode'])
		except:
			season = None
			ep_index = None

		try:
			date = Datetime.ParseDate(details[1].split('Original Air Date: ')[1]).date()
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
				thumb = Resource.ContentsOfURLWithFallback(url=thumb)
			))
		else:
			oc.add(VideoClipObject(
				url = link,
				title = video_title,
				summary = summary,
				thumb = Resource.ContentsOfURLWithFallback(url=thumb)
			))

	return oc
