# Running news-sniper on a schedule

By default this skill only runs when the creator asks for it. To get a real "ping me the moment something
breaks" watch, something needs to call Claude Code on a timer. Two free options, pick whichever matches the
creator's computer:

## Windows: Task Scheduler
1. Create a short script that opens the project folder and runs the skill headless, e.g.
   `claude -p "/creator-os:news-sniper" --headless` (check `claude --help` for the exact headless flag —
   it changes between versions).
2. Open Task Scheduler → Create Task → Trigger: "Daily", repeat every 30 minutes, during the hours the
   creator actually wants pings (don't run it at 3 AM unless they want 3 AM alerts).
3. Action: run the script from step 1.

## Mac/Linux: cron
1. Same headless command as above, saved as a shell script.
2. `crontab -e` → add a line like `*/30 7-23 * * * /path/to/news-sniper-check.sh` (every 30 minutes,
   7 AM–11 PM).

## Keep it light
- Running every 30 minutes is plenty for "same-day" urgency — there's no benefit to checking every minute,
  and it burns through search quota faster for no real gain.
- If nothing is breaking, Step 3 of the skill says so in one line and Step 4 sends no alert — a scheduled
  run that finds nothing should be silent, not a notification every 30 minutes saying "nothing happening."
- This is entirely optional. Running the skill by hand whenever the creator wonders "is anything happening?"
  works fine with zero setup — scheduling is for creators who want it running in the background.
