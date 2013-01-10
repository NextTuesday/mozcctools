import gobject
import sys
import time
from subprocess import Popen, PIPE
from zeitgeist.client import ZeitgeistClient
from zeitgeist.datamodel import Event, Subject, Interpretation, Manifestation

ZG = ZeitgeistClient()

def format_log_entry(log):
    log = log.split("||")
    if len(log) < 5:
        return None
    return {
        "uri": log[0],
        "timestamp": int(log[1].split(".")[0]),
        "actor": log[2],
        "desc": log[3].lower(),
        "files": set(log[4].split(" "))
    }

def get_commits():
    t1 = time.time()
    COMMAND = """hg log --no-merges --template '{node}||{date}||{author|person} <{author|email}>||{desc}||{files}-!-'"""
    p = Popen(COMMAND, shell=True, stdout=PIPE)
    logs = p.communicate()[0].split("-!-")
    print "===> Found %i commits %i in seconds" % (len(logs), time.time() - t1)
    t1 = time.time()
    commits = []
    for log in logs:
        commit = format_log_entry(log)
        commits.append(commit)
    print "===> Formated %i commits in %i seconds" % (len(logs), time.time() - t1)
    return commits

def format_events(commits):
    events = []
    for commit in commits:
        if not commit["desc"].lower().startswith("merge"):
            event = Event()
            event.timestamp = commit["timestamp"] * 1000
            event.actor = commit["actor"]
            event.interpretation = Interpretation.MODIFY_EVENT
            event.manifestation = Manifestation.USER_ACTIVITY
            subj = Subject()
            subj.uri = "dav://%s" % commit["uri"]
            subj.origin = "dav:// " + event.actor
            subj.interpretation = Interpretation.MESSAGE
            subj.manifestation = Manifestation.FILE_DATA_OBJECT.REMOTE_DATA_OBJECT
            subj.text = commit["desc"]
            event.subjects = [subj]
            for f in commit["files"]:
                if f.strip() != "":
                    subj = Subject()
                    subj.uri = "file://" + f
                    subj.interpretation = Interpretation.DOCUMENT
                    subj.manifestation = Manifestation.FILE_DATA_OBJECT.REMOTE_DATA_OBJECT
                    subj.text = f.split("/")[-1]
                    event.subjects.append(subj)
            events.append(event)
    return events

def push_to_zeitgeist(commits):
    commits = commits
    def error_handler(error):
        print "===> ERROR:", error
    def ids_reply_handler(ids):
        global commits
        print len(commits)
        if len(commits) > 0:
            events = format_events(commits[0:100])
            commits = commits[100:]
            time.sleep(0.5)
            ZG.insert_events(events, ids_reply_handler, error_handler)
    events = format_events(commits[0:100])
    commits = commits[100:]
    ZG.insert_events(events, ids_reply_handler, error_handler)

if __name__=="__main__":
    t = time.time()
    mainloop = gobject.MainLoop()
    commits = get_commits()
    print "===> Retrieved %i commits in %i seconds" %(len(commits), time.time() - t)
    push_to_zeitgeist(commits)
    mainloop.run()
