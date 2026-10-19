# Contributing

Thanks for helping. Small, focused pull requests are easiest to review.

## Set up

```bash
git clone https://github.com/andreas-ships/launch-autopilot.git
cd launch-autopilot
pip install playwright segno && playwright install chromium   # only for render.py / video.py
```

## Test your change

```bash
python3 launch-autopilot/scripts/contentq.py selftest   # expect "selftest ok"
python3 launch-autopilot/scripts/video.py --selftest     # needs Playwright + ffmpeg
```

To test the skill itself, copy `launch-autopilot/` to `~/.claude/skills/` and run `/launch-autopilot setup` on a small project.

## Send a change

1. Fork, then branch from `main` (`fix/queue-export`, `feat/new-template`).
2. Keep `SKILL.md` short; put detail in the matching `references/*.md`.
3. Don't edit files in `references/marketingskills/`; they are vendored from upstream. Fix those in [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills).
4. Add a line to `CHANGELOG.md` under an `Unreleased` heading.
5. Open a pull request and fill in the template.
