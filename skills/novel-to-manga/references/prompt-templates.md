# Novel To Manga Prompt Templates

Use these templates when the user asks for image-generation prompts, batch prompts, or revisions.

## Analysis Output Skeleton

```markdown
## Adaptation Summary
- Source length:
- Target format:
- Genre and tone:
- Suggested page count:
- Suggested panel density:
- Must-keep moments:
- Visual risks:

## Scene Breakdown
### Scene 1
- Location:
- Time:
- Characters:
- Mood:
- Key action:
- Required dialogue:
- Visual motif:
- Suggested pages:

## Beat List
### Scene 1
#### Beat 1
- Story action:
- Visual action:
- Camera / shot:
- Emotion:
- Dialogue:
- Continuity notes:
```

## Character Bible

```markdown
## Character Bible

### Character Name
- Role:
- Age / apparent age:
- Body type:
- Face:
- Hair:
- Eyes:
- Clothing:
- Props:
- Signature expressions:
- Body language:
- Speech style:
- Relationship cues:
- Do-not-change:

### Image prompt anchor
Keep this character visually consistent across all manga pages. Do not change hairstyle, hair color, eye shape, body type, clothing silhouette, or signature props.
```

## Character Baseline YAML

Use this machine-friendly format for long manga books, Gemini Gem setup, batch generation, or any workflow where character identity must be copied into many prompts.

```yaml
characters:
  - id: "character_id"
    name_zh: "角色中文名"
    role: "角色定位 / 故事功能"
    age_or_apparent_age: "年齡或外觀年齡"
    visual_tags: >-
      English or bilingual prompt tags that preserve identity, face, body type,
      hair, clothing silhouette, signature props, aura, and recurring pose.
    dialogue_style: "說話風格，口頭禪，語氣"
    relationship_cues:
      - "和其他角色互動時要保留的關係線索"
    do_not_change:
      - "髮型"
      - "服裝輪廓"
      - "代表道具"
    first_appears: "Page X"
    recurring_pages:
      - "Page X"
      - "Page Y"
```

Checklist:

1. Every recurring character has a stable `id`.
2. `visual_tags` is never blank.
3. Signature props and silhouette are explicit.
4. Do-not-change constraints are concrete.
5. Character IDs are used in every page prompt where that character appears.

## Scene Bible

```markdown
## Scene Bible

### Scene / Location Name
- Location layout:
- Time of day:
- Lighting:
- Weather:
- Props:
- Background details:
- Mood:
- Camera language:
- Continuity constraints:

### Image prompt anchor
Use the same location layout, lighting, props, and mood whenever this scene appears.
```

## Style Bible / Model Profile

Use this when fixed visual settings should be repeated across all pages or embedded into a reusable assistant.

```markdown
## Style Bible / Model Profile

- Project title:
- Target model/tool:
- Page format: complete manga page
- Aspect ratio:
- Color mode: full color / black-and-white / limited palette
- Reading direction:
- Panel density:
- Art style:
- Rendering tags:
- Dialogue language:
- Title/page-number placement:
- Text rules:
- Cover style:
- Back-cover style:
- Negative constraints:
- Batch size limit:
```

Example compact style line:

```text
Full-color historical fantasy manga, cel-shaded color, vivid but controlled palette, cinematic lighting, detailed backgrounds, dynamic camera angles, 9:16 vertical page, readable Traditional Chinese text, page title and page number at the top-left, complete manga page with clear panel borders.
```

## Page List

Use this before detailed scripting for 10+ page manga-book projects.

```markdown
## Page List

| Page | Theme | Key event | Characters | Location | Page function | Hook |
| --- | --- | --- | --- | --- | --- | --- |
| 1 |  |  |  |  | establish |  |
```

## Page Input Card

Use this lightweight format when feeding one page at a time into Gemini Gem, Custom GPT, or an image model workflow.

```markdown
## Page X

- Theme:
- Page function:
- Characters by ID:
- Location / scene ID:
- Previous page context:
- Required title text:
- Required dialogue language:
- Panel count:

### Panels
1. Shot:
   Visual:
   Characters:
   Dialogue:
   SFX:
2. Shot:
   Visual:
   Characters:
   Dialogue:
   SFX:

- Final panel emphasis:
- Continuity notes:
```

## Page And Panel Script

```markdown
# Page X

Page function:
Page beats:
Mood:
Setting:
Characters:
Continuity notes:

## Panel 1
- Shot:
- Composition:
- Characters:
- Action:
- Expression:
- Dialogue:
- Narration:
- SFX:
- Background:

## Panel 2
...

Final panel emphasis:
```

## Single Page Image Prompt

```text
Create Page X of a complete manga adaptation.

Global style:
- polished black-and-white Japanese manga style
- clean line art
- professional screentone shading
- crisp panel borders
- expressive faces
- cinematic panel composition
- complete manga page, not a poster, not a single illustration
- page number at the bottom corner
- readable Traditional Chinese dialogue

Reading and layout:
- [left-to-right or right-to-left]
- [page aspect ratio]
- [panel count] panels
- do not skip any panel

Character consistency:
[Insert character bible or image-reference mapping]

Scene consistency:
[Insert scene bible]

Previous page context:
[One sentence summary]

This is Page X.

Page function:
[Page function]

Panel plan:

Panel 1:
- Shot:
- Visual:
- Characters:
- Emotion:
- Dialogue:
- Narration:
- SFX:

Panel 2:
...

Final panel emphasis:
[Final beat, joke, reveal, transition, or cliffhanger]

Important:
- Keep dialogue legible.
- Use Traditional Chinese text exactly as written.
- Keep character hairstyles, clothing, body type, and props consistent.
- Use the listed character IDs and their Character Baseline YAML.
- Maintain coherent page flow.
- Do not merge panels.
- Do not add unrelated characters or events.
```

