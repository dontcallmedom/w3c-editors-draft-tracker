import json
import subprocess
import os

urisFile = open("editor-drafts")

mapFile = open("map-url-to-vcs.json")
vcsData = json.load(mapFile)

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
    res = open(name,"w")
    for uriprefix,rule in vcsData.iteritems():
        if uri.startswith(uriprefix):
            found = True
            if rule["vcs"]=="cvs":
                with cd("/home/dom/dev.w3.org"):
                    path = uri.replace(uriprefix,"")
                    subprocess.call(["cvs","-d","%s:%s" %(rule["server"],rule["root"]),"co",path])
                    if path[0:path.rfind('/') + 1]==path:
                        path = path + "Overview.html"
                    subprocess.call(["cvs","-d","%s:%s" %(rule["server"],rule["root"]),"log",path],stdout=res)
            elif rule["vcs"]=="hg":
                pass
            elif rule["vcs"]=="git":
                pass
        if found:
            break
    if not found:
        print "No match for %s" % uri
