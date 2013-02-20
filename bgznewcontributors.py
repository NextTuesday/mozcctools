# run giving to numbers (start release) and (end release)
# e.g: python bgznewcontributors.py 10 18
# It will dump two files:
#     - new.txt: with a list of all new contributors to the last release with the bugs they fixed
#     - stats.csv: a scv with statistics about each release

import urllib
import urllib2
import simplejson as json
import sys


LINK = '<a href="https://bugzilla.mozilla.org/show_bug.cgi?id=%i">%i</a>'

def get_new_assignees(milestone):
    """
    Return 2 dicts reportes and assignees, with the ids of each reporter/
    assignee as a key and the list of bugs reported/assigned as a value
    """
    query_args = {
        'username': '',  # insert username
        'password': '',  # insert password
        'target_milestone': milestone,
        'resolution': 'FIXED'
        }
    encoded_args = urllib.urlencode(query_args, True)

    url = 'https://api-dev.bugzilla.mozilla.org/latest/bug/?' + encoded_args
    print url
    result_json = urllib2.urlopen(url).read()
    result = json.loads(result_json)
    bugs = result['bugs']

    assignees = {}

    for bug in bugs:
        assignee = bug['assigned_to']
        if 'real_name' in assignee:
            assignee = assignee['real_name'] + "   <" + assignee['name'] + ">"
        else:
            assignee = assignee['name']
        if not assignee == "nobody@mozilla.org":
            if not assignee in assignees:
                assignees[assignee] = []
            assignees[assignee].append(bug)
    return assignees, bugs


if __name__ == "__main__":
    args = sys.argv[1:]
    release_nr = int(args[1])
    start = int(args[0])
    release = {}
    missing = {}
    missing_p = {}
    new = {}
    num_bugs = {}
    comebacks = {}
    bugs = {}
    release[start], bugs[start] = get_new_assignees(["Firefox %i" % (start), "mozilla%i" % (start)])
    all_hackers = set(release[start].keys())
    for i in xrange(start+1, release_nr + 1):
        release[i], bugs[i] = get_new_assignees(["Firefox %i" % (i), "mozilla%i" % (i)])
        missing[i] = set()
        new[i] = {}
        comebacks[i] = set()
        for p in release[i-1]:
            if not p in release[i]:
                missing[i].add(p)
        for p in release[i]:
            if not p in release[i-1]:
                if not p in all_hackers:
                    new[i][p] = [LINK % (bug["id"], bug["id"]) for bug in release[i][p]]
                else:
                    comebacks[i].add(p)
            missing_p[p] = (i, release[i][p])
        all_hackers = all_hackers.union(set(release[i].keys()))

    f = open("new.txt", "w")
    newb = []
    for p in new[release_nr]:
        newb.append(p.encode('utf-8','ignore') + ": " + ", ".join([str(bug) for bug in new[release_nr][p]]))
    f.write("\n".join(newb))
    f.close()

    f = open("stats.csv", "w")
    stats = "Release; Number of Contributors; Missing Contributors; New Contributors; Returning Contributors; Existing Contributors; Number of fixed bugs;\n"
    for i in xrange(start + 1, release_nr + 1):
        stats += "%i;%i;%i;%i;%i;%i;%i\n" % (i, len(release[i]), len(missing[i]), len(new[i]), len(comebacks[i]), len(release[i]) - (len(new[i]) + len(comebacks[i])), len(bugs[i]))
    f.write(stats)
    f.close()

    missing_list = {}
    for p, r in missing_p.iteritems():
        if release_nr - r[0] >= 3:
            line = p + ": " + " Last assigned bug at mozilla release " + str(r[0]) + ". Bugs: " + ", ".join(["#" + str(b["id"]) for b in r[1]]) + "\n"
            if r[0] not in missing_list:
                missing_list[r[0]] = []
            missing_list[r[0]].append(line)
 
    f = open("missing.csv", "w")
    for r, lines in missing_list.iteritems():
        f.write("====================\n" + str(r) + "\n")
        for line in lines:
            try:
                f.write(line)
            except:
                print line
    f.close()
