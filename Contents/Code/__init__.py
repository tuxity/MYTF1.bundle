import re

TITLE = 'MYTF1'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
PREFIX = '/video/mytf1'

BASE_URL = 'http://www.tf1.fr'
PROGRAMS = '%s/programmes-tv' % BASE_URL
VIDEOS = '%s/videos'

RE_MEDIA_ID = Regex("c_idwat = '(?P<media_id>[^']+)'")
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

    oc = ObjectContainer(
        title2="Program Categories"
    )

    html = HTML.ElementFromURL(PROGRAMS)

    for category in html.xpath('//ul[contains(@class, "filters_2") and contains(@class, "contentopen")]/li/a'):
        oc.add(DirectoryObject(
            key=Callback(Programs, prog_cat=category.xpath('./@data-target')[0]),
            title=category.xpath('./text()')[0]
        ))

    return oc


@route(PREFIX + '/programs/{prog_cat}')
def Programs(prog_cat):

    oc = ObjectContainer(
        title2="Programs"
    )

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
            key=Callback(VideoCategories, prog_url=program.xpath('./div/a/@href')[0]),
            title=program.xpath('./div/div/a/div/p/text()')[0],
            thumb='http:' + img.split(',')[-1].split(' ')[0]
        ))

    return oc


@route(PREFIX + '/videos')
def VideoCategories(prog_url):

    oc = ObjectContainer(
        title2="Video Categories"
    )

    html = HTML.ElementFromURL(VIDEOS % (prog_url))

    for category in html.xpath('//ul[contains(@class, "filters_1") and contains(@class, "contentopen")]/li/a'):
        oc.add(DirectoryObject(
            key=Callback(Videos, video_cat=category.xpath('./@data-filter')[0], prog_url=prog_url),
            title=category.xpath('./text()')[0]
        ))

    return oc


@route(PREFIX + '/videos/{video_cat}')
def Videos(video_cat, prog_url):

    oc = ObjectContainer(
        title2="Videos"
    )

    html = HTML.ElementFromURL((VIDEOS + '?filter=%s') % (prog_url, video_cat))

    for video in html.xpath('//ul[contains(@class, "grid")]/li'):

        imgs = video.xpath('./div/a/div/picture/source/@data-srcset')
        if (len(imgs) != 0):
            img = imgs[0]
        else:
            img = video.xpath('./div/a/div/picture/source/@srcset')[0]

        url = video.xpath('./div/div/a/@href')[0]
        title = video.xpath('./div/div/a/div/p[contains(@class, "title")]/text()')[0]
        summary = video.xpath('./div/div/a/div/p[contains(@class, "stitle")]/text()')[0]
        thumb = 'http:' + img.split(',')[-1].split(' ')[0]
        try:
            duration = int(video.xpath('./div/div/a/div/p[contains(@class, "uptitle")]/span/text()')[0]) * 1000
        except:
            duration = None
        try:
            oaa = Datetime.ParseDate(video.xpath('./div/div/a/div/p[contains(@class, "uptitle")]/span/text()')[2])
        except:
            oaa = None

        oc.add(VideoClipObject(
            key=Callback(VideoDetails, title=title, summary=summary, thumb=thumb, duration=duration, originally_available_at=originally_available_at, rating_key=title, url=url),
            title=title,
            summary=summary,
            thumb=thumb,
            rating_key=title
        ))

    return oc


@route(PREFIX + '/video/details')
def VideoDetails(title, summary, thumb, duration, originally_available_at, rating_key, url):

    oc = ObjectContainer()

    playlist_url = GetVideoPlaylistURL(url)
    streams = GetHLSStreams(playlist_url)

    oc.add(VideoClipObject(
        key=Callback(VideoDetails, title=title, summary=summary, thumb=thumb, duration=duration, originally_available_at=originally_available_at, rating_key=title, url=url),
        title=title,
        summary=summary,
        thumb=thumb,
        duration=int(duration) * 1000,
        originally_available_at=Datetime.ParseDate(originally_available_at).date(),
        rating_key=rating_key,
        items=[
            MediaObject(
                #protocol=Protocol.HLS,
                bitrate=stream['bitrate']/1000,
                audio_channels=2,
                audio_codec=AudioCodec.AAC,
                video_codec=VideoCodec.H264,
                video_resolution=stream['resolution'],
                #container=Container.MP4,
                #container=Container.MPEGTS,
                video_frame_rate=25,
                optimized_for_streaming=True,
                parts=[
                    PartObject(
                        key=HTTPLiveStreamURL(stream['url'])
                    )
                ]
            ) for stream in streams
        ]
    ))

    return oc


####################################################################################################
def GetVideoPlaylistURL(prog_url):

    page = HTTP.Request(BASE_URL + prog_url).content
    media_id = RE_MEDIA_ID.search(page).group('media_id')

    def GetAuthKey(app_name, media_id):

        secret = String.Decode('VzNtMCMxbUZJ')
        timestamp = HTTP.Request('http://www.wat.tv/servertime2', cacheTime=60).content

        string = '%s-%s-%s-%s-%s' % (media_id, secret, app_name, secret, timestamp)

        auth_key = Hash.MD5(string) + '/' + timestamp
        return auth_key

    user_agent = 'MyTF1/16090602 CFNetwork/808.1.4 Darwin/16.1.0'
    app_name = 'sdk/Iphone/1.0'
    method = 'getUrl'
    auth_key = GetAuthKey(app_name, media_id)
    version = '1.8.14'
    hosting_application_name = 'com.tf1.applitf1'
    hosting_application_version = '6.3'

    data = ('appName=%s&method=%s&mediaId=%s&authKey=%s&version=%s&hostingApplicationName=%s&hostingApplicationVersion=%s') % (app_name, method, media_id, auth_key, version, hosting_application_name, hosting_application_version)
    payload = JSON.ObjectFromString(HTTP.Request('http://api.wat.tv/services/Delivery', headers={'User-Agent': user_agent}, cacheTime=60, data=data).content)

    m3u8_url = re.sub(r'&?bw(?:max|min)=\d+', '', payload['message'])
    Log.Debug('Playing: ' + m3u8_url)

    return m3u8_url

def GetHLSStreams(url):

    playlist = HTTP.Request(url).content
    streams = []

    for line in playlist.splitlines():
        if "BANDWIDTH" in line:
            stream            = {}
            stream["bitrate"] = int(Regex('(?<=BANDWIDTH=)[0-9]+').search(line).group(0))

            if "RESOLUTION" in line:
                stream["resolution"] = int(Regex('(?<=RESOLUTION=)[0-9]+x[0-9]+').search(line).group(0).split("x")[1])
            else:
                stream["resolution"] = 0

        elif ".m3u8" in line:
            path = ''

            if not "audio=" in line or not "video=" in line:
                break

            if not line.startswith("http"):
                path = url[ : url.rfind('/') + 1]

            stream["url"] = path + line

            streams.append(stream)

    return sorted(streams, key = lambda stream: stream["bitrate"], reverse = True)
