"""Build the Paediatrick or Treats website from site/content/ and site/site.json.

Usage:  python site/build.py            -> writes the site to _site/
The website has its OWN content and does not follow Instagram:
  site/content/notes/<slug>/  slides.json, slide*.jpg (optional), meta.json {"date", "instagram"?}
  site/content/reels/<slug>/  caption.txt, meta.json {"date", "audience": "pg"|"parents", "instagram"?}
Content is added here by hand (via Claude), never automatically from posts/ or reels/.
Links (Instagram, YouTube) and books are set in site/site.json.
Standard library only, so it runs anywhere (including GitHub Actions) for free.
"""
import html
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "_site"
CFG = json.loads((HERE / "site.json").read_text(encoding="utf-8"))
# Fingerprint of the stylesheet: pages link to style.css?v=<this>, so browsers
# fetch the new CSS the moment it changes instead of mixing old CSS with new HTML.
CSS_VER = __import__("hashlib").md5((HERE / "style.css").read_bytes()).hexdigest()[:10]
HANDLE = "paediatrick_or_treats"
IG = CFG.get("instagram") or f"https://www.instagram.com/{HANDLE}/"
YT = CFG.get("youtube") or ""
BOOKS = CFG.get("books") or []
SITE_NAME = "Paediatrick or Treats"
TAGLINE = "A happy little corner of paediatrics, for future paediatricians and for parents"

esc = html.escape


def fmt(text):
    """Escape text and apply the slide markup:
    **bold**, ==highlight==, ==y:highlight== / ==t:highlight== (colours), ~~circled~~."""
    t = esc(text or "")
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"==([a-z]):(.+?)==", r'<mark class="hl-\1">\2</mark>', t)
    t = re.sub(r"==(.+?)==", r"<mark>\1</mark>", t)
    t = re.sub(r"~~(.+?)~~", r'<span class="ring">\1</span>', t)
    return t


def plain(text):
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", text or "")
    t = re.sub(r"==(?:[a-z]:)?(.+?)==", r"\1", t)
    return re.sub(r"~~(.+?)~~", r"\1", t)


def load_json(p):
    return json.loads(p.read_text(encoding="utf-8"))


def nice_date(iso):
    try:
        d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return d.strftime("%d %b %Y"), d.strftime("%Y-%m-%d")
    except Exception:
        return "", ""


# ---------------------------------------------------------------- content
CONTENT = HERE / "content"


def load_posts():
    posts = []
    ndir = CONTENT / "notes"
    if not ndir.exists():
        return posts
    for d in sorted(ndir.iterdir()):
        sj, mj = d / "slides.json", d / "meta.json"
        if not (d.is_dir() and sj.exists()):
            continue
        data = load_json(sj)
        pub = load_json(mj) if mj.exists() else {}
        slides = data.get("slides", [])
        is_drug = data.get("slot") == "drug" or any(s.get("kind") == "drug" for s in slides)
        title = data.get("topic", d.name)
        if is_drug:
            title = title.replace("Drug of the Day:", "").strip()
        cover = next((s for s in slides if s.get("kind") == "cover"), None)
        drug = next((s for s in slides if s.get("kind") == "drug"), None)
        notebook = data.get("style") == "notes"
        summary = ((cover or {}).get("subtitle") or (cover or {}).get("sub")
                   or (drug or {}).get("drug_class") or "")
        images = sorted(p.name for p in d.glob("slide*.jpg"))
        shown, iso = nice_date(pub.get("date", ""))
        posts.append(dict(
            slug=d.name, dir=d, title=title, summary=plain(summary), slides=slides,
            kind="drug" if is_drug else "topic", images=images, notebook=notebook,
            date=shown, iso=iso,
            references=data.get("references", []), hashtags=data.get("hashtags", []),
            emoji=(cover or drug or {}).get("emoji") or ("💊" if is_drug else ("📒" if notebook else "🩺")),
        ))
    posts.sort(key=lambda p: p["iso"], reverse=True)
    return posts


def load_reels():
    reels = []
    rdir = CONTENT / "reels"
    if not rdir.exists():
        return reels
    for d in sorted(rdir.iterdir()):
        cap, mj = d / "caption.txt", d / "meta.json"
        if not (d.is_dir() and cap.exists()):
            continue
        pub = load_json(mj) if mj.exists() else {}
        lines = [l.strip() for l in cap.read_text(encoding="utf-8").splitlines()]
        title = next((l for l in lines if l), d.name)
        body = [l for l in lines[1:] if l and not l.startswith("#") and l != "."]
        shown, iso = nice_date(pub.get("date", ""))
        audience = pub.get("audience") or ("parents" if "parents" in d.name else "pg")
        reels.append(dict(slug=d.name, title=title, body=body, date=shown, iso=iso, audience=audience))
    reels.sort(key=lambda r: r["iso"], reverse=True)
    return reels


