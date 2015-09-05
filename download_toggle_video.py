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

# sample wvm link
#url = "http://video.toggle.sg/en/series/marvel-s-agents-of-s-h-i-e-l-d-yr-2/ep6/327671"

# prints usage information only
def usage():
    print "Run the script as %s toggle_url_1 toggle_url_2 ..." % (sys.argv[0])	

# function takes in a video.toggle.sg URL, and returns a tuple of the direct download URL and the media name
def parseurl(url):

	print "[i] Given Toggle URL = %s" % (url)
	urlsplit = url.split('/')
	mediaID = urlsplit[-1]
	if (debug):
		print "[*] Obtained mediaID = %s" % (mediaID)
	print "[i] Performing HTTP GET request on Toggle URL ..."
	urlresp = urllib2.urlopen(url).read()

	if (debug):
		text_file = open("1.urlresp.txt", "w")
		text_file.write("{}".format(urlresp))
		text_file.close()

	mwembedIndex = urlresp.find("mwEmbed",3500)
	mwembedStr = urlresp[(mwembedIndex-70):(mwembedIndex+60)]
	mwembedValue = re.split('//|">',mwembedStr)[1]
	mwembedValue = "http://"+mwembedValue
	if (debug):
		print "[*] Obtained mwembed URL = %s" % (mwembedValue)

	apiUserIndex = urlresp.find("apiUser",40000)
	apiUserStr = urlresp[apiUserIndex:(apiUserIndex+30)]
	apiUserValue = re.split('"',apiUserStr)[1]
	if (debug):
		print "[*] Obtained apiUser = %s" % (apiUserValue)

	apiPassIndex = urlresp.find("apiPass",40000)
	apiPassStr = urlresp[apiPassIndex:(apiPassIndex+30)]
	apiPassValue = re.split('"',apiPassStr)[1]
	if (debug):
		print "[*] Obtained apiPass = %s" % (apiPassValue)

	print "[i] Performing HTTP GET request on mwembed URL ..."
	mwembedresp = urllib2.urlopen(mwembedValue).read()

	if (debug):
		text_file = open("2.mwembedresp.txt", "w")
		text_file.write("{}".format(mwembedresp))
		text_file.close()

	scriptloaderIndex = mwembedresp.find("SCRIPT_LOADER_URL",100)
	scriptloaderStr = mwembedresp[scriptloaderIndex:(scriptloaderIndex+130)]
	scriptloaderValue = re.split('\'',scriptloaderStr)[2]
	scriptloaderValue = scriptloaderValue[0:-8]
	if (debug):
		print "[*] Obtained Amazon AWS URL (front) = %s" % (scriptloaderValue)

	print "[i] Building download URL ..."
	downloadUrl = scriptloaderValue + "mwEmbedFrame.php?&wid=_27017&uiconf_id=8413350&entry_id=" + mediaID + "&flashvars[proxyData]=%7B%22initObj%22%3A%7B%22Locale%22%3A%7B%22LocaleLanguage%22%3A%22%22%2C%22LocaleCountry%22%3A%22%22%2C%22LocaleDevice%22%3A%22%22%2C%22LocaleUserState%22%3A0%7D%2C%22Platform%22%3A0%2C%22SiteGuid%22%3A0%2C%22DomainID%22%3A%220%22%2C%22UDID%22%3A%22%22%2C%22ApiUser%22%3A%22" + apiUserValue + "%22%2C%22ApiPass%22%3A%22" + apiPassValue + "%22%7D%2C%22MediaID%22%3A%22" + mediaID + "%22%2C%22iMediaID%22%3A%22" + mediaID + "%22%2C%22picSize%22%3A%22640X360%22%7D&callback=mwi_SilverlightContainer0"
	#print "[i] Built download URL = %s" % (downloadUrl)

	print "[i] Performing HTTP GET request on download URL ..."
	downloadresp = urllib2.urlopen(downloadUrl).read()

	if (debug):
		text_file = open("3.downloadresp.txt", "w")
		text_file.write("{}".format(downloadresp))
		text_file.close()

	print "[i] Performing JSON parsing ..."
	jsonFrom = downloadresp.find("kalturaIframePackageData",3000)
	jsonTo = downloadresp.find("isIE8",20000)
	jsonextract = downloadresp[(jsonFrom+27):(jsonTo-13)]
	jsonextract = jsonextract.decode('string_escape')
	jsondata = json.loads(jsonextract)

	if (debug):
		text_file = open("4.jsondata.txt", "w")
		text_file.write("{}".format(json.dumps(jsondata,indent=4)))
		text_file.close()

	print "[i] Obtaining output URLs ...\n"
	urlarray = []
	# location 1 where URLs may be found
	for x in range(0,10):
		outputurl = ""
		try:
			outputurl = jsondata["entryResult"]["contextData"]["flavorAssets"][x]["partnerData"]["url"].replace("\\","")
		except:
			pass
		if (outputurl.endswith("m3u8") or outputurl.endswith("wvm") or outputurl.endswith("mp4")):
			urlarray.append(outputurl)

	# location 2 where URLs may be found		
	for x in range(0,10):
		outputurl = ""
		try:
			outputurl = jsondata["entryResult"]["meta"]["partnerData"]["Files"][x]["URL"].replace("\\","")
		except:
			pass
		if (outputurl.endswith("m3u8") or outputurl.endswith("wvm") or outputurl.endswith("mp4")):
			urlarray.append(outputurl)

	for y in range(1,len(urlarray)+1):
		print "[%s]: %s" % (y,urlarray[y-1])

	print "\n[i] Note that for m3u8 and wvm, STB seems to be highest quality, followed by IPAD, then IPH, then ADD."
	in1 = input('Enter the number to download: ')

	# no error checking here
	selectedurl = urlarray[in1-1]
	print "\n[*] Selected %s" % (selectedurl)

	if (debug):
		text_file = open("5.selected.txt", "a")
		text_file.write("{}".format(selectedurl))
		text_file.write("{}".format("\n"))
		text_file.close()
		
	print "\n[i] Obtaining media name ..."
	medianame = jsondata["entryResult"]["meta"]["name"].replace("  ","_").replace(" ","_")
	try:
		print "[*] Obtained media name = %s" % (medianame.decode('unicode-escape'))
	except:
		medianame = mediaID
		print "[*] Unicode title encountered. New media name = %s" % (medianame)

	if (debug):
		print "[i] Obtaining media duration ..."
		mediaduration = jsondata["entryResult"]["meta"]["duration"]
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
	
	for url in sys.argv[1:]:
		curr += 1
		print "\n\n================================"
		print "[*] Downloading file %i of %i ..." % (curr, total)
		print "================================"
		tmpurl, tmpmedianame = parseurl(url)
		if (autodl):
			download(tmpurl, tmpmedianame)
		else:
			print "[i] Autodownload is disabled"

	return 0

if __name__ == '__main__':
	main()