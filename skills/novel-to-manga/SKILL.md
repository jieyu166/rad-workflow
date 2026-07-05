---
name: novel-to-manga
description: Convert novel text, web-novel chapters, or prose scenes into manga/comic production plans and image-generation prompts. Use when the user asks to turn a novel into manga, make comic pages from story text, create manga page prompts, generate character/scene bibles, split prose into beats/panels/pages, batch-generate comic images, or revise generated manga pages while preserving character consistency.
---

# Novel To Manga

Use this skill to transform prose into a manga production package: story analysis, scene and beat breakdown, page/panel plans, character and scene bibles, image-generation prompts, and optional page-by-page image generation.

## Operating Rules

- Preserve the original story order. Do not skip key emotional turns, reveals, jokes, action beats, or dialogue.
- Ask for missing constraints only when needed: target page count, manga style, reading direction, aspect ratio, color vs black-and-white, and whether image generation should be run.
- For research-based manga such as historical, educational, travel, biography, or public-domain classic adaptations, collect and summarize source material before planning pages.
- If the user provides character reference images, use them as the visual source of truth. If no image is provided, create a character bible before generating prompts.
- Keep generated dialogue short enough to fit balloons. Prefer Traditional Chinese dialogue when the user writes Chinese or asks for Chinese output.
- Use consistent names, hairstyles, clothing, body type, props, locations, and tone across all pages.
- Treat image models as fallible: generate structured prompts with explicit panel count, panel content, character consistency, readable text requirements, and continuity anchors.
- For long novels, process one chapter or one scene range at a time and maintain a continuity bible.
- For book-length or batch production, keep a production tracker with page status, prompt status, generated-image status, and known consistency issues.

## Workflow

1. **Intake**
   - Identify source text, genre, tone, target audience, and requested output.
   - Record optional inputs: character images, style references, page count, panel density, reading direction, aspect ratio, color mode, and model/tool preference.
   - If the user wants a reusable manga-making assistant or Gemini Gem, record the fixed instructions that should persist across repeated page generations.

2. **Research and source intake**
   - Use this step when the source is a classic, historical topic, educational topic, biography, travel subject, or any project where the user has not provided full prose.
   - Gather or request sources, then summarize the usable canon, timeline, characters, locations, and must-keep events.
   - Note source reliability, adaptation boundaries, and details that should not be invented.
   - Convert research notes into a concise story outline before page planning.

3. **Story analysis**
   - Summarize the excerpt.
   - Identify characters, relationships, setting, conflict, emotional arc, and must-keep dialogue.
   - Decide how many scenes, beats, pages, and panels are needed. Default to 4-6 panels per page and 1-3 story beats per page.
   - For manga-book projects, create a page list first: page number, page theme, key event, characters, and hook.

4. **Scene breakdown**
   - Split prose into scenes with location, time, characters, mood, key action, dialogue, and visual motif.
   - Keep narration that cannot be shown visually as captions or inner monologue.

5. **Beat list**
   - Convert each scene into beats. Each beat should have action, camera/shot idea, emotional purpose, required dialogue, and continuity notes.

6. **Page plan**
   - Group beats into pages.
   - Give every page a function: establish, escalate, reveal, joke, confrontation, quiet beat, transition, cliffhanger, or resolution.
   - End each page with a clear turn, impact, question, or emotional hook when possible.
   - For long runs, produce compact page cards that can be fed to a page-generation assistant one page at a time.

7. **Character, scene, and style bibles**
   - Create bibles before image prompts when there are recurring characters or locations.
   - Include visual identity, clothing, expressions, body language, props, dialogue style, and image-prompt consistency instructions.
   - For batch image generation, also create a machine-friendly Character Baseline YAML with stable character IDs, names, roles, visual tags, props, and do-not-change constraints.
   - Create a Style Bible / Model Profile when the project has fixed settings such as color mode, aspect ratio, model name, page title placement, dialogue language, or recurring art direction.

8. **Panel script**
   - Write each page with panels, shot type, composition, characters, action, expression, dialogue, narration, SFX, and continuity notes.
   - Use concise dialogue and mark exact text that should appear in balloons.

9. **Reusable assistant setup**
   - If the user wants repeated generation in Gemini Gem, Custom GPT, or another assistant, create a reusable instruction block.
   - The reusable setup should include the Character Baseline YAML, Style Bible / Model Profile, output contract, page-card input format, and quality rules.
   - Tell the user to feed one page card at a time for better continuity control unless the model/tool explicitly supports reliable multi-page batches.

10. **Image-generation prompts**
   - Read `references/prompt-templates.md` when producing prompts or revision prompts.
   - Generate one prompt per page by default. For batch generation, group at most 3-5 pages per batch unless the user asks otherwise.
   - Include global style, character bible, scene bible, previous-page context, exact panel plan, and negative constraints.
   - Before image generation, run Prompt QA: no blank character baseline, correct panel count, exact dialogue included, style settings included, page title/page number present when required, and all recurring characters referenced by stable IDs.

11. **Image generation and review**
   - If the user asks to generate images, use the image generation tool.
   - After generation, review page readability, character consistency, panel count, story order, and text legibility.
   - For fixes, create regeneration prompts that preserve correct elements and list only the problems to fix.

12. **Cover, back cover, and packaging**
   - For manga-book projects, offer cover and back-cover prompts after the page plan is stable.
   - Cover prompts should include title, main cast, core visual motif, genre signal, style bible, and spoiler limits.
   - Back-cover prompts should include title treatment, synopsis area, smaller supporting visuals, tone, and any blank space needed for metadata.
   - Maintain a production tracker for page prompts, generated images, revisions, cover, and back cover.

## Output Package

For a full adaptation, provide these sections unless the user asks for a smaller output:

- `## Adaptation Summary`
- `## Scene Breakdown`
- `## Beat List`
- `## Page Plan`
- `## Character Bible`
- `## Scene Bible`
- `## Style Bible`
- `## Character Baseline YAML`
- `## Panel Script`
- `## Image Generation Prompts`
- `## Reusable Assistant Setup`
- `## Production Tracker`
- `## Revision Checklist`

When the user wants files, write Markdown outputs with stable names such as:

- `novel-to-manga-summary.md`
- `character-bible.md`
- `scene-bible.md`
- `style-bible.md`
- `character-baseline.yaml`
- `page-plan.md`
- `image-prompts.md`
- `gem-setup.md`
- `production-tracker.md`

## Quality Checklist

- Story order is preserved.
- Every page has a clear narrative function.
- Each panel has a visual action, not only abstract emotion.
- Dialogue is short, readable, and assigned to speakers.
- Character bible is specific enough to preserve identity across pages.
- Scene bible defines location layout, lighting, props, and mood.
- Style bible defines color mode, aspect ratio, reading direction, page-number/title placement, model/tool assumptions, and recurring art direction.
- Character baseline YAML has non-empty stable IDs and visual tags for every recurring character.
- Prompt QA passes before image generation.
- Image prompts say "complete manga page", not poster or single illustration.
- Prompts specify readable Traditional Chinese text when Chinese text appears.
- Revision prompts preserve correct page structure and only fix named issues.
- Manga-book projects include cover and back-cover prompts when requested or naturally expected.

## References

- Read `references/prompt-templates.md` for page prompt, batch prompt, and regeneration prompt templates.
