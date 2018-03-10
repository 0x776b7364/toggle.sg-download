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

*note: going forward I will only be testing the script on Linux and OSX. Sorry, Windows users. The script should still work as expected though.*

# Configuration Options

The following configuration option is directly editable in the script file:
## FILE_PREFERENCES
Default: Highest to lowest priority: STB-ADD-IPAD-IPH

Specifies the download file format preference, in order.


For other options, run ``` download_toggle_video2.py -h```.

# ffmpeg Dependency Notes
## Windows
ffmpeg.exe must be located in the same folder as the Python script. Recent builds in Windows x64 can be found in https://ffmpeg.zeranoe.com/builds/win64/static/ .

## Linux
On Ubuntu 12.04, the version of libav-tools in the repo is not updated for m3u8; hence, you'll need to build ffmpeg from source from git://source.ffmpeg.org/ffmpeg.git

Ubuntu 15.04+ has a sufficiently recent libav-tools in the stock repository.

## Mac OS X
Install ffmpeg from [Homebrew](https://brew.sh/).

```shell
$ brew install ffmpeg
```

Note: there are many hardcoded values used, which could cause the script to break if Toggle changes their page structure

# Reporting issues

Before reporting an issue, please make sure that your issue is still present with the latest copy of the script.

If the issue still persists, please run the script with the `-d` debug flag, like so:
```shell
$ ./download_toggle_video2.py -d http://video.toggle.sg/blah
```

The output should be pasted into either the issue form field, or into a Pastebin-like site, and the particular paste referenced in the issue.

To really make my day, provide the contents of the debug files by uploading them to said Pastebin-like site, and reference them in the issue as well. These files are automatically-created when the debug flag is present:
- v1.t_video_url_resp.txt
- v2.download_url_resp.txt
- v3.download_url_resp_json.txt
- s1.selected_records.txt
- e1.episodeListUrl.txt (only if input contains an episode URL)

Also, please try to describe the issue in more detail especially in the title. Titles like "cannot work" or "cannot download anything" are not very useful (because.. you wouldn't be posting an issue if it was working).

# Acknowledgements

This script would not be possible without the various contributors, and the people out there who submit bug reports. In particular, I'd like to thank:
- @ping
- @gromgit
- @freemanang1989
- @JackeJR
- @peterhoeg

# Other

I'm aware that the ```youtube-dl``` project (https://github.com/rg3/youtube-dl/) has support for Toggle links. Consider using their program if my script does not work for you.
