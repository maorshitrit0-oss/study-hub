"""Media steps: download a Zoom recording, snapshot the slides/board, transcribe Hebrew audio."""
import os
import re
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
LOCAL_MODEL = "ivrit-ai/whisper-large-v3-turbo-ct2"  # Whisper fine-tuned for Hebrew
NO_WINDOW = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


def fmt_time(sec):
    sec = int(sec)
    return f"{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def run_ffmpeg(args):
    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", *args],
                   check=True, creationflags=NO_WINDOW)


def duration(path):
    """Length of a media file in seconds (0 if unknown)."""
    p = subprocess.run([FFMPEG, "-hide_banner", "-i", str(path)],
                       capture_output=True, text=True, errors="ignore", creationflags=NO_WINDOW)
    m = re.search(r"Duration: (\d+):(\d+):(\d+)", p.stderr)
    return int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3]) if m else 0


def has_audio(path):
    p = subprocess.run([FFMPEG, "-hide_banner", "-i", str(path)],
                       capture_output=True, text=True, errors="ignore", creationflags=NO_WINDOW)
    return "Audio:" in p.stderr


# ---------- 1. download ----------

def youtube_cookies():
    """YouTube refuses GitHub's servers without a signed-in session: cookies.txt from the YT_COOKIES secret."""
    text = os.environ.get("YT_COOKIES", "").strip()
    if not text:
        return {}
    path = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "yt_cookies.txt"
    path.write_text(text + "\n", encoding="utf-8")
    return {"cookiefile": str(path)}


