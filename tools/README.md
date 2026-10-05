# Updating website data from the Google Sheet

1. In Google Sheets: File -> Download -> Microsoft Excel (.xlsx).
2. Save it over `assets/CCS Research Activity.xlsx` (this file is git-ignored; it is NOT published).
3. Run `python3 tools/build_data.py` (needs `pip install openpyxl`).
4. Commit and push `assets/data/site-data.json`.

Only whitelisted sheets/columns reach `site-data.json` (see the top of `build_data.py`).
Names, contact details, peer reviews, applications and free-text notes are never copied.

## What the sheet drives
- Core Area columns (Projects Proposed / Sanctioned, Internship Projects): per-area counts, pipeline and student project titles on research.html. Blank = keyword rules in `build_data.py`.
- Standard Institution / Institution Type (Internship Projects): override the institution rules on impact.html. Yellow = needs review.
- Publication Summary, Journals Spanned: paper and citation tiles on impact.html.
- Key Findings: cards on research.html. Put the figure in `assets/images/findings/` and use its filename in the sheet.

Update steps: save the sheet over `assets/CCS Research Activity.xlsx`, run `python3 tools/build_data.py`, commit `assets/data/site-data.json`.

## Facilities (devices and photos)
Cards on the home page come from `assets/data/facilities.json`. To add a device, add an item to a category (copy an existing one). Drop its photo in `assets/images/facilities/` named `<id>.jpg` (or .png/.webp), or set `"image"` to the file name. Clicking a card flips it to show the photo; without a photo it shows "Photo coming soon".

## Ideas page (internal)
`ideas.html` shows proposal counts by year and area from `assets/data/ideas.json` (built by `build_data.py`). It is not linked from the site and is marked noindex. Note: GitHub Pages is public, so anyone with the URL can open it; it holds counts only, no titles. Project costs and proposal statistics are deliberately left out of `site-data.json`.
