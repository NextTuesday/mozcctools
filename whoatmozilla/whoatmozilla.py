from os.path import expanduser
from zeitgeist.datamodel import *

import dbus
import sqlite3
import sys
import time

QUERY = """SELECT actor_uri FROM event_view 
WHERE subj_text_id IN (SELECT id FROM text where VALUE = "%s")
ORDER BY timestamp  DESC LIMIT 200"""

bus = dbus.SessionBus()
obj = bus.get_object('org.gnome.zeitgeist.SimpleIndexer',
                      '/org/gnome/zeitgeist/index/activity')
index = dbus.Interface(obj, dbus_interface='org.gnome.zeitgeist.Index')

def search(query):
    t = time.time()
    path = expanduser('~/.local/share/zeitgeist/activity.sqlite')
    con = sqlite3.connect(path)
    cur = con.cursor()

    def query_file(query):
        print "==> Looking for File"
        results = []
        cur.execute(QUERY % query)
        data = cur.fetchall()
        actor_hash = {}
        for d in data:
            d = d[0]
            if d not in actor_hash:
                actor_hash[d] = 0
            actor_hash[d] += 1
            x = [(k, v) for v, k in actor_hash.iteritems()]
            x.sort(reverse=True)
            results = (s[1] for s in x[:10])
        return results

    results = query_file(query)
    con.close() 
    if not results:
        print "==> Looking for Keyword"
        events, num_estimated_matches, matches = index.SearchWithRelevancies(query, TimeRange.always(), [], 2, 0, 200, 0)
        events = map(Event, events)
        id_hash = {}
        actor_hash = {}
        if len(events) > 0:
            for event in events:
                id_hash[event.id] = event
                if event.actor not in actor_hash:
                    actor_hash[event.actor] = 0
                actor_hash[event.actor] += 1
            x = [(k, v) for v, k in actor_hash.iteritems()]
            x.sort(reverse=True)
            results = (s[1] for s in x[:10])
    print time.time() - t
    return results

if __name__=="__main__":
    contacts = search('IPC')
    for c in contacts:
        print "-", c
