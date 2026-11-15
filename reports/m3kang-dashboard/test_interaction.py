"""Browser test of the dashboard's linked selections and problem browser.

    <venv with playwright>/bin/python test_interaction.py
Uses the system Chromium. Expected counts come from the same CSV the dashboard reads.
"""
import os
import sys

import csv

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = "file://" + os.path.join(HERE, "m3kang_dashboard.html")
SHOTS = os.path.join(HERE, "check")
os.makedirs(SHOTS, exist_ok=True)

with open(os.path.join(HERE, "data", "m3kang_rows.csv"), encoding="utf-8") as f:
    eng = [r for r in csv.DictReader(f) if r["language"] == "eng"]
n_all = len(eng)
n_l1 = sum(r["level"] == "1" for r in eng)
n_l1_d = sum(r["level"] == "1" and r["label"] == "D" for r in eng)

fails = []


def check(name, got, want):
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'} {name}: got {got!r}, want {want!r}")
    if not ok:
        fails.append(name)


def count(page):
    return int(page.inner_text("#count").split(" of ")[0])


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/usr/bin/chromium-browser")
    page = browser.new_page(viewport={"width": 1300, "height": 1000})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(HTML)
    page.wait_for_selector("#vis svg", timeout=30000)
    page.wait_for_function("document.querySelector('#count').textContent.includes(' of ')")
    check("default: all problems listed", count(page), n_all)

    # 1 level picker -> browser + fade
    bar = page.locator('#vis path[aria-roledescription="bar"][aria-label*="Level: 1;"]').first
    bar.click()
    page.wait_for_timeout(300)
    check("click level 1 bar", count(page), n_l1)

    # 2 bias cell (level 1, D) -> intersects with level selection
    cell = page.locator('#vis path[aria-roledescription="rect mark"][aria-label*="Level: 1;"][aria-label*="Letter: D;"]').first
    cell.click()   # centre of the cell, where the value label sits: also tests the label passes clicks through
    page.wait_for_timeout(300)
    check("click bias cell level 1 / D", count(page), n_l1_d)
    page.screenshot(path=os.path.join(SHOTS, "state_level1_D.png"), full_page=True)

    # 3 row click -> image loads
    page.locator("#rows tr").first.click()
    page.wait_for_selector("#detail img")
    page.wait_for_function("document.querySelector('#detail img').complete")
    w = page.evaluate("document.querySelector('#detail img').naturalWidth")
    check("problem image loaded", w > 0, True)
    page.locator("#detail").screenshot(path=os.path.join(SHOTS, "detail.png"))

    # 4 search narrows within selection
    page.fill("#q", "zzzz-no-match")
    page.wait_for_timeout(100)
    check("search with no match", count(page), 0)
    page.fill("#q", "")

    check("no page errors", errors, [])
    browser.close()

sys.exit(1 if fails else 0)
