from os.path import expanduser
from zeitgeist.datamodel import *

import dbus
import sqlite3
import sys
import time

QUERY = """SELECT actor_uri, subj_uri FROM event_view WHERE id IN (SELECT id FROM event_view
WHERE subj_text_id IN (SELECT id FROM text where VALUE = "%s")
AND subj_interpretation IN (SELECT id FROM interpretation WHERE value = "http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#Document"))
ORDER BY timestamp DESC LIMIT 1000"""


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
        uri_hash = {}
        for d in data:
            u = str(d[1])
            d = d[0]
            if d not in actor_hash:
                actor_hash[d] = 0
            actor_hash[d] += 1
            if u.startswith("file://"):
                u = u.replace("file://", "")
                if u not in uri_hash:
                    uri_hash[u] = 0
                uri_hash[u] += 1
        x = [(k, v) for v, k in actor_hash.iteritems()]
        x.sort(reverse=True)
        results = []
        for s in x[:10]:
            results.append(s[1])
        y = [(k, v) for v, k in uri_hash.iteritems()]
        y.sort(reverse=True)
        results2 = []
        for s in y[:10]:
            results2.append(s[1])
        return results, results2, "Files"

    results, results2, qtype = query_file(query)
    con.close() 
    if not results:
        print "==> Looking for Keyword"
        events, num_estimated_matches, matches = index.SearchWithRelevancies(query, TimeRange.always(), [], 2, 0, 200, 0)
        events = map(Event, events)
        id_hash = {}
        actor_hash = {}
        uri_hash = {}
        if len(events) > 0:
            for event in events:
                id_hash[event.id] = event
                if event.actor not in actor_hash:
                    actor_hash[event.actor] = 0
                actor_hash[event.actor] += 1
                for subject in event.subjects:
                    if subject.uri.startswith("file://"):
                        u = subject.uri.replace("file://", "")
                        if u not in uri_hash:
                            uri_hash[u] = 0
                        uri_hash[u] += 1
            x = [(k, v) for v, k in actor_hash.iteritems()]
            x.sort(reverse=True)
            results = (s[1] for s in x[:10])
            y = [(k, v) for v, k in uri_hash.iteritems()]
            y.sort(reverse=True)
            results2 = (s[1] for s in y[:10])
            qtype = "Keyword"
    print time.time() - t
    return results, results2, qtype

if __name__=="__main__":
    contacts, files, t = search('nsXPConnect.cpp')
    print "---"
    for c in contacts:
        print c
    print "---"
    for f in files:
        print f
