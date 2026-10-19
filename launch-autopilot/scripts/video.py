#!/usr/bin/env python3
"""Storyboard JSON -> MP4 (H.264, captions burned in, optional music). Needs Playwright + ffmpeg.

  video.py storyboard.json            # writes storyboard["out"] (default video.mp4 next to it)
  video.py --selftest

storyboard.json:
{
  "size": "1080x1920", "fps": 30, "out": "launch-reel.mp4",
  "data": ["../../brand.json"],                 # placeholder values for HTML scenes
  "audio": "music.mp3",                          # optional; trimmed + faded to video length
  "scenes": [
    {"html": "scene-hook.html", "duration": 2.5, "animate": true, "data": {"headline": "..."}},
    {"html": "scene-card.html", "duration": 3},                 # static, gets a slow push-in
    {"image": "screens/dashboard.png", "duration": 3, "caption": "Export in one click"}
  ]
}
animate=true records the page live, so CSS/JS animations play. Static scenes and images get a
slow zoom so nothing sits frozen. Paths are relative to the storyboard file.
"""
import json, os, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from render import fill, settle  # noqa: E402

CAPTION_HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;width:{{w}}px;height:{{h}}px;background:{{bg}};overflow:hidden;font-family:{{font}},system-ui,sans-serif}
img{position:absolute;inset:6% 5% 30% 5%;width:90%;height:64%;object-fit:contain;border-radius:24px}
.cap{position:absolute;left:6%;right:6%;top:72%;text-align:center;color:#fff;font-weight:800;
font-size:{{fs}}px;line-height:1.15;-webkit-text-stroke:2px #000;paint-order:stroke fill;text-shadow:0 4px 12px #000a}
</style></head><body><img src="{{src}}"><div class="cap">{{caption}}</div></body></html>"""


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def still_clip(png, out, dur, w, h, fps):
    frames = int(dur * fps)
    vf = (f"scale={w*2}:{h*2},zoompan=z='min(zoom+0.0006,1.05)':d={frames}:s={w}x{h}:fps={fps},"
          f"fade=t=in:d=0.25,fade=t=out:st={dur-0.25}:d=0.25,format=yuv420p")
    ff("-loop", "1", "-i", png, "-t", str(dur), "-vf", vf, "-r", str(fps), "-c:v", "libx264", out)


def build(sb_path):
    sb_path = Path(sb_path).resolve(); base = sb_path.parent
    sb = json.loads(sb_path.read_text())
    w, h = map(int, sb.get("size", "1080x1920").split("x")); fps = sb.get("fps", 30)
    data = {}
    for d in sb.get("data", []):
        data.update(json.loads((base / d).read_text()))
    work = Path(tempfile.mkdtemp()); clips = []
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        for i, s in enumerate(sb["scenes"]):
            dur = float(s.get("duration", 3)); clip = str(work / f"c{i:02d}.mp4"); vals = {**data, **s.get("data", {})}
            if "image" in s:
                html = fill(CAPTION_HTML, {"w": w, "h": h, "bg": vals.get("bg", "#111"), "font": vals.get("font_body", "Inter"),
                                           "fs": int(w * 0.065), "src": (base / s["image"]).resolve().as_uri(),
                                           "caption": s.get("caption", "")})
                src = work / f"s{i}.html"; src.write_text(html)
            else:
                src = work / f"s{i}.html"
                src.write_text(fill((base / s["html"]).read_text(), vals).replace(
                    "<head>", f'<head><base href="{(base / s["html"]).parent.as_uri()}/">', 1))
            if s.get("animate"):
                ctx = b.new_context(viewport={"width": w, "height": h}, record_video_dir=str(work),
                                    record_video_size={"width": w, "height": h})
                pg = ctx.new_page(); pg.goto(src.as_uri(), wait_until="load"); pg.wait_for_timeout(int(dur * 1000) + 300)
                webm = pg.video.path(); ctx.close()
                ff("-i", webm, "-ss", "0.15", "-t", str(dur), "-vf", f"fps={fps},scale={w}:{h},format=yuv420p",
                   "-c:v", "libx264", clip)
            else:
                pg = b.new_page(viewport={"width": w, "height": h}); pg.goto(src.as_uri(), wait_until="networkidle"); settle(pg)
                png = str(work / f"s{i}.png"); pg.screenshot(path=png); pg.close()
                still_clip(png, clip, dur, w, h, fps)
            clips.append(clip)
        b.close()
    lst = work / "list.txt"; lst.write_text("".join(f"file '{c}'\n" for c in clips))
    out = str(base / sb.get("out", "video.mp4")); silent = str(work / "silent.mp4")
    ff("-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", silent)
    if sb.get("audio"):
        total = sum(float(s.get("duration", 3)) for s in sb["scenes"])
        ff("-i", silent, "-i", str(base / sb["audio"]), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
           "-af", f"afade=t=out:st={max(total-1, 0)}:d=1", "-shortest", out)
    else:
        os.replace(silent, out)
    print(out)
    return out


def selftest():
    d = Path(tempfile.mkdtemp())
    from PIL import Image
    Image.new("RGB", (800, 500), "#3b82f6").save(d / "shot.png")
    (d / "a.html").write_text('<!doctype html><html><head><style>body{margin:0;background:{{bg}};color:#fff;'
                              'font:800 90px sans-serif;display:grid;place-items:center;height:100vh}'
                              'h1{animation:u 1s ease-out}@keyframes u{from{transform:translateY(200px);opacity:0}}'
                              '</style></head><body><h1>{{headline}}</h1></body></html>')
    (d / "sb.json").write_text(json.dumps({"size": "540x960", "fps": 24, "out": "t.mp4", "scenes": [
        {"html": "a.html", "duration": 1.5, "animate": True, "data": {"bg": "#111", "headline": "Hi"}},
        {"html": "a.html", "duration": 1, "data": {"bg": "#222", "headline": "Still"}},
        {"image": "shot.png", "duration": 1, "caption": "Real screenshot"}]}))
    out = build(d / "sb.json")
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out],
                               capture_output=True, text=True).stdout)
    assert abs(dur - 3.5) < 0.3, dur
    print(f"selftest ok ({dur:.2f}s)")


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else build(sys.argv[1])
