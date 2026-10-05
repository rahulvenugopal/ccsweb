# Release notes

## v2.0.0 (5 October 2026)

A major update that brings the CCS overview deck's content into the site and makes it data-driven.

### New pages
- **Research**: the research framework, four core areas, sanctioned projects, student and intern projects by area, funding partners, and a filterable "Key findings from our science" section with 15 figures.
- **Impact**: placements by year, trainee institutions (with an institution-type breakdown), talks, events, papers since 2020 by core area, and separate counts for preprints, conference papers and posters/abstracts.
- **Ideas** (internal, unlisted): proposal counts by year and area. Not linked from the site and marked noindex.

### Changes to existing pages
- **Home**: new stats band, four core-area cards, and updated navigation (Research, Impact).
- **Facilities**: now rendered from `assets/data/facilities.json`. Each device card flips to show a photo from `assets/images/facilities/`. New devices need no HTML edits.
- **Publications**: 15 papers added from the sheet and the published-papers folder (Sleep Medicine, Annals of Indian Academy of Neurology, preprints, Springer proceedings and others), taking the list from 101 to 116.
- Core areas are now Sleep & dream science; Mind–body & contemplative science; Clinical & developmental neuroscience; and Neurotechnology & translational neuroscience (animal and cell studies now sit here), plus cross-cutting methods for methods work.

### Data pipeline
- New `tools/build_data.py` builds `assets/data/site-data.json` and `ideas.json` from the private research activity workbook. Add or edit rows in the sheet, rerun the script, and commit the JSON.
- The workbook is git-ignored, along with the local `Claude outputs/` folder.
- New dependency-free charts in `assets/js/ccs-charts.js` and `.css` (accessible, with table fallback).

### Removed
- Project costs and proposal statistics are no longer shown on any public page or included in `site-data.json`.
- Content related to UNISON and NIYAMITA was left out.

### Notes
- Paper counts are 2020 onward, journal articles and book chapters only. Citation counts are blank until filled in the sheet.
- Figures in "Key findings" are crops from published papers; confirm reuse permission.
- Photos are in for 7 of the 18 devices (EEG systems, HydroCel net, Muse, polysomnography); the other cards show "Photo coming soon" until their photos are added. The photos are large PNGs (about 7 MB in total); compressing them would speed up the page.
- This release also publishes the existing local commit "bugfixes", which was ahead of `origin/main`.
