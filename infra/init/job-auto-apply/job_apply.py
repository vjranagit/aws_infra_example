import os, sys, time, json, re, pathlib
from typing import Optional, Dict, Any
import yaml
import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

HERE = pathlib.Path(__file__).parent

def env_bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")

def load_selectors() -> Dict[str, Any]:
    with open(HERE / "form_selectors.yml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_text(path: pathlib.Path) -> Optional[str]:
    if not path or not path.exists():
        return None
    return path.read_text(encoding="utf-8", errors="ignore").strip()

def generate_cover_letter(llm_url: str, system_prompt: str, job_text: str, base_profile: Dict[str,str]) -> str:
    if not llm_url:
        # fallback: short template
        return (f"Dear Hiring Team,\n\nI’m excited to apply for the {base_profile.get('job_title','the role')}. "
                "I bring hands-on DevSecOps/HPC experience, infrastructure automation, and measurable impact. "
                "I would value the chance to contribute immediately and continuously improve your systems.\n\n"
                "Thank you for your time!\n— " + base_profile.get("FULL_NAME","Candidate"))
    try:
        payload = {
            "system": system_prompt,
            "user": f"Job description:\n{job_text}\n\nCandidate profile:\n{json.dumps(base_profile, indent=2)}"
        }
        r = requests.post(llm_url, json=payload, timeout=60)
        r.raise_for_status()
        txt = r.json().get("text") or r.text
        return txt.strip()
    except Exception as e:
        print(f"[WARN] LLM generation failed: {e}")
        return generate_cover_letter("", system_prompt, job_text, base_profile)  # fallback

def smart_fill(page, selector: str, value: str):
    if not value or not selector:
        return False
    el = page.locator(selector).first
    if el.count() == 0:
        return False
    # If it's a <select>, try select_option
    try:
        tag = el.evaluate("el => el.tagName.toLowerCase()")
        if tag == "select":
            try:
                el.select_option(label=value)
            except:
                # try exact value or partial
                el.select_option(value=value)
            return True
    except:
        pass
    try:
        el.fill(value, timeout=2000)
        return True
    except:
        # maybe type
        try:
            el.click(timeout=1500)
            page.keyboard.type(value, delay=15)
            return True
        except:
            return False

def fill_by_labels(page, label_map: Dict[str,str], profile: Dict[str,str]):
    # try to map by known label keys
    attempts = [
        ("First Name", profile.get("FIRST_NAME") or profile.get("FULL_NAME","" ).split(" ")[0]),
        ("Last Name",  profile.get("LAST_NAME")  or (profile.get("FULL_NAME","" ).split(" ")[-1] if len(profile.get("FULL_NAME","" ).split(" "))>1 else "")),
        ("Name",       profile.get("FULL_NAME")),
        ("Email",      profile.get("EMAIL")),
        ("Phone",      profile.get("PHONE")),
        ("City",       profile.get("CITY")),
        ("State",      profile.get("STATE")),
        ("Country",    profile.get("COUNTRY")),
        ("LinkedIn",   profile.get("LINKEDIN_URL",""))
    ]
    for label, val in attempts:
        if not val:
            continue
        sel = label_map.get(label)
        filled = smart_fill(page, sel, val)
        # If strict selector failed, try label-to-input association
        if not filled:
            try:
                # find label elements with matching text, then its for= or sibling input
                lab = page.locator(f"label:has-text('{label}')").first
                if lab.count() > 0:
                    for_attr = lab.get_attribute("for")
                    if for_attr:
                        filled = smart_fill(page, f'#{for_attr}', val)
                    if not filled:
                        # sibling input/textarea
                        sib = lab.locator("xpath=following::*[self::input or self::textarea][1]")
                        if sib.count():
                            sib.first.fill(val)
                            filled = True
            except:
                pass

def upload_resume(page, selector: str, resume_path: str):
    if not resume_path or not pathlib.Path(resume_path).exists():
        print("[WARN] Resume path missing.")
        return False
    inp = page.locator(selector).first
    if inp.count() == 0:
        return False
    try:
        inp.set_input_files(resume_path)
        return True
    except Exception as e:
        print(f"[WARN] Resume upload failed: {e}")
        return False

def paste_cover_letter(page, selector: str, text: str):
    if not text:
        return False
    area = page.locator(selector).first
    if area.count() == 0:
        return False
    try:
        area.fill(text)
        return True
    except:
        try:
            area.click()
            page.keyboard.type(text, delay=8)
            return True
        except:
            return False

def read_job_text(page) -> str:
    # Best-effort: gather visible content to feed LLM
    try:
        body_text = page.locator("body").inner_text(timeout=3000)
        # truncate to a sane size
        return body_text[:4000]
    except:
        return ""

def main():
    load_dotenv()
    sel = load_selectors()
    headless = env_bool("HEADLESS", False)
    require_approval = env_bool("REQUIRE_APPROVAL", True)

    # Inputs
    if len(sys.argv) < 2:
        print("Usage: python job_apply.py <job_url> [site_key]")
        print("Example site_key: workday | greenhouse | lever  (defaults used if omitted)")
        sys.exit(1)

    job_url = sys.argv[1].strip()
    site_key = (sys.argv[2].strip().lower() if len(sys.argv) > 2 else None)

    # Profile from env
    profile = {
        "FULL_NAME": os.getenv("FULL_NAME",""),
        "EMAIL": os.getenv("EMAIL",""),
        "PHONE": os.getenv("PHONE",""),
        "CITY": os.getenv("CITY",""),
        "STATE": os.getenv("STATE",""),
        "COUNTRY": os.getenv("COUNTRY",""),
        "LINKEDIN_URL": os.getenv("LINKEDIN_URL",""),
    }
    if " " in profile["FULL_NAME"]:
        parts = profile["FULL_NAME"].split()
        profile["FIRST_NAME"] = parts[0]
        profile["LAST_NAME"]  = parts[-1]
    else:
        profile["FIRST_NAME"] = profile["FULL_NAME"]
        profile["LAST_NAME"] = ""

    resume_path = os.getenv("RESUME_PATH","")
    cover_letter_path = os.getenv("COVER_LETTER_PATH","")
    llm_url = os.getenv("LLM_URL","")
    system_prompt = load_text(HERE / "prompts" / "cover_letter_system.txt") or "Write a concise cover letter."

    config = sel.get(site_key or "", {})
    defaults = sel.get("defaults", {})
    label_map = {**defaults.get("label_map", {}), **config.get("label_map", {})}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ])
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()

        print(f"[INFO] Navigating → {job_url}")
        page.goto(job_url, wait_until="domcontentloaded", timeout=60_000)

        # Best effort: click "Apply" if present
        try:
            apply_btn = page.locator('a:has-text("Apply"), button:has-text("Apply")').first
            if apply_btn.count():
                apply_btn.click(timeout=5000)
                page.wait_for_load_state("domcontentloaded")
        except:
            pass

        # Basic multi-step support: try "Next" a couple of times to reach form
        for _ in range(2):
            try:
                nb = page.locator(config.get("next_button") or defaults.get("next_button","" )).first
                if nb.count():
                    nb.click(timeout=2000)
                    page.wait_for_load_state("domcontentloaded")
            except:
