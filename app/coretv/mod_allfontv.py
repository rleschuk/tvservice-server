
from . import ResourceBase

class Resource(ResourceBase):
    url = 'http://allfon-tv.com'

    def _get_origins(self):
        soup = self.get_soup(self.url)
        for c in soup.findAll('figure', class_ = 'img'):
            try:
                yield {
                    'name': c.find('figcaption').string.strip(),
                    'link': '%s%s' % (self.url, c.find('a').get('href')),
                    'logo': '%s%s' % (self.url, c.find('img').get('src'))
                }
            except Exception:
                self.logger.error(self.traceback.format_exc().strip())

    def _get_stream(self, origin):
        stream = self.research('acestream://(.*?)"',
            self.get_html(origin['link']))
        return 'http://{ace_host}:{ace_port}/ace/getstream?id=%s' % stream
