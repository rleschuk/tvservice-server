
from . import ResourceBase


class Resource(ResourceBase):
    url = ''
    epgurl = 'http://new.s-tv.ru/tv/'

    def _get_epg(self):
        for d in self.date_ranges(1):
            soup = self.get_soup(
                '%s-/%s/' % (self.epgurl, d.strftime("%Y-%m-%d")),
                cookies = self.cookie
            )
            for c in soup.findAll('table', class_='item_table'):
                name = c.find('td', class_='channel').find('img').get('alt')
                self.logger.debug('#########: %r', name)
                yield {
                    'name': name,
                    'items': self._get_epg_items(c.findAll('div', class_='prg_item'), d)
                }

    def _get_epg_items(self, item, date):
        priv = None
        for i in item:

            h, m = i.find('span', class_='prg_item_time').string.split('.')
            if priv is not None and int(h) < priv:
                date = date + self.datetime.timedelta(days=1)
            priv = int(h)

            date_start = date.replace(hour=int(h), minute=int(m), second=0)
            title = category = description = arts = ''

            prg_item = i.find('a')
            if not prg_item:
                prg_item = i.find('span', class_='prg_item_no')
                title = prg_item.getText()
            else:
                title = prg_item.getText()
                href = prg_item.get('href')
                ab, an, pab, pan = (0,0,0,0)
                m = self.re.search('^#(ab|an|pab|pan)(\d+)$', href)
                if m and m.group(1) == 'ab': ab = m.group(2)
                if m and m.group(1) == 'an': an = m.group(2)
                if m and m.group(1) == 'pab': pab = m.group(2)
                if m and m.group(1) == 'pan': pan = m.group(2)
                if ab or an:
                    try:
                        info_soup = self.get_soup('%sajaxinfo/%s/%s/%s/%s' % \
                            (self.epgurl, ab, an, pab, pan))
                        desc_soup = info_soup.find('div', class_='ajax-info-desc').find('p')
                        if desc_soup:
                            description = desc_soup.getText('\n')
                        h3_soup = info_soup.find('h3')
                        if h3_soup:
                            title = h3_soup.string
                            h4_soup = info_soup.find('h4')
                            if h4_soup:
                                description = '%s\n%s' % (h4_soup.string, description)
                        arts_soup = info_soup.findAll('img', src=self.re.compile('^http'))
                        if arts_soup:
                            arts = [i.get('src') for i in arts_soup]
                        details_soup = info_soup.find('div', class_='ajax-info-people')
                        if details_soup:
                            cat_soup = details_soup.find('p', class_='type')
                            if cat_soup: category = cat_soup.string
                            r = self.re.search(r'Жанр:\n(.*?)\n', details_soup.getText('\n'))
                            if category and r:
                                category = '%s/%s' % (cat, r.group(1))
                            elif r:
                                category = r.group(1)
                    except Exception as e:
                        pass

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
