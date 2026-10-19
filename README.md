<div align="center">

# Launch Autopilot

**A Claude skill that turns your product's own files into a launch plan, finished marketing assets and a content queue that stays full.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python 3](https://img.shields.io/badge/python-3-blue.svg)
![Claude Skill](https://img.shields.io/badge/Claude-Skill-d97757.svg)

</div>

## What it does

You have a product (an app, SaaS, library, game or side project) and need to tell people about it. Launch Autopilot reads your README, docs, changelog, code and screenshots, writes your positioning, plans a day-by-day launch and growth calendar, then makes the posts, carousels, OG cards, posters and short videos for it. Every claim comes from your files, never from thin air, and the queue re-plans itself when you ship a new feature.

It drafts and schedules. It never posts, emails or spends money until you approve specific posts.

## Example prompts

- "Launch my app, here's the repo."
- "Make a 30-day content calendar for this project, launching 2026-11-15."
- "We just shipped dark mode, plan a mini-launch for it."
- "What do I post today?"
- `/launch-autopilot video "export in one click"`

## Features

- **Reads before it asks.** Builds a positioning doc and feature inventory from README, docs, changelog, `package.json`/`pyproject.toml`, CSS tokens and `git log`, then asks at most one round of questions.
- **Strategy and calendar.** 30/60/90-day plans with goals, ICP, channels, phases and KPIs, plus a task for every day.
- **Real assets.** Renders HTML templates to PNG/PDF (social posts, carousels, OG images, posters, story scenes) and storyboards to MP4 with burned-in captions.
- **Content queue that adapts.** `contentq.py` keeps every post in one JSON file; dated launch posts take their slot and evergreen posts move forward; `flag` catches posts a product change made wrong.
- **Export anywhere.** CSV for Buffer/Later/Hootsuite bulk upload and ICS reminders for your calendar.
- **Honest by design.** No invented stats, fake reviews or sockpuppets; AI avatars, paid posts and affiliate links are disclosed.

## Commands

Type `/launch-autopilot <command>` or just describe what you want. With no command it runs `go`.

| Command | Does |
|---|---|
| `go` | setup → strategy → first 2 weeks of assets → queue → offer `schedule` |
| `setup` | Read product files, write positioning context and `brand.json` |
| `strategy [30\|60\|90] [launch=YYYY-MM-DD]` | Strategy, day-by-day calendar, queue skeleton |
| `assets [week N\|P0007\|type]` | Write copy and render assets for queued posts |
| `video <topic\|post-id>` | Storyboard → MP4 |
| `poster [size] [count]` | Print posters (PDF) |
| `queue` / `today` / `week` | Status and runway, or what to post today / this week |
| `new-feature [ref\|description]` | Tier what shipped, inject a mini-launch, re-plan |
| `refill [days]` | Top the queue up to N days of runway |
| `review` | Weekly performance review into the context doc |
| `audit` | Find queued posts and pages a change made wrong |
| `export [csv\|ics]` | Bulk-upload CSV or calendar ICS |
| `schedule` | Recurring tasks: daily brief, weekly refill + review, release watch |

## What you get

In your product's repo (or working folder):

```text
.agents/product-marketing.md   # positioning + feature inventory
marketing/
  brand.json                   # colors, fonts, logo, URL
  strategy.md                  # goals, ICP, channels, phases, KPIs
  calendar.md                  # day-by-day plan
  queue.json                   # every planned post: copy, assets, UTM link, status
  state.json                   # last processed commit / release
  assets/<post-id>/            # rendered PNG / PDF / MP4 + their sources
```

## Install

**Claude app (claude.ai / desktop):** download `launch-autopilot.skill` from the [latest release](https://github.com/andreas-ships/launch-autopilot/releases/latest) and upload it in Claude's Skills settings.

**Claude Code:**

```bash
git clone https://github.com/andreas-ships/launch-autopilot.git
cp -r launch-autopilot/launch-autopilot ~/.claude/skills/        # personal
# or: cp -r launch-autopilot/launch-autopilot .claude/skills/   # one project
```

### Requirements

The rendering scripts need Python 3, Playwright with Chromium, and ffmpeg (video only). `segno` is needed only for QR codes on posters.

```bash
pip install playwright segno
playwright install chromium
# ffmpeg: brew install ffmpeg  /  sudo apt install ffmpeg
```

The skill checks for these itself and offers to install what's missing.

## Using the scripts directly

The queue tool runs on its own with the standard library:

```bash
python3 launch-autopilot/scripts/contentq.py init --file queue.json --product "My App" --tz UTC
python3 launch-autopilot/scripts/contentq.py add --file queue.json --posts posts.json
python3 launch-autopilot/scripts/contentq.py due --file queue.json --days 7
python3 launch-autopilot/scripts/contentq.py export --file queue.json --csv buffer.csv
python3 launch-autopilot/scripts/contentq.py selftest   # prints "selftest ok"
```

Render a template with your brand:

```bash
python3 launch-autopilot/scripts/render.py launch-autopilot/assets/templates/og-image.html og.png \
  --data marketing/brand.json --data post.json
```

Unfilled `{{placeholders}}` stop the render, so a half-filled image never ships.

## How it works

`SKILL.md` holds the workflow and rules; it loads one reference file per step instead of everything at once.

```text
launch-autopilot/
├── SKILL.md                 # workflow, commands, copy rules, publishing boundary
├── NOTICE.md                # attribution for the vendored prompts
├── references/
│   ├── strategy.md          # strategy + calendar method
│   ├── assets.md            # copy, images, posters, video
│   ├── autopilot.md         # queue, new-feature, refill, review, audit, schedule
│   └── marketingskills/     # vendored MIT marketing guides (Corey Haines)
├── assets/templates/        # HTML templates + _brand.example.json
└── scripts/
    ├── contentq.py          # content queue (stdlib only)
    ├── render.py            # HTML → PNG/PDF via Playwright
    └── video.py             # storyboard → MP4 via Playwright + ffmpeg
```

## Contributing

Bug reports and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Support

Ask questions or report bugs in [GitHub Issues](https://github.com/andreas-ships/launch-autopilot/issues). For security problems see [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE). Includes MIT-licensed guides from [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) (© 2025 Corey Haines); see [`launch-autopilot/NOTICE.md`](launch-autopilot/NOTICE.md) and [their licence](launch-autopilot/references/marketingskills/LICENSE).

## Acknowledgements

The marketing guides in `references/marketingskills/` are from Corey Haines' [marketingskills](https://github.com/coreyhaines31/marketingskills), vendored at the commit in `SOURCE_COMMIT`.
