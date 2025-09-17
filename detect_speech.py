import subprocess
import argparse, os, urllib
import tempfile
from inaSpeechSegmenter import Segmenter

def get_temp_file_name():
    cid = os.getpid()
    f = "{}.wav".format(cid)
    return os.path.join(tempfile.gettempdir(), f)

def ensure_wav(input_path):
    unescaped = urllib.parse.unquote(input_path, encoding='utf-8', errors='replace')
    wav_path = get_temp_file_name()
    subprocess.run([
        "ffmpeg", "-y", "-i", unescaped, "-ss", "10", "-t", "60", "-ac", "1", "-ar", "16000", wav_path
    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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
    has_speech, segment = has_speech_inaspeech(args.input_media,
                                                min_seconds=args.min_seconds,
                                                batch_size=args.batch_size,
                                                start_sec=args.start_sec,
                                                stop_sec=args.stop_sec
                                                )
    return bool(has_speech)

if __name__ == "__main__":
    result = main()
    print("1" if result else "0")

