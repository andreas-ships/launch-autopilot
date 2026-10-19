#!/usr/bin/env python3
"""Content queue for launch-autopilot. One JSON file holds every planned post.

  contentq.py init     --file Q --product NAME [--tz Europe/Bucharest]
  contentq.py add      --file Q --posts posts.json         # append (array of posts)
  contentq.py inject   --file Q --posts posts.json         # fixed-date posts win; evergreen slots they collide with move to the next free day
  contentq.py due      --file Q [--date YYYY-MM-DD] [--days 1]
  contentq.py status   --file Q [--date YYYY-MM-DD]        # counts + runway (days of approved/draft content left)
  contentq.py set      --file Q --ids P0001,P0002 --status approved
  contentq.py flag     --file Q --grep "old text"          # future posts containing text -> needs_review (claim drift)
  contentq.py export   --file Q --csv out.csv | --ics out.ics
  contentq.py selftest

Post fields: date, time, platform, format, pillar, kind (launch|feature|evergreen|fixed),
title, copy, assets[], alt, cta_url, status (draft|approved|scheduled|posted|needs_review|skipped), source, notes.
"""
import argparse, csv, json, os, sys, tempfile
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlencode, urlparse, parse_qsl, urlunparse

LIVE = {"draft", "approved", "scheduled", "needs_review"}  # still going out


def load(p):
    with open(p) as f:
        return json.load(f)


def save(p, q):
    q["posts"].sort(key=lambda x: (x["date"], x.get("time", ""), x["id"]))
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(q, f, indent=2, ensure_ascii=False)
    os.replace(tmp, p)  # atomic: a crash never leaves a half-written queue


def utm(url, post):
    if not url or "utm_source" in url:
        return url
    u = urlparse(url)
    qs = dict(parse_qsl(u.query))
    qs.update(utm_source=post["platform"], utm_medium="social",
              utm_campaign=post.get("source") or post.get("kind", "evergreen"), utm_content=post["id"])
    return urlunparse(u._replace(query=urlencode(qs)))


def normalize(q, posts):
    n = max([int(p["id"][1:]) for p in q["posts"]] or [0])
    out = []
    for p in posts:
        for k in ("date", "platform"):
            if k not in p:
                sys.exit(f"post missing '{k}': {p}")
        date.fromisoformat(p["date"])  # validate
        if not p.get("id"):
            n += 1
            p["id"] = f"P{n:04d}"
        p.setdefault("kind", "evergreen")
        p.setdefault("status", "draft")
        p.setdefault("assets", [])
        p["cta_url"] = utm(p.get("cta_url", ""), p)
        out.append(p)
    return out


def taken(q):
    return {(p["date"], p["platform"]) for p in q["posts"] if p["status"] in LIVE}


def inject(q, new):
    """Fixed-date posts claim their slot; a colliding evergreen post moves to the next free day
    on its platform (cascading). Launch/feature/fixed posts never move."""
    for p in new:
        slot = (p["date"], p["platform"])
        clash = [o for o in q["posts"] if (o["date"], o["platform"]) == slot and o["status"] in LIVE]
        q["posts"].append(p)
        for o in clash:
            if o.get("kind", "evergreen") != "evergreen":
                continue  # two dated posts on one slot is allowed; user asked for both
            d = date.fromisoformat(o["date"])
            busy = taken(q) - {(o["date"], o["platform"])} | {slot}
            while (d.isoformat(), o["platform"]) in busy:
                d += timedelta(days=1)
            o["notes"] = (o.get("notes", "") + f" moved from {o['date']} for {p['id']}").strip()
            o["date"] = d.isoformat()


def runway(q, today):
    live = [p["date"] for p in q["posts"] if p["status"] in LIVE and p["date"] >= today]
    return (date.fromisoformat(max(live)) - date.fromisoformat(today)).days if live else 0


