# Asset factory

For each post in scope (`contentq.py due --date <start> --days 14` or the IDs asked for): write
the copy, make the asset, update the post in the queue (`copy`, `assets`, `alt`, `cta_url`,
`status: draft`). Work in `marketing/assets/<post-id>/`. Batch similar assets with one small
script and one data file per post rather than hand-editing many HTML files.

Pick the format from the post's `format`; if unset, choose what the platform rewards
(`marketingskills/social/references/platforms.md`): carousels on LinkedIn/Instagram, short video
on TikTok/Reels/Shorts, image or 20–40 s clip on X, screenshots on Product Hunt/directories.

## Copy

Hook formulas and post templates: `marketingskills/social/GUIDE.md` and
`social/references/post-templates.md`. Carousels: pick a framework from
`social/references/carousel-frameworks.md` first. Long-form (blog/launch post/landing):
`marketingskills/copywriting/GUIDE.md`. Each post: hook from a real detail → one point → proof →
one CTA. Put links where the platform prefers (LinkedIn: first comment).

## Images, carousels, OG cards, stories

Templates in `<skill>/assets/templates/` (sizes in each file's `<meta name="size">`):
`social-post.html` 1080×1350 · `carousel-slide.html` 1080×1350 · `story-scene.html` 1080×1920
(also the default video scene) · `og-image.html` 1200×630 · `poster.html` A3.

```bash
cp <skill>/assets/templates/social-post.html marketing/assets/P0007/
# P0007/data.json: {"eyebrow":"…","headline":"…","sub":"…","image":"../screens/export.png","alt":"…"}
python3 <skill>/scripts/render.py marketing/assets/P0007/social-post.html marketing/assets/P0007/post.png \
  --data marketing/brand.json --data marketing/assets/P0007/data.json
```

Unfilled `{{placeholders}}` stop the render; pass `""` for optional ones (empty images hide).
Templates are starting points — change layout freely, keep brand tokens. For other sizes, change
the meta size and canvas CSS together (specs: `marketingskills/image/GUIDE.md`).

**Look at every render** (Read the PNG): text clipped or overflowing (render.py also warns),
contrast, headline readable at phone size (zoom out), nothing important in 9:16 safe zones, real
UI only, no leftover placeholder text. Fix and re-render, up to 3 rounds.

Generated imagery (backgrounds, lifestyle scenes): use an image model only if the user has one
connected; prompting guide in `marketingskills/image/references/ai-image-prompting.md`. Never
generate the product's UI. If Canva is connected, `canva:bulk-create` can fill a brand template
from the queue CSV and `canva:resize-for-social-media` makes platform variants.

## Video

Default pipeline (no paid tools): HTML scenes + real screenshots → `scripts/video.py`.

1. Script from `marketingskills/social/references/short-form-video.md`: visual + verbal + text
   hook in the first second; problem → product doing the job → result → CTA. 15–30 s for
   Reels/TikTok, 30–60 s for Shorts/LinkedIn, 60–90 s for a launch trailer.
2. Storyboard — one scene per beat, 1.5–4 s each:

```json
{"size": "1080x1920", "fps": 30, "out": "reel.mp4", "data": ["../../brand.json"],
 "audio": "",
 "scenes": [
  {"html": "story-scene.html", "duration": 2.5, "animate": true,
   "data": {"kicker": "Stop retyping notes", "headline": "Meeting audio → tasks", "sub": ""}},
  {"image": "../screens/upload.png",  "duration": 3, "caption": "Drop in a recording"},
  {"image": "../screens/tasks.png",   "duration": 3, "caption": "Owners and dates, filled in"},
  {"html": "story-scene.html", "duration": 3, "animate": true,
   "data": {"kicker": "Free to try", "headline": "acmenotes.app", "sub": "Link in bio"}}
 ]}
```

Remove the `"audio"` key or set a licensed track the user supplied (no copyrighted music).
`python3 <skill>/scripts/video.py marketing/assets/P0012/storyboard.json`. Then pull 3 frames
(`ffmpeg -i reel.mp4 -vf "select='not(mod(n\,45))',scale=270:-1,tile=4x1" -frames:v 1 strip.png`)
and look at them. 16:9 versions: set `"size": "1920x1080"` and use landscape scenes.

**Real product motion:** for a web app the user can run, record the actual flow with Playwright
(`marketingskills/video/references/product-demo-recording.md`) and use it as a scene source or
standalone demo. **Voice/avatars:** if HeyGen, ElevenLabs or similar is connected, generate the
voiceover/avatar from the script and mux it in with ffmpeg; label AI avatars. Otherwise the
captions carry the message, and face-cam clips are tasks for the user in the calendar.

## Posters and print

If `/make-poster` is installed, use it (it reads the same README/brand and has print checks).
Otherwise: `poster.html` + `render.py … poster.pdf` for print and `… poster.png` for a preview.
QR: set `qr_url` (with `utm_source=poster`) in the data file; needs `pip install segno`.
Monochrome variant: designed black-on-white, not a filter. Tell the user: print at 100%, A3/11×17,
matte 150 gsm.

## Launch kit (produce once, before day 0)

OG image · Product Hunt gallery (1270×760, up to 6, real UI) + 60 s demo · X/LinkedIn banners ·
launch-day thread and post · launch email · 3 short videos (trailer, 1 feature, 1 "how it works") ·
directory blurbs at 3 lengths (`directory-submissions/references/positioning-variations.md`) ·
press/newsletter pitch · FAQ replies for the top objections in the context doc.
