
from . import ResourceBase

class Resource(ResourceBase):
    url = 'http://www.trambroid.com/playlist.xspf'

    def _get_origins(self):
        soup = self.get_soup(self.url)
        for c in soup.findAll('track'):
            try:
                yield {
                    'name': c.find('title').string.strip(),
                    'link': '/ace/getstream?url=%s' % \
                        c.find('location').string.strip()
                }
            except Exception:
                self.logger.error(self.traceback.format_exc().strip())

    def _get_stream(self, origin):
        for orig in self._get_origins():
            if orig['name'] == origin['name']:
                return 'http://{ace_host}:{ace_port}%s' % orig['link']