## Reusable Assistant / Gemini Gem Setup

Use this when the user wants a repeated manga-production helper that receives one page card at a time and turns it into image prompts or direct generation instructions.

```text
You are a manga production assistant.

Goal:
Create consistent complete manga pages from page cards. Each output must preserve the story order, panel count, recurring character identities, style bible, page title, page number, and readable dialogue.

Character Baseline YAML:
[Insert Character Baseline YAML]

Style Bible / Model Profile:
[Insert Style Bible / Model Profile]

Scene Bible:
[Insert Scene Bible or recurring location anchors]

Input format:
The user will provide one Page Input Card at a time. Treat it as the source of truth for page number, theme, panel count, characters, dialogue, and final panel emphasis.

Output format:
1. Prompt QA checklist with pass/fix notes.
2. Final image-generation prompt for the page.
3. If direct image generation is available, generate the page after the prompt is complete.

Rules:
- Do not leave character baseline fields blank.
- Do not change character IDs, names, hairstyles, clothing silhouettes, body types, or signature props.
- Do not skip, merge, or add panels unless the page card asks for it.
- Keep all visible text in readable Traditional Chinese when the page card is Chinese.
- Include page title and page number exactly where the Style Bible says.
- Ask for clarification only if the page card is missing page number, panel count, or recurring character identity.
```

## Prompt QA Checklist

Run this before generating images:

1. Source/page card has page number and theme.
2. Panel count is explicit and matches the prompt.
3. Character Baseline YAML is present and non-empty for recurring characters.
4. All recurring characters in the page use stable IDs.
5. Style Bible / Model Profile is included.
6. Aspect ratio, color mode, reading direction, and title/page-number placement are included when relevant.
7. Dialogue text is exact, short, and assigned to speakers.
8. Required language is explicit, especially Traditional Chinese.
9. Final panel emphasis is present.
10. Negative constraints prevent posters, single illustrations, merged panels, unrelated events, and garbled text.

## Batch Prompt

Use batch prompts only for short runs. Prefer 3-5 pages per batch.

```text
Batch generate Page X to Page Y as complete manga pages.

Global style:
- black-and-white Japanese manga
- clean line art
- screentone shading
- crisp panel borders
- readable Traditional Chinese dialogue
- consistent character design
- coherent scene continuity
- each page must be a complete manga page
- each page must include page number
- do not skip middle events
- each page should end with a clear emotional beat, joke, transition, or cliffhanger

Reference images:
- Use provided character images as visual references.
- Keep each character consistent with their assigned reference.
- If a character has no image reference, use the character bible.

Character Bible:
[Insert character bible]

Scene Bible:
[Insert scene bible]

Style Anchor:
[Describe or reference previously generated page style]

---

## Page X Prompt
[Insert single page prompt content]

---

## Page X+1 Prompt
[Insert single page prompt content]
```

## Revision Checklist

Check each generated page for:

1. Story order preserved.
2. Correct number of panels.
3. No missing important beat.
4. Character identities consistent.
5. Clothing and hairstyle consistent.
6. Dialogue readable and assigned to correct speaker.
7. Traditional Chinese text is not garbled.
8. Final panel has impact.
9. Page is a manga page, not a poster.
10. No unrelated objects, characters, or events.

## Production Tracker

Use this for manga-book projects, especially 10+ pages.

```markdown
## Production Tracker

| Page | Theme | Script | Prompt QA | Image | Revision Needed | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Cover |  | pending | pending | pending |  |  |
| 1 |  | pending | pending | pending |  |  |
| Back cover |  | pending | pending | pending |  |  |
```

Suggested statuses: `pending`, `drafted`, `passed`, `generated`, `needs-revision`, `final`.

## Regenerate Whole Page Prompt

```text
Regenerate Page X.

Keep:
- same manga style
- same page number
- same character designs
- same scene
- same panel count
- same story order
- all correct dialogue from the original panel plan

Fix:
1. [Problem 1]
2. [Problem 2]
3. [Problem 3]

Requirements:
- do not remove any important story beat
- improve panel readability
- make Traditional Chinese dialogue clearer
- preserve character consistency
- strengthen the final panel impact

Original panel plan:
[Insert panel plan]
```

## Revise One Panel Prompt

```text
Revise only Panel X of Page Y.

Keep:
- rest of the page concept unchanged
- same character design
- same manga style
- same story order

Problem:
[Describe problem]

Correction goal:
[Describe desired change]

Panel X should show:
[Corrected panel description]
```

## Cover Prompt

```text
Create the front cover for this manga book.

Title:
[Title]

Style Bible / Model Profile:
[Insert style bible]

Character Baseline YAML:
[Insert relevant main cast]

Cover concept:
- Main visual:
- Mood:
- Main characters:
- Background / motif:
- Spoiler limits:
- Title placement:
- Additional text:

Requirements:
- Make this a book cover, not an interior manga page.
- Keep character designs consistent with the Character Baseline YAML.
- Use readable Traditional Chinese title text exactly as written.
- Leave clean space for title and author text if needed.
```

## Back Cover Prompt

```text
Create the back cover for this manga book.

Title:
[Title]

Style Bible / Model Profile:
[Insert style bible]

Back-cover concept:
- Summary area:
- Supporting visual:
- Mood:
- Background:
- Space for metadata / barcode / class info:

Requirements:
- Make this a back cover, not an interior manga page.
- Keep the design visually consistent with the front cover.
- Leave readable blank or low-detail space for synopsis text.
- Do not spoil the ending unless requested.
```
