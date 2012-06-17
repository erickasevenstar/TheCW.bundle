TheCW_PLUGIN_PREFIX   = "/video/TheCW"

TheCW_ROOT            = "http://www.cwtv.com"
TheCW_SHOWS_LIST      = "http://www.cwtv.com/shows"
EP_URL             = "http://www.cwtv.com/cw-video/"

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(TheCW_PLUGIN_PREFIX, MainMenu, "The CW", "icon-default.jpg", "art-default.jpg")
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
      title=title.replace("-"," ")
      thumb=item.xpath("a/img")[0].get('src')
      thumb=TheCW_ROOT + thumb
      oc.add(DirectoryObject(key=Callback(EpList, pageUrl=link, title=title), title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback='icon-default.png')))
    return oc

####################################################################################################
def Eplist(pageUrl, title):
    dir = MediaContainer(title2=title)
    content = HTML.ElementFromURL(pageUrl)
    for item in content.xpath('//div[contains(@id,"videotabcontents_2")]//div/div[@class="videowrapped"]'):
      link =item.xpath("a")[0].get('href')
      link=TheCW_ROOT + link
      thumb = item.xpath("a/span/img")[0].get('src')
      page = HTTP.Request(link)
      mediakey=re.compile("var curPlayingGUID = '(.+?)';").findall(page)[0]
      title =item.xpath("a/span")[1].text
      link="http://www.cwtv.com/images/dsplayer/vsplayer.swf?config=vsplayer.xml&mediaKey=" + mediakey + "&alwaysAutoPlay=true"

      oc.add(EpisodeObject(url=link, title=title, thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback='icon-default.png')))
    return oc

