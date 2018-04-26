
import base64
from . import ResourceBase

class Resource(ResourceBase):
    url = 'http://www.alltvonline.ru/api/channels?language_id=2'

    def _get_origins(self):
        for c in self.get_json(self.url)['channels']:
            try:
                yield {
                    'name': c['name'],
                    'link': '%s://%s/channel/%s' % \
                        (self.urlparse(self.url).scheme,
                         self.urlparse(self.url).netloc,
                         c['url']),
                    'logo': '%s://%s/data/channels/%s' % \
                        (self.urlparse(self.url).scheme,
                         self.urlparse(self.url).netloc,
                         c['url'])
                }
            except Exception:
                self.logger.error(self.traceback.format_exc().strip())

    def _get_stream(self, origin):
        html = self.get_html(origin['link'])
        stream = self.research("var m_link = '(.*?)'", html)
        if stream.endswith('flv'): return
        stream = base64.decodestring(stream)
        if 'tvrec' in stream: return
        if 'peers' in stream: return
        return stream
