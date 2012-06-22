RE_SEASON_EP = Regex("Season (?P<season>[0-9]+), EP. (?P<episode>[0-9]+)")

TheCW_PLUGIN_PREFIX   = "/video/thecw"

TheCW_ROOT            = "http://www.cwtv.com"
TheCW_SHOWS_LIST      = "http://www.cwtv.com/shows"
EP_URL             = "http://www.cwtv.com/cw-video/"

####################################################################################################
def Start():
    Plugin.AddPrefixHandler(TheCW_PLUGIN_PREFIX, MainMenu, "The CW", "icon-default.png", "art-default.jpg")
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    ObjectContainer.art = R('art-default.jpg')
    ObjectContainer.title1 = 'The CW'
    DirectoryObject.thumb=R("icon-default.png")
  
####################################################################################################
def MainMenu():
    oc = ObjectContainer()
    pageUrl=TheCW_SHOWS_LIST
    content = HTML.ElementFromURL(pageUrl)
    for item in content.xpath('//ul[@id="shows-all-list"]//li/div'):
	link = item.xpath("a")[0].get('href').replace("/shows","")
	link=EP_URL + link
	link=link.replace('video//','video/')
	title = item.xpath("a/img")[0].get('title')
	title=title.replace("-"," ").title()
	thumb=item.xpath("a/img")[0].get('src')
	if not thumb.startswith('http://'):
	    thumb = TheCW_ROOT + thumb
	oc.add(DirectoryObject(key=Callback(EpList, pageUrl=link, title=title), title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback='icon-default.png')))
    return oc

####################################################################################################
def EpList(pageUrl, title):
    oc = ObjectContainer(title2=title)
    content = HTML.ElementFromURL(pageUrl)
    for item in content.xpath('//div[contains(@class,"videotabrows_")]'):
	link = item.xpath(".//a")[0].get('href')
	if not link.startswith('http://'):
	    link = TheCW_ROOT + link
	thumb = item.xpath(".//img")[0].get('src')
	if not thumb.startswith('http://'):
	    thumb = TheCW_ROOT + thumb
	video_title = item.xpath('.//p[@class="header"]')[0].text.title()
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
	    oc.add(VideoClipObject(url=link, title=video_title, summary=summary, duration=duration, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback='icon-default.png')))
    return oc