def load_videos():
    vids = []
    vdir = CONTENT / "videos"
    if not vdir.exists():
        return vids
    for d in sorted(vdir.iterdir()):
        mj = d / "meta.json"
        if not (d.is_dir() and mj.exists() and (d / "video.mp4").exists()):
            continue
        m = load_json(mj)
        shown, iso = nice_date(m.get("date", ""))
        vids.append(dict(slug=d.name, title=m.get("title", d.name), intro=m.get("intro", []),
                         chapters=m.get("chapters", []), points=m.get("points", []),
                         audience=m.get("audience", "parents"), youtube=m.get("youtube", ""),
                         thumb=(d / "thumb.jpg").exists(), date=shown, iso=iso))
    vids.sort(key=lambda v: v["iso"], reverse=True)
    return vids


# ---------------------------------------------------------------- cartoons (inline SVG)
HERO_ART = """<svg class="hero-art" viewBox="0 0 520 440" role="img" aria-label="Cartoon of a happy baby wearing a stethoscope, with a teddy bear, balloons and toy blocks">
  <circle cx="275" cy="235" r="190" fill="#FFE9DA"/>
  <circle cx="420" cy="90" r="34" fill="#FFF3B8"/>
  <g fill="#fff"><ellipse cx="380" cy="60" rx="40" ry="16"/><ellipse cx="405" cy="50" rx="24" ry="18"/></g>
  <g stroke="#B8AFCF" stroke-width="2" fill="none"><path d="M100 120 Q115 200 150 270"/><path d="M160 92 Q160 190 155 270"/><path d="M62 175 Q110 230 148 272"/></g>
  <ellipse cx="100" cy="92" rx="30" ry="36" fill="#F7A8C4"/><path d="M95 127 l5 6 5-6z" fill="#F7A8C4"/>
  <ellipse cx="160" cy="62" rx="30" ry="36" fill="#9CC7F2"/><path d="M155 97 l5 6 5-6z" fill="#9CC7F2"/>
  <ellipse cx="60" cy="148" rx="26" ry="31" fill="#F6D77E"/><path d="M55 178 l5 6 5-6z" fill="#F6D77E"/>
  <g fill="#fff" opacity=".7"><ellipse cx="90" cy="80" rx="7" ry="10"/><ellipse cx="150" cy="50" rx="7" ry="10"/></g>
  <!-- baby -->
  <ellipse cx="280" cy="345" rx="92" ry="74" fill="#9CC7F2"/>
  <ellipse cx="200" cy="330" rx="26" ry="20" fill="#FFD9C2"/><ellipse cx="360" cy="330" rx="26" ry="20" fill="#FFD9C2"/>
  <circle cx="204" cy="215" r="17" fill="#FFCDB0"/><circle cx="356" cy="215" r="17" fill="#FFCDB0"/>
  <circle cx="280" cy="210" r="80" fill="#FFD9C2"/>
  <path d="M268 134 q8-26 30-14 q-14 2-12 16" fill="none" stroke="#8B5E3C" stroke-width="6" stroke-linecap="round"/>
  <ellipse cx="250" cy="212" rx="8" ry="10" fill="#2B2440"/><ellipse cx="310" cy="212" rx="8" ry="10" fill="#2B2440"/>
  <circle cx="253" cy="208" r="3" fill="#fff"/><circle cx="313" cy="208" r="3" fill="#fff"/>
  <ellipse cx="232" cy="240" rx="14" ry="9" fill="#F7A8C4" opacity=".7"/><ellipse cx="328" cy="240" rx="14" ry="9" fill="#F7A8C4" opacity=".7"/>
  <path d="M262 246 q18 20 36 0" fill="#E8566C" stroke="#2B2440" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- stethoscope -->
  <path d="M232 282 q-6 40 48 52 q54-12 48-52" fill="none" stroke="#5B4BDB" stroke-width="7" stroke-linecap="round"/>
  <path d="M280 334 v18" stroke="#5B4BDB" stroke-width="7" stroke-linecap="round"/>
  <circle cx="280" cy="365" r="15" fill="#C7B5F0" stroke="#5B4BDB" stroke-width="5"/>
  <!-- teddy -->
  <g transform="translate(70 290)">
    <ellipse cx="50" cy="95" rx="44" ry="42" fill="#E3B487"/>
    <circle cx="16" cy="18" r="15" fill="#E3B487"/><circle cx="84" cy="18" r="15" fill="#E3B487"/>
    <circle cx="16" cy="18" r="7" fill="#F6D6B4"/><circle cx="84" cy="18" r="7" fill="#F6D6B4"/>
    <circle cx="50" cy="45" r="38" fill="#E3B487"/>
    <ellipse cx="50" cy="58" rx="17" ry="13" fill="#F6D6B4"/>
    <ellipse cx="50" cy="52" rx="6" ry="4.5" fill="#5A3B26"/>
    <circle cx="36" cy="38" r="4.5" fill="#2B2440"/><circle cx="64" cy="38" r="4.5" fill="#2B2440"/>
    <path d="M44 63 q6 6 12 0" stroke="#5A3B26" stroke-width="3" fill="none" stroke-linecap="round"/>
    <ellipse cx="50" cy="100" rx="22" ry="20" fill="#F6D6B4"/>
    <path d="M42 96 a8 8 0 0 1 8 -6 a8 8 0 0 1 8 6 q-8 10 -8 12 q0 -2 -8 -12z" fill="#F7A8C4"/>
  </g>
  <!-- blocks -->
  <g font-family="Fredoka, Nunito, sans-serif" font-weight="700" font-size="34" text-anchor="middle">
    <rect x="388" y="350" width="56" height="56" rx="10" fill="#8FD3C7"/><text x="416" y="391" fill="#fff">A</text>
    <rect x="448" y="350" width="56" height="56" rx="10" fill="#FFC59E"/><text x="476" y="391" fill="#fff">B</text>
    <rect x="418" y="290" width="56" height="56" rx="10" fill="#C7B5F0" transform="rotate(-6 446 318)"/><text x="446" y="331" fill="#fff" transform="rotate(-6 446 318)">C</text>
  </g>
  <g fill="#F7A8C4"><path d="M400 200 a7 7 0 0 1 12 -5 a7 7 0 0 1 12 5 q0 8 -12 15 q-12 -7 -12 -15z"/><path d="M180 140 a5 5 0 0 1 9 -4 a5 5 0 0 1 9 4 q0 6 -9 11 q-9 -5 -9 -11z" fill="#C7B5F0"/></g>
  <g fill="#F6D77E"><path d="M470 160 l5 11 12 1 -9 8 3 12 -11 -7 -11 7 3 -12 -9 -8 12 -1z"/><path d="M360 110 l3 7 8 1 -6 5 2 8 -7 -4 -7 4 2 -8 -6 -5 8 -1z"/></g>
</svg>"""

