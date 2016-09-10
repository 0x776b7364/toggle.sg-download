Python script to download mp4/m3u8/wvm files from toggle.sg.

This new and updated program:
- supports selection of the file quality to download
- supports 'episode' or 'series' URLs
- supports selection of episodes from a series
- implements a more correct 'auto-download' function that is fully non-interactive post-command
- supports multi-threaded downloads
- has some modifications made in preparation for Python 3 (but is not fully supported on that version yet)

# Usage
On Linux and Mac OS X, first make the script executable:

`chmod +x download_toggle_video2.py`

Then run the script with as many Toggle URLs as you want:

`./download_toggle_video2.py http://video.toggle.sg/blah http://video.toggle.sg/blerk ...`

Or, you can include 'episode' URLs as such:

`./download_toggle_video2.py http://video.toggle.sg/blah http://tv.toggle.sg/en/channel8/shows/blerk/episodes ...`

On Windows, if you installed Python from the official binaries, you should already have the necessary file associations, so the following command line should work from the script directory:

`download_toggle_video2.py http://video.toggle.sg/blah http://video.toggle.sg/blerk ...`

Debug mode can be enabled with the ```-d``` parameter like so:

`./download_toggle_video2.py -d http://video.toggle.sg/blah`

Tested with:
- Python v2.7.6 on Windows 7 x64
- Python v2.7.11 on Windows 7 x64
- Python v2.7.11 on Windows 10 10586.104 x64
- Python v2.7.12 on Xubuntu 16.04 x64

# Configuration Options

The following configuration options are directly editable in the script file:
## AUTO_DOWNLOAD
Default: 0 (do not auto-download)

Set to 1 to enable auto-download of media files. The order of file formats in FILE_PREFERENCES can also be changed if you prefer ADD-mp4 to be of a higher priority than STB-m3u8.
## CHECK_AND_DOWNLOAD_SUBTITLES
Default: 1 (enable)

Pretty self-explanatory.
## NO_OF_DOWNLOAD_THREADS
Default: 2

Specifies the number of download threads. More threads = quicker download completion.
## FILE_PREFERENCES
Default: Highest to lowest priority: STB-ADD-IPAD-IPH

Specifies the download file format preference, in order.

# ffmpeg Dependency Notes
## Windows
ffmpeg.exe must be located in the same folder as the python script. Script has been tested against ffmpeg.exe in https://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-20150418-git-edbb9b5-win64-static.7z. Recent builds in Windows x64 can be found in https://ffmpeg.zeranoe.com/builds/win64/static/

## Linux
On Ubuntu 12.04, the version of libav-tools in the repo is not updated for m3u8; hence, you'll need to build ffmpeg from source from git://source.ffmpeg.org/ffmpeg.git

Ubuntu 15.04 has a sufficiently recent libav-tools in the stock repository.

## Mac OS X
Install ffmpeg from [Homebrew](http://brew.sh/).

Note: there are many hardcoded values used, which could cause the script to break if Toggle changes their page structure
