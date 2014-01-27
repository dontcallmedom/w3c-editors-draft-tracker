Running getEdDraftActivity.py (use --help for details) will gather data as XML files in the data directory about the dates at which commits have been made in W3C editors drafts.

The mapping between the URL of an editor draft and the version control systems it is maintained in is defined in the JSON file map-url-to-vcs.json.

getEdDraftActivity.py can be used on a single url, or on a file with a series of URLs (one per line).

Examples:
```bash
# fetch data on all documents listed in the file
python getEdDraftActivity.py --map map-url-to-vcs.json --list editor-drafts /tmp

# fetch data for CSS Background editors draft
python getEdDraftActivity.py --map map-url-to-vcs.json --url https://dvcs.w3.org/hg/csswg /tmp

The XML files can be turned into SVG representation of the activity using the XSLT style sheet build-spec-activity.xsl:
```bash
 saxon data/devw3orgcsswgcssbackgrounds.xml build-spec-activity.xsl
```