WAVE = '<svg class="wave" viewBox="0 0 1440 60" preserveAspectRatio="none" aria-hidden="true"><path d="M0 30 Q180 0 360 30 T720 30 T1080 30 T1440 30 V60 H0Z"/></svg>'


# ---------------------------------------------------------------- rendering
def render_notebook(s):
    """Slides in the notebook ('notes') style: cover, card, number, table, mnemonic."""
    kind = s.get("kind")
    if kind == "cover":
        chips = "".join(f'<span class="chipnb" style="background:{esc(c.get("color", "#eee"))}">{esc(c.get("text", ""))}</span>'
                        for c in s.get("chips", []))
        kick = f'<p class="kicker">{fmt(s["kicker"])}</p>' if s.get("kicker") else ""
        chipdiv = f'<div class="chipsnb">{chips}</div>' if chips else ""
        sub = f'<p class="sub">{fmt(s["sub"])}</p>' if s.get("sub") else ""
        return (f'<section class="block nb-cover">{kick}'
                f'<h2>{fmt(s.get("title"))} {fmt(s.get("title2"))}</h2>{chipdiv}{sub}</section>')
    if kind == "card":
        color = esc(s.get("color", "#E3D9FA"))
        rows = "".join(f"<tr><th>{fmt(k)}</th><td>{fmt(v)}</td></tr>" for k, v in s.get("rows", []))
        pill = f'<span class="pillnb" style="background:{color}">{esc(s["pill"])}</span>' if s.get("pill") else ""
        tag = f'<p class="sub">{fmt(s["tagline"])}</p>' if s.get("tagline") else ""
        return (f'<section class="block nb-card" style="border-left-color:{color}">{pill}'
                f'<h2>{fmt(s.get("title"))}</h2>{tag}<div class="tablewrap"><table class="kv"><tbody>{rows}</tbody></table></div></section>')
    if kind == "number":
        checks = ""
        if s.get("checks"):
            checks = (f'<h3>{fmt(s.get("checks_title", ""))}</h3><ul class="checks">' +
                      "".join(f"<li>{fmt(c)}</li>" for c in s["checks"]) + "</ul>")
        note = f'<p class="pearl"><b>Note</b>{fmt(s["note"])}' + (f' <em>({fmt(s["note_hand"])})</em>' if s.get("note_hand") else "") + "</p>" if s.get("note") else ""
        kick = f'<p class="kicker">{fmt(s["kicker"])}</p>' if s.get("kicker") else ""
        return (f'<section class="block nb-number">{kick}<div class="bignum">{esc(s.get("big", ""))}</div>'
                f'<p class="lead">{fmt(s.get("text"))}</p>{note}{checks}</section>')
    if kind == "table":
        cols = s.get("cols", [])
        head = "<th></th>" + "".join(f'<th style="background:{esc(c.get("color", "#CFE5FA"))}">{esc(c.get("text", ""))}</th>' for c in cols)
        body = "".join("<tr>" + f"<th>{fmt(r[0])}</th>" + "".join(f"<td>{fmt(c)}</td>" for c in r[1:]) + "</tr>"
                       for r in s.get("rows", []))
        return (f'<section class="block nb-table"><h2><span class="emo">📋</span>{fmt(s.get("title"))}</h2>'
                f'<div class="tablewrap"><table class="nbt"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div></section>')
    if kind == "mnemonic":
        kick = f'<p class="kicker">{fmt(s["kicker"])}</p>' if s.get("kicker") else ""
        lines = "".join(f"<li>{fmt(l)}</li>" for l in s.get("lines", []))
        return f'<section class="block takeaway nb-mnemonic"><h2><span class="emo">🧠</span>Remember</h2>{kick}<ul class="lines">{lines}</ul></section>'
    return ""


