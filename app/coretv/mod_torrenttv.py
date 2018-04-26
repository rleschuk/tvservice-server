import requests, os
from . import ResourceBase

class Resource(ResourceBase):
    url = 'http://torrent-tv.ru/'
    epgurl = 'http://torrent-tv.ru/epg_listing.php?category=all&date='

    def __init__(self):
        ResourceBase.__init__(self)
        self.username = os.getenv('%s_USERNAME' % self.module.upper())
        self.password = os.getenv('%s_PASSWORD' % self.module.upper())

    def get_response(self, url, referer=None, **kwargs):
        with requests.session() as session:
            if not self.cookie:
                response = session.post('http://torrent-tv.ru/auth.php', verify=False, data = {
                    'email': self.username,
                    'password': self.password,
                    'remember': 'on',
                    'enter': 'Войти',
                }, headers = {
                    'Host': self.urlparse(self.url).netloc,
                    'Referer': self.url,
                    'User-Agent': 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60',
                    'Accept': 'text/html, application/xml, application/xhtml+xml, */*',
                    'Accept-Language': 'ru-RU',
                    'Content-Type': 'application/x-www-form-urlencoded',
                }, timeout = self.timeout)
                cookies = requests.utils.dict_from_cookiejar(response.cookies)
                if 'torrenttv_remember' in cookies:
                    self.cookie = cookies
            else:
                session.cookies = self.cookie
            headers={
                'User-Agent': 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60',
                'Accept': 'text/html, application/xml, application/xhtml+xml, */*',
                'Accept-Language': 'ru,en;q=0.9'
            }
            if referer: headers['Referer'] = referer
            response = session.get(url, headers=headers, timeout=self.timeout, **kwargs)
            self.logger.debug(response.url)
            response.encoding = 'utf-8'
            return response

    def _get_origins(self):
        soup = self.get_soup(self.url)
        for c in soup.findAll('div', class_='channel-wrapper'):
            try:
                yield {
                    'name': c.get('descr').strip(),
                    'link': 'http://torrent-tv.ru/torrent-online.php?translation=%s&engine=acestream' %\
                        self.research('translation=(\d+)', c.find('a').get('href'))
                }
            except Exception as err:
                self.logger.error(repr(err)[:100])

    def _get_stream(self, origin):
        soup = self.get_soup(origin['link'])
        ttvp = soup.find('div', id='ttv-player')
        return 'http://{ace_host}:{ace_port}/ace/getstream?url=%s' %\
            ttvp.get('data-stream_url')

    def _get_epg(self):
        for d in self.date_ranges(1):
            soup = self.get_soup(
                '%s%s' % (self.epgurl, d.strftime("%Y-%m-%d")),
                cookies = self.cookie
            )
            for c in soup.findAll('div', class_='epg-channel'):
                name = c.get('data-name')
                self.logger.debug('#########: %r', name)
                yield {
                    'name': name,
                    'items': self._get_epg_items(c.findAll('li'), d)
                }

    def _get_epg_items(self, item, date):
        for i in item:
            title = i.getText().strip()
            title = self.re.sub(r'^.*\xa0', '', title).strip()
            date_start = self.datetime.datetime.fromtimestamp(int(i.get('data-mdb-program-date')))
            jd = self.get_json(
                'http://1ttvapi.top/timeline_epg_program.php?pid=%s&date=%s&zid=14' %
                    (i.get('data-mdb-program'), i.get('data-mdb-program-date')),
                default={},
                cookies = self.cookie
            ).get('info',{})
            category = jd.get('cat','')
            description = jd.get('comment') if jd.get('comment') else ''
            arts = ['http://mdb.torrent-tv.ru/%s' % i for i in jd.get('images', [])]
            self.logger.debug('### title: %r', title)
            self.logger.debug('### categ: %r', category)
            self.logger.debug('### descr: %r', description)
            self.logger.debug('### start: %s', date_start)
            self.logger.debug('###  arts: %s', arts)
            yield {
                'title': title,
                'date_start': date_start,
                'category': category,
                'description': description,
                'arts': arts
            }
