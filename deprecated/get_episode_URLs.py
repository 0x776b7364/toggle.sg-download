#!/usr/bin/env python
# Written by 0x776b7364

import urllib2
import re
import json
import argparse

# set to 1 for debugging
# note that enabling debugging writes files to disk
debug = 0

# sample episode links
#url = "http://tv.toggle.sg/en/channel8/shows/love-on-the-plate-3/episodes"

VALID_URL = r"http?://tv\.toggle\.sg/(?:en|zh)/.+?/episodes"
CONTENT_NAVIGATION_EXPR = r'10, 0,  (?P<content_id>[0-9]+), (?P<navigation_id>[0-9]+), isCatchup'
EPISODE_TITLE_EXPR = r'<title>([\s\S]*?)</title>'
# dirty regex to extract video URLs and titles
URL_TITLE_EXPR = r'<h4.+?href="([\s\S]*?)">([\s\S]*?)</a>'

# function takes in a tv.toggle.sg episode URL, and returns a list of (video_url,title) tuples
def parseurl(epiurl):

	print "[i] Given Toggle episodes URL = %s" % (epiurl)

	mobj = re.match(VALID_URL, epiurl)
	if not mobj:
		print "[!] Invalid episodes url %s" % (epiurl)
		return None, None

	print "[i] Performing HTTP GET request on Toggle episodes URL ..."
	urlresp = urllib2.urlopen(epiurl).read()
	
	mobj = re.search(CONTENT_NAVIGATION_EXPR, urlresp, flags=re.DOTALL|re.MULTILINE)
	contentid = mobj.group("content_id")
	navigationid = mobj.group("navigation_id")
	
	# i'm sure this can be done more efficiently; i'm lousy with regex ...
	mobj = re.search(EPISODE_TITLE_EXPR, urlresp, flags=re.DOTALL|re.MULTILINE)
	seriestitle = mobj.group(0).decode('unicode_escape').encode('ascii','ignore')
	seriestitle = " ".join(seriestitle.split())
	seriestitle = re.sub(r"\s+", "_", seriestitle[8:-8])
	print "[*] Series name = %s" % (seriestitle)
	
	if (debug):
		print "[*] Obtained content_id = %s" % (contentid)
		print "[*] Obtained navigation_id = %s" % (navigationid)
	
	epilisturl = 'http://tv.toggle.sg/en/blueprint/servlet/toggle/paginate?pageSize=99&pageIndex=0&contentId=' + contentid + '&navigationId=' + navigationid + '&isCatchup=1'
	print "[i] Performing HTTP GET request on Toggle blueprint URL:"
	print epilisturl
	urlresp = urllib2.urlopen(epilisturl).read()

	if (debug):
		text_file = open("1.epilisturl.txt", "w")
		text_file.write("{}".format(urlresp))
		text_file.close()

	print "[i] Parsing bluprint URL output ..."
	mobj = re.findall(URL_TITLE_EXPR, urlresp, flags=re.DOTALL|re.MULTILINE)
	if (debug):
		print mobj
	
	return (seriestitle, mobj)

# function writes the episode URLs and titles to a CSV file
def writeCsv(title, urllist):

	print "[i] Exporting to CSV ..."
	outputfile = title + ".csv"
	text_file = open(outputfile, "w")
	
	# writing a table of URL,title
	for url in urllist:
		line = url[0] + "," + " ".join(url[1].split()) + "\n"
		text_file.write("{}".format(line))
	
	text_file.write("\n")
	
	# writing URLs into a single line for import into download_toggle_video.py
	line = ""
	for url in urllist:
		line = line + url[0] + " "
	
	text_file.write("{}".format(line))
	
	text_file.close()

def main():
	curr = 0
	parser = argparse.ArgumentParser(description='Retrieve Toggle video URLs from episodes pages.',add_help=False)
	parser.add_argument('episode_URL',nargs='+')
	args = parser.parse_args()
	total = len(args.episode_URL)
	
	try:
		for turl in args.episode_URL:
			curr += 1
			print "\n\n================================"
			print "[*] Processing URL %i of %i ..." % (curr, total)
			print "================================"
			seriestitle, urllist = parseurl(turl)
			if not urllist:
				print "[i] Unable to process %s" % (turl)
			else:
				writeCsv(seriestitle, urllist)
	except (KeyboardInterrupt, SystemExit):
		print "\n[i] Bye!"
		sys.exit(0)

	print "[i] Done!"

if __name__ == '__main__':
	main()

