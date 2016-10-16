TITLE = 'MYTF1'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

DATABASE = 'database.json'
API_INIT = 'http://api.mytf1.tf1.fr/mobile/init?device=%s'
API_SYNC = 'http://api.mytf1.tf1.fr/mobile/sync/%s?device=%s&key=%s'

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
def Programs():

    oc = ObjectContainer()

    for program in JSON.ObjectFromURL(R(DATABASE))['programs']:
        oc.add(DirectoryObject(
            key = Callback(Videos, program_slug=program['slug']),
            title = program['title'],
            summary = program['description']
        ))

    return oc

####################################################################################################
@route('/video/mytf1/{program_slug}')
def Videos(program_slug):

    program = {}

    for p in JSON.ObjectFromURL(R(DATABASE))['programs']:
        if p['slug'] is program_slug:
            program = p

    oc = ObjectContainer(title2=program['title'])

    return oc
