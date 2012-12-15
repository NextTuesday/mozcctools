# Run in hg repo of mozilla-release

import simplejson as json
import sys
from subprocess import Popen, PIPE

COMMAND = "hg log -r 'ancestor(%s,%s)::%s' --template '{author|email} '"


def get_commit_stats_for_tags(tags):
    """
    Returns a dict with counts of commits per author
    """
    info = {"num_commits": {}}
    for i in xrange(len(tags) - 1):
        p = Popen(COMMAND % (tags[i], tags[i + 1], tags[i + 1]),
                    shell=True, stdout=PIPE)
        log = p.communicate()[0].split(" ")
        info[tags[i + 1]] = {"num_commits": len(log),
                            "num_authors": len(set(c for c in log))}
        for a in log:
            if not a in info["num_commits"]:
                info["num_commits"][a] = dict((k, 0) for k in tags[1:])
            info["num_commits"][a][tags[i + 1]] += 1
    return info

if __name__ == "__main__":
    tags = sys.argv[1:]
    info = get_commit_stats_for_tags(tags)
    print json.dumps(info, sort_keys=True, indent=4, separators=(',', ': '))
