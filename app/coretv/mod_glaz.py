
from . import ResourceBase

class Resource(ResourceBase):
    url = 'https://www.glaz.tv/online-tv/'

    def _get_origins(self):
        for p in self.get_soup(self.url).findAll('a', class_ = 'js-pager-item'):
            soup = self.get_soup('%s://%s%s' % \
                (self.urlparse(self.url).scheme,
                 self.urlparse(self.url).netloc,
                 p.get('href')))
            for c in soup.findAll('section', class_ = 'list-channel'):
                try:
                    if c.find('span', class_ = 'external-label'): continue
                    yield {
                        'name': c.find('span', class_ = 'list-channel-info__name').string,
                        'link': '%s://%s%s' % \
                            (self.urlparse(self.url).scheme,
                             self.urlparse(self.url).netloc,
                             c.find('a', class_ = 'list-channel__info').get('href')),
                        'logo': '%s:%s' % \
                            (self.urlparse(self.url).scheme,
                             c.find('div', class_ = 'list-channel-info__logo')\
                              .find('img').get('src'))
                    }
                except Exception:
                    self.logger.error(self.traceback.format_exc().strip())

    def _get_stream(self, origin):
        stream = None
        html = self.get_html(origin['link'])
        if 'wmsAuthSign' in html:
            sig = self.research('var signature = "(.*?)"', html)
            stream = self.research('url: "(.*?)" \+ signature', html)
            if stream: stream += sig
        elif 'rosshow' in html:
            soup = self._get_soup(html)
            id_ = soup.find('iframe').get('src').replace('//rosshow.ru/iframe/','')
            stream = r'https://live-rmg.cdnvideo.ru/rmg/%s_new.sdp/chunklist.m3u8?hls_proxy_host=pub1.rtmp.s01.l.rmg' % id
        else:
            soup = self._get_soup(html)
            param = soup.find('param', dict(name = 'flashvars'))
            if param:
                stream = self.research('file=(.*)',
                    soup.find('param', dict(name = 'flashvars')).get('value'))
        return stream
