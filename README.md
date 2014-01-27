Running getEdDraftActivity.py (use --help for details) will gather data as XML files in the data directory about the dates at which commits have been made in a series of URLs pointing to W3C editors drafts.

The mapping between the URLs of these drafts and the version control systems they are maintained in is defined in the JSON file map-url-to-vcs.json.

The list of editors draft is to be provided in a text format whose lines looks like:
http://dev.w3.org/2006/webapi/FileAPI/|filereader
where the part after the "|" is the name that will be used to create the data file. The XSLT style sheet extract-editors-draft.xsl gets such a list from the [Standards for Web Applications on Mobile](http://www.w3.org/Mobile/mobile-web-app-state/) document.

Examples:
```bash
# fetch data on all documents listed in the list
python getEdDraftActivity.py --map map-url-to-vcs.json --list editor-drafts /tmp all

# fetch data for the spec whose alias is serviceworker
python getEdDraftActivity.py --map map-url-to-vcs.json --list editor-drafts /tmp serviceworker


The XML files can be turned into SVG representation of the activity using the XSLT style sheet build-spec-activity.xsl:
```bash
 saxon data/filereader.xml build-spec-activity.xsl
```

