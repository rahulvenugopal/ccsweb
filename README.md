# CCS website

Website of the Centre for Consciousness Studies (CCS), NIMHANS, Bengaluru: https://www.ccsnimhans.com/

It is a static site hosted on GitHub Pages (`CNAME` sets the domain). There is no build step for the pages themselves. A small Python script turns the CCS research activity register into a public JSON file that the pages read in the browser.

## Pages

| Page | What it shows |
|---|---|
| `index.html` | Home: about, stats band, four core areas, publications, **facilities** (flip cards), events, opportunities, contact |
| `research.html` | Four core areas, research framework, sanctioned projects, student and intern projects, funding partners, key findings |
| `impact.html` | Placements, trainee institutions, talks, events, papers by core area, preprints, conference papers and posters |
| `publications.html` | Full publication list with search |
| `projects.html`, `media.html` | Project highlights and media |
| `ideas.html` | **Internal** view of idea generation (proposal counts). Unlisted and noindex; not linked from the site |

## Data

```
CCS Research Activity.xlsx   (private, git-ignored)
        |  python3 tools/build_data.py
        v
assets/data/site-data.json   public; read by the pages
assets/data/ideas.json       counts only; read by ideas.html
assets/data/facilities.json  hand-edited; read by the Facilities section
```

- The workbook never leaves your computer (`*.xlsx` is in `.gitignore`). Only the JSON files are committed.
- The public JSON deliberately contains no project costs and no proposal statistics.
- Core areas come from the **Core Area** column on the Proposed, Sanctioned, Internship and Publications sheets. A blank cell falls back to keyword rules in `tools/build_data.py`.
- Institutions can be corrected in the **Standard Institution** and **Institution Type** columns (yellow rows need review).
- Paper counts use the **Publications** sheet (Year, Status, Core Area, Output type, Citations). Counts cover published items from 2020, and preprints, conference papers and abstracts/posters are counted separately.
- Key findings cards come from the **Key Findings** sheet; their images live in `assets/images/findings/`.

### Updating the site data

1. Download or edit the workbook and save it as `assets/CCS Research Activity.xlsx`.
2. `pip install openpyxl` (once), then `python3 tools/build_data.py`.
3. Commit `assets/data/*.json` (and any new images), then push to `main`. GitHub Pages republishes in a minute or two.

See `tools/README.md` for column-level details.

### Adding a device to Facilities

Add an item to `assets/data/facilities.json` (copy an existing one) and put its photo in `assets/images/facilities/` as `<id>.jpg` (or `.png`/`.webp`). Clicking a card flips it to the photo; with no photo it shows "Photo coming soon".

## Structure

```
assets/data/     JSON read by the pages
assets/images/   team, backgrounds, figures, findings, facilities
assets/js/       ccs-charts.js / .css (dependency-free SVG charts)
tools/           build_data.py and its README
```

## Design notes

Dark and light sections share the CSS tokens at the top of each page (ink `#0D1B2A`, saffron `#E8830A`, teal `#24A0A0`; Cormorant Garamond, Source Serif 4, DM Mono). Charts are hand-drawn SVG with a table fallback and keyboard-focusable marks.

## Release

Releases are tagged `vMAJOR.MINOR.PATCH`; see `RELEASE_NOTES.md`.
