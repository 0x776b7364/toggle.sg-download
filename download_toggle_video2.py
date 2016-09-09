#!/usr/bin/env python
# Written by 0x776b7364

import re
import json
import os
import time
import sys
import argparse
import threading
import random

try:
	import Queue
except ImportError:
	import queue as Queue

try:
	import urllib2 as urllib_request
except ImportError:
	import urllib.request as urllib_request

########## START USER CONFIGURATION ##########
	
# set to 1 for debugging
# note that enabling debugging writes files to disk
DEBUG = 0

# set to 1 for auto-download (less interactive)
# for videos, this would auto-select the best quality file
# for episodes, this would auto-select all episodes in the series
AUTO_DOWNLOAD = 1

# set to 1 for script to check and download video subtitles, if present
CHECK_AND_DOWNLOAD_SUBTITLES = 1

# set the number of download threads here
NO_OF_DOWNLOAD_THREADS = 2

# preferred order of file formats to download
# highest preference is first
# in some cases, mp4 is the only downloadable file even though
#   m3u8 is in the URL list
FILE_PREFERENCES = 	[(1,'STB','m3u8'),	# generally 720p, Set-top Box, requires ffmpeg
					(2,'ADD','mp4'),	# generally 540p, Android device
					(3,'IPAD','m3u8'),	# generally 540p, iPad, requires ffmpeg
					(4,'IPH','m3u8')]	# generally 360p, iPhone, requires ffmpeg

# only download direct-accessible files i.e. ignore streaming files
#FILE_PREFERENCES =	[(1,,'ADD','mp4')]

########## END USER CONFIGURATION ##########

# sample (m3u8 and mp4) links
#url = "http://video.toggle.sg/en/series/sabo/ep12/327339"
#url = "http://video.toggle.sg/en/series/118-catch-up/ep126/328542"
#url = "http://video.toggle.sg/zh/series/118-catch-up/webisodes/document/330134"
#url = "http://video.toggle.sg/en/series/double-bonus/ep23/279063"

# sample wvm link
#url = "http://video.toggle.sg/en/series/marvel-s-agents-of-s-h-i-e-l-d-yr-2/ep6/327671"

# sample episode link
#url = "http://tv.toggle.sg/en/channel8/shows/love-on-the-plate-3/episodes"

# regex
VALID_VIDEO_URL = r"https?://video\.toggle\.sg/(?:en|zh)/(?:series|clips|movies|tv-show)/.+?/(?P<id>[0-9]+)"
API_USER_PASS_EXPR = r'apiUser:\s*"(?P<user>[^"]+?)".+?apiPass:\s*"(?P<password>[^"]+?)"'
VALID_EPISODES_URL = r"http?://tv\.toggle\.sg/(?:en|zh)/.+?/episodes"
CONTENT_NAVIGATION_EXPR = r'10, 0,  (?P<content_id>[0-9]+), (?P<navigation_id>[0-9]+), isCatchup'
EPISODE_TITLE_EXPR = r'<title>([\s\S]*?)</title>'
URL_TITLE_EXPR = r'<h4.+?href="([\s\S]*?)">([\s\S]*?)</a>'
FORMAT_EXPR = r'(?:STB|IPH|IPAD|ADD)'

URL_CATEGORY = ['t_video','t_episodes']

MAIN_DOWNLOAD_QUEUE = Queue.Queue()

