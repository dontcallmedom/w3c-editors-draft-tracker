#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Gathers data on W3C editors draft"""

import json
import subprocess
import os
import sys
import re
import requests
try:
    from collections import OrderedDict
except Exception, e:
    # python < 2.7 doesn't have OrderedDict
    # pip install ordereddict solves this
    from ordereddict import OrderedDict

def writable_dir(string):
    if not os.path.isdir(string):
        raise argparse.ArgumentTypeError("%s does not exist")  %string
    if not os.access(string, os.W_OK):
        raise argparse.ArgumentTypeError("Cannot write to %s")  %string
    if string[-1]=="/":
        string = string[:-1]
    return string

def url(string):
    if string[:7] == "http://" or string[:8] == "https://":
        return string
    else:
        raise argparse.ArgumentTypeError("%s not an URL")  %string

def json_file(string):
    try:
        f = open(string)
    except Exception, e:
        raise argparse.ArgumentTypeError("Failed to open %s: %s" %(string,str(e)))
    try:
        vcsData = json.load(f)
    except Exception, e:
        raise argparse.ArgumentTypeError("Failed to parse %s as JSON: %s" %(string,str(e)))
    return vcsData

def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument("path", metavar="<output_directory>", type=writable_dir, help="Path of the directory where the checkout will be made")
    parser.add_argument("--map","-m", dest="map", default="map-url-to-vcs.json", type=json_file, help="Path of the JSON file mapping editor drafts URL to version control systems")
    group.add_argument("--list", metavar="<uri list>",dest="list", default=None, type=argparse.FileType('r'), help="Path of the text file listing URLs of editors drafts (one per line)")
    group.add_argument("--url", metavar="<url>", dest="filter", type=url, help="URL of the editors draft on which to collected data")
    parser.add_argument("--ghissues", dest="ghissues", help="for an editor draft in a github repo, also collect data on open issues and pull requests", action='store_true')
    return parser.parse_args()

def report_gh_issues(cloneurl):
    issues = get_gh_data(cloneurl, "issues?state=all")
    pulls = get_gh_data(cloneurl, "pulls")

    issues = filter(lambda x: not x.has_key("pull_request"), issues)

    return {"issues":
            { "all": len(issues),
              "open": len(filter(lambda x: x["state"] == "open", issues))
              },
            "pullrequests": len(pulls)
            }

def get_gh_data(cloneurl, datatype):
    url = build_gh_api_url(cloneurl, datatype)
    return fetch_gh_data(url)

def fetch_gh_data(url):
    r = requests.get(url, params={"per_page":100})
    try:
        data = r.json()
    except:
        # old requests module compat
        data = r.json
    if r.links.has_key("next"):
        data = data + fetch_gh_data(r.links["next"]["url"])
    return data

def build_gh_api_url(cloneurl, endpoint):
    return cloneurl.replace("https://github.com", "https://api.github.com/repos") + "/" + endpoint


def print_cvs_log(uri, rule, res, checkout_dir):
    res.write("<log>")
    res.flush()
    dir_name = checkout_dir + "/" + rule["server"]
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)
    with cd(dir_name):
        path = rule["path"]
        subprocess.call(["cvs","-d","%s:%s" %(rule["server"],rule["root"]),"-Q","co",path], stderr=None)
        if path[0:path.rfind('/') + 1]==path:
            path = path + "Overview.html"
        cvslog = subprocess.check_output(["cvs","-d","%s:%s" %(rule["server"],rule["root"]),"log",path])
        for line in cvslog.split("\n"):
            if line.startswith("date: "):
                res.write("<logentry><date>%s</date></logentry>" % line.split(" ")[1])
    res.write("</log>")

