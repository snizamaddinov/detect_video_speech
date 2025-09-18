import argparse
import os
import sys
import tempfile
import urllib.parse
import urllib.request
import ffmpeg
import subprocess
from inaSpeechSegmenter import Segmenter

def get_temp_file_name():
    cid = os.getpid()
    f = "{}.wav".format(cid)
    return os.path.join(tempfile.gettempdir(), f)

def url_status_code(url, timeout=10):
    req = urllib.request.Request(url, method='HEAD')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.getcode()
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        req = urllib.request.Request(url, headers={'Range': 'bytes=0-0'})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.getcode()
        except urllib.error.HTTPError as e:
            return e.code
        except Exception:
            return None

def has_audio_stream(url):
    try:
        info = ffmpeg.probe(url)
    except ffmpeg.Error as e:
        stderr = e.stderr.decode('utf-8', errors='replace') if isinstance(e.stderr, (bytes, bytearray)) else (e.stderr or "")
        if "404" in stderr or "Not Found" in stderr:
            return "404"
        return None

    streams = info.get("streams", []) if isinstance(info, dict) else []
    for s in streams:
        if s.get("codec_type") == "audio":
            return True
    return False

def ensure_wav(input_path):
    unescaped = urllib.parse.unquote(input_path, encoding='utf-8', errors='replace')
    wav_path = get_temp_file_name()
    stream = ffmpeg.input(unescaped)
    audio = stream.audio
    out = ffmpeg.output(audio, wav_path, ss=10, t=60, ac=1, ar=16000).overwrite_output()
    try:
        out.run(capture_stdout=True, capture_stderr=True)
    except ffmpeg.Error as e:
        stdout = e.stdout.decode('utf-8', errors='replace') if isinstance(e.stdout, (bytes, bytearray)) else (e.stdout or "")
        stderr = e.stderr.decode('utf-8', errors='replace') if isinstance(e.stderr, (bytes, bytearray)) else (e.stderr or "")
        rc = getattr(e, "returncode", 1)
        raise subprocess.CalledProcessError(rc, "ffmpeg", output=stdout, stderr=stderr)
    return wav_path, True

def total_speech_seconds(segments):
    s = 0.0
    for label, start, end in segments:
        if label == "speech":
            s += end - start
    return s

def has_speech_inaspeech(input_media, min_seconds=1.5, batch_size=256, start_sec=0, stop_sec=60):
    wav, tmp_created = ensure_wav(input_media)
    seg = Segmenter(detect_gender=False, batch_size=batch_size)
    segments = seg(wav, start_sec=start_sec, stop_sec=stop_sec)
    speech_sec = total_speech_seconds(segments)
    decision = speech_sec >= min_seconds
    if tmp_created:
        try:
            os.remove(wav)
        except:
            pass
    return decision, segments

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_media")
    parser.add_argument("--min-seconds", type=float, default=10.0)
    parser.add_argument("--batch_size", type=int, default=256)
    parser.add_argument("--start_sec", type=int, default=0)
    parser.add_argument("--stop_sec", type=int, default=60)
    args = parser.parse_args()

    input_url = args.input_media
    code = url_status_code(input_url)
    if code == 404:
        print("-1")
        return -1

    audio_check = has_audio_stream(input_url)
    if audio_check == "404":
        print("-1")
        return -1
    if audio_check is False:
        print("0")
        return 0

    try:
        has_speech, segments = has_speech_inaspeech(
            input_url,
            min_seconds=args.min_seconds,
            batch_size=args.batch_size,
            start_sec=args.start_sec,
            stop_sec=args.stop_sec
        )
    except subprocess.CalledProcessError as e:
        stderr = getattr(e, "stderr", "")
        if isinstance(stderr, bytes):
            try:
                stderr = stderr.decode("utf-8", errors="replace")
            except:
                stderr = str(stderr)
        if "404" in stderr or "Not Found" in stderr:
            print("-1")
            return -1
        if "Output file does not contain any stream" in stderr or "does not contain any stream" in stderr:
            print("0")
            return 0
        print("ERROR", file=sys.stderr)
        return 2
    except Exception:
        print("ERROR", file=sys.stderr)
        return 2

    print("1" if has_speech else "0")
    return 1 if has_speech else 0

if __name__ == "__main__":
    main()
