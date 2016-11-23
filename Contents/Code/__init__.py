TITLE = 'MYTF1'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

BASE_URL = 'http://www.tf1.fr'
PROGRAMS = '%s/programmes-tv' % BASE_URL
VIDEOS = '%s/%s/videos'

####################################################################################################
def Start():

    ObjectContainer.title1 = NAME
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    VideoClipObject.thumb = R(ICON)
    VideoClipObject.art = R(ART)

    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'

####################################################################################################
@handler('/video/mytf1', TITLE)
def MainMenu():

    oc = ObjectContainer()

    html = HTML.ElementFromURL(PROGRAMS)

    for category in html.xpath('//ul[contains(@class, "filters_2") and contains(@class, "contentopen")]/li/a'):
        oc.add(DirectoryObject(
            key = Callback(Programs, category=category.xpath('./@data-target')[0]),
            title = category.xpath('./text()')[0]
        ))

    return oc

@route('/video/mytf1/programs')
def Programs(category):

    oc = ObjectContainer()

    html = HTML.ElementFromURL(PROGRAMS)

    for program in html.xpath('//ul[contains(@id, "js_filter_el_container")]/li'):
        if program.xpath('./@data-type')[0] == category or category == 'all':
            imgs = program.xpath('./div/a/div/picture/source/@data-srcset')
            if (len(imgs) != 0):
                img = imgs[0]
            else:
                img = program.xpath('./div/a/div/picture/source/@srcset')[0]

            oc.add(DirectoryObject(
                key = Callback(Videos, program_url=program.xpath('./div/a/@href')[0]),
                title = program.xpath('./div/div/a/div/p/text()')[0],
                thumb = 'http:' + img.split(',')[-1].split(' ')[0]
            ))

    return oc

@route('/video/mytf1/programs/videos')
def Videos(program_url):

    oc = ObjectContainer()

    html = HTML.ElementFromURL(VIDEOS % (BASE_URL, program_url))

    for video in html.xpath('//ul[contains(@class, "grid")]/li'):
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
            url = url,
            title = title,
            summary = summary,
            thumb = 'http:' + img.split(',')[-1].split(' ')[0],
            duration = int(duration),
            originally_available_at = Datetime.ParseDate(originally_available_at)
        ))

    return oc
