from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
import tempfile
from importlib.metadata import version as pkg_version
from pathlib import Path

from playwright.sync_api import sync_playwright

EXPECTED_GOLDEN = "e056e7f7ab8b71cd82a05763d8390d61bc5afa50c5c50d1a34b21b90e1a72bb1"
EXPECTED_PLAYWRIGHT = "1.62.0"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"NOT_A_PNG: {path}")
    return struct.unpack(">II", data[16:24])


def wait_qa(page, mode: str, expected_stage: str) -> None:
    page.wait_for_selector(f'html[data-qa-ready="{mode}"]', state="attached", timeout=15000)
    page.wait_for_function(
        "stage => document.documentElement.dataset.qaStage === stage",
        arg=expected_stage,
        timeout=15000,
    )
    page.evaluate("() => document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()")


def metrics(page) -> dict:
    return page.evaluate(
        """() => ({
            innerWidth: window.innerWidth,
            innerHeight: window.innerHeight,
            scrollWidth: document.documentElement.scrollWidth,
            bodyScrollWidth: document.body ? document.body.scrollWidth : 0,
            mobileMedia: matchMedia('(max-width:520px)').matches,
            qaReady: document.documentElement.dataset.qaReady || null,
            qaStage: document.documentElement.dataset.qaStage || null
        })"""
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--chrome", required=True)
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--head", required=True)
    args = ap.parse_args()

    actual_pw = pkg_version("playwright")
    if actual_pw != EXPECTED_PLAYWRIGHT:
        raise SystemExit(f"PLAYWRIGHT_VERSION_MISMATCH expected={EXPECTED_PLAYWRIGHT} actual={actual_pw}")

    root = Path(args.root).resolve()
    evidence = Path(args.evidence).resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    chrome = str(Path(args.chrome).resolve())
    base = args.base.rstrip("/") + "/"

    golden = root / "projects" / "golden-journey" / "assets" / "sanctuaire.png"
    golden_hash = sha256(golden)
    if golden_hash != EXPECTED_GOLDEN:
        raise SystemExit(f"GOLDEN_CANON_MISMATCH expected={EXPECTED_GOLDEN} actual={golden_hash}")

    shots = [
        ("desktop-canon.png", 1672, 941, "canon", "sanctuary"),
        ("desktop-lesson.png", 1672, 941, "lesson3", "lesson-3"),
        ("desktop-workshop.png", 1672, 941, "workshop", "workshop"),
        ("desktop-transmission.png", 1672, 941, "transmission", "transmission"),
        ("mobile-sanctuary.png", 390, 844, "canon", "sanctuary"),
        ("mobile-lesson.png", 390, 844, "lesson3", "lesson-3"),
        ("mobile-workshop.png", 390, 844, "workshop", "workshop"),
        ("mobile-transmission.png", 390, 844, "transmission", "transmission"),
    ]

    profile = Path(tempfile.mkdtemp(prefix="lumen-real01-playwright-profile-"))
    screenshot_records: dict[str, dict] = {}

    try:
        with sync_playwright() as p:
            # Phase 1 — full journey in a persistent Chrome profile.
            ctx = p.chromium.launch_persistent_context(
                user_data_dir=str(profile),
                executable_path=chrome,
                headless=True,
                viewport={"width": 1672, "height": 941},
                locale="fr-FR",
            )
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.goto(base + "?qa=e2e-seed", wait_until="networkidle", timeout=30000)
            page.wait_for_function(
                "() => document.body && document.body.innerText.includes('REAL01_E2E_SEED_OK')",
                timeout=20000,
            )
            write_text(evidence / "e2e-seed-dom.html", page.content())
            ctx.close()

            # Phase 2 — fresh Chrome process/context, same profile.
            ctx = p.chromium.launch_persistent_context(
                user_data_dir=str(profile),
                executable_path=chrome,
                headless=True,
                viewport={"width": 1672, "height": 941},
                locale="fr-FR",
            )
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.goto(base + "?qa=e2e-verify", wait_until="networkidle", timeout=30000)
            page.wait_for_function(
                "() => document.body && document.body.innerText.includes('REAL01_E2E_PASS')",
                timeout=15000,
            )
            write_text(evidence / "e2e-verify-dom.html", page.content())
            ctx.close()
            print("REAL-01 PLAYWRIGHT E2E + PERSISTENCE ACROSS BROWSER RESTART PASS")

            browser = p.chromium.launch(executable_path=chrome, headless=True)
            try:
                for name, width, height, mode, stage in shots:
                    is_mobile = name.startswith("mobile-")
                    context = browser.new_context(
                        viewport={"width": width, "height": height},
                        screen={"width": width, "height": height},
                        device_scale_factor=1,
                        is_mobile=is_mobile,
                        has_touch=is_mobile,
                        locale="fr-FR",
                    )
                    page = context.new_page()
                    page.goto(base + f"?qa={mode}", wait_until="networkidle", timeout=30000)
                    wait_qa(page, mode, stage)
                    m = metrics(page)

                    if m["qaReady"] != mode:
                        raise RuntimeError(f"QA_READY_FAIL {name}: {m}")
                    if m["qaStage"] != stage:
                        raise RuntimeError(f"QA_STAGE_FAIL {name}: expected={stage} actual={m['qaStage']}")
                    if m["innerWidth"] != width:
                        raise RuntimeError(f"VIEWPORT_WIDTH_FAIL {name}: expected={width} actual={m['innerWidth']}")
                    if m["scrollWidth"] > width or m["bodyScrollWidth"] > width:
                        raise RuntimeError(
                            f"HORIZONTAL_OVERFLOW {name}: inner={m['innerWidth']} "
                            f"doc={m['scrollWidth']} body={m['bodyScrollWidth']}"
                        )
                    if is_mobile and not m["mobileMedia"]:
                        raise RuntimeError(f"MOBILE_MEDIA_QUERY_FAIL {name}: {m}")

                    out = evidence / name
                    page.screenshot(path=str(out), full_page=False, animations="disabled")
                    actual_w, actual_h = png_size(out)
                    if (actual_w, actual_h) != (width, height):
                        raise RuntimeError(
                            f"SCREENSHOT_SIZE_FAIL {name}: expected={width}x{height} actual={actual_w}x{actual_h}"
                        )

                    write_text(evidence / f"{name}.qa-dom.html", page.content())
                    screenshot_records[name] = {
                        "sha256": sha256(out),
                        "bytes": out.stat().st_size,
                        "viewport": {"width": width, "height": height},
                        "metrics": m,
                        "qa_mode": mode,
                        "qa_stage": stage,
                    }
                    print(
                        f"VIEWPORT_PASS {name} innerWidth={m['innerWidth']} "
                        f"scrollWidth={m['scrollWidth']} bodyScrollWidth={m['bodyScrollWidth']} "
                        f"png={actual_w}x{actual_h}"
                    )
                    context.close()
            finally:
                browser.close()
    finally:
        shutil.rmtree(profile, ignore_errors=True)

    if screenshot_records["desktop-canon.png"]["sha256"] == screenshot_records["desktop-transmission.png"]["sha256"]:
        raise SystemExit("TRANSMISSION_CAPTURE_EQUALS_CANON")

    review_state = {
        "mission": "LUMEN-REAL-01",
        "certified_head_sha": args.head,
        "golden_sha256": golden_hash,
        "browser": {
            "engine": "Google Chrome via Playwright 1.62.0",
            "desktop": "DONE_OBSERVED",
            "mobile": "DONE_OBSERVED_TRUE_VIEWPORT_EMULATION",
            "persistence": "OBSERVED_ACROSS_BROWSER_RESTART",
        },
        "tasks": {
            "R-006": "DONE",
            "R-007": "DONE",
            "R-008": "READY",
            "R-009": "BLOCKED_BY_R008",
        },
        "independent_review": False,
        "screenshots": screenshot_records,
    }
    write_text(evidence / "review-state.json", json.dumps(review_state, ensure_ascii=False, indent=2))

    manifest = {
        "mission": "LUMEN-REAL-01",
        "browser": "Google Chrome via Playwright 1.62.0",
        "canon_sha256": golden_hash,
        "certified_head_sha": args.head,
        "desktop": [x[0] for x in shots if x[0].startswith("desktop-")],
        "mobile": [x[0] for x in shots if x[0].startswith("mobile-")],
        "result": "READY_FOR_INDEPENDENT_REVIEW",
        "note": (
            "Viewport is emulated by Playwright BrowserContext, not inferred from Chrome outer-window size. "
            "User actions and return remain SELF_REPORTED."
        ),
    }
    write_text(evidence / "browser-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))

    print("REAL-01 PLAYWRIGHT DESKTOP/MOBILE CAPTURES PASS")
    print(f"CERTIFIED_HEAD {args.head}")
    print(f"GOLDEN_CANON_PASS {golden_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
