"""RUTUBE for Kodi: search, categories and channels through the public rutube.ru API."""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

BASE = sys.argv[0]
HANDLE = int(sys.argv[1])
ARGS = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
API = 'https://rutube.ru/api/'
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'
ADDON = xbmcaddon.Addon()
NAME = ADDON.getAddonInfo('name')
HISTORY_SIZE = 10


def tr(string_id):
    return ADDON.getLocalizedString(string_id)


class ApiError(Exception):
    pass


def get(url):
    if 'format=json' not in url:
        url += ('&' if '?' in url else '?') + 'format=json'
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Referer': 'https://rutube.ru/'})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode('utf-8'))
    except (urllib.error.URLError, ValueError, OSError) as e:
        xbmc.log('[%s] %s: %s' % (ADDON.getAddonInfo('id'), url, e), xbmc.LOGWARNING)
        raise ApiError(str(e))


def plugin_url(**kw):
    return BASE + '?' + urllib.parse.urlencode(kw)


def search_url(query):
    return API + 'search/video/?query=' + urllib.parse.quote(query)


def folder(label, url, icon=None):
    li = xbmcgui.ListItem(label)
    if icon:
        li.setArt({'thumb': icon, 'icon': icon})
    xbmcplugin.addDirectoryItem(HANDLE, url, li, True)


def history():
    try:
        h = json.loads(ADDON.getSetting('history') or '[]')
        return [q for q in h if isinstance(q, str)]
    except ValueError:
        return []


def remember(query):
    h = [q for q in history() if q != query]
    h.insert(0, query)
    ADDON.setSetting('history', json.dumps(h[:HISTORY_SIZE], ensure_ascii=False))


def root():
    folder('[B]%s[/B]' % tr(30001), plugin_url(mode='search'))
    for q in history():
        folder('%s: %s' % (tr(30002), q), plugin_url(mode='list', url=search_url(q)))
    folder(tr(30003), plugin_url(mode='cats'))
    xbmcplugin.endOfDirectory(HANDLE)


def cats():
    for c in get(API + 'video/category/'):
        if isinstance(c, dict) and 'id' in c:
            folder(c.get('name', str(c['id'])), plugin_url(mode='list', url=API + 'video/category/%d/' % c['id']))
    xbmcplugin.endOfDirectory(HANDLE)


def search():
    q = ARGS.get('q')
    if not q:
        kb = xbmc.Keyboard('', '%s: %s' % (NAME, tr(30001)))
        kb.doModal()
        if not kb.isConfirmed() or not kb.getText().strip():
            xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
            return
        q = kb.getText().strip()
    remember(q)
    listing(search_url(q))


def listing(url=None):
    d = get(url or ARGS['url'])
    xbmcplugin.setContent(HANDLE, 'videos')
    for v in d.get('results', []):
        if not isinstance(v, dict) or 'id' not in v:
            continue
        title = v.get('title', '')
        li = xbmcgui.ListItem(title)
        thumb = v.get('thumbnail_url')
        li.setArt({'thumb': thumb, 'icon': thumb, 'fanart': thumb})
        author = v.get('author') or {}
        tag = li.getVideoInfoTag()
        tag.setTitle(title)
        tag.setPlot(v.get('description') or '')
        tag.setDuration(int(v.get('duration') or 0))
        if author.get('name'):
            tag.setStudios([author['name']])
        if v.get('created_ts'):
            tag.setPremiered(v['created_ts'][:10])
        li.setProperty('IsPlayable', 'true')
        if author.get('id'):
            channel = plugin_url(mode='list', url=API + 'video/person/%s/' % author['id'])
            li.addContextMenuItems([('%s: %s' % (tr(30004), author.get('name', '')), 'Container.Update(%s)' % channel)])
        xbmcplugin.addDirectoryItem(HANDLE, plugin_url(mode='play', id=v['id']), li, False)
    if d.get('has_next') and d.get('next'):
        folder('[B]%s >>[/B]' % tr(30005), plugin_url(mode='list', url=d['next']))
    xbmcplugin.endOfDirectory(HANDLE)


def play():
    options = get(API + 'play/options/%s/' % urllib.parse.quote(ARGS['id']))
    balancer = options.get('video_balancer') or {}
    url = balancer.get('m3u8') or balancer.get('default')
    if not url:
        xbmcgui.Dialog().notification(NAME, tr(30006), xbmcgui.NOTIFICATION_ERROR)
        xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())
        return
    li = xbmcgui.ListItem(path=url)
    li.setMimeType('application/vnd.apple.mpegurl')
    li.setContentLookup(False)
    if xbmc.getCondVisibility('System.HasAddon(inputstream.adaptive)'):
        li.setProperty('inputstream', 'inputstream.adaptive')
        li.setProperty('inputstream.adaptive.stream_headers', 'User-Agent=' + urllib.parse.quote(UA))
        li.setProperty('inputstream.adaptive.chooser_resolution_max', ADDON.getSetting('max_resolution') or '1080p')
    xbmcplugin.setResolvedUrl(HANDLE, True, li)


def main():
    mode = ARGS.get('mode')
    try:
        {'search': search, 'cats': cats, 'list': listing, 'play': play}.get(mode, root)()
    except ApiError:
        xbmcgui.Dialog().notification(NAME, tr(30007), xbmcgui.NOTIFICATION_ERROR)
        if mode == 'play':
            xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())
        else:
            xbmcplugin.endOfDirectory(HANDLE, succeeded=False)


main()
