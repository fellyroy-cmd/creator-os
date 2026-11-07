---
name: sponsor-desk
description: Read a brand/sponsorship email (pasted in, or fetched read-only from Gmail), decide what package and price fits from their rate card, and draft a reply (or a polite decline) for the creator to review and send themselves — never sends anything on its own. Triggers on "draft a reply to this sponsor", "is this a good deal", "sponsor email", "check my inbox for sponsors", "/creator-os:sponsor-desk".
---

# Sponsor desk: triage a brand email, draft the reply, never send it

This skill never sends email and never agrees to a price on the creator's behalf. It can optionally **read**
the creator's own inbox (never write to it — no sending, labeling or deleting) to find candidate emails
instead of the creator pasting them by hand, see Step 1. Either way it drafts a reply **for the creator to
read, edit and send themselves.** That line doesn't move as this skill grows.

## Step 0: Load the creator
Read `creator/profile.md`. If it doesn't exist, tell the creator to run `/creator-os:setup` first and stop.
Then read `creator/rate-card.md`. If it doesn't exist, tell the creator: "I need your rate card first — copy
[`skills/sponsor-desk/references/rate-card-template.md`](references/rate-card-template.md) to
`creator/rate-card.md` and fill in your prices, floors and payment terms. I won't guess at numbers that
aren't yours." and stop.

## Step 1: Get the email
Ask the creator to paste the brand's email (or forward the text) if they haven't already.

**Tired of pasting?** If `.env` has `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD` set, run
`python scripts/fetch_sponsor_emails.py --json` yourself, right here in this step — don't ask the creator to
open a terminal, that's the whole point of this option. Add `--days` to widen the window if nothing recent
comes back. The `--json` output is a numbered array (`id`, `from`, `subject`, `date`, `body`); turn it into a
short numbered list in chat (subject + sender + how recent) and ask which one to triage by number — never
pick for them. An `{"error": "..."}` result (missing `.env`, bad app password, etc.) means something's wrong
with the connection, not that there's nothing to show — read the message and relay it plainly. An empty `[]`
genuinely means no matches in that window; say so and offer to widen `--days` or fall back to pasting.
No `.env` secrets set yet? Point the creator at
[references/gmail-connection.md](references/gmail-connection.md) once, then fall back to pasting for this
run. This connection is **read-only** — it cannot send, label, or delete anything, see the reference for why
that's guaranteed and not just a promise.

Either way, pull out from the chosen email:
- Brand name and what they're selling
- What they're asking for (a short? a video segment? a newsletter mention? something not on the rate card?)
- Any price, timeline or exclusivity terms they've already proposed
- How they contacted the creator (cold outreach vs. a reply to something the creator posted)

## Step 2: Check it against the auto-decline list first
Before anything else, check `creator/rate-card.md`'s "Auto-decline" section (gambling, crypto schemes, a tool
the creator wouldn't actually use, obvious spam). A match → skip straight to **Step 5 (decline draft)** and
say why in one line. Don't spend time pricing an offer that was never going to happen.

## Step 3: Match it to a package and price
Using [references/triage-rules.md](references/triage-rules.md):
1. Find the closest package on the rate card to what the brand is asking for.
2. If the brand already named a number: compare it to that package's **list price** and **floor**.
3. Decide which of the four outcomes in the triage rules applies: quote list price, accept their offer, counter
   once, or flag the creator without replying. Say which one and why, in plain language, before drafting anything.

## Step 4: Draft the reply
Write a short, warm, specific reply — never generic — using
[references/reply-templates.md](references/reply-templates.md) as the shape, filled in with this brand's
actual details (never a placeholder left unfilled). Include:
- A one-line thank-you that references what they actually make/do (proves the creator read the email)
- The package and price (or counter) from Step 3
- Payment terms and usage rights from the rate card, stated plainly
- A clear next step ("if that works, I'll send a deposit link")

## Step 5: Decline draft (auto-decline matches, or the creator says no)
Short, polite, no explanation owed, door left open for the future if the mismatch is about timing/fit rather
than ethics. Template in [references/reply-templates.md](references/reply-templates.md).

## Step 6: Flag instead of drafting
Some situations get a flag to the creator instead of a draft — see "Always flag, don't draft" in
[references/triage-rules.md](references/triage-rules.md) (contracts needing a signature, offers above the
creator's "flag me" threshold, anything in the rate card's ethics grey zone, requests for personal/financial
details). Say plainly what's unusual about it and let the creator decide — don't draft a reply that papers
over a real decision.

## Step 7: Save and hand off
Save the triage + draft to `content/sponsors/[YYYY-MM-DD]-[brand-name].md` (create the folder if it doesn't
exist) with this shape:

```
# [Brand] — [date]

**They offered:** [what they asked for, verbatim summary]
**Outcome:** [quote list / accept / counter / decline / flagged] — [one-line why]

## Draft reply
[the full drafted email, ready to copy-paste]

## Status
- [ ] Sent
- [ ] Replied
- [ ] Deposit received
- [ ] Delivered
```

Tell the creator the path and remind them: **this is a draft.** Nothing goes out until they copy it into
their own email and hit send.
