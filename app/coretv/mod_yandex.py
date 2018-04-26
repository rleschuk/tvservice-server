
from . import ResourceBase

class Resource(ResourceBase):
    url = 'https://www.yandex.ru/portal/tvstream_json/channels?locale=ru&from=morda'
    epgurl = 'https://m.tv.yandex.ru/ajax/i-tv-region/get?'

    def _get_origins(self):
        data = self.get_json(self.url)
        for c in data.get('set',[]):
            try:
                yield {
                    'name': c.get('title'),
                    'link': c.get('content_url'),
                    'logo': 'http:%s' % c.get('logo') if c.get('logo') else ''
                }
            except Exception:
                self.logger.error(self.traceback.format_exc().strip())

    def _get_stream(self, origin):
        for orig in self._get_origins():
            if orig['name'] == origin['name']:
                return orig['link']

    def _get_epg(self):
        now = self.now_datetime
        ncrd = int(self.now_timestamp) * 1000 + 1080
        j = self.get_json(self.epgurl, params={
            'resource': 'schedule',
            'userRegion': 193,
            'params': self.json.dumps({'channelLimit': 1})
        })
        channelIds = sorted(j['availableChannelsIds'])
        channelLimit = 20
        for n in range(0, int(len(channelIds)/channelLimit) + 1):
            j = self.get_json(self.epgurl, params={
                "params": self.json.dumps({
                    "channelLimit": channelLimit,
                    "channelIds": channelIds[n * channelLimit : n * channelLimit + channelLimit],
                    "start": now.strftime('%Y-%m-%d') + "T03:00:00+03:00",
                    "duration": 96400,
                    "channelProgramsLimit": 500,
                    "lang": "ru"
                }),
                "userRegion": 193,
                "resource": "schedule",
                "ncrd": ncrd
            })
            for c in j['schedules']:
                self.logger.debug('#########: %r', c['channel']['title'])
                yield {
                    'name': c['channel']['title'],
                    'items': self._get_epg_items(c['events'])
                }

    def _get_epg_items(self, item):
        for p in item:
            title = p['program']['title']
            date_start = self.datetime.datetime.strptime(p['start'][:-6], '%Y-%m-%dT%H:%M:%S')
            #date_stop = self.datetime.datetime.strptime(p['finish'][:-6], '%Y-%m-%dT%H:%M:%S')
            category = p['program'].get('type', {}).get('name', '')
            description = p['program'].get('description', '')

            arts = []
            for img in p.get('program', {}).get('images', []):
                size = [i for i in img.get('sizes', {}).keys() if int(i) > 300]
                if size: arts.append('http:%s' % img['sizes'][size[-1]]['src'])

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