def render_slide(s, notebook=False):
    kind = s.get("kind")
    if notebook:
        return render_notebook(s)
    if kind in ("cover", "cta"):
        return ""  # cover is the page header; site has its own follow box
    emoji, title = esc(s.get("emoji", "")), fmt(s.get("title", ""))
    sub, pts, hl = s.get("subtitle", ""), s.get("points", []), s.get("highlight", "")
    out = []

    if kind == "drug":
        out.append('<section class="block drug">')
        out.append(f'<dl class="drugfacts"><dt>Class</dt><dd>{fmt(s.get("drug_class"))}</dd>'
                   f'<dt>Mechanism</dt><dd>{fmt(s.get("moa"))}</dd></dl>')
        if s.get("uses"):
            out.append('<h2><span class="emo">🎯</span>Uses</h2><ul>' +
                       "".join(f"<li>{fmt(u)}</li>" for u in s["uses"]) + "</ul>")
        if s.get("doses"):
            out.append('<h2><span class="emo">💉</span>Paediatric doses</h2><ul class="doses">' +
                       "".join(f"<li>{fmt(u)}</li>" for u in s["doses"]) + "</ul>")
        if hl:
            out.append(f'<p class="pearl caution"><b>Caution</b>{fmt(hl)}</p>')
        out.append("</section>")
        return "\n".join(out)

    out.append(f'<section class="block {esc(kind or "")}">')
    out.append(f'<h2><span class="emo">{emoji}</span>{title}</h2>')
    if kind == "compare":
        heads = [h.strip() for h in sub.split("||")] if "||" in sub else ["", ""]
        out.append('<div class="tablewrap"><table><thead><tr>' +
                   "".join(f"<th>{fmt(h)}</th>" for h in heads) + "</tr></thead><tbody>")
        for p in pts:
            out.append("<tr>" + "".join(f"<td>{fmt(c.strip())}</td>" for c in p.split("||")) + "</tr>")
        out.append("</tbody></table></div>")
    elif kind == "mnemonic":
        if sub:
            out.append(f'<p class="sub">{fmt(sub)}</p>')
        out.append('<ul class="mnemonic">')
        for p in pts:
            m = re.match(r"^\s*(\S{1,3})\s*[-–:]\s*(.+)$", p)
            if m:
                out.append(f'<li><span class="letter">{esc(m.group(1))}</span><span>{fmt(m.group(2))}</span></li>')
            else:
                out.append(f"<li><span></span><span>{fmt(p)}</span></li>")
        out.append("</ul>")
    else:
        if sub:
            out.append(f'<p class="sub">{fmt(sub)}</p>')
        out.append("<ul>" + "".join(f"<li>{fmt(p)}</li>" for p in pts) + "</ul>")
    if hl:
        out.append(f'<p class="pearl"><b>Pearl</b>{fmt(hl)}</p>')
    out.append("</section>")
    return "\n".join(out)


IG_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.5" cy="6.5" r="1.3" fill="currentColor"/></svg>'
YT_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="5" width="20" height="14" rx="4" fill="none" stroke="currentColor" stroke-width="2"/><path d="M10 9l5 3-5 3z" fill="currentColor"/></svg>'


def social_buttons(cls="btn"):
    b = f'<a class="{cls} ig" href="{esc(IG)}" rel="noopener" target="_blank">{IG_ICON}Instagram</a>'
    if YT:
        b += f'<a class="{cls} yt" href="{esc(YT)}" rel="noopener" target="_blank">{YT_ICON}YouTube</a>'
    return b


NAV = [("index.html", "Home", "home"), ("notes.html", "Study notes", "notes"),
       ("drugs.html", "Drug of the Day", "drugs"), ("parents.html", "Parents", "parents"),
       ("reels.html", "Videos", "reels"), ("books.html", "Books", "books"), ("about.html", "About", "about")]


def page(title, body, desc="", depth=0, active=""):
    up = "../" * depth
    full = SITE_NAME if title == SITE_NAME else f"{title} · {SITE_NAME}"
    on = ' class="on"'
    links = "".join(f'<a href="{up}{h}"{on if k == active else ""}>{l}</a>' for h, l, k in NAV)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>{esc(full)}</title>
<meta name="description" content="{esc(desc or TAGLINE)}">
<meta property="og:title" content="{esc(full)}">
<meta property="og:description" content="{esc(desc or TAGLINE)}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🧸</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}style.css?v={CSS_VER}">
</head>
<body>
<header class="top">
  <a class="brand" href="{up}index.html"><span class="logo">🧸</span>{SITE_NAME}</a>
  <details class="menu"><summary aria-label="Menu">☰ Menu</summary><nav>{links}</nav></details>
  <nav class="desk">{links}</nav>
</header>
<main>
{body}
</main>
<footer>
  {WAVE}
  <div class="footin">
    <p class="fbrand">🧸 {SITE_NAME}</p>
    <div class="social">{social_buttons("pill")}</div>
    <p><b>For education only.</b> Not a substitute for a doctor's advice. Always follow local protocols and verify doses with a current formulary.</p>
  </div>
