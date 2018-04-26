
from . import ResourceBase

class Resource(ResourceBase):
    url = 'http://tv-only.org'

    def _get_origins(self):
        soup = self.get_soup(self.url)
        for c in soup.findAll('li', class_='item_tv'):
            try:
                yield {
                    'name': c.find('img').get('alt').replace('смотреть онлайн','').strip(),
                    'link': c.find('a').get('href'),
                    'logo': self.url + c.find('img').get('src'),
                }
            except AttributeError:
                pass
            except Exception:
                self.logger.error(self.traceback.format_exc().strip())

    def _get_stream(self, origin):
        html = self.get_html(origin['link'])
        stream = self.research("var src = \"(.*?)\"", html)
        return stream
