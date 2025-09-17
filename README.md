## Detect if video has any speech in it or not.

Code determines whether provided video (.mov or any other) has speech it by using [inaSpeechSegmenter](https://github.com/ina-foss/inaSpeechSegmenter).

### Prerequisites

Detect video speech requires ffmpeg for decoding. It can be installed on linux as following:

```bash
$ sudo apt-get install ffmpeg
```


### PIP installation
```bash
# create a python 3 virtual environment and activate it
$ virtualenv -p python3 env
$ source env/bin/activate
# install framework and dependencies
$ pip install -r requirements.txt
```


## Using detect_video_speech
You need to provide either a url or local path:

```bash
python detect_speech 'media/example.mp4'
```

the output is either `1` - if it has a speech, `0` - if not.