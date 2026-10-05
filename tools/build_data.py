#!/usr/bin/env python3
"""
Build the website's public data file from the CCS Research Activity workbook.

  python3 tools/build_data.py            # uses assets/CCS Research Activity.xlsx
  python3 tools/build_data.py other.xlsx

Output: assets/data/site-data.json  (this is the ONLY file the website reads).

PRIVACY: the workbook itself is git-ignored and must never be committed (the repo
and site are public). Only the sheets/columns listed below are copied out. Never
read: Internship Applications, Review, PotentialCollab, Collaboration, Visitors,
intern/PhD names, contact details, investigator lists, free-text status notes.
Requires: pip install openpyxl
"""
import json, re, sys, datetime as dt
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "assets" / "CCS Research Activity.xlsx"
OUT = ROOT / "assets" / "data" / "site-data.json"
IDEAS_OUT = ROOT / "assets" / "data" / "ideas.json"   # internal page only (ideas.html)


def clean(v):
    return re.sub(r"\s+", " ", str(v)).strip() if v is not None else ""


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def year(v):
    if isinstance(v, (dt.datetime, dt.date)):
        return v.year
    m = re.search(r"(20\d\d)", clean(v))
    return int(m.group(1)) if m else None


def iso(v):
    if isinstance(v, dt.datetime):
        return v.date().isoformat()
    return clean(v) or None


def iso_range(v):
    """'09/09/2025 to 11/09/2025' (dd/mm/yyyy) -> ('2025-09-09', 3). Returns (None, None) if not that shape."""
    m = re.match(r"\s*(\d{1,2})[/.](\d{1,2})[/.](\d{4})\s*(?:to|-|\u2013)\s*(\d{1,2})[/.](\d{1,2})[/.](\d{4})", clean(v))
    if not m: return None, None
    d1 = dt.date(int(m[3]), int(m[2]), int(m[1])); d2 = dt.date(int(m[6]), int(m[5]), int(m[4]))
    return d1.isoformat(), (d2 - d1).days + 1


def rows(wb, name):
    ws = wb[name]
    it = ws.iter_rows(values_only=True)
    head = [clean(c) for c in next(it)]
    for r in it:
        if any(c is not None for c in r[:6]):
            yield {head[i]: r[i] for i in range(len(head)) if head[i]}


def project_status(text):
    t = clean(text).lower()
    if "hold" in t: return "On hold"
    if "manuscript" in t: return "Manuscript under review"
    if "ongoing" in t or "pilot" in t or "underway" in t: return "Ongoing"
    if "complet" in t: return "Completed"
    return "Sanctioned"


# Core research areas. Rules are checked in order; the first keyword hit wins.
# Edit here if a project lands in the wrong area. Unmatched -> "cross" (cross-cutting).
AREAS = [
    ("neurotech", ["tacs", "tvns", "closed-loop", "closed loop", "neurofeedback", "technology development",
                   "wearable", "olfactometer", "stimulation", "gurney", "brain-computer"]),
    ("sleep", ["dream", "sleep", "spindle", "insomnia", "polysomnograph", "psg"]),
    ("clinical", ["photoperiod", "chronic pain", "adolescent", "schizophrenia", "depression", "anxiety",
                  "hallucination", "epilepsy", "addiction", "cognitive ageing", "child cognitive", "coma", "mci"]),
    ("mindbody", ["meditat", "yoga", "vipassana", "raja", "kundalini", "sky ", "upanishad", "consciousness",
                  "heartfulness", "breath", "mind-wandering"]),
]


def area_of(title):
    t = " " + clean(title).lower() + " "
    for key, words in AREAS:
        if any(w in t for w in words):
            return key
    return "cross"


# Institutions: (regex on lowercase name, canonical name, category)
CAT_NATIONAL = "IITs, IISERs & national institutes"
CAT_MEDICAL = "Medical & health sciences"
CAT_UNIV = "Universities & colleges"
CAT_INTL = "International"
INSTITUTES = [
    (r"trinity college", "Trinity College Dublin", CAT_INTL), (r"amsterdam", "University of Amsterdam", CAT_INTL),
    (r"unito|turin", "University of Turin", CAT_INTL), (r"sydney", "University of Sydney", CAT_INTL),
    (r"iit gandhinagar", "IIT Gandhinagar", CAT_NATIONAL), (r"iit madras", "IIT Madras", CAT_NATIONAL),
    (r"iit mandi", "IIT Mandi", CAT_NATIONAL), (r"iit hyderabad", "IIT Hyderabad", CAT_NATIONAL),
    (r"iiser[- ]?mohali", "IISER Mohali", CAT_NATIONAL), (r"iiser[- ]?tirupati", "IISER Tirupati", CAT_NATIONAL),
    (r"iiser[- ]?pune", "IISER Pune", CAT_NATIONAL), (r"iiser[- ]?berhampur", "IISER Berhampur", CAT_NATIONAL),
    (r"um-dae|cebs", "UM-DAE CEBS, Mumbai", CAT_NATIONAL), (r"nfsu", "NFSU, Gandhinagar", CAT_NATIONAL),
    (r"rashtriya raksha", "Rashtriya Raksha University", CAT_NATIONAL),
    (r"aiims", "AIIMS Bhopal", CAT_MEDICAL), (r"jss aher", "JSS AHER, Mysuru", CAT_MEDICAL),
    (r"mahe|manipal", "MAHE, Manipal", CAT_MEDICAL), (r"trivandrum medical", "Govt. Medical College, Thiruvananthapuram", CAT_MEDICAL),
    (r"svyasa", "S-VYASA, Bengaluru", CAT_MEDICAL),
    (r"christ university", "Christ University", CAT_UNIV), (r"st\.? joseph", "St Joseph's University", CAT_UNIV),
    (r"ramaiah", "M.S. Ramaiah University", CAT_UNIV), (r"jain university", "JAIN University", CAT_UNIV),
    (r"dayananda sagar", "Dayananda Sagar University", CAT_UNIV), (r"bangalore institute of technology", "Bangalore Inst. of Technology", CAT_UNIV),
    (r"cusat|cochin university", "CUSAT, Kochi", CAT_UNIV), (r"gitam", "GITAM", CAT_UNIV),
    (r"jiwaji", "Jiwaji University, Gwalior", CAT_UNIV), (r"university of hyderabad", "University of Hyderabad", CAT_UNIV),
    (r"ignou", "IGNOU", CAT_UNIV), (r"mit world peace|mit-wpu", "MIT World Peace University", CAT_UNIV),
    (r"\bvit\b", "VIT, Vellore", CAT_UNIV), (r"university of rajasthan", "University of Rajasthan", CAT_UNIV),
]


AREA_LABELS = {
    "sleep": "Sleep & dream science", "mindbody": "Mind\u2013body & contemplative science",
    "clinical": "Clinical & developmental neuroscience", "neurotech": "Neurotechnology & translational neuroscience",
    "cross": "Cross-cutting methods",
}
LABEL_TO_KEY = {v.lower(): k for k, v in AREA_LABELS.items()}
LABEL_TO_KEY["neurotechnology & closed-loop modulation"] = "neurotech"   # old labels still accepted
LABEL_TO_KEY["basic & translational neuroscience"] = "neurotech"


def area_from_sheet(value, title):
    """Core Area column wins; blank -> keyword rules."""
    k = LABEL_TO_KEY.get(clean(value).lower())
    return k or area_of(title)


def institute_of(name):
    t = clean(name).lower()
    for pat, canon, cat in INSTITUTES:
        if re.search(pat, t):
            return canon, cat
    return clean(name), CAT_UNIV  # unknown: keep the typed name, file under universities


