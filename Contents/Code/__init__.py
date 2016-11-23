import hashlib, base64, urllib2

TITLE = 'MYTF1'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
PREFIX = '/video/mytf1'

BASE_URL = 'http://www.tf1.fr'
PROGRAMS = '%s/programmes-tv' % BASE_URL
VIDEOS = '%s/%s/videos'

RE_MEDIA_ID = Regex('www.wat.tv/embedframe/(?P<media_id>[^"]+)"')

####################################################################################################
def Start():

    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    VideoClipObject.thumb = R(ICON)
    VideoClipObject.art = R(ART)

    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'

####################################################################################################
@handler(PREFIX, TITLE)
def MainMenu():

    oc = ObjectContainer()

    html = HTML.ElementFromURL(PROGRAMS)

    for category in html.xpath('//ul[contains(@class, "filters_2") and contains(@class, "contentopen")]/li/a'):
        oc.add(DirectoryObject(
            key = Callback(Programs, prog_cat=category.xpath('./@data-target')[0]),
            title = category.xpath('./text()')[0]
        ))

    return oc

@route(PREFIX + '/programs/{prog_cat}')
def Programs(prog_cat):

    oc = ObjectContainer()

    html = HTML.ElementFromURL(PROGRAMS)

    for program in html.xpath('//ul[contains(@id, "js_filter_el_container")]/li'):
        if program.xpath('./@data-type')[0] != prog_cat and prog_cat != 'all':
            continue

        imgs = program.xpath('./div/a/div/picture/source/@data-srcset')
        if (len(imgs) != 0):
            img = imgs[0]
        else:
            img = program.xpath('./div/a/div/picture/source/@srcset')[0]

        oc.add(DirectoryObject(
            key = Callback(VideoCategories, prog_url=program.xpath('./div/a/@href')[0]),
            title = program.xpath('./div/div/a/div/p/text()')[0],
            thumb = 'http:' + img.split(',')[-1].split(' ')[0]
        ))

    return oc

@route(PREFIX + '/videos')
def VideoCategories(prog_url):

    oc = ObjectContainer()

    html = HTML.ElementFromURL(VIDEOS % (BASE_URL, prog_url))

    #TODO: it's possible to retrieve video filters, but I can't find a way to filter the videos, idk how they are doing it
    for category in html.xpath('//ul[contains(@class, "filters_1") and contains(@class, "contentopen")]/li/a'):
        oc.add(DirectoryObject(
            key = Callback(Videos, video_cat=category.xpath('./@data-filter')[0], prog_url=prog_url),
            title = category.xpath('./text()')[0]
        ))

    return oc

@route(PREFIX + '/videos/{video_cat}')
def Videos(video_cat, prog_url):

    oc = ObjectContainer()

    html = HTML.ElementFromURL(VIDEOS % (BASE_URL, prog_url))

    for video in html.xpath('//ul[contains(@class, "grid")]/li'):
        #if video.xpath('./@data-filter')[0] != video_cat and video_cat != 'all':
        #    continue

        imgs = video.xpath('./div/a/div/picture/source/@data-srcset')
        if (len(imgs) != 0):
            img = imgs[0]
        else:
            img = video.xpath('./div/a/div/picture/source/@srcset')[0]

        url = video.xpath('./div/div/a/@href')[0]
        title = video.xpath('./div/div/a/div/p[contains(@class, "title")]/text()')[0]
        summary = video.xpath('./div/div/a/div/p[contains(@class, "stitle")]/text()')[0]
        duration = video.xpath('./div/div/a/div/p[contains(@class, "uptitle")]/span/text()')[0]
        originally_available_at = video.xpath('./div/div/a/div/p[contains(@class, "uptitle")]/span/text()')[2]

        oc.add(VideoClipObject(
            url = GetVideoURL(url),
            title = title,
            summary = summary,
            thumb = 'http:' + img.split(',')[-1].split(' ')[0],
            duration = int(duration),
            originally_available_at = Datetime.ParseDate(originally_available_at)
        ))

    return oc

def GetVideoURL(prog_url):

    page = HTTP.Request(BASE_URL + prog_url).content
    media_id = RE_MEDIA_ID.search(page).group('media_id')

    def GetServerTimestamp():
        servertime = HTTP.Request('http://www.wat.tv/servertime').content
        timestamp = servertime.split(u"""|""")[0]
        return int(timestamp)

    def GetAuthKey(app_name, media_id, timestamp):
        secret = base64.b64decode('VzNtMCMxbUZJ')
        string = '%s-%s-%s-%s-%d' % (media_id, secret, app_name, secret, timestamp)
        auth_key = hashlib.md5(string).hexdigest() + '/' + str(timestamp)
        return auth_key

    user_agent = 'myTF1/60010000.15040209 CFNetwork/609 Darwin/13.0.0'
    app_name = 'sdk/Iphone/1.0'
    method = 'getUrl'
    timestamp = GetServerTimestamp()
    version = '1.4.32'
    auth_key = GetAuthKey(app_name, media_id, timestamp)
    hosting_application_name = 'com.tf1.applitf1'
    hosting_application_version = '60010000.15040209'

    data = ('appName=%s&method=%s&mediaId=%s&authKey=%s&version=%s&hostingApplicationName=%s&hostingApplicationVersion=%s') % (app_name, method, media_id, auth_key, version, hosting_application_name, hosting_application_version)

    data = HTTP.Request('http://api.wat.tv/services/Delivery', headers={'User-Agent': user_agent}, data=data).content
    data = JSON.ObjectFromString(data)

    res = HTTP.Request(data['message'], headers={'User-Agent': user_agent}).content
    return res.url + '|User-Agent=' + urllib2.quote(user_agent)
