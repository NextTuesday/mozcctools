import urllib
import urllib2
import simplejson as json


def get_bug_stats_for_milestone(milestone):
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
    encoded_args = urllib.urlencode(query_args)

    url = 'https://api-dev.bugzilla.mozilla.org/latest/bug/?' + encoded_args
    result_json = urllib2.urlopen(url).read()
    result = json.loads(result_json)
    bugs = result['bugs']

    reporters = {}
    assignees = {}

    for bug in bugs:
        reporter = bug['creator']['name']
        if not reporter in reporters:
            reporters[reporter] = []
        reporters[reporter].append(bug)
        assignee = bug['assigned_to']['name']
        if not assignee in assignees:
            assignees[assignee] = []
        assignees[assignee].append(bug)

    return reporters, assignees

if __name__ == "__main__":
    reporters, assignees = get_bug_stats_for_milestone("mozilla17")
    max_num_reports = 0
    reporter = None
    for k, v in reporters.iteritems():
        if len(v) > max_num_reports:
            max_num_reports = len(v)
            reporter = k
    print "Max reporter:", reporter, max_num_reports
    max_num_assignments = 0
    assignee = None
    for k, v in assignees.iteritems():
        if len(v) > max_num_assignments and k != "nobody@mozilla.org":
            max_num_assignments = len(v)
            assignee = k
    print "Max assignee:", assignee, max_num_assignments
