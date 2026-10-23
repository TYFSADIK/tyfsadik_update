#!/usr/bin/env python3
"""
build_api.py - generate static machine-readable endpoints under /api/
from site-data.json and the search index. No private data; everything here
mirrors what is visible on the public pages.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://tyfsadik.org"


def main():
    data = json.loads((ROOT / "site-data.json").read_text(encoding="utf-8"))
    api = ROOT / "api"
    api.mkdir(exist_ok=True)

    profile = {
        "name": "MD. Taki Yasir Faraji Sadik",
        "alternateName": ["Taki Sadik", "TYFSADIK"],
        "jobTitle": "Cybersecurity & IT Professional",
        "location": {"locality": "North York", "region": "Toronto, Ontario", "country": "Canada"},
        "url": f"{BASE}/",
        "email": "taki@tyfsadik.org",
        "sameAs": [
            "https://github.com/TYFSADIK",
            "https://www.linkedin.com/in/md-taki-yasir-faraji-sadik-63a026278/",
        ],
        "factsPage": f"{BASE}/about/facts.html",
        "stats": data["stats"],
        "generatedFrom": "site-data.json",
    }

    projects = [{
        "title": p["title"],
        "category": p["category"],
        "url": f"{BASE}/{p['url']}",
        "description": p["description"],
        "tags": p.get("tags", []),
        "techStack": p.get("techStack", []),
        "year": p.get("year"),
    } for p in data["projects"]]

    idx = json.loads((ROOT / "search-index.json").read_text(encoding="utf-8"))
    labs = [{
        "title": i["title"],
        "url": f"{BASE}/{i['url']}",
        "track": i["track"],
        "difficulty": i["difficulty"],
        "description": i["description"],
    } for i in idx if i["kind"] == "lab"]

    skills = sorted({t for p in data["projects"] for t in p.get("techStack", [])}
                    | {t for p in data["projects"] for t in p.get("tags", [])})

    (api / "profile.json").write_text(json.dumps(profile, indent=1) + "\n")
    (api / "projects.json").write_text(json.dumps(projects, indent=1) + "\n")
    (api / "labs.json").write_text(json.dumps(labs, indent=1) + "\n")
    (api / "skills.json").write_text(json.dumps(skills, indent=1) + "\n")
    print(f"api: profile, {len(projects)} projects, {len(labs)} labs, {len(skills)} skills")


if __name__ == "__main__":
    main()
