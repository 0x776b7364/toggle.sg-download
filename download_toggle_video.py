#!/usr/bin/env python
# Written by 0x776b7364

import urllib2
import re
import json
import os
import time
import sys

# set to 1 for debugging
# note that enabling debugging writes files to disk
debug = 0

# set to 1 for auto-download (less interactive)
autodl = 1

# sample (m3u8 and mp4) links
#url = "http://video.toggle.sg/en/series/sabo/ep12/327339"
#url = "http://video.toggle.sg/en/series/118-catch-up/ep126/328542"
#url = "http://video.toggle.sg/zh/series/118-catch-up/webisodes/document/330134"
#url = "http://video.toggle.sg/en/tv-show/news/nov-2015-singapore-today-6/sun-8-nov-2015/348183"

# sample wvm link
#url = "http://video.toggle.sg/en/series/marvel-s-agents-of-s-h-i-e-l-d-yr-2/ep6/327671"

VALID_URL = r"https?://video\.toggle\.sg/(?:en|zh)/(?:series|clips|movies|tv-show)/.+?/(?P<id>[0-9]+)"
API_USER_PASS_EXPR = r'apiUser:\s*"(?P<user>[^"]+?)".+?apiPass:\s*"(?P<password>[^"]+?)"'

# prints usage information only
def usage():
	print "Run the script as %s toggle_url_1 toggle_url_2 ..." % (sys.argv[0])  

# function takes in a video.toggle.sg URL, and returns a tuple of the direct download URL and the media name
def parseurl(url):

	print "[i] Given Toggle URL = %s" % (url)

	mobj = re.match(VALID_URL, url)
	if not mobj:
		print "[!] Invalid url %s" % (url)
		return None, None
	mediaID = mobj.group('id')
	if (debug):
		print "[*] Obtained mediaID = %s" % (mediaID)
	print "[i] Performing HTTP GET request on Toggle URL ..."
	urlresp = urllib2.urlopen(url).read()

	if (debug):
		text_file = open("1.urlresp.txt", "w")
		text_file.write("{}".format(urlresp))
		text_file.close()

	mobj = re.search(API_USER_PASS_EXPR, urlresp, flags=re.DOTALL|re.MULTILINE)
	if not mobj:
		print "[!] Unable to obtain api user / password"
		return None, None

	apiUserValue = mobj.group("user")
	apiPassValue = mobj.group('password')
	if (debug):
		print "[*] Obtained apiUser = %s" % (apiUserValue)
		print "[*] Obtained apiPass = %s" % (apiPassValue)

	params = {
		"initObj": {
			"Locale": {
				"LocaleLanguage": "", "LocaleCountry": "",
				"LocaleDevice": "", "LocaleUserState": 0
			},
			"Platform": 0, "SiteGuid": 0, "DomainID": "0", "UDID": "",
			"ApiUser": apiUserValue, "ApiPass": apiPassValue
		},
		"MediaID": mediaID,
		"mediaType": 0,
	}
	
	print "[i] Performing HTTP GET request on download URL ..."
	req = urllib2.Request(
		"http://tvpapi.as.tvinci.com/v2_9/gateways/jsonpostgw.aspx?m=GetMediaInfo",
		json.dumps(params).encode("utf-8"))
	jsonResp = urllib2.urlopen(req).read()

	if (debug):
		text_file = open("2.jsonresp.txt", "w")
		text_file.write("{}".format(jsonResp))
		text_file.close()

	print "[i] Performing JSON parsing ..."
	jsondata = json.loads(jsonResp)
	
	if (debug):
		text_file = open("3.jsondata.txt", "w")
		text_file.write("{}".format(json.dumps(jsondata,indent=4)))
		text_file.close()

	print "[i] Obtaining output URLs ...\n"
	urlarray = []
	for fileInfo in jsondata.get('Files', []):
		outputurl = fileInfo.get('URL')
		for ext in ["m3u8", "wvm", "mp4"]:
			if outputurl.endswith(ext):
				urlarray.append(outputurl)

	for y in range(1,len(urlarray)+1):
		print "[%s]: %s" % (y,urlarray[y-1])

	print "\n[i] Note that for m3u8 and wvm, STB seems to be highest quality, followed by IPAD, then IPH, then ADD."
	in1 = input('Enter the number to download: ')

	# no error checking here
	selectedurl = urlarray[in1-1]
	print "\n[*] Selected %s" % (selectedurl)

	if (debug):
		text_file = open("4.selected.txt", "a")
		text_file.write("{}".format(selectedurl))
		text_file.write("{}".format("\n"))
		text_file.close()
		
	print "\n[i] Obtaining media name ..."
	medianame = re.sub(r"\s+", "_", jsondata.get("MediaName", "UNKNOWN"))
	try:
		print "[*] Obtained media name = %s" % (medianame.decode('unicode-escape'))
	except:
		medianame = mediaID
		print "[*] Unicode title encountered. New media name = %s" % (medianame)

	if (debug):
		print "[i] Obtaining media duration ..."
		mediaduration = jsondata.get("Duration") or 0
		print "[*] Obtained media duration = %s" % (time.strftime("%H hrs %M mins %S secs", time.gmtime(float(mediaduration))))
		
	return (selectedurl, medianame)

# function takes in a URL and a save-target name, and performs the download
def download(selectedurl, medianame):
	if (selectedurl.endswith("m3u8")):
		print "[i] Crafting ffmpeg command ..."
		cmd = 'ffmpeg -i ' + selectedurl + " -c copy -bsf:a aac_adtstoasc \"" + medianame + ".mp4\""
		print "------------------------------------------------------------"
		print "[*] Executing the following command: "
		print cmd
		raw_input('\nPress <ENTER> to continue')

		print "[i] Executing ffmpeg command ...\n"
		dlrtn = os.system(cmd)
		
		if (dlrtn == 0):
			print "\n[*] " + medianame +".mp4 file created!"
		else:
			print "\n[!] Error: ffmpeg file not found, or existing file is for incorrect architecture." 

	if (selectedurl.endswith("mp4") or selectedurl.endswith("wvm")):
		#http://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python
		file_name = selectedurl.split('/')[-1]
		u = urllib2.urlopen(selectedurl)
		f = open(file_name, 'wb')
		meta = u.info()
		file_size = int(meta.getheaders("Content-Length")[0])
		print "Downloading: %s Bytes: %s" % (file_name, file_size)

		file_size_dl = 0
		block_sz = 8192
		while True:
			buffer = u.read(block_sz)
			if not buffer:
				break

			file_size_dl += len(buffer)
			f.write(buffer)
			status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
			status = status + chr(8)*(len(status)+1)
			print status,

		f.close()
		
def main():
	curr = 0
	total = len(sys.argv) - 1

	if len(sys.argv) == 1:
		usage()
		exit(0)
	
	try:
		for url in sys.argv[1:]:
			curr += 1
			print "\n\n================================"
			print "[*] Downloading file %i of %i ..." % (curr, total)
			print "================================"
			tmpurl, tmpmedianame = parseurl(url)
			if not tmpurl:
				print "[i] Unable to process %s" % (url)
			elif (autodl):
				download(tmpurl, tmpmedianame)
			else:
				print "[i] Autodownload is disabled"

		return 0
	except (KeyboardInterrupt, SystemExit):
		print "\n[i] Bye!"
		sys.exit(0)

if __name__ == '__main__':
	main()
