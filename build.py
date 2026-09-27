#!/usr/bin/env python3
"""ShowUp Calendar: build add-to-calendar pages and .ics files from events.json.

Usage: python3 build.py [events.json] [output_dir]
Each event gets <slug>/index.html (the chooser page to link from emails)
and <slug>/event.ics (the file iPhones open straight into Apple Calendar).
"""
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "events.json")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "site")


def utc(iso):
    return datetime.fromisoformat(iso).astimezone(timezone.utc)


def ics_stamp(dt):
    return dt.strftime("%Y%m%dT%H%M%SZ")


def ics_escape(text):
    return (text.replace("\\", "\\\\").replace(";", "\\;")
            .replace(",", "\\,").replace("\n", "\\n"))


def fold(line):
    # RFC 5545: lines over 75 octets are folded with CRLF + space
    out, cur = [], ""
    for ch in line:
        if len((cur + ch).encode("utf-8")) > 74:
            out.append(cur)
            cur = " " + ch
        else:
            cur += ch
    out.append(cur)
    return "\r\n".join(out)


def build_ics(ev, organiser):
    start, end = utc(ev["start"]), utc(ev["end"])
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0",
        "PRODID:-//ShowUp Calendar//EN",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:{ev['slug']}@debszabo.com",
        f"DTSTAMP:{ics_stamp(datetime.now(timezone.utc))}",
        f"DTSTART:{ics_stamp(start)}",
        f"DTEND:{ics_stamp(end)}",
        f"SUMMARY:{ics_escape(ev['title'])}",
        f"DESCRIPTION:{ics_escape(ev['details'])}",
        f"LOCATION:{ics_escape(ev['location'])}",
        f"URL:{ev['location']}",
        "STATUS:CONFIRMED", "TRANSP:OPAQUE",
    ]
    for mins in ev.get("reminders_minutes", []):
        lines += ["BEGIN:VALARM", f"TRIGGER:-PT{mins}M", "ACTION:DISPLAY",
                  f"DESCRIPTION:{ics_escape(ev['short_title'])}", "END:VALARM"]
    lines += ["END:VEVENT", "END:VCALENDAR"]
    return "\r\n".join(fold(l) for l in lines) + "\r\n"


def links(ev):
    start, end = utc(ev["start"]), utc(ev["end"])
    t, d, loc = quote(ev["title"]), quote(ev["details"]), quote(ev["location"])
    iso = lambda dt: quote(dt.strftime("%Y-%m-%dT%H:%M:%SZ"))
    outlook = (f"/calendar/0/deeplink/compose?path=/calendar/action/compose&rru=addevent"
               f"&subject={t}&startdt={iso(start)}&enddt={iso(end)}&body={d}&location={loc}")
    return {
        "google": (f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={t}"
                   f"&dates={ics_stamp(start)}/{ics_stamp(end)}&details={d}&location={loc}"),
        "outlook": "https://outlook.live.com" + outlook,
        "office": "https://outlook.office.com" + outlook,
        "yahoo": (f"https://calendar.yahoo.com/?v=60&title={t}&st={ics_stamp(start)}"
                  f"&et={ics_stamp(end)}&desc={d}&in_loc={loc}"),
    }


PAGE = """<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Add to calendar | {short}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=League+Spartan:wght@600&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{{--navy:#030529;--raised:#2A3B6E;--paper:#FAFBFC;--panel:#FFFFFF;--ink:#5D6178;--green:#1BF2AF;--focus:#3E8FD8}}
*{{box-sizing:border-box}}
body{{margin:0;min-height:100vh;background:var(--paper);color:var(--navy);font:400 17px/1.55 Inter,system-ui,sans-serif;display:flex;align-items:center;justify-content:center;padding:24px 16px}}
main{{width:100%;max-width:460px;background:var(--panel);border-radius:18px;padding:32px 24px;box-shadow:0 12px 40px rgba(3,5,41,.08)}}
h1{{font:600 30px/1.15 "League Spartan",system-ui,sans-serif;margin:0 0 10px}}
.event{{margin:0 0 4px;font-weight:600}}
.when{{margin:0 0 24px;color:var(--ink)}}
.btn{{display:flex;align-items:center;justify-content:space-between;width:100%;padding:16px 18px;margin:0 0 10px;border-radius:12px;border:1.5px solid #E3E6EC;background:var(--panel);color:var(--navy);font:600 17px Inter,system-ui,sans-serif;text-decoration:none}}
.btn:hover{{border-color:var(--navy)}}
.btn:focus-visible{{outline:3px solid var(--focus);outline-offset:2px}}
.btn.primary{{background:var(--navy);border-color:var(--navy);color:var(--green)}}
.btn span{{font-weight:400;font-size:14px;opacity:.75}}
.note{{margin:18px 0 0;font-size:14px;color:var(--ink)}}
.made{{margin:22px 0 0;font-size:12px;color:var(--ink);text-align:center}}
.made a{{color:var(--ink)}}
</style>
</head>
<body>
<main>
<h1>Add it to your calendar</h1>
<p class="event">{short}</p>
<p class="when">{when}</p>
<a class="btn primary" data-k="google" href="{google}" target="_blank" rel="noopener">Google Calendar <span>Android, Gmail</span></a>
<a class="btn" data-k="apple" href="event.ics">Apple Calendar <span>iPhone, iPad, Mac</span></a>
<a class="btn" data-k="outlook" href="{outlook}" target="_blank" rel="noopener">Outlook <span>Hotmail, Outlook.com</span></a>
<a class="btn" data-k="office" href="{office}" target="_blank" rel="noopener">Office 365 <span>Work accounts</span></a>
<a class="btn" data-k="yahoo" href="{yahoo}" target="_blank" rel="noopener">Yahoo Calendar</a>
<a class="btn" data-k="other" href="event.ics" download="{slug}.ics">Other calendar <span>Download file</span></a>
<p class="note">Your Zoom link is saved inside the calendar entry, so it's there when you need it.</p>
<p class="made">Made with <a href="https://github.com/Debszabo/showup-calendar">ShowUp Calendar</a></p>
</main>
</body>
</html>
"""


def main():
    cfg = json.loads(SRC.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ".nojekyll").write_text("")
    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
    (OUT / "index.html").write_text(
        '<!doctype html><meta name="robots" content="noindex"><title>Deb Szabo</title>'
        '<meta http-equiv="refresh" content="0; url=https://www.debszabo.com/">')
    for ev in cfg["events"]:
        folder = OUT / ev["slug"]
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "event.ics").write_bytes(build_ics(ev, cfg["organiser_email"]).encode("utf-8"))
        l = links(ev)
        (folder / "index.html").write_text(PAGE.format(
            short=html.escape(ev["short_title"]), when=html.escape(ev["display_when"]),
            slug=ev["slug"], **{k: html.escape(v) for k, v in l.items()}))
        print("built", ev["slug"])


if __name__ == "__main__":
    main()
