# ShowUp Calendar

Free add-to-calendar links that get people to actually show up.

If your webinar isn't in their calendar, they don't turn up. Paid tools like AddEvent charge a monthly fee for this. ShowUp Calendar does the same job for free, and it works on iPhones, which is where most "add to calendar" buttons quietly fail.

## What you get for each event

- **A chooser page** with buttons for Apple Calendar, Google Calendar, Outlook, Office 365, Yahoo and a plain download. Put this one link in your emails and on your thank-you page.
- **A real calendar file (.ics)** hosted at its own web address. iPhones open it straight into Apple Calendar, with your reminders and joining link inside.
- The page highlights the right button for the visitor's device and is hidden from search engines.

## How to use it

1. Copy this repo (use **Use this template** or fork it).
2. Add your event to `events.json`: title, start and end time with timezone, the joining link and a short description of what's in it for them.
3. Run `python3 build.py events.json docs` (Python 3, no installs needed).
4. Push, then turn on GitHub Pages for the `docs` folder (Settings, Pages, branch `main`, folder `/docs`).
5. Your link is `https://<your-username>.github.io/showup-calendar/<slug>/`.

Tip: you can ask Claude or ChatGPT to do steps 2 to 4 for you.

## Why a hosted file beats a button

Most add-to-calendar buttons build the calendar file inside the page with JavaScript. iPhone Safari and the browsers inside Instagram, Facebook and Gmail often block that, so nothing happens when people tap it. A real file at a real web address just works.

## Licence

MIT. Built by [Deb Szabo](https://www.debszabo.com/) with Claude.
