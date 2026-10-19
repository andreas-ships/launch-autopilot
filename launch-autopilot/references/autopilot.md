# Autopilot: queue, change, refill, review

The queue is the source of truth: `marketing/queue.json`, managed only through
`<skill>/scripts/contentq.py` (it keeps IDs unique, adds UTMs, saves atomically).
Statuses: `draft → approved → scheduled → posted`, plus `needs_review` and `skipped`.
`kind`: `launch`/`feature`/`fixed` posts keep their date; `evergreen` posts can move.

## queue / today / week

`contentq.py status` (counts, `runway_days`, `refill_needed` when < 14 days) ·
`contentq.py due --days 1` (today) · `--days 7` (week). For today/week, show each post's
platform, time, copy and asset paths (send the files), flag anything still `draft` or
`needs_review`, and list non-post tasks due from `calendar.md`.

## New feature (the "something new shipped" case)

1. **Find what's new** since `state.json` → `last_commit` (or last changelog version):
   merged PRs, `git log <last>..HEAD --no-merges`, changelog entries, docs diffs, or the user's
   description. Follow `marketingskills/launch/references/shipped-changes.md`: only what
   customers can use today; write "You can now ___" for each; tier as major / medium / minor.
2. **Update the context doc:** add rows to the Feature inventory, bump version + changelog line.
   Capture fresh screenshots of the feature.
3. **Plan the mini-launch** by tier and inject it:

| Tier | Posts (days from release R) |
|---|---|
| Major | R−2 teaser (real UI peek) · R launch post on every channel + video · R+1 how-to carousel · R+3 use-case/story · R+7 recap or tip; email to list; changelog; consider Product Hunt relaunch if never done or ≥6 months since |
| Medium | R post on the 1–2 best channels + short clip · R+4 tip post · changelog + email segment |
| Minor | Batch into the next weekly "what's new" post / changelog |

   Write them with `"kind": "feature"`, `"source": "feature:<slug>"`, then
   `contentq.py inject --posts new.json`. Evergreen posts on those slots move to the next free day
   per platform automatically; report which moved.
4. **Audit** (below) for claims the feature changed, render the assets (`assets.md`), set
   `state.json.last_commit` to the commit you processed.

## Refill

When `runway_days` < 14, or on the weekly run, top the queue up to the target (default 30 days):
- Spread pillars per `strategy.md`; at most one direct-promo post in five.
- Sources in order: Feature inventory items not posted in the last 60 days · objections and FAQs
  from the context doc · content atoms from new docs/blog/changelog (repurposing system in
  `marketingskills/social/GUIDE.md`) · top performers from Learnings, re-angled (reuse after
  90 days) · build-in-public notes from recent commits.
- Dedupe: no two posts with the same angle within 30 days (compare titles/briefs in the queue).
- Render assets only for the next 14 days; later posts keep copy + brief so they render against
  the current product.

## Review (weekly)

Pull numbers the user can give or a connected tool can read (platform analytics, scheduler stats,
signups by `utm_content` = post ID). Report top 3 / bottom 3 posts and why, follower and click
trend, signups vs goal. Propose Learnings rows (format and bar in
`marketingskills/product-marketing/GUIDE.md` §Maintaining Learnings); add only on approval. Then
adjust: shift cadence toward formats that convert, retire angles that flop twice, and change
upcoming drafts that contradict a learning.

## Audit (claim drift)

After any change to pricing, plans, limits, names or features: list the statements that are now
false, then `contentq.py flag --grep "<old claim>"` for each so those future posts become
`needs_review`, and list site/docs/listing pages to update. Fix the flagged drafts.

## Schedule

Offer three scheduled tasks, created with the environment's scheduling tool (in the Claude app:
a scheduled task; elsewhere: a durable cron that runs the agent with the prompt). Each prompt must
be standalone: name the repo/folder, this skill, and the command.

| Task | Cadence | Prompt core |
|---|---|---|
| Daily brief | weekdays, 15 min before the first post time | "Run launch-autopilot `today` for <folder>: list today's posts with copy and files; flag drafts awaiting approval." |
| Weekly run | Monday morning | "Run launch-autopilot `new-feature` (since state.json), then `audit`, `refill 30`, render the next 14 days, and `review` with whatever data is available. Draft only." |
| Release watch | on the user's release cadence or daily | "Check <repo> for new tags/merged PRs since state.json; if any are customer-visible, run `new-feature`. Otherwise do nothing." |

Guardrails for every scheduled run (from `marketingskills/marketing-loops/references/loop-guardrails.md`):
draft and render only; never publish, send, submit or spend; idempotent via `state.json`
(skip work already done); if the repo or queue can't be read, stop and report instead of guessing;
most runs should end "checked, nothing to do".
