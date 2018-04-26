
from . import ResourceBase

class Resource(ResourceBase):
    url = 'http://fanat.tv/channels'

    def _get_origins(self):
        soup = self.get_soup(self.url)
        for c in soup.findAll('div', class_ = 'row'):
            for a in c.findAll('a'):
                try:
                    yield {
                        'name': a.find('p').string,
                        'link': a.get('href'),
                        'logo': '%s://%s/%s' % \
                            (self.urlparse(self.url).scheme,
                             self.urlparse(self.url).netloc,
                             a.find('img').get('src')),
                    }
                except Exception:
                    self.logger.error(self.traceback.format_exc().strip())

    def _get_stream(self, origin):
        html = self.get_html(origin['link'])
        stream = self.research('file:"(.*?)"', html)
        return stream