# Funders: (regex on lowercase agency, canonical label, group). First hit wins.
FUNDERS = [
    (r"wellcome|india alliance", "Wellcome\u2013DBT India Alliance", "Foundations & international"),
    (r"peace|mind.?life", "Mind & Life (PEACE)", "Foundations & international"),
    (r"rerf|sparc", "RERF-SpARC", "Foundations & international"),
    (r"temple", "Temple of Consciousness", "Foundations & international"),
    (r"sree|sreepvf", "SreePVF", "Foundations & international"),
    (r"svyasa", "SVYASA", "Foundations & international"),
    (r"turtle", "Turtle Technologies", "Industry"), (r"wakefit", "Wakefit", "Industry"),
    (r"satyam|shri", "DST-SATYAM / SHRI", "Government"), (r"csri", "DST-CSRI", "Government"),
    (r"bdtd", "DST-BDTD", "Government"), (r"serb", "DST-SERB", "Government"), (r"crg", "DST-CRG", "Government"),
    (r"icmr", "ICMR", "Government"), (r"birac|bdt-birac", "BIRAC", "Government"), (r"anrf", "ANRF", "Government"),
    (r"iks", "IKS (MoE)", "Government"), (r"ccras|ayush", "CCRAS-AYUSH", "Government"), (r"\bdbt\b", "DBT", "Government"),
]


def funder_of(agency):
    t = clean(agency).lower()
    for pat, canon, grp in FUNDERS:
        if re.search(pat, t):
            return canon, grp
    return clean(agency)[:40], "Other"


def outcome_of(status):
    t = clean(status).lower()
    if t.startswith("sanction"): return "sanctioned"
    if "reject" in t or "not funded" in t: return "not_funded"
    return "pipeline"  # under review, submitted, LoI


def count_by_year(items):
    out = {}
    for y in items:
        if y: out[str(y)] = out.get(str(y), 0) + 1
    return dict(sorted(out.items()))