# Page: http://www.blog.pythonlibrary.org/2012/08/01/python-concurrency-an-example-of-a-queue/
# Author: Mike Driscoll
class Downloader(threading.Thread):

	def __init__(self, queue, debug = False):
		threading.Thread.__init__(self,name = os.urandom(4).encode('hex'))
		self.queue = queue
		self.debug = debug

	def download_file(self, record):
		
		name = record[0]
		url = record[1]
		
		if (url.endswith("m3u8")):
			print("[i] Crafting ffmpeg command ...")
			ffmpeg_download_cmd = 'ffmpeg -i ' + url + " -c copy -bsf:a aac_adtstoasc \"" + name + ".mp4\""

			print("[i] Executing ffmpeg command ...\n")
			try:
				download_return_val = os.system(ffmpeg_download_cmd)
			except (KeyboardInterrupt, SystemExit):
				print("\n[i] Received KeyboardInterrupt. Quitting ...")
				sys.exit(0)
			
			if (download_return_val == 0):
				print("\n[*] " + name +".mp4 file created!")
			else:
				print("\n[!] Error: ffmpeg file not found, or existing file is for incorrect architecture, or download was interrupted prematurely.")

		if (url.endswith("mp4") or url.endswith("wvm") or url.endswith("srt")):
			# Page: http://stackoverflow.com/questions/22676/how-do-i-download-a-file-over-http-using-python
			# Author: PabloG
			file_name = url.split('/')[-1]
			u = urllib_request.urlopen(url)
			f = open(file_name, 'wb')
			meta = u.info()
			file_size = int(meta.getheaders("Content-Length")[0])
			print("Downloading: %s Bytes: %s" % (file_name, file_size))

			file_size_dl = 0
			block_sz = 8192
			print("Thread\t\tDownloaded\tPercentage")
			print("-------------------------------")
			while True:
				buffer = u.read(block_sz)
				if not buffer:
					break

				file_size_dl += len(buffer)
				f.write(buffer)
				if (random.randint(-100,100) == 0):
					status = r"%s	%10d	[%3.2f%%]" % (self.name, file_size_dl, file_size_dl * 100. / file_size)
					status = status + chr(8)*(len(status)+1)
					print(status)
			f.close()

		print("[i] Thread %s completed download!" % (self.name))
		
	def run(self):
		while True:
			record = self.queue.get()
			print("[i] Thread %s: processing URL %s\n" % (self.name, record[1]))
			self.download_file(record)
			self.queue.task_done()
			
def print_script_header():
	print("\n=====================================")
	print("Toggle video and episodes downloader")
	print("by 0x776b7364")
	print("=====================================")

def process_url(url):
	"""
	Returns a list of translated URLs to be enqueued and downloaded
	"""
	input_url_category = get_url_category(url)
			
	if input_url_category == 't_video':
		return process_video_url(url)
	elif input_url_category == 't_episodes':
		return process_episodes_url(url)
	else:
		print("[!] Error: %s is not a valid URL" % (url))
		return []

def get_url_category(url):
	"""
	Returns the matching URL_CATEGORY of 'url'
	"""
	if re.match(VALID_VIDEO_URL, url):
		return URL_CATEGORY[0]
	elif re.match(VALID_EPISODES_URL, url):
		return URL_CATEGORY[1]
	else:
		return None