def download(url, work_dir, log=print):
    import yt_dlp

    def fetch(fmt, name):
        opts = {
            **youtube_cookies(),
            "format": fmt,
            "outtmpl": str(work_dir / f"{name}.%(ext)s"),
            "ffmpeg_location": FFMPEG,
            "quiet": True,
            "noprogress": True,
            "retries": 10,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return Path(ydl.prepare_filename(info)), info

    # Prefer the screen-share stream: slides/board in full resolution, no camera overlay.
    log("מוריד את ההקלטה (זה יכול לקחת כמה דקות)...")
    # YouTube's single-file formats stop at 360p (unreadable board): take video + audio and merge them.
    youtube = re.search(r"youtube\.com/|youtu\.be/", url)
    video, info = fetch("bv*[height<=1080]+ba/b" if youtube else "share/view_with_share/view/b", "video")
    audio = video
    if not has_audio(video):
        log("לזרם שיתוף המסך אין אודיו - מוריד גם את זרם המצלמה בשביל הקול...")
        audio, _ = fetch("view_with_share/view/b", "audio_src")
    return video, audio, info.get("title") or "lecture"


# ---------- 2. transcription ----------

def transcribe_local(audio, log=print):
    from faster_whisper import WhisperModel

    log(f"טוען מודל תמלול עברית ({LOCAL_MODEL}). בפעם הראשונה הוא יורד (~1.6GB)...")
    model = WhisperModel(LOCAL_MODEL, device="cpu", compute_type="int8",
                         cpu_threads=os.cpu_count() or 4)
    # Decode with our own ffmpeg: faster-whisper's PyAV loader breaks on newer PyAV releases.
    pcm = subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-i", str(audio), "-vn",
                          "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True, creationflags=NO_WINDOW).stdout
    samples = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
    segments, info = model.transcribe(samples, language="he", beam_size=1,
                                      vad_filter=True, condition_on_previous_text=False)
    out, last_pct = [], -10
    for s in segments:
        out.append((s.start, s.end, s.text.strip()))
        pct = int(100 * s.end / max(info.duration, 1))
        if pct >= last_pct + 5:
            log(f"מתמלל... {pct}%  ({fmt_time(s.end)} מתוך {fmt_time(info.duration)})")
            last_pct = pct
    return out


# ---------- 3. slide detection ----------

def detect_slides(video, sensitivity=0.5, interval=2.0, min_gap=8.0, log=print):
    """Return [(start, end)] of visually stable scenes (slides / board states)."""
    w, h = 320, 180
    frame_size = w * h
    # Fraction of pixels that must change to count as a new slide (higher sensitivity -> lower bar).
    thr = 0.05 - 0.04 * sensitivity
    proc = subprocess.Popen(
        [FFMPEG, "-hide_banner", "-loglevel", "error", "-i", str(video),
         "-vf", f"fps=1/{interval},scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
        stdout=subprocess.PIPE, creationflags=NO_WINDOW)

    scenes, ref, ref_t, t = [], None, 0.0, 0.0
    i = 0
    while True:
        buf = proc.stdout.read(frame_size)
        if len(buf) < frame_size:
            break
        t = i * interval
        i += 1
        frame = np.frombuffer(buf, np.uint8).astype(np.int16)
        if ref is None:
            ref, ref_t = frame, t
            continue
        changed = (np.abs(frame - ref) > 30).mean()
        if changed > thr and t - ref_t >= min_gap:
            scenes.append((ref_t, t - interval))
            ref, ref_t = frame, t
        if i % 300 == 0:
            log(f"מזהה שקפים... {fmt_time(t)}")
    proc.wait()
    scenes.append((ref_t, t))

    # Handwritten boards (pan/zoom/scroll) trigger constantly. Cap at ~1 snapshot per minute by
    # folding the shortest scene into the next one; the later frame usually has more writing on it.
    max_slides = max(20, min(90, int(t / 60)))
    while len(scenes) > max_slides:
        i = min(range(len(scenes) - 1), key=lambda k: scenes[k][1] - scenes[k][0])
        scenes[i + 1] = (scenes[i][0], scenes[i + 1][1])
        del scenes[i]
    return scenes


def save_slides(video, scenes, out_dir):
    slide_dir = out_dir / "slides"
    slide_dir.mkdir(exist_ok=True)
    paths = []
    for n, (start, end) in enumerate(scenes, 1):
        # Snapshot at the end of the scene: the board / slide is in its most complete state.
        p = slide_dir / f"slide_{n:03d}.webp"
        run_ffmpeg(["-ss", f"{end:.2f}", "-i", str(video), "-frames:v", "1",
                    "-vf", "scale='min(1280,iw)':-2", "-c:v", "libwebp", "-quality", "70", str(p)])
        if p.exists():
            paths.append((n, start, p))
    return paths


# ---------- Google Drive files (recordings and PDFs from the department Drive) ----------

VIDEO_EXT = {".mp4", ".mkv", ".mov", ".webm", ".m4a", ".mp3", ".wav", ".m4v"}
MIME = {".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".webp": "image/webp", ".txt": "text/plain", ".md": "text/plain"}


def is_drive(url):
    return "drive.google.com" in url or "docs.google.com" in url


def is_video(path):
    return Path(path).suffix.lower() in VIDEO_EXT


def mime_of(path):
    return MIME.get(Path(path).suffix.lower(), "application/pdf")


def download_drive(url, work_dir, log=print):
    """Download a shared Drive file ('anyone with the link'). Google Docs are exported as PDF."""
    import gdown

    log("מוריד מהדרייב...")
    m = re.search(r"/d/([-\w]{20,})", url) or re.search(r"[?&]id=([-\w]{20,})", url)
    if not m:
        raise RuntimeError("זה לא קישור לקובץ בדרייב (צריך קישור לקובץ, לא לתיקייה)")
    file_id = m.group(1)
    if "docs.google.com/document" in url or "docs.google.com/presentation" in url:
        kind = "document" if "/document/" in url else "presentation"
        url = f"https://docs.google.com/{kind}/d/{file_id}/export?format=pdf"
        out = gdown.download(url, str(Path(work_dir) / "drive.pdf"), quiet=True)
    else:
        out = gdown.download(id=file_id, output=str(Path(work_dir)) + "/", quiet=True)
    if not out:
        raise RuntimeError("ההורדה מהדרייב נכשלה - ודא שהקובץ משותף עם 'כל מי שיש לו את הקישור'")
    return Path(out)