def main():
    wb = openpyxl.load_workbook(SRC, data_only=True)

    sanc = list(rows(wb, "Projects Sanctioned"))
    sanctioned = [{
        "title": clean(r.get("Title")),
        "agency": clean(r.get("Agency")),
        "budget_lakhs": num(r.get("Budget (in Lakhs)")),
        "status": project_status(r.get("Status")),
        "start_year": year(r.get("Start")),
        "area": area_from_sheet(r.get("Core Area"), r.get("Title")),
    } for r in sanc]

    prop = list(rows(wb, "Projects Proposed"))
    prop_status = {}
    for r in prop:
        raw = clean(r.get("Status"))
        s = "LoI obtained" if "loi" in raw.lower() else (raw.title() or "Other")
        prop_status[s] = prop_status.get(s, 0) + 1

    areas = {k: {"sanctioned": 0, "funding_lakhs": 0.0} for k, _ in AREAS}
    areas["cross"] = {"sanctioned": 0, "funding_lakhs": 0.0}
    for sp in sanctioned:
        a = areas[sp["area"]]; a["sanctioned"] += 1; a["funding_lakhs"] = round(a["funding_lakhs"] + (sp["budget_lakhs"] or 0), 2)

    for a in areas.values():
        a["pipeline"] = 0; a["students"] = 0; a["student_titles"] = []
    for r in prop:
        if outcome_of(r.get("Status")) == "pipeline":
            areas[area_from_sheet(r.get("Core Area"), r.get("Title"))]["pipeline"] += 1
    seen_titles = set()
    for r in rows(wb, "Internship Projects"):
        t = clean(r.get("Title of Project"))
        if not t: continue
        a = areas[area_from_sheet(r.get("Core Area"), t)]
        a["students"] += 1
        if t.lower() not in seen_titles:
            seen_titles.add(t.lower()); a["student_titles"].append(t)

    # ---- proposals: outcome by submission year ----
    by_year, outcomes = {}, {"sanctioned": 0, "pipeline": 0, "not_funded": 0}
    for r in prop:
        o = outcome_of(r.get("Status")); outcomes[o] += 1
        y = year(r.get("Month of Submission"))
        if y:
            by_year.setdefault(str(y), {"sanctioned": 0, "pipeline": 0, "not_funded": 0})[o] += 1
    proposals_by_year = dict(sorted(by_year.items()))

    # ---- funders engaged (sanctioned + proposed) ----
    fund = {}
    for src in (sanc, prop):
        for r in src:
            if not r.get("Agency") or "non-funded" in clean(r.get("Agency")).lower(): continue
            name, grp = funder_of(r.get("Agency"))
            fund.setdefault(grp, {})
            fund[grp][name] = fund[grp].get(name, 0) + 1
    funders = {g: [{"name": n, "count": c} for n, c in sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))]
               for g, d in sorted(fund.items())}

    # ---- trainee institutions (names of institutions only, never people) ----
    interns_all = list(rows(wb, "Internship Projects"))
    inst = {}
    for r in interns_all:
        if not r.get("Institute of Intern"): continue
        name, cat = institute_of(r.get("Institute of Intern"))
        if clean(r.get("Standard Institution")): name = clean(r.get("Standard Institution"))
        if clean(r.get("Institution Type")) in (CAT_NATIONAL, CAT_MEDICAL, CAT_UNIV, CAT_INTL): cat = clean(r.get("Institution Type"))
        inst.setdefault(cat, {})
        inst[cat][name] = inst[cat].get(name, 0) + 1
    order = [CAT_NATIONAL, CAT_MEDICAL, CAT_UNIV, CAT_INTL]
    institutions = {c: [{"name": n, "count": k} for n, k in sorted(inst.get(c, {}).items(), key=lambda kv: (-kv[1], kv[0]))]
                    for c in order}

    events = []
    for r in rows(wb, "Events Organised"):
        start, days = iso(r.get("Start Date")), num(r.get("No of Days"))
        if start and not re.match(r"^\d{4}-\d{2}-\d{2}$", start):
            start, rng_days = iso_range(start)
            days = days or rng_days
        events.append({
            "title": clean(r.get("Title")), "type": clean(r.get("Event Type")),
            "start": start, "days": days,
            "organised_with": clean(r.get("Organised with")), "place": clean(r.get("Place")),
        })
    events.sort(key=lambda e: e["start"] or "", reverse=True)

    talks = list(rows(wb, "Talks Given"))
    interns = list(rows(wb, "Internship Projects"))
    pubs = list(rows(wb, "Publications"))
    published = sum(1 for r in pubs if clean(r.get("Status")).lower().startswith("published"))

    pub_summary = [{"theme": clean(r.get("Theme")), "papers": num(r.get("Papers")),
                    "citations": num(r.get("Citations")), "as_of": clean(r.get("As of"))}
                   for r in rows(wb, "Publication Summary") if clean(r.get("Theme"))] if "Publication Summary" in wb.sheetnames else []
    journals = [clean(r.get("Journal")) for r in rows(wb, "Journals Spanned")] if "Journals Spanned" in wb.sheetnames else []
    findings = []
    if "Key Findings" in wb.sheetnames:
        for r in rows(wb, "Key Findings"):
            if not clean(r.get("Title")): continue
            findings.append({
                "order": num(r.get("Order")), "theme": clean(r.get("Theme")), "title": clean(r.get("Title")),
                "text": clean(r.get("Finding (one or two sentences)")), "citation": clean(r.get("Citation")),
                "link": clean(r.get("Link (DOI or URL)")), "image": clean(r.get("Image file (in assets/images/findings)")),
            })
        findings.sort(key=lambda f: f["order"] or 0)

    # ---- research outputs since PUB_SINCE (Publications sheet) ----
    PUB_SINCE = 2020
    PRE = ("biorxiv", "arxiv", "ssrn", "qeios", "preprints")
    by_area = {k: {"papers": 0, "citations": 0} for k in AREA_LABELS}
    other = {"Preprint": 0, "Conference paper": 0, "Abstract / poster": 0}
    pub_total = pub_cites = 0
    for r in pubs:
        st = clean(r.get("Status")).lower(); y = year(r.get("Year")); jn = clean(r.get("Journal")).lower()
        if not y or y < PUB_SINCE: continue
        if not st.startswith("published"): continue
        typ = clean(r.get("Output type"))
        if not typ:
            typ = "Preprint" if any(w in jn for w in PRE) or "preprint" in st else \
                  "Conference paper" if "ieee" in jn else "Journal article"
        if typ in other:
            other[typ] += 1; continue
        k = area_from_sheet(r.get("Core Area"), r.get("Title"))
        c = num(r.get("Citations (latest)")) or 0
        by_area[k]["papers"] += 1; by_area[k]["citations"] += c
        pub_total += 1; pub_cites += c
    pub_areas = [{"key": k, "label": AREA_LABELS[k], **by_area[k]} for k in ("sleep", "mindbody", "clinical", "neurotech", "cross")]
    has_cites = pub_cites > 0

    funded = [s["budget_lakhs"] for s in sanctioned if s["budget_lakhs"]]
    data = {
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "stats": {
            "sanctioned_projects": len(sanctioned),
            "sanctioned_funding_lakhs": round(sum(funded), 2),
            "proposals_submitted": len(prop),
            "proposals_by_status": prop_status,
            "student_intern_placements": len(interns),
            "intern_institutions": sum(len(v) for v in institutions.values()),
            "intern_institutions_international": len(institutions[CAT_INTL]),
            "invited_talks": len(talks),
            "events_organised": len(events),
            "publications_published": published,
            "papers_since_2020": pub_total,
        },
        "areas": areas,
        "proposal_outcomes": outcomes,
        "proposals_by_year": proposals_by_year,
        "funders": funders,
        "institutions": institutions,
        "talks_by_year": count_by_year(year(r.get("Date")) for r in talks),
        "placements_by_year": count_by_year(year(r.get("Start Date")) for r in interns),
        "publications": {"since": PUB_SINCE, "total": pub_total, "citations": pub_cites, "has_citations": has_cites,
                         "other_outputs": other,
                         "by_area": pub_areas, "summary": pub_summary, "journals": [j for j in journals if j]},
        "key_findings": findings,
        "area_labels": AREA_LABELS,
        "sanctioned_projects": sanctioned,
        "events_organised": events,
    }
    # ---- internal "idea generation" data (proposals): counts only, no titles, no outcomes by name ----
    ideas_by_area = {k: 0 for k in AREA_LABELS}
    for r in prop:
        ideas_by_area[area_from_sheet(r.get("Core Area"), r.get("Title"))] += 1
    sanc_funders = {}
    for r in sanc:
        if not r.get("Agency") or "non-funded" in clean(r.get("Agency")).lower(): continue
        name, grp = funder_of(r.get("Agency"))
        sanc_funders.setdefault(grp, set()).add(name)
    ideas = {
        "generated": data["generated"],
        "ideas_total": len(prop),
        "taken_forward": outcomes["sanctioned"],
        "by_year": {y: sum(v.values()) for y, v in proposals_by_year.items()},
        "by_area": [{"key": k, "label": AREA_LABELS[k], "count": ideas_by_area[k]} for k in ("sleep", "mindbody", "clinical", "neurotech", "cross")],
        "partners_approached": funders,
    }
    IDEAS_OUT.write_text(json.dumps(ideas, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---- public data: no project costs, no proposal statistics ----
    for sp in data["sanctioned_projects"]: sp.pop("budget_lakhs", None)
    for a in data["areas"].values(): a.pop("funding_lakhs", None); a.pop("pipeline", None)
    for k in ("sanctioned_funding_lakhs", "proposals_submitted", "proposals_by_status"): data["stats"].pop(k, None)
    for k in ("proposal_outcomes", "proposals_by_year"): data.pop(k, None)
    data["funders"] = {g: sorted(v) for g, v in sorted(sanc_funders.items())}   # names of partners on sanctioned projects only
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    s = data["stats"]
    for k, v in areas.items(): print(f"  area {k}: {v}")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    for k, v in s.items(): print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
