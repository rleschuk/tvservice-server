
from . import ResourceBase

class Resource(ResourceBase):
    url = 'http://only-tv.org'

    def _get_origins(self):
        soup = self.get_soup(self.url)
        for c in soup.findAll('div', class_='popimageslider-item'):
            try:
                link = c.find('a').get('href')
                if link.startswith('/'):
                    link = self.url + c.find('a').get('href')
                soup = self.get_soup(link)
                link = soup.find('iframe', src=self.re.compile('.*php$')).get('src')
                yield {
                    'name': c.find('img').get('alt'),
                    'link': link,
                    'logo': self.url + c.find('img').get('src'),
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