</footer>
</body>
</html>
"""


def card(p, up=""):
    img = f'<img src="{up}posts/{p["slug"]}/{p["images"][0]}" alt="" loading="lazy">' if p["images"] else ""
    label = "Drug of the Day" if p["kind"] == "drug" else ("MBBS notes" if p["notebook"] else "Topic notes")
    hay =esc((p["title"] + " " + p["summary"] + " " + " ".join(p["hashtags"])).lower())
    return (f'<a class="card" href="{up}posts/{p["slug"]}/index.html" data-kind="{p["kind"]}" data-hay="{hay}">'
            f'{img}<div class="cardtext"><span class="tag {p["kind"]}">{label}</span>'
            f'<h3>{esc(p["title"])}</h3><p>{esc(p["summary"])}</p><time>{p["date"]}</time></div></a>')


def follow_box():
    return f"""<aside class="follow">
  <div class="fart">📱</div>
  <div><h2>Come say hi!</h2>
  <p>New notes, Drug of the Day and reels every week.</p></div>
  <div class="social">{social_buttons()}</div>
</aside>"""


SEARCH_JS = """<script>
(function(){
  var q=document.getElementById('q'), cards=[].slice.call(document.querySelectorAll('.card')),
      chips=[].slice.call(document.querySelectorAll('.chip')), kind='all', none=document.getElementById('none');
  function run(){
    var t=(q.value||'').toLowerCase().trim(), shown=0;
    cards.forEach(function(c){
      var ok=(kind==='all'||c.dataset.kind===kind)&&(!t||c.dataset.hay.indexOf(t)>-1);
      c.hidden=!ok; if(ok) shown++;
    });
    none.hidden=shown>0;
  }
  q.addEventListener('input',run);
  chips.forEach(function(ch){ch.addEventListener('click',function(){
    chips.forEach(function(x){x.classList.remove('on')}); ch.classList.add('on'); kind=ch.dataset.k; run();
  })});
})();
</script>"""

FUN_FACTS = [
    ("🦴", "About 300 bones", "Babies are born with around 300 bones. Many fuse as they grow, leaving 206 in adults."),
    ("👀", "Face-distance focus", "Newborns see most clearly at 20–30 cm, about the distance to a parent's face while feeding."),
    ("🧠", "Busy little brains", "A baby's brain roughly doubles in size during the first year of life."),
    ("💓", "Speedy hearts", "A newborn's heart beats about 120–160 times a minute, roughly twice an adult's."),
    ("🦵", "Soft kneecaps", "Babies' kneecaps start out as soft cartilage and slowly turn into bone over the early years."),
    ("📏", "Growth spurt", "Most babies grow about 25 cm in length during their first year."),
]

PARENT_TIPS = [
    ("🚨", "See a doctor quickly if your child",
     ["Is breathing fast or with difficulty", "Is not feeding or drinking at all",
      "Is unusually sleepy or hard to wake", "Has a fit (seizure)",
      "Is under 3 months old and has a fever"]),
    ("💉", "Vaccines on time", ["Follow your national or IAP immunisation schedule",
                                "Keep the vaccination card safe and bring it to every visit",
                                "Mild fever or soreness after a vaccine is common"]),
    ("🤱", "Feeding", ["Only breast milk for the first 6 months (WHO)",
                      "Start soft home foods at 6 months and continue breastfeeding",
                      "No honey before 1 year of age"]),
    ("💧", "Diarrhoea & vomiting", ["Give ORS in small, frequent sips",
                                    "Keep feeding: don't stop breast milk or food",
                                    "Zinc is advised for children with diarrhoea in India"]),
    ("😴", "Safe sleep for babies", ["Always put babies to sleep on their back",
                                     "Firm, flat mattress; no pillows or soft toys in the cot",
                                     "Keep the baby smoke-free"]),
    ("📈", "Growth & milestones", ["Get weight and height checked at well-baby visits",
                                   "Smiles by about 2 months, sits by about 6–8 months, walks by about 12–15 months",
                                   "Ask your doctor if you notice any delay"]),
]


def build():
    # OneDrive can lock folders on Windows, so clear what we can and overwrite the rest.
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(exist_ok=True)
    shutil.copy(HERE / "style.css", OUT / "style.css")
    (OUT / ".nojekyll").write_text("")
    if (HERE / "books").exists():
        shutil.copytree(HERE / "books", OUT / "books", dirs_exist_ok=True)

    posts, reels, videos = load_posts(), load_reels(), load_videos()
    topics = [p for p in posts if p["kind"] == "topic"]
    drugs = [p for p in posts if p["kind"] == "drug"]
    parent_reels = [r for r in reels if r["audience"] == "parents"]
    for v in videos:
        vdir = OUT / "videos" / v["slug"]
        vdir.mkdir(parents=True, exist_ok=True)
        for f in ("video.mp4", "thumb.jpg"):
            if (CONTENT / "videos" / v["slug"] / f).exists():
                shutil.copy(CONTENT / "videos" / v["slug"] / f, vdir / f)

    # --- post pages
    for p in posts:
        pdir = OUT / "posts" / p["slug"]
        pdir.mkdir(parents=True, exist_ok=True)
        for im in p["images"]:
            shutil.copy(p["dir"] / im, pdir / im)
        notes = "\n".join(render_slide(s, p["notebook"]) for s in p["slides"])
        gallery = ""
        if p["images"]:
            gallery = ('<details class="gallery"><summary>🖼️ View the original slides '
                       f'({len(p["images"])})</summary><div class="slides">' +
                       "".join(f'<img src="{im}" alt="Slide {i+1}" loading="lazy">'
                               for i, im in enumerate(p["images"])) + "</div></details>")
        refs = ('<p class="refs"><b>Source:</b> ' + "; ".join(esc(r) for r in p["references"]) + "</p>") if p["references"] else ""
        is_drug = p["kind"] == "drug"
        lede = p["summary"] if p["summary"] and not is_drug else ""
        body = f"""<article class="post">
