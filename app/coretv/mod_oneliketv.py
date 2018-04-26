import re
from . import ResourceBase

class Resource(ResourceBase):
    url = 'http://onelike.tv'

    def _get_origins(self):
        soup = self.get_soup(self.url)
        for c in soup.findAll('a', target='_blank', href=re.compile('\/\S+\.html')):
            try:
                soup = self.get_soup(self.url + c.get('href'))
                name = self.research('^(.*?) смотреть онлайн', soup.title.string)
                yield {
                    'name': name,
                    'link': soup.find('iframe').get('src'),
                    'logo': self.url + soup.find('img', title=name).get('src'),
                }
            except AttributeError:
                pass
            except Exception:
                self.logger.error(self.traceback.format_exc().strip())

    def _get_stream(self, origin):
        html = self.get_html(origin['link'])
        stream = self.research("file: '(.*?)'", html)
        if not stream: stream = self.research("file=(.*?m3u8)", html)
        return stream
