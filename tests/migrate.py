import json
import sqlite3
from pprint import pprint

dbf = '/opt/production/tvserver/resources/database.db'
JSON = {}

with sqlite3.connect(dbf, timeout=20) as conn:
    conn.row_factory = lambda c, r: dict([(col[0], r[idx]) for idx, col in enumerate(c.description)])
    rows = conn.cursor().execute('''
        select
        g.title as group_title,
        g.disabled as group_disabled,
        c.name as channel_name,
        c.cnt as channel_cnt,
        c.ch_disabled as channel_disabled,
        co.title as name,
        co.resource,
        co.link,
        co.cost,
        co.disabled
        from channels_orig co
        inner join channels_names cn on co.hash = cn.channel_hash
        inner join channels_groups cg on co.hash = cg.channel_hash
        inner join groups g on cg.group_title = g.title
        inner join channels c on c.hash = cn.hash
        order by c.name, co.cost''').fetchall()
    for row in rows:
        if row['group_title'].capitalize() not in JSON:
            JSON[row['group_title'].capitalize()] = {
                'name': row['group_title'].capitalize(),
                'disable': row['group_disabled'],
                '_channels': {}
            }
        if row['channel_name'] not in JSON[row['group_title'].capitalize()]['_channels']:
            JSON[row['group_title'].capitalize()]['_channels'][row['channel_name']] = {
                'name': row['channel_name'],
                'disable': True if (row['channel_disabled'] >= row['channel_cnt']) else False,
                '_origins': []
            }
        JSON[row['group_title'].capitalize()]['_channels'][row['channel_name']]['_origins'].append({
            'resource': 'mod_%s' % row['resource'][:-3],
            'name': row['name'],
            'link': row['link'],
            'cost': row['cost'],
            'disable': True if row['disabled'] in [1,2] else False,
            'deleted': True if row['disabled'] == 3 else False
        })

with open('deploy/db.json', 'w') as f:
    json.dump(JSON, f, indent=4, ensure_ascii=False)