def print_hg_log(uri, rule, res, checkout_dir):
    cloneurl = None
    path = rule["path"]
    path = path.replace("/raw-file/default","").replace("/raw-file/tip","")
    if rule.has_key("file") and (len(path)==0 or path[-1]=="/"):
        path = path + rule["file"]
    if rule.has_key("clone"):
        cloneurl = rule["clone"]
        repo = cloneurl[cloneurl.rfind("/"):]
    elif rule.has_key("server"):
        repo = path[0:path.find("/",1)]
        cloneurl = rule["server"] + repo
        path = path[len(repo) + 1:]
    print "Cloning repo %s from %s for %s" % (repo, cloneurl, path)
    if cloneurl == None:
        raise LookupError("No git clone URL for %s" % uri)

    dir_name = checkout_dir + "/" + cloneurl.split("/")[2] + "/"
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    with cd(dir_name):
        # clone if dir not exist, pull otherwise
        if not os.path.isdir(dir_name + repo):
            subprocess.call(["hg","clone",cloneurl])
        else:
            with cd(dir_name + repo):
                subprocess.call(["hg","pull"],stderr=None)
        with cd(dir_name + repo):
            subprocess.call(["hg","log","--style=xml",path],stdout=res)

def print_git_log(uri, rule, res, checkout_dir, ghissues):
    cloneurl = None
    path = rule["path"]
    if rule.has_key("clone"):
        cloneurl = rule["clone"]
        repo = cloneurl[cloneurl.rfind("/"):]
    elif rule.has_key("server"):
        repo = path[0:path.find("/",1)]
        cloneurl = rule["server"] + repo
        path = path[len(repo) + 1:]
    if rule.has_key("file") and (len(path) == 0 or path[-1]=="/"):
        path = path + rule["file"]
    branch = "master"
    if rule.has_key("branch"):
        branch = rule["branch"]
    print "Cloning repo %s from %s for %s" % (repo, cloneurl, path)
    if cloneurl == None:
        raise LookupError("No git clone URL for %s" % uri)

    dir_name = checkout_dir + "/" + cloneurl.split("/")[2] + "/"
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)
    #collecting data on github repos
    gh_data = None
    if ghissues and cloneurl.startswith("https://github.com"):
        gh_data = report_gh_issues(cloneurl)
    res.write("<log>")
    if gh_data:
        res.write("<issues><open>%d</open><all>%d</all></issues>" % (gh_data["issues"]["open"], gh_data["issues"]["all"]))
        res.write("<pullrequests>%d</pullrequests>" % (gh_data["pullrequests"]))
    res.flush()
    with cd(dir_name):
        # clone if dir not exist, pull otherwise
        if not os.path.isdir(dir_name + repo):
            subprocess.call(["git","clone",cloneurl])
        with cd(dir_name + repo):
            subprocess.call(["git","fetch","origin",branch])
            subprocess.call(["git","log","--pretty=format:<logentry><date>%ci</date></logentry>","origin/%s" % branch,path], stdout=res)
        res.write("</log>")


# from http://stackoverflow.com/questions/431684/how-do-i-cd-in-python
class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def process_uris(args):
    urisFile = args.list
    checkout_dir = args.path
    vcsData = args.map
    vcsData = OrderedDict(sorted(vcsData.iteritems(), key=lambda x: -len(x[0])))

    uri_cleaner = re.compile(r"[^a-z0-9]")
    for l in urisFile:
        found = False
        uri = l.strip()
        name = uri_cleaner.sub("", "".join(uri.split(":")[1:]).split("#")[0])
        res = open("data/%s.xml" % name,"w")
        for uriprefix,rule in vcsData.iteritems():
            if uri.startswith(uriprefix):
                found = True
                if not rule.has_key("path"):
                    rule["path"] = uri.replace(uriprefix,"").split("#")[0]

                if rule["vcs"]=="cvs":
                    print_cvs_log(uri, rule, res, checkout_dir)
                elif rule["vcs"]=="hg":
                    print_hg_log(uri, rule, res, checkout_dir)
                elif rule["vcs"]=="git":
                    print_git_log(uri, rule, res, checkout_dir, args.ghissues)
            if found:
                break
        if not found:
            print "No match for %s" % uri

if __name__ == "__main__":
    args = parse_arguments()
    if args.list:
        # we don't load github issues for lists of specs
        # to avoid rate limit issues
        args.ghissues = False
    else:
        args.list = [args.filter]
    process_uris(args)
