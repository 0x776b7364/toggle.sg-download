Python script to download mp4/m3u8/wvm files from toggle.sg.

# Usage
On Linux and Mac OS X, first make the script executable:

`chmod +x download_toggle_video.py`

Then run the script with as many Toggle URLs as you want:

`./download_toggle_video.py http://video.toggle.sg/blah http://video.toggle.sg/blerk ...`

On Windows, if you installed Python from the official binaries, you should already have the necessary file associations, so the following command line should work from the script directory:

`download_toggle_video.py http://video.toggle.sg/blah http://video.toggle.sg/blerk ...`

Tested with:
- Python v2.7.8 on Windows 7 x86
- Python v2.7.6 on Windows 7 x64
- Python v2.7.3 on Ubuntu 12.04 x86 (caveats apply; see below)
- Python v2.7.9 on Ubuntu 15.04 x86
- Python v2.7.5 on Mac OS X Mavericks

# Installation Notes
## Windows
ffmpeg.exe must be located in the same folder as the python script. Script has been tested against ffmpeg.exe in http://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-20150418-git-edbb9b5-win64-static.7z. Recent builds in Windows x64 can be found in http://ffmpeg.zeranoe.com/builds/win64/static/

## Linux
On Ubuntu 12.04, the version of libav-tools in the repo is not updated for m3u8; hence, you'll need to build ffmpeg from source from git://source.ffmpeg.org/ffmpeg.git

Ubuntu 15.04 has a sufficiently recent libav-tools in the stock repository.

## Mac OS X
Install ffpmeg from [Homebrew](http://brew.sh/).

Note: there are many hardcoded values used, which could cause the script to break if Toggle changes their page structure
