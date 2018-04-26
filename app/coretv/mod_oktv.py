
from . import ResourceBase

class Resource(ResourceBase):
    url = 'http://ok-tv.org'

    def _get_origins(self):
        soup = self.get_soup(self.url)
        for c in soup.findAll('a', class_='bt-image-link'):
            try:
                yield {
                    'name': self.re.sub(
                        '\s+cмотреть\s+онлайн.*', '',
                        c.get('title'), flags=re.I).strip(),
                    'link': self.get_soup(self.url + c.get('href'))\
                                .find('iframe').get('src'),
                    'logo': self.url + c.find('img').get('src'),
                }
            except AttributeError:
                pass
            except Exception:
                self.logger.error(self.traceback.format_exc().strip())

    def _get_stream(self, origin):
        html = self.get_html(origin['link'])
        stream = self.research("file: '(.*?)'", html)
        return stream
