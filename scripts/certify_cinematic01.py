from __future__ import annotations
import argparse, json, hashlib, struct, time
from pathlib import Path
from importlib.metadata import version as pkg_version
from playwright.sync_api import sync_playwright

EXPECTED_PLAYWRIGHT="1.62.0"

def png_size(path:Path):
    b=path.read_bytes()
    if b[:8]!=b"\x89PNG\r\n\x1a\n": raise RuntimeError(f"NOT_PNG {path}")
    return struct.unpack(">II",b[16:24])

def sha(path:Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base",required=True)
    ap.add_argument("--chrome",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()

    if pkg_version("playwright")!=EXPECTED_PLAYWRIGHT:
        raise SystemExit("PLAYWRIGHT_VERSION_MISMATCH")

    base=args.base.rstrip("/")+"/cinematic-voir/"
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    chrome=str(Path(args.chrome).resolve())
    telemetry={}

    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=chrome,headless=True,args=["--use-angle=swiftshader-webgl"])
        try:
            # Functional journey
            ctx=browser.new_context(viewport={"width":1672,"height":941},locale="fr-FR")
            page=ctx.new_page()
            page.goto(base,wait_until="networkidle")
            page.wait_for_selector("#enterVoir")
            page.locator("#enterVoir").click()
            page.wait_for_function("() => document.documentElement.dataset.scene==='threshold'")
            page.locator("#situation").fill("Je dois choisir mon prochain geste sans confondre ce que je contrôle et ce que je ne contrôle pas.")
            page.locator("#engraveSituation").click()
            page.wait_for_function("() => document.documentElement.dataset.scene==='reading'")
            for _ in range(5):
                page.locator("#nextPage").click()
            page.locator("#nextPage").click()
            page.wait_for_function("() => document.documentElement.dataset.scene==='reflection'")
            page.locator("#reflection").fill("Je distingue maintenant la situation, mon interprétation et la prochaine prise réellement disponible.")
            page.locator("#sealReflection").click()
            page.wait_for_function("() => document.documentElement.dataset.scene==='complete'")
            assert page.evaluate("document.documentElement.scrollWidth")<=1672
            telemetry["functional_journey"]="PASS"

            # Motion probe
            page.goto(base+"?qa=threshold",wait_until="networkidle")
            page.wait_for_function("() => document.documentElement.dataset.qaReady==='threshold'")
            page.mouse.move(120,420)
            page.wait_for_timeout(250)
            left=page.evaluate("() => getComputedStyle(document.documentElement).getPropertyValue('--px').trim()")
            page.mouse.move(1540,420)
            page.wait_for_timeout(450)
            right=page.evaluate("() => getComputedStyle(document.documentElement).getPropertyValue('--px').trim()")
            if left==right:
                raise RuntimeError(f"PARALLAX_STATIC left={left} right={right}")
            telemetry["parallax"]={"left":left,"right":right,"result":"PASS"}
            telemetry["atmosphere"]=page.evaluate("() => window.__LUMEN_CINEMATIC__.atmosphere")
            ctx.close()

            shots=[
                ("desktop-entry.png",1672,941,"entry"),
                ("desktop-threshold.png",1672,941,"threshold"),
                ("desktop-reading.png",1672,941,"reading"),
                ("desktop-reading-late.png",1672,941,"reading-late"),
                ("desktop-reflection.png",1672,941,"reflection"),
                ("mobile-entry.png",390,844,"entry"),
                ("mobile-threshold.png",390,844,"threshold"),
                ("mobile-reading.png",390,844,"reading"),
            ]

            records={}
            for name,w,h,qa in shots:
                mobile=name.startswith("mobile-")
                ctx=browser.new_context(
                    viewport={"width":w,"height":h},
                    screen={"width":w,"height":h},
                    device_scale_factor=1,
                    is_mobile=mobile,
                    has_touch=mobile,
                    locale="fr-FR",
                )
                page=ctx.new_page()
                page.goto(base+f"?qa={qa}",wait_until="networkidle")
                page.wait_for_function("q => document.documentElement.dataset.qaReady===q",arg=qa)
                page.wait_for_timeout(250 if mobile else 350)

                inner=page.evaluate("innerWidth")
                scroll=page.evaluate("document.documentElement.scrollWidth")
                if inner!=w or scroll>w:
                    raise RuntimeError(f"VIEWPORT_FAIL {name}: inner={inner} scroll={scroll} expected={w}")

                atmosphere=page.evaluate("document.documentElement.dataset.atmosphere")
                if atmosphere not in ("webgl","fallback"):
                    raise RuntimeError(f"ATMOSPHERE_NOT_READY {name}: {atmosphere}")

                path=out/name
                page.screenshot(path=str(path),full_page=False,animations="disabled")
                pw,ph=png_size(path)
                if (pw,ph)!=(w,h):
                    raise RuntimeError(f"PNG_SIZE_FAIL {name}: {pw}x{ph}")

                records[name]={
                    "sha256":sha(path),
                    "viewport":[w,h],
                    "innerWidth":inner,
                    "scrollWidth":scroll,
                    "atmosphere":atmosphere,
                    "quality":page.evaluate("document.documentElement.dataset.quality"),
                    "frameMs":page.evaluate("document.documentElement.dataset.frameMs || null"),
                }
                print(f"CINEMATIC_CAPTURE_PASS {name} viewport={w}x{h} atmosphere={atmosphere}")
                ctx.close()

            telemetry["captures"]=records
            (out/"cinematic-telemetry.json").write_text(json.dumps(telemetry,ensure_ascii=False,indent=2),encoding="utf-8")
            print("LUMEN_CINEMATIC_01_BROWSER_PASS")
        finally:
            browser.close()

if __name__=="__main__":
    main()
