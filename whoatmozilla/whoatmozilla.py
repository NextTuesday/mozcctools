from zeitgeist.client import ZeitgeistClient
from zeitgeist.datamodel import *
 
zeitgeist = ZeitgeistClient()
index = zeitgeist._iface.get_extension('Index', 'index/activity')
 
query            = 'nsDocShell.cpp' # search query
time_range       = TimeRange.always()
event_templates  = []
offset           = 0
num_events       = 100
result_type      =  ResultType.MostPopularActor # magic number for "relevancy" (ResultType.* also work)
 
def on_reply(events, num_estimated_matches):
    print 'Got %d out of ~%d results.' % (len(events), num_estimated_matches)
    events = map(Event, events)
    for event in events:
        print ' - %s' % event.actor
 
def on_error(exception):
    print 'Error from FTS:', exception
 
index.Search(query, time_range, event_templates,
             offset, num_events, result_type,
             reply_handler=on_reply, error_handler=on_error)
 
# Start a mainloop
from gi.repository import GLib
GLib.MainLoop().run()