<a class="back" href="../../{'drugs' if is_drug else 'notes'}.html">← All {'drugs' if is_drug else 'study notes'}</a>
<header class="posthead">
  <span class="tag {p['kind']}">{'Drug of the Day' if is_drug else ('MBBS notes' if p['notebook'] else 'Topic notes')}</span>
  <h1><span class="emo">{esc(p['emoji'])}</span>{esc(p['title'])}</h1>
  {f'<p class="lede">{esc(lede)}</p>' if lede and not p['notebook'] else ''}
  <p class="meta"><time datetime="{p['iso']}">{p['date']}</time></p>
</header>
{notes}
{refs}
{gallery}
{follow_box()}
</article>"""
        (pdir / "index.html").write_text(
            page(p["title"], body, p["summary"], depth=2, active="drugs" if is_drug else "notes"), encoding="utf-8")

    # --- home: a welcome, not study matter
    facts = "".join(f'<div class="fact"><span class="big">{e}</span><h3>{t}</h3><p>{d}</p></div>' for e, t, d in FUN_FACTS)
    books_teaser = ""
    if BOOKS:
        b = BOOKS[0]
        label = "Coming soon" if b.get("status") == "coming_soon" else "Latest"
        books_teaser = f'<p><b>{label}:</b> {esc(b.get("title", ""))}</p>'
    yt_card = ""
    if YT:
        yt_card = f'<a class="path p-yt" href="{esc(YT)}" target="_blank" rel="noopener"><span class="pic">▶️</span><h3>YouTube</h3><p>Longer videos and explainers.</p><span class="go">Watch →</span></a>'
    home = f"""<section class="hero">
  <div class="herotext">
    <span class="hello">👋 Hello and welcome!</span>
    <h1>Step into the little world of <em>paediatrics</em></h1>
    <p>Children aren't small adults. They grow, play, catch colds and surprise us every day. This is a cheerful corner of the internet for <b>future paediatricians</b> and for <b>parents</b> who want to understand their little ones better.</p>
    <div class="cta"><a class="btn primary" href="#paths">Start exploring</a>{social_buttons()}</div>
  </div>
  {HERO_ART}
</section>

<section class="world">
  <h2 class="center">What is paediatrics? 🧸</h2>
  <p class="center narrow">Paediatrics is the branch of medicine that cares for babies, children and teenagers, from the very first breath until about 18 years of age. It covers growth, development, vaccines, nutrition and every illness in between.</p>
  <div class="ages">
    <div class="age a1"><span>👶</span><h3>Newborn</h3><p>First 28 days</p></div>
    <div class="age a2"><span>🍼</span><h3>Infant</h3><p>Up to 1 year</p></div>
    <div class="age a3"><span>🧒</span><h3>Toddler &amp; preschool</h3><p>1–5 years</p></div>
    <div class="age a4"><span>🎒</span><h3>School age</h3><p>6–12 years</p></div>
    <div class="age a5"><span>🧑‍🎓</span><h3>Adolescent</h3><p>10–18 years</p></div>
  </div>
</section>

<section id="paths" class="paths-wrap">
  <h2 class="center">Where would you like to go? ✨</h2>
  <div class="paths">
    <a class="path p-notes" href="notes.html"><span class="pic">📚</span><h3>Study notes</h3><p>High-yield tables, mnemonics and exam pearls for NEET-PG, INI-CET, FMGE and MBBS.</p><span class="go">{len(topics)} topics →</span></a>
    <a class="path p-drug" href="drugs.html"><span class="pic">💊</span><h3>Drug of the Day</h3><p>Paediatric doses, uses and mechanisms, one drug at a time.</p><span class="go">{len(drugs)} drugs →</span></a>
    <a class="path p-parents" href="parents.html"><span class="pic">👨‍👩‍👧</span><h3>For parents</h3><p>Simple, calm guidance on fever, feeding, vaccines and when to see a doctor.</p><span class="go">Parent corner →</span></a>
    <a class="path p-reels" href="reels.html"><span class="pic">🎬</span><h3>Videos</h3><p>Calm video guides and quick reels for students and parents.</p><span class="go">{len(videos) + len(reels)} videos →</span></a>
    <a class="path p-books" href="books.html"><span class="pic">📖</span><h3>Books</h3><p>Our medical books and revision guides.</p>{books_teaser}<span class="go">See books →</span></a>
    {yt_card}
  </div>
</section>

<section class="facts-wrap">
  <h2 class="center">Tiny humans, amazing facts 🌟</h2>
  <div class="facts">{facts}</div>
</section>

{follow_box()}"""
    (OUT / "index.html").write_text(page(SITE_NAME, home, active="home"), encoding="utf-8")

    # --- study notes
    grid = "".join(card(p) for p in posts)
    notes = f"""<section class="phead s-notes"><span class="big">📚</span><div><h1>Study notes</h1>
