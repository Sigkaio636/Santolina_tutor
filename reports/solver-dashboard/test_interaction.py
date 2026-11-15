"""Browser test of the solver dashboard: default state, speed slider, row click.

    ~/buscapiso/.venv/bin/python test_interaction.py
Expected counts come from the same CSV with the same formula as the dashboard.
"""
import csv
import os
import sys

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = "file://" + os.path.join(HERE, "solver_dashboard.html")
SHOTS = os.path.join(HERE, "check")
os.makedirs(SHOTS, exist_ok=True)
rows = list(csv.DictReader(open(os.path.join(HERE, "data", "solver_rows.csv"), encoding="utf-8")))


def expected(setup, inp, dataset, read, write):
    sel = [r for r in rows if r["setup"] == setup and r["input"] == inp and r["dataset"] == dataset]
    fit = [float(r["extra_s"]) + int(r["read_tokens"]) / read + int(r["written_tokens"]) / write + 1 <= 57 for r in sel]
    right = [r["program_right"] == "1" for r in sel]
    return (f"fits in time: {sum(fit)} of {len(sel)}   ·   right programs still in time: "
            f"{sum(f and g for f, g in zip(fit, right))} of {sum(right)}")


fails = []


def check(name, got, want):
    ok = want in got
    print(f"{'PASS' if ok else 'FAIL'} {name}: want {want!r}")
    if not ok:
        print("   got:", got)
        fails.append(name)


def summaries(page):
    return " | ".join(t for t in page.locator("#vis svg text").all_text_contents() if t.startswith("fits in time"))


def slide(page, label, value):
    page.evaluate("""([label, value]) => {
        for (const el of document.querySelectorAll('.vega-bind')) {
            if (el.textContent.includes(label)) {
                const input = el.querySelector('input[type=range]');
                input.value = value; input.dispatchEvent(new Event('input', {bubbles: true}));
            }
        }}""", [label, value])
    page.wait_for_timeout(400)


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/usr/bin/chromium-browser")
    page = browser.new_page(viewport={"width": 1900, "height": 1200})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(HTML)
    page.wait_for_selector("#vis svg", timeout=30000)
    page.wait_for_timeout(800)
    base = ("Qwen-Math · examples prompt", "eng")
    check("default practice", summaries(page), expected(*base, "practice", 5.2, 3.0))
    check("default M3Kang", summaries(page), expected(*base, "M3Kang", 5.2, 3.0))

    slide(page, "reading speed", 3.0)
    check("read 3.0 practice", summaries(page), expected(*base, "practice", 3.0, 3.0))
    check("read 3.0 M3Kang", summaries(page), expected(*base, "M3Kang", 3.0, 3.0))
    page.screenshot(path=os.path.join(SHOTS, "read3.png"), full_page=True)
    slide(page, "reading speed", 5.2)

    cell = page.locator('#vis path[fill-opacity="0"][aria-label*="Noema-2B · examples prompt"]'
                        '[aria-label*="input: eng"]').first
    cell.click()
    page.wait_for_timeout(400)
    got = summaries(page)
    check("click Noema eng row", got, expected("Noema-2B · examples prompt", "eng", "practice", 5.2, 3.0))
    check("Noema has no M3Kang run", str(got.count("fits in time")), "1")
    page.screenshot(path=os.path.join(SHOTS, "noema.png"), full_page=True)

    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(300)
    top = page.evaluate("document.querySelector('.vega-bindings').getBoundingClientRect().top")
    check("sliders stay in view after scrolling", f"{0 <= top < 5} top={top}", "True")
    check("no page errors", str(errors), "[]")
    browser.close()
sys.exit(1 if fails else 0)
