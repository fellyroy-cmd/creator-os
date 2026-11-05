# Creator OS

**Your AI content team, inside Claude Code.** Turn one video into a week of posts, find ideas worth making,
get your niche's news, plan the week and write shorts that hold attention, all in your own voice.

Free, open source, and running a real YouTube channel every day.

```
/creator-os:setup          2 minutes of questions → your creator profile
/creator-os:ideas          10 ideas for your niche, top 3 ranked
/creator-os:news           this week's news in your niche, with sources + content angles
/creator-os:plan-week      your content calendar, matched to how often you actually post
/creator-os:repurpose      one video → X thread, LinkedIn, Instagram, short script, newsletter
/creator-os:shorts-script  a 7-beat short script, 3 hook variants + a recording sheet
/creator-os:news-sniper    check right now for breaking news worth a same-day post
/creator-os:sponsor-desk   triage a brand email and draft a reply from your rate card — you still hit send
```

## Install

You need [Claude Code](https://claude.com/claude-code) (the terminal app, the desktop app's Code tab, or the VS Code extension).

```
/plugin marketplace add fellyroy-cmd/creator-os
/plugin install creator-os@creator-os
```

If your chat window says `/plugin isn't available`, run the same thing from a terminal instead:

```
claude plugin marketplace add fellyroy-cmd/creator-os
claude plugin install creator-os@creator-os
```

Then start a **new** session (plugins load when a session starts), open a folder for your content (an empty one is fine) and run:

```
/creator-os:setup
```

## How it works

Setup writes one file, `creator/profile.md`: your niche, audience, voice, platforms, pillars and call-to-action.
Every skill reads it before it writes anything. That's why the output sounds like you and not like a template.
Change the file and every skill changes with it.

Everything is saved as plain Markdown in your folder:

```
creator/profile.md        who you are, how you sound
content/ideas/            /ideas
content/research/         /news
content/calendar/         /plan-week
content/repurposed/       /repurpose
content/shorts/           /shorts-script
content/research/breaking/  /news-sniper
content/sponsors/        /sponsor-desk
```

The skills talk to each other through these files. `/ideas` and `/plan-week` pick up this week's `/news` digest
automatically, and `/shorts-script` checks your last scripts so it doesn't repeat a hook.

A typical week:
1. **Monday:** `/creator-os:news` → `/creator-os:plan-week`
2. **Script day:** `/creator-os:shorts-script` on each short in the plan
3. **After the main video:** paste the script into `/creator-os:repurpose`

## What's coming

- [ ] **Clip maker:** long video → captioned vertical shorts, on your own computer
- [ ] **Chat with your channel:** ask questions about everything you've ever said on video

`/creator-os:news-sniper` checks for breaking news on demand today. Telegram/Discord pings on a schedule
work too, with a little extra setup — see [`skills/news-sniper/references/scheduling.md`](skills/news-sniper/references/scheduling.md).

`/creator-os:sponsor-desk` triages one pasted brand email against your own `creator/rate-card.md` and drafts
a reply — it never reads your inbox and never sends anything, you copy the draft yourself. Copy
[`skills/sponsor-desk/references/rate-card-template.md`](skills/sponsor-desk/references/rate-card-template.md)
to `creator/rate-card.md` first.

Want one of these sooner, or have a better idea? [Open an issue](../../issues).

## Contributing

Creator OS is built so that adding a skill is easy. Each skill is one folder with one Markdown file in it.
No code required. See [CONTRIBUTING.md](CONTRIBUTING.md).

Good first contributions:
- A skill for a platform we don't cover yet (Pinterest, Threads, podcasts, blogs)
- A better formula for a format you know well
- An example profile for your niche in [`examples/`](examples/)

## Who made this

[Dara Obafemi](https://www.youtube.com/@dara_obafemi). I make videos about building with AI, and Creator OS is the
system behind my channel, cleaned up so anyone can use it.

MIT licensed.