<p>Exam-ready paediatrics for NEET-PG, INI-CET, FMGE, MBBS and residents. Search or filter below.</p></div></section>
<div class="tools">
  <input id="q" type="search" placeholder="🔎 Search a topic, drug or keyword…" aria-label="Search">
  <div class="chips"><button class="chip on" data-k="all">All</button><button class="chip" data-k="topic">Topic notes</button><button class="chip" data-k="drug">Drug of the Day</button></div>
</div>
<div class="grid">{grid}</div>
<p id="none" class="none" hidden>Nothing matches yet. More topics are added every week!</p>
{follow_box()}
{SEARCH_JS}"""
    (OUT / "notes.html").write_text(page("Study notes", notes, "High-yield paediatrics notes for NEET-PG and MBBS.", active="notes"), encoding="utf-8")

    # --- drugs
    dgrid = "".join(card(p) for p in drugs)
    dbody = f"""<section class="phead s-drug"><span class="big">💊</span><div><h1>Drug of the Day</h1>
<p>Class, mechanism, uses and paediatric doses. Always check doses against your unit's formulary.</p></div></section>
<div class="grid">{dgrid}</div>{follow_box()}"""
    (OUT / "drugs.html").write_text(page("Drug of the Day", dbody, "Paediatric drug doses, uses and mechanisms.", active="drugs"), encoding="utf-8")

    # --- videos (long videos played right here) + reel notes
    def reel_card(r):
        items = "".join(f"<li>{esc(l.lstrip('•· ').strip())}</li>" for l in r["body"][:6])
        who = "For parents" if r["audience"] == "parents" else "For PG / MBBS"
        return f"""<article class="reel r-{r['audience']}"><span class="tag reel">{who}</span>
<h3>{esc(r['title'])}</h3><ul>{items}</ul>
<p class="meta"><time>{r['date']}</time></p></article>"""

    def video_block(v):
        poster = f' poster="videos/{v["slug"]}/thumb.jpg"' if v["thumb"] else ""
        chapters = "".join(f'<li><button class="chap" data-t="{esc(t)}">{esc(t)}</button> {esc(n)}</li>' for t, n in v["chapters"])
        pts = "".join(f"<li>{esc(x)}</li>" for x in v["points"])
        intro = "".join(f"<p>{esc(x)}</p>" for x in v["intro"])
        yt = f'<a class="btn yt" href="{esc(v["youtube"])}" target="_blank" rel="noopener">{YT_ICON}Watch on YouTube</a>' if v["youtube"] else ""
        who = "For parents" if v["audience"] == "parents" else "For PG / MBBS"
        return f"""<article class="video" id="{esc(v['slug'])}">
<video controls preload="metadata" playsinline{poster} src="videos/{v['slug']}/video.mp4"></video>
<div class="vtext"><span class="tag reel">{who}</span><h2>{esc(v['title'])}</h2>{intro}
{f'<h3>Chapters</h3><ol class="chapters">{chapters}</ol>' if chapters else ''}
{f'<h3>In this video</h3><ul>{pts}</ul>' if pts else ''}
<p class="meta"><time>{v['date']}</time></p>{yt}</div></article>"""

    CHAPTER_JS = """<script>
document.querySelectorAll('.video').forEach(function(box){
  var vid=box.querySelector('video');
  box.querySelectorAll('.chap').forEach(function(b){b.addEventListener('click',function(){
    var p=b.dataset.t.split(':'); vid.currentTime=(+p[0])*60+(+p[1]); vid.play(); vid.scrollIntoView({behavior:'smooth',block:'center'});
  })});
});
</script>"""
    vblocks = "".join(video_block(v) for v in videos)
    rbody = f"""<section class="phead s-reels"><span class="big">🎬</span><div><h1>Videos</h1>
<p>Calm, simple video guides you can watch right here, plus notes from our short reels.</p></div></section>
{f'<div class="videos">{vblocks}</div>' if vblocks else ''}
{f'<h2 class="center mt">Reel notes 📝</h2><div class="reels">{"".join(reel_card(r) for r in reels)}</div>' if reels else ''}
{follow_box()}
{CHAPTER_JS if vblocks else ''}"""
    (OUT / "reels.html").write_text(page("Videos", rbody, "Paediatric video guides for parents and students.", active="reels"), encoding="utf-8")

    # --- parents
    tips = "".join(f'<div class="tip"><span class="big">{e}</span><h3>{t}</h3><ul>' +
                   "".join(f"<li>{esc(x)}</li>" for x in xs) + "</ul></div>" for e, t, xs in PARENT_TIPS)
    preels = "".join(reel_card(r) for r in parent_reels)
    pvids = "".join(f'<a class="vcard" href="reels.html#{esc(v["slug"])}">'
                    + (f'<img src="videos/{v["slug"]}/thumb.jpg" alt="" loading="lazy">' if v["thumb"] else "")
                    + f'<span class="play">▶</span><div><span class="tag reel">Video guide</span><h3>{esc(v["title"])}</h3></div></a>'
                    for v in videos if v["audience"] == "parents")
    pbody = f"""<section class="phead s-parents"><span class="big">👨‍👩‍👧</span><div><h1>Parent corner</h1>