def export_ics(q, path):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//launch-autopilot//EN"]
    for p in q["posts"]:
        if p["status"] not in LIVE:
            continue
        t = (p.get("time") or "09:00").replace(":", "")
        start = p["date"].replace("-", "") + "T" + t + "00"
        desc = (p.get("copy", "") + "\\n" + p.get("cta_url", "")).replace("\n", "\\n").replace(",", "\\,")
        lines += ["BEGIN:VEVENT", f"UID:{p['id']}@launch-autopilot", f"DTSTAMP:{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}",
                  f"DTSTART;TZID={q.get('timezone', 'UTC')}:{start}", "DURATION:PT15M",
                  f"SUMMARY:[{p['platform']}] {p.get('title', p['id'])}", f"DESCRIPTION:{desc}", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    with open(path, "w") as f:
        f.write("\r\n".join(lines) + "\r\n")


def main(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("cmd")
    a.add_argument("--file", default="marketing/queue.json")
    a.add_argument("--product"); a.add_argument("--tz", default="UTC")
    a.add_argument("--posts"); a.add_argument("--date", default=date.today().isoformat())
    a.add_argument("--days", type=int, default=1)
    a.add_argument("--ids"); a.add_argument("--status"); a.add_argument("--grep")
    a.add_argument("--csv"); a.add_argument("--ics")
    o = a.parse_args(argv)

    if o.cmd == "selftest":
        return selftest()
    if o.cmd == "init":
        if os.path.exists(o.file):
            sys.exit(f"{o.file} exists; refusing to overwrite")
        os.makedirs(os.path.dirname(o.file) or ".", exist_ok=True)
        save(o.file, {"product": o.product, "timezone": o.tz, "posts": []})
        return print(f"created {o.file}")

    q = load(o.file)
    if o.cmd in ("add", "inject"):
        new = normalize(q, load(o.posts))
        q["posts"].extend(new) if o.cmd == "add" else inject(q, new)
        save(o.file, q)
        print(f"{o.cmd}: {len(new)} posts -> {', '.join(p['id'] for p in new)}")
    elif o.cmd == "due":
        end = (date.fromisoformat(o.date) + timedelta(days=o.days - 1)).isoformat()
        for p in q["posts"]:
            if o.date <= p["date"] <= end and p["status"] in LIVE:
                print(json.dumps(p, ensure_ascii=False))
    elif o.cmd == "status":
        counts = {}
        for p in q["posts"]:
            counts[p["status"]] = counts.get(p["status"], 0) + 1
        r = runway(q, o.date)
        print(json.dumps({"total": len(q["posts"]), "by_status": counts, "runway_days": r,
                          "refill_needed": r < 14}, indent=2))
    elif o.cmd == "set":
        ids = set(o.ids.split(","))
        for p in q["posts"]:
            if p["id"] in ids:
                p["status"] = o.status
        save(o.file, q)
    elif o.cmd == "flag":
        hit = [p for p in q["posts"] if p["date"] >= o.date and p["status"] in LIVE
               and o.grep.lower() in json.dumps(p, ensure_ascii=False).lower()]
        for p in hit:
            p["status"] = "needs_review"
        save(o.file, q)
        print(f"flagged {len(hit)}: {', '.join(p['id'] for p in hit)}")
    elif o.cmd == "export":
        if o.csv:
            cols = ["id", "date", "time", "platform", "format", "title", "copy", "cta_url", "assets", "alt", "status"]
            with open(o.csv, "w", newline="") as f:
                w = csv.writer(f); w.writerow(cols)
                for p in q["posts"]:
                    if p["status"] in LIVE:
                        w.writerow([";".join(p[c]) if c == "assets" else p.get(c, "") for c in cols])
        if o.ics:
            export_ics(q, o.ics)
        print("exported")
    else:
        sys.exit(f"unknown command {o.cmd}")


def selftest():
    d = tempfile.mkdtemp(); f = os.path.join(d, "q.json"); pf = os.path.join(d, "p.json")
    main(["init", "--file", f, "--product", "T"])
    json.dump([{"date": "2030-01-01", "platform": "x", "cta_url": "https://t.co/a"},
               {"date": "2030-01-02", "platform": "x"}], open(pf, "w"))
    main(["add", "--file", f, "--posts", pf])
    json.dump([{"date": "2030-01-01", "platform": "x", "kind": "feature", "copy": "new export"}], open(pf, "w"))
    main(["inject", "--file", f, "--posts", pf])
    q = load(f)
    by = {p["id"]: p for p in q["posts"]}
    assert by["P0003"]["date"] == "2030-01-01"
    assert by["P0001"]["date"] == "2030-01-03", by["P0001"]  # skipped the taken 01-02
    assert "utm_content=P0001" in by["P0001"]["cta_url"]
    assert runway(q, "2030-01-01") == 2
    main(["flag", "--file", f, "--grep", "NEW EXPORT", "--date", "2030-01-01"])
    assert load(f)["posts"][0]["status"] == "needs_review"
    main(["export", "--file", f, "--ics", os.path.join(d, "q.ics"), "--csv", os.path.join(d, "q.csv")])
    print("selftest ok")


if __name__ == "__main__":
    main()