def process_video_url(t_video_url):
	"""
	Returns a list of translated URLs from a video URL, else returns
	None if errors are encountered
	"""
	
	queued_urls = []
	
	print("\n[i] Toggle video %s detected" % (t_video_url))
	
	mediaID = re.match(VALID_VIDEO_URL, t_video_url).group('id')
	print("[i] Obtained mediaID = %s" % (mediaID))
	
	print("[i] Performing HTTP GET request on Toggle video URL ...")
	t_video_url_resp = urllib_request.urlopen(t_video_url).read()
	
	if (DEBUG):
		text_file = open("v1.t_video_url_resp.txt", "w")
		text_file.write("{}".format(t_video_url_resp))
		text_file.close()
		
	apiUserPassRegex = re.search(API_USER_PASS_EXPR, t_video_url_resp, flags=re.DOTALL|re.MULTILINE)
	if apiUserPassRegex:
		apiUserValue = apiUserPassRegex.group("user").decode("utf-8")
		apiPassValue = apiUserPassRegex.group('password').decode("utf-8")
		print("[i] Obtained apiUser = %s" % (apiUserValue))
		print("[i] Obtained apiPass = %s" % (apiPassValue))
	else:
		print("[!] Unable to obtain api user / password")
		return None

	download_url_params = {
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
	
	print("[i] Performing HTTP GET request on download URL ...")
	download_url_req_url = "http://tvpapi.as.tvinci.com/v2_9/gateways/jsonpostgw.aspx?m=GetMediaInfo"
	download_url_req_params = json.dumps(download_url_params).encode("utf-8")
	download_url_resp = urllib_request.urlopen(download_url_req_url, download_url_req_params).read()
	
	if (DEBUG):
		text_file = open("v2.download_url_resp.txt", "w")
		text_file.write("{}".format(download_url_resp))
		text_file.close()

	print("[i] Performing JSON parsing ...")
	download_url_resp_json = json.loads(download_url_resp)
	
	if (DEBUG):
		text_file = open("v3.download_url_resp_json.txt", "w")
		text_file.write("{}".format(json.dumps(download_url_resp_json,indent=4)))
		text_file.close()

	print("\n[i] Obtaining media name ...")
	medianame = re.sub(r"\s+", "_", download_url_resp_json.get("MediaName", "UNKNOWN"))
	medianame = re.sub('[^a-zA-Z0-9-]', '_', medianame)
	try:
		print("[i] Obtained media name = %s" % (medianame.decode('unicode-escape')))
	except UnicodeEncodeError:
		medianame = mediaID
		print("[i] Unicode title encountered. New media name = %s" % (medianame))

	print("[i] Obtaining URL records from download URL response ...\n")
	temp_urlList = []
	for fileInfo in download_url_resp_json.get('Files', []):
		urlRecord = fileInfo.get('URL')
		for ext in ["m3u8", "wvm", "mp4"]:
			if urlRecord.startswith('http') and urlRecord.endswith(ext):
				fileformat = re.findall(FORMAT_EXPR, urlRecord, flags=re.DOTALL|re.MULTILINE)
				if fileformat:
					temp_urlList.append((medianame+"_"+fileformat[0],urlRecord))

	# the auto-download function chooses only one URL based on the ranking in FILE_PREFERENCES
	if (AUTO_DOWNLOAD):
		temp_queue1 = Queue.Queue()
		
		for priority,quality,format in FILE_PREFERENCES:
			for url in temp_urlList:
				if re.search(quality, url[1]) and re.search(format, url[1]):
					temp_queue1.put(url)
					if (DEBUG):
						print("[i] Inserted into temporary queue: %s" % (url[1]))

		if temp_queue1.empty():
			print("[!] No files selected based on FILE_PREFERENCES")
			print("[i] Consider relaxing preference criteria, or setting AUTO_DOWNLOAD to 0\n")
		else:
			autoSelectedUrl = temp_queue1.get()			
			queued_urls.append(autoSelectedUrl)
			print("\n[i] Auto-selected URL: %s" % (autoSelectedUrl[1]))
	else:
		print("[i] Entering video selection function ...\n")
		queued_urls = user_select_options(temp_urlList)

	if (DEBUG):
		print("[i] Obtaining media duration ...")
		mediaduration = download_url_resp_json.get("Duration") or 0
		print("[i] Obtained media duration = %s" % (time.strftime("%H hrs %M mins %S secs", time.gmtime(float(mediaduration)))))
	
	if (CHECK_AND_DOWNLOAD_SUBTITLES):
		print("[i] Performing HTTP GET request to check for subtitles ...")
		subtitle_link = "http://sub.toggle.sg:8080/toggle_api/v1.0/apiService/getSubtitleFilesForMedia?mediaId=" + mediaID 
		subtitle_link_resp = urllib_request.urlopen(subtitle_link).read()
		print("[i] Performing JSON parsing ...")
		subtitle_link_resp_json = json.loads(subtitle_link_resp)
		if not subtitle_link_resp_json.get('subtitleFiles', []):
			print("[!] No subtitles found!")
		for sfile in subtitle_link_resp_json.get('subtitleFiles', []):
			print("[i] Found " + sfile.get('subtitleFileLanguage') + " subtitles! Adding to queue list ...")
			queued_urls.append(("Subtitles for "+mediaID,sfile.get('subtitleFileUrl')))

	return queued_urls

def process_episodes_url(t_episodes_url):
	"""
	Returns a list of translated URLs from an episodes URL, else returns
	None if errors are encountered
	"""
	
	queued_urls = []
	
	print("\n[i] Toggle episodes %s detected" % (t_episodes_url))
	
	print("[i] Performing HTTP GET request on Toggle episodes URL ...")
	t_episodes_url_resp = urllib_request.urlopen(t_episodes_url).read()
	
	contentNavigationRegex = re.search(CONTENT_NAVIGATION_EXPR, t_episodes_url_resp, flags=re.DOTALL|re.MULTILINE)
	contentid = contentNavigationRegex.group("content_id")
	navigationid = contentNavigationRegex.group("navigation_id")
	
	if (DEBUG):
		print("[*] Obtained content_id = %s" % (contentid))
		print("[*] Obtained navigation_id = %s" % (navigationid))
	
	if not (contentid or navigationid):
		return None
	
	# quick and dirty regex
	episodeTitleRegex = re.search(EPISODE_TITLE_EXPR, t_episodes_url_resp, flags=re.DOTALL|re.MULTILINE)
	seriesTitle = episodeTitleRegex.group(0).decode('unicode_escape').encode('ascii','ignore')
	seriesTitle = " ".join(seriesTitle.split())
	seriesTitle = re.sub(r"\s+", "_", seriesTitle[8:-8])
	print("[*] Series title = %s" % (seriesTitle))
	
	episodeListUrl = 'http://tv.toggle.sg/en/blueprint/servlet/toggle/paginate?pageSize=99&pageIndex=0&contentId=' + contentid + '&navigationId=' + navigationid + '&isCatchup=1'
	print("[i] Performing HTTP GET request on Toggle blueprint URL:")
	print(episodeListUrl)
	episodeListResp = urllib_request.urlopen(episodeListUrl).read()

	if (DEBUG):
		text_file = open("e1.episodeListUrl.txt", "w")
		text_file.write("{}".format(episodeListResp))
		text_file.close()

	print("[i] Parsing blueprint URL output ...")
	urlTitleRegex = re.findall(URL_TITLE_EXPR, episodeListResp, flags=re.DOTALL|re.MULTILINE)
	
	episodes_list = []
	for record in reversed(urlTitleRegex):
		episodes_list.append((" ".join(record[1].split()),record[0]))
	
	# the auto-download function chooses all episodes in the series
	if (AUTO_DOWNLOAD):
		print("[i] Auto-selecting all episodes ...")
		episodes_list_selected = episodes_list
	else:
		print("[i] Entering episode selection function ...\n")
		episodes_list_selected = user_select_options(episodes_list)
	
	print("\n[i] Processing selected episodes ...")
	for episode in episodes_list_selected:
		for record in process_video_url(episode[1]):
			queued_urls.append(record)
		
	print("[i] Completed episodes processing!")
	return queued_urls

def user_select_options(recordsList):
	"""
	Returns a list of user-selected names and URLs from 'recordsList'
	recordsList is a list of (title,url) tuples
	"""
	user_selected_records = []
	
	for cnt in range(1,len(recordsList)+1):
		print("[%s]: %s" % (cnt,recordsList[cnt-1][0]))

	is_invalid_selection = True
	while (is_invalid_selection):
		user_selection_input_list = list(set(raw_input('\nEnter selection (delimit multiple selections with space, 0 to select all): ').split()))
		
		for selection in user_selection_input_list:
			try:
				if int(selection) > len(recordsList) or int(selection) < 0:
					raise ValueError
				if int(selection) == 0:
					user_selected_records = []
					user_selected_records = recordsList
				else:
					user_selected_records.append(recordsList[int(selection)-1])
				is_invalid_selection = False
			except ValueError:
				print("[!] Invalid value: %s" % (selection))
				continue

	if user_selected_records:
		print("\n[*] Selected URL(s):")
		for record in user_selected_records:
			print(record[1])

		if (DEBUG):
			text_file = open("s1.selected_records.txt", "a")
			for selection in user_selection_input_list:
				try:
					text_file.write("{}".format(recordsList[int(selection)-1]))
					text_file.write("{}".format("\n"))
				except (ValueError, IndexError):
					continue
			text_file.close()
		
	return user_selected_records

def main():
	currParam = 0
	parser = argparse.ArgumentParser(description='Download Toggle videos.',add_help=True)
	parser.add_argument('URL',nargs='+',help="Toggle video or episodes URL")
	args = parser.parse_args()
	totalParams = len(args.URL)
	
	print_script_header()
	
	try:
		for input_url in args.URL:
			currParam += 1
			print("\n================================")
			print("[*] Processing input %i of %i ..." % (currParam, totalParams))
			print("================================")
			
			records_to_enqueue = process_url(input_url)
			if records_to_enqueue:
				for record in records_to_enqueue:
					MAIN_DOWNLOAD_QUEUE.put(record)
			else:
				print("[!] Nothing to download for %s" % (input_url))
			
		if  MAIN_DOWNLOAD_QUEUE.empty():
			print("[!] No files in queue. Quitting ...")
			sys.exit(0)		
		
		print("\n[i] Starting download of queued URLs ...\n")
		for i in range(NO_OF_DOWNLOAD_THREADS):
			t = Downloader(MAIN_DOWNLOAD_QUEUE, DEBUG)
			t.setDaemon(True)
			t.start()
			
		MAIN_DOWNLOAD_QUEUE.join()
	
	except (KeyboardInterrupt, SystemExit):
		print("\n[i] Received KeyboardInterrupt. Quitting ...")
		sys.exit(0)
	
	print("[i] Done!")
	
if __name__ == '__main__':
	main()