<p>Calm, simple guidance for everyday childhood worries. This is general information, so your child's own doctor always knows best.</p></div></section>
{f'<div class="vcards">{pvids}</div>' if pvids else ''}
<div class="tips">{tips}</div>
{f'<h2 class="center mt">Reel notes for parents 🎬</h2><div class="reels">{preels}</div>' if preels else ''}
<p class="pearl caution wide"><b>Emergency?</b>If your child is very unwell, go to the nearest hospital or call your local emergency number. Don't wait for online advice.</p>
{follow_box()}"""
    (OUT / "parents.html").write_text(page("Parent corner", pbody, "Simple paediatric guidance for parents.", active="parents"), encoding="utf-8")

    # --- books
    if BOOKS:
        bc = []
        for b in BOOKS:
            soon = b.get("status") == "coming_soon"
            if b.get("cover"):
                cover = f'<img src="{esc(b["cover"])}" alt="Cover of {esc(b.get("title", ""))}">'
            elif b.get("cover_text"):
                lines = b["cover_text"]
                cover = ('<div class="drawncover"><span class="dc-top">' + esc(b.get("series", "")) + '</span>' +
                         "".join(f'<span class="dc-l{i}">{esc(l)}</span>' for i, l in enumerate(lines)) +
                         '<span class="dc-curve"></span></div>')
            else:
                cover = '<div class="nocover">📖</div>'
            ribbon = '<span class="ribbon">Coming soon</span>' if soon else ""
            if b.get("link") and not soon:
                action = f'<a class="btn primary" href="{esc(b["link"])}" target="_blank" rel="noopener">{esc(b.get("button", "Get the book"))}</a>'
            elif soon:
                action = f'<a class="btn ig" href="{esc(IG)}" target="_blank" rel="noopener">{IG_ICON}Follow for launch news</a>'
            else:
                action = ""
            price = f'<p class="price">{esc(b["price"])}</p>' if b.get("price") and not soon else ""
            series = f'<span class="series">{esc(b["series"])}</span>' if b.get("series") else ""
            aud = f'<p class="aud">🎯 {esc(b["audience"])}</p>' if b.get("audience") else ""
            hl = ("<ul class='bhl'>" + "".join(f"<li>{esc(h)}</li>" for h in b["highlights"]) + "</ul>") if b.get("highlights") else ""
            fm = f'<p class="formats">📦 {esc(b["formats"])}</p>' if b.get("formats") else ""
            bc.append(f'<article class="book{" upcoming" if soon else ""}"><div class="bcover">{ribbon}{cover}</div><div class="bt">{series}'
                      f'<h3>{esc(b.get("title", ""))}</h3>{aud}<p>{esc(b.get("description", ""))}</p>{hl}{fm}{price}{action}</div></article>')
        books_html = f'<div class="books">{"".join(bc)}</div>'
    else:
        books_html = f"""<div class="soon"><span class="big">📖✨</span><h2>Books are on the way!</h2>
<p>Revision guides and medical books by {SITE_NAME} will appear here. Follow along to hear first.</p><div class="social">{social_buttons()}</div></div>"""
    bbody = f"""<section class="phead s-books"><span class="big">📖</span><div><h1>Books</h1>
<p>Medical books and revision guides, made with the same love as the posts.</p></div></section>
{books_html}"""
    (OUT / "books.html").write_text(page("Books", bbody, "Medical books by Paediatrick or Treats.", active="books"), encoding="utf-8")

    # --- about
    abody = f"""<article class="post about">
<section class="phead s-about"><span class="big">🧸</span><div><h1>About</h1>
<p>{SITE_NAME} turns paediatrics into clear, friendly, swipeable notes.</p></div></section>
<section class="block"><h2><span class="emo">🎓</span>Who it's for</h2><ul>
<li><strong>NEET-PG, INI-CET and FMGE aspirants</strong>: high-yield tables, mnemonics and exam pearls.</li>
<li><strong>MBBS students and paediatric residents</strong>: quick revision for wards and OPDs.</li>
<li><strong>Parents</strong>: simple guides on common childhood illnesses and when to see a doctor.</li></ul></section>
<section class="block"><h2><span class="emo">📚</span>How the notes are made</h2><ul>
<li>Based on standard references and guidelines (IAP, WHO, ISPAD and standard paediatric textbooks).</li>
<li>Every post is checked before it is published.</li>
<li>Spotted an error? Send a DM on Instagram and it will be corrected.</li></ul></section>
<p class="pearl caution"><b>Disclaimer</b>All content is for education only and is not a substitute for professional medical advice. Doses must be verified against a current formulary and local protocols.</p>
{follow_box()}
</article>"""
    (OUT / "about.html").write_text(page("About", abody, active="about"), encoding="utf-8")

    (OUT / "404.html").write_text(page("Not found", '<section class="soon"><span class="big">🧸❓</span><h2>Oops, page not found</h2><p><a href="/paeds-carousels/">Back to the home page</a></p></section>'), encoding="utf-8")
    print(f"Built {len(topics)} topics, {len(drugs)} drugs, {len(videos)} videos, {len(reels)} reels, {len(BOOKS)} books -> {OUT}")


if __name__ == "__main__":
    build()
