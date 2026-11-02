# Contributing to Creator OS

Thanks for helping. Most contributions here are **writing, not code**: a skill is a Markdown file that tells
Claude how to do one creator job well.

## Add a skill

1. Fork the repo and create `skills/<your-skill-name>/SKILL.md` (lowercase, hyphens).
2. Start it with this frontmatter:

   ```markdown
   ---
   name: your-skill-name
   description: What it does and when to use it, in 1–3 sentences. Include the phrases a creator would say, e.g. "write a pinterest pin".
   ---
   ```

3. Follow the house pattern (copy [`skills/ideas/SKILL.md`](skills/ideas/SKILL.md) as a starting point):
   - **Step 0 reads `creator/profile.md`** and stops with "run `/creator-os:setup` first" if it's missing.
   - Numbered steps, plain language, one job per skill.
   - **Saves its output** to a dated file under `content/` and says where.
   - **Honesty rule:** no invented numbers, quotes or sources.
4. Longer reference material (formulas, examples) goes in `skills/<name>/references/` and is linked from SKILL.md.
5. Run the checker: `python scripts/validate.py`
6. Test it for real: install your fork locally (below), run the skill on a real piece of content and paste
   the output (or a screenshot) in your pull request.

## Test your fork locally

```
/plugin marketplace add /path/to/your/creator-os
/plugin install creator-os@creator-os
```

After editing a skill, run `/plugin` to update or reinstall it so Claude picks up the change.

## Improve an existing skill

Open an issue first if it changes how the skill works, so we can agree on it before you write it.
Small wording or format fixes can go straight to a pull request.

## Ground rules

- Keep skills **niche-neutral**. Anything specific to one creator belongs in their `creator/profile.md`, not in a skill.
- No paid APIs required for core skills. If a skill needs one, say so at the top and make it optional.
- Be kind in reviews. Lots of people here are making their first pull request.
