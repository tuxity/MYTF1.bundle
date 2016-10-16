TITLE = 'MYTF1'
ART = 'art-default.jpg'
ICON = 'icon-default.png'

####################################################################################################
def Start():

    ObjectContainer.title1 = NAME
    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'

####################################################################################################
@handler('/video/mytf1', TITLE, art=ART, thumb=ICON)
def MainMenu():

    oc = ObjectContainer()
    return oc
