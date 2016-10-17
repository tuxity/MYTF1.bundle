TITLE = 'MYTF1'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

DB = 'database'
DB_PROGRAMS = '%s/programs.json' % DB
DB_LINKS = '%s/links.json' % DB

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
def MainMenu():

    oc = ObjectContainer()

    categories = [{'slug': 'all', 'name': 'Tous les genres'}]

    for prog in JSON.ObjectFromString(Resource.Load(DB_PROGRAMS)):
        exists = False
        for cat in categories:
            if cat['slug'] == prog['categorySlug']:
                exists = True
        if exists is False:
            categories.append({'slug': prog['categorySlug'], 'name': prog['category']})

    for cat in categories:
        oc.add(DirectoryObject(
            key = Callback(Programs, filter_by=cat['slug']),
            title = cat['name']
        ))

    return oc

@route('/video/mytf1/{filter_by}')
def Programs(filter_by):

    oc = ObjectContainer()

    for prog in JSON.ObjectFromString(Resource.Load(DB_PROGRAMS)):
        if filter_by != 'all' and filter_by != prog['categorySlug']:
            continue

        #thumb = None
        #if 'menuImage' in prog:
        #    thumb = 'http://photos1.tf1.fr/image/320/160/%s/%s' % (prog['menuImage'], 000000) #last param is a 6 lenght key

        oc.add(DirectoryObject(
            key = Callback(Videos, program_slug=prog['slug']),
            title = prog['title'],
            summary = prog['description'] if 'description' in prog else None
        ))

    oc.objects.sort(key=lambda obj: obj.title)

    return oc

####################################################################################################
@route('/video/mytf1/{program_slug}')
def Videos(program_slug):

    program = None

    for prog in JSON.ObjectFromString(Resource.load(DB_PROGRAMS)):
        if prog['slug'] is program_slug:
            program = prog

    oc = ObjectContainer(title2=program['title'])

    return oc
