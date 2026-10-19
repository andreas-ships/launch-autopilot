# Strategy and day-by-day calendar

Inputs: `.agents/product-marketing.md`, the user's answers (or stated defaults). Read
`marketingskills/launch/GUIDE.md` (ORB, SLC gate, phases, Product Hunt) and
`marketingskills/social/GUIDE.md` (pillars, cadence) before writing. For apps on a store, also
`marketingskills/aso/GUIDE.md`; for directories, `marketingskills/directory-submissions/GUIDE.md`.

## 1. Gates before planning

- **SLC readiness gate** (launch skill). If the product fails it, say which part and plan a
  "build in public" pre-launch instead of a launch.
- **Foundation check** — each missing item becomes a Day −N task, not a footnote:
  landing page with one clear CTA · analytics + UTM-aware signup tracking · OG image on the site ·
  email capture (waitlist or newsletter) · social profiles with bio/banner/link · a demo GIF or
  60 s video · a support/feedback channel · pricing page if paid · privacy policy if collecting data.

## 2. Pick the channels (fewer is better)

Use ORB: one **owned** channel (email list almost always), 1–2 **rented** where the ICP already
is, 1–2 **borrowed** (newsletters, podcasts, communities, creators). Choose from the ICP, not
habit:

| Product / audience | Rented | Borrowed / launch spots |
|---|---|---|
| Dev tool, OSS, API | X, LinkedIn, Bluesky | Hacker News (Show HN), r/programming-adjacent subs, dev.to, GitHub README, awesome-lists, newsletters |
| B2B SaaS | LinkedIn, X | Product Hunt, niche Slack/Discord, G2/Capterra, podcasts, partner co-marketing |
| Consumer / mobile app | TikTok, Instagram Reels, YouTube Shorts | Product Hunt, App Store featuring request, creators, Reddit niche subs |
| Local / service | Instagram, Facebook groups, Google Business Profile | local press, posters, events |
| Creator / course | YouTube, X, Instagram | podcast guesting, newsletter swaps |

Write one line per channel: why this audience is there, cadence, what success looks like.
Cadence must fit the user's hours: roughly 20 min per text post, 45 min per carousel,
60–90 min per video the user appears in (AI-made videos from this skill cost the user only
review time). If the plan exceeds their hours, cut channels, not quality.

## 3. Goals and KPIs

One primary goal with a number and date (e.g. 300 signups by day 30), 2–3 leading indicators
(profile→site clicks, waitlist conversion, activation rate), and the baseline if known. Every
queued post links with UTMs (the queue adds them), so the review can attribute signups to posts.

## 4. Phases → calendar

Day 0 = launch date. If already live, skip to the compounding phase and add a **relaunch moment**
(new feature, v2, Product Hunt if never done) within 3–5 weeks — launching again is cheaper than
waiting for organic momentum.

| Phase | Days | Focus |
|---|---|---|
| Foundation | −21 to −15 | Gate fixes, profiles, tracking, screenshots, brand, waitlist page |
| Build anticipation | −14 to −1 | Build-in-public posts, teasers with real UI, borrowed-channel pitches (send by −10), PH page + hunter/assets ready by −7, 10–20 people personally asked to try it and give feedback, launch email drafted |
| Launch day | 0 | Hour-by-hour run sheet (below) |
| Launch week | 1 to 7 | Reply to everything, ship 1 visible fix from feedback and post about it, recap post with real numbers, thank-you to early users, directories batch 1 |
| Compounding | 8 to 30 | Pillar content, repurposing, comparison/alternative pages, directories batch 2, community answers (90/10), first email newsletter, first customer story (only with permission) |
| Ongoing | 31 to 90 | Steady cadence, one mini-launch per month (feature or integration), monthly review, refresh evergreen |

**Launch-day run sheet** (adapt times to the audience's timezone; Product Hunt day starts 00:01 PT):
00:01 PH live + maker comment · 07:00 email to list · 08:00 X thread + LinkedIn post (with video) ·
09:00 community posts where allowed · hourly reply sweeps · 12:00 midday update post ·
18:00 thank-you + numbers · next morning recap. Never ask for upvotes; ask for feedback.

**Content mix** (social skill pillars, adjust to the product): 30% educational (the problem
space), 25% product in action (real UI, demos), 20% behind the scenes / build story, 15% proof
(results, user stories — real only), 10% direct promotion. Launch weeks tilt to product.

## 5. Write the files

`marketing/strategy.md`: assumptions · positioning one-liner · ICP · channels table with reasons ·
goals/KPIs · phase summary · risks (e.g. "no audience yet → borrowed channels carry launch").

`marketing/calendar.md` — every day of the horizon, including non-post tasks:

```markdown
| Day | Date | Phase | Channel | Task / post | Post ID | Asset | Who | ✓ |
|---|---|---|---|---|---|---|---|---|
| −14 | 2026-11-02 | Anticipation | X | Teaser: the problem, real screenshot | P0003 | social-post | AI draft → you approve | |
| −10 | 2026-11-06 | Anticipation | Email | Pitch 5 newsletters (list in strategy.md) | — | pitch drafts | you send | |
```

Then create the queue: `python3 <skill>/scripts/contentq.py init --file marketing/queue.json
--product "<name>" --tz <user tz>`, write every post in the horizon to a JSON array, and `add` it.
Launch-day and launch-week posts use `"kind": "launch"` (they never move); everything else is
`"evergreen"` unless tied to a date (`"fixed"`: events, holidays, deadlines). Each post needs at
least: `date, time, platform, format, pillar, kind, title` and a one-line `brief`; copy and assets
are filled by the assets step.

## 6. Also plan (only the ones that apply)

- **Email:** welcome/onboarding sequence + launch email + monthly update (`marketingskills/emails`).
- **Directories:** tiered list from `directory-submissions/references/directory-list.md`, spread
  over weeks 1–6, tracked with its CSV template. User submits; you prepare copy and images.
- **PR/borrowed:** 10 targeted pitches with a reason each target's audience cares (`public-relations`).
- **Localization:** if the user publishes in more than one language (e.g. English + Romanian),
  plan native-language posts per market rather than translations of every post, and keep each
  market's cadence realistic.
- **Paid:** only when there's a working conversion path and budget; then use `ad-creative`.
