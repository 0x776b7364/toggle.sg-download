Python script to download mp4/m3u8/wvm files from toggle.sg. Paste your video URL as the 'url' parameter.

Tested with:
[X] Python v2.7.8 on Windows 7 x86
[X] Python v2.7.6 on Windows 7 x64
[X] Python v2.7.3 on Ubuntu 12.04 x86 (caveats apply; see below)

WINDOWS:
ffmpeg.exe must be located in the same folder as the python script
script has been tested against ffmpeg.exe in http://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-20150418-git-edbb9b5-win64-static.7z
recent builds in Windows x64 can be found in http://ffmpeg.zeranoe.com/builds/win64/static/

LINUX:
On Ubuntu 12.04, the version of libav-tools in the repo is not updated for m3u8; hence, you'll need to build ffmpeg from source from git://source.ffmpeg.org/ffmpeg.git

Note: there are many hardcoded values used, which could cause the script to break if Toggle changes their page structure
