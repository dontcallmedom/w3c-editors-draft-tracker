#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Gathers data on W3C editors draft"""

import json
import subprocess
import os
import sys

def writable_dir(string):
    if not os.path.isdir(string):
        raise argparse.ArgumentTypeError("%s does not exist")  %string
    if not os.access(string, os.W_OK):
        raise argparse.ArgumentTypeError("Cannot write to %s")  %string
    if string[-1]=="/":
        string = string[:-1]
    return string

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

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("path", metavar="<path>", type=writable_dir, help="Path of the directory where the checkout will be made")
parser.add_argument("filter", metavar="name", default=None, help="Restrict data gathering to the spec matched by the said name (see list)")
parser.add_argument("--map","-m", dest="map", default="map-url-to-vcs.json", type=json_file, help="Path of the JSON file mapping editor drafts URL to version control systems")
parser.add_argument("--list","-l", dest="list", default="editor-drafts", type=argparse.FileType('r'), help="Path of the text file listing |-separated URLs of editors drafts and their shortnames")

args = parser.parse_args()
urisFile = args.list
vcsData = args.map
checkout_dir = args.path
filter = args.filter


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


for l in urisFile:
    found = False 
    uri,name = l.strip().split("|")
    res = open("data/%s.xml" % name,"w")
    if filter!=None and filter!=name:
        continue
    for uriprefix,rule in vcsData.iteritems():
        if uri.startswith(uriprefix):
            found = True
            if rule["vcs"]=="cvs":
                res.write("<log>")
                res.flush()
                dir_name = checkout_dir + "/" + rule["server"]
                if not os.path.isdir(dir_name):
                    os.mkdir(dir_name)
                with cd(dir_name):
                    path = uri.replace(uriprefix,"").split("#")[0]
                    subprocess.call(["cvs","-d","%s:%s" %(rule["server"],rule["root"]),"-Q","co",path], stderr=None)
                    if path[0:path.rfind('/') + 1]==path:
                        path = path + "Overview.html"
                    cvslog = subprocess.check_output(["cvs","-d","%s:%s" %(rule["server"],rule["root"]),"log",path])
                    for line in cvslog.split("\n"):
                        if line.startswith("date: "):
                            res.write("<logentry><date>%s</date></logentry>" % line.split(" ")[1])
                res.write("</log>")                                          
            elif rule["vcs"]=="hg":
                cloneurl = None
                if rule.has_key("path"):
                    path = rule["path"]
                else:
                    path = uri.replace(uriprefix,"").split("#")[0]
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
                    print "No HG clone URL for %s" % uri
                    break

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
            elif rule["vcs"]=="git":

                cloneurl = None
                if rule.has_key("path"):
                    path = rule["path"]
                else:
                    path = uri.replace(uriprefix,"").split("#")[0]
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
                    print "No git clone URL for %s" % uri
                    break

                dir_name = checkout_dir + "/" + cloneurl.split("/")[2] + "/"
                if not os.path.isdir(dir_name):
                    os.mkdir(dir_name)
                res.write("<log>")
                res.flush()
                with cd(dir_name):
                    # clone if dir not exist, pull otherwise
                    if not os.path.isdir(dir_name + repo):
                        subprocess.call(["git","clone",cloneurl])
                    with cd(dir_name + repo):
                        subprocess.call(["git","fetch","origin",branch])
                        subprocess.call(["git","log","--pretty=format:<logentry><date>%ci</date></logentry>","origin/%s" % branch,path], stdout=res)
                    res.write("</log>")
        if found:
            break
    if not found:
        print "No match for %s" % uri
