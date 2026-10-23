"""Build the Our World landing page artefacts from one content definition.

Outputs (next to this file):
  our-world-elementor-template.json  Elementor template for import into page 17225
  preview/our-world.html             Local preview using the live site's real page shell

Usage:
  python build.py [path/to/gala-dinner.html]

The preview shell is any live GP Refresh page that uses the Elementor Full Width
template (page-template-elementor_header_footer), e.g. a saved copy of
https://www.gprefresh.com/gala-dinner/. Its header, footer, theme CSS and scripts
are kept untouched; only the Elementor page body is swapped for this page's markup.
"""

import base64
import copy
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
UPLOADS = "https://www.gprefresh.com/wp-content/uploads/2026/03"
PAGE_ID = 17225  # existing draft page at https://www.gprefresh.com/our-world/

# ---------------------------------------------------------------- content

REGISTER_URL = "https://events.gprefresh.com/"

# Hero: headline and facts are the homepage's own ("Join the 6-Minute GP Refresh CPD Revolution",
# "Built Around Four Pillars"); the cities and group saving come from the sections below.
EYEBROW = "GP Refresh | 2027 Conferences"
TITLE = "Join the 6-Minute GP Refresh CPD Revolution"
LEDE = ("77 six-minute talks, up to 53 CPD hours and no sponsored talks. "
        "Register together and save up to 50% with group discounts.")
STATUS = "Melbourne | Sydney | Brisbane"
BUTTON = {"text": "Register Now", "url": REGISTER_URL}

PILLARS_EYEBROW = "Refresh | Reframe | Reignite"  # existing homepage eyebrow
PILLARS_LINES = [  # existing homepage slide headings
    "Refresh the basics.",
    "Reframe the evidence.",
    "Reignite your passion for patient care.",
]
PILLARS_COPY = ("Up to 53 CPD hours, 77 six-minute talks, no sponsored talks, "
                "and the Grand Gala Dinner to bring it all together.")

# Upcoming Conferences: copied from the homepage "Upcoming Conferences" block (verified 23 Oct 2026)
EVENTS_EYEBROW = "GP Refresh Int’l Congress"
EVENTS_TITLE = "Upcoming Conferences"
EVENTS_LEDE = "Two days of six-minute talks, up to 53 CPD hours and the Gala Dinner, in a city near you."
EVENTS = [
    {"date": "15–16 May ’27", "city": "Melbourne",
     "image": "assets/melbourne.jpeg", "image_width": 1600, "image_height": 1066,
     "image_alt": "Melbourne city skyline overlooking Flinders Street Station",
     "venue": "Melbourne Convention and Exhibition Centre (MCEC)", "url": REGISTER_URL, "cta": "Register Now"},
    {"date": "26–27 June ’27", "city": "Sydney",
     "image": "assets/sydney.jpeg", "image_width": 1600, "image_height": 900,
     "image_alt": "Sydney Opera House and city skyline beside the harbour",
     "venue": "International Convention & Exhibition Centre (ICC Sydney)", "url": REGISTER_URL, "cta": "Register Now"},
    {"date": "18–19 Sep ’27", "city": "Brisbane",
     "image": "assets/brisbane.jpeg", "image_width": 1600, "image_height": 1200,
     "image_alt": "Brisbane city skyline and bridge spanning the Brisbane River",
     "venue": "Brisbane Convention & Exhibition Centre (BCEC)", "url": REGISTER_URL, "cta": "Register Now"},
    {"date": "Dec ’27", "tbc": True, "city": "Int’l Cruises",
     "venue": "Dates and itinerary to be confirmed", "url": "https://www.gprefresh.com/expression-of-interest/",
     "cta": "Learn More"},
    {"date": "8–9 Jan ’28", "tbc": True, "city": "Dubai",
     "venue": "Venue to be confirmed", "url": "https://www.gprefresh.com/dubai/", "cta": "Learn More"},
]

# Counts down to the first conference date, not an unconfirmed session start time.
# May in Melbourne uses AEST (UTC+10); an explicit offset is independent of the visitor's timezone.
COUNTDOWN_TARGET = "2027-05-15T00:00:00+10:00"
COUNTDOWN_LABEL = "Until Melbourne"
COUNTDOWN_DATE = "15 May 2027 · Melbourne time"

# Group Discounts: the "2nd Release" table on https://www.gprefresh.com/pricing/ (verified 23 Oct 2026).
# Keep in step with the admin panel; the 5+ price is listed there as excl. GST.
GROUPS_EYEBROW = "Group Discounts | 2nd Release"
GROUPS_TITLE = "Register together and save up to 50%."
GROUPS_LEDE = ("Bring colleagues from your practice and every delegate pays less per Conference Pass. "
               "Group discounts also apply to the Gala Dinner pass.")
GROUP_TIERS = [
    {"label": "Individual Pass", "off": "30%", "price": "A$979.30", "gst": "incl. GST", "was": "A$1399"},
    {"label": "Group of 2", "off": "33%", "price": "A$937.33", "gst": "incl. GST"},
    {"label": "Group of 3", "off": "36%", "price": "A$895.36", "gst": "incl. GST"},
    {"label": "Group of 4", "off": "40%", "price": "A$839.40", "gst": "incl. GST"},
    {"label": "Group of 5+", "off": "50%", "price": "A$699.50", "gst": "excl. GST", "best": True},
]
GROUP_NOTES = [
    "Conference Pass A$1399 (incl. GST): symposium program and materials, lunch and coffee breaks.",
    "Gala Dinner A$329: complimentary (special promotion). CPR Workshop: complimentary for all delegates.",
]
TERMS_URL = "https://www.gprefresh.com/terms-conditions/"
PRICING_URL = "https://www.gprefresh.com/pricing/"

# Discount artwork from the BLT group. Add one entry per image once supplied, e.g.
#   {"src": "https://www.gprefresh.com/wp-content/uploads/2026/10/group-offer.webp", "alt": "...", "width": 1200, "height": 900}
BLT_VISUALS = []

# Testimonials: the self-contained section in preview/social.html, embedded as-is in an HTML widget
SOCIAL_HTML = HERE / "preview" / "social.html"


def picture(name, alt, sizes, loading, extra=""):
    """<img> using the existing WordPress-generated crops of a gallery image (3:2, 2304x1536 original)."""
    srcset = ", ".join([
        f"{UPLOADS}/{name}-768x512.webp 768w",
        f"{UPLOADS}/{name}-1536x1024.webp 1536w",
        f"{UPLOADS}/{name}.webp 2304w",
    ])
    return (f'<img src="{UPLOADS}/{name}-1536x1024.webp" srcset="{srcset}" sizes="{sizes}" '
            f'width="2304" height="1536" alt="{html.escape(alt)}" loading="{loading}" decoding="async"{extra}>')


HERO_IMG = picture(
    "conference-8",
    "Two delegates wearing GP Refresh lanyards in conversation during a conference break",
    "100vw", "eager", ' fetchpriority="high"')
PILLARS_IMG = picture(
    "conference-6",
    "GP Refresh delegates seated at round tables during a conference session",
    "(max-width: 1024px) 100vw, 50vw", "lazy")

PILLARS_TITLE_HTML = "".join(f'<span class="gpr-ow-line">{html.escape(l)}</span>' for l in PILLARS_LINES)


def events_html(embed_images=False):
    rows = []
    for e in EVENTS:
        tbc = ' <span class="gpr-ow-event__tbc">TBC</span>' if e.get("tbc") else ""
        # The preview uses the supplied JPEG files directly. Embed the same bytes in
        # the Elementor export so an import cannot point at nonexistent /assets URLs.
        media = ""
        if e.get("image"):
            src = e["image"]
            if embed_images and src.startswith("assets/"):
                image_bytes = (HERE / "preview" / src).read_bytes()
                src = "data:image/jpeg;base64," + base64.b64encode(image_bytes).decode("ascii")
            media = (f'<div class="gpr-ow-event__media"><img src="{html.escape(src)}" '
                     f'alt="{html.escape(e["image_alt"])}" width="{e["image_width"]}" '
                     f'height="{e["image_height"]}" loading="lazy" decoding="async"></div>')
        modifier = "" if media else " gpr-ow-event--compact"
        rows.append(
            f'<li class="gpr-ow-event{modifier}">{media}'
            '<div class="gpr-ow-event__content">'
            f'<p class="gpr-ow-event__date">{html.escape(e["date"])}{tbc}</p>'
            '<div class="gpr-ow-event__body">'
            f'<h3 class="gpr-ow-event__city">{html.escape(e["city"])}</h3>'
            f'<p class="gpr-ow-event__venue">{html.escape(e["venue"])}</p></div>'
            f'<a class="gpr-ow-pill" href="{e["url"]}" aria-label="{html.escape(e["cta"])}: {html.escape(e["city"])}">'
            f'{html.escape(e["cta"])}</a></div></li>')
    return f'<ol class="gpr-ow-events__rows">{"".join(rows)}</ol>'


def countdown_html():
    units = "".join(
        f'<div class="gpr-ow-countdown__unit"><span data-unit="{unit}" '
        f'class="gpr-ow-countdown__value">--</span><span class="gpr-ow-countdown__label">{unit}</span></div>'
        for unit in ("days", "hours", "minutes", "seconds")
    )
    return (
        f'<div class="gpr-ow-countdown" data-gpr-countdown data-target="{html.escape(COUNTDOWN_TARGET)}">'
        '<div class="gpr-ow-countdown__topline">'
        '<span class="gpr-ow-countdown__eyebrow">Conference countdown</span>'
        f'<span class="gpr-ow-countdown__edition">{html.escape(COUNTDOWN_TARGET[:4])}</span></div>'
        f'<p class="gpr-ow-countdown__heading">{html.escape(COUNTDOWN_LABEL)}</p>'
        f'<div class="gpr-ow-countdown__digits" role="timer" aria-live="off" '
        f'aria-label="Countdown to Melbourne conference">{units}</div>'
        f'<p class="gpr-ow-countdown__date"><time datetime="{html.escape(COUNTDOWN_TARGET)}">'
        f'{html.escape(COUNTDOWN_DATE)}</time></p>'
        '<p class="gpr-ow-countdown__status" role="status" hidden>Conference countdown complete.</p>'
        '</div>'
        r"""<script>
(function () {
    'use strict';
    document.querySelectorAll('[data-gpr-countdown]').forEach(function (root) {
        if (root.dataset.initialized) return;
        var target = Date.parse(root.dataset.target);
        if (!Number.isFinite(target)) return;
        root.dataset.initialized = 'true';
        var timer;
        function update() {
            if (!root.isConnected) {
                clearInterval(timer);
                return false;
            }
            var remaining = Math.max(0, Math.ceil((target - Date.now()) / 1000));
            var values = {
                days: Math.floor(remaining / 86400),
                hours: Math.floor(remaining % 86400 / 3600),
                minutes: Math.floor(remaining % 3600 / 60),
                seconds: remaining % 60
            };
            Object.keys(values).forEach(function (unit) {
                root.querySelector('[data-unit="' + unit + '"]').textContent = String(values[unit]).padStart(2, '0');
            });
            if (remaining === 0) {
                root.querySelector('.gpr-ow-countdown__status').hidden = false;
                clearInterval(timer);
                return false;
            }
            return true;
        }
        if (update()) timer = setInterval(update, 1000);
    });
})();
</script>"""
    )


def groups_html():
    tiers = []
    for t in GROUP_TIERS:
        was = f'<s><span class="screen-reader-text">Was </span>{t["was"]}</s>' if t.get("was") else ""
        tiers.append(
            f'<li class="gpr-ow-tier{" gpr-ow-tier--best" if t.get("best") else ""}">'
            f'<p class="gpr-ow-tier__label">{html.escape(t["label"])}</p>'
            f'<p class="gpr-ow-tier__off">{t["off"]}<small>off</small></p>'
            f'<p class="gpr-ow-tier__price">{t["price"]}{was}'
            f'<span class="gpr-ow-tier__unit">per pass, {t["gst"]}</span></p></li>')
    notes = "".join(f"<li>{html.escape(n)}</li>" for n in GROUP_NOTES)
    notes += f'<li>See the <a href="{TERMS_URL}">terms and conditions</a>.</li>'
    visuals = ""
    if BLT_VISUALS:
        imgs = "".join(
            f'<img src="{v["src"]}" alt="{html.escape(v["alt"])}" width="{v["width"]}" height="{v["height"]}" '
            'loading="lazy" decoding="async">' for v in BLT_VISUALS)
        visuals = f'<div class="gpr-ow-visuals">{imgs}</div>'
    return (f'<ul class="gpr-ow-tiers">{"".join(tiers)}</ul>'
            '<div class="gpr-ow-groups__foot">'
            f'<ul class="gpr-ow-groups__notes">{notes}</ul>'
            '<div class="gpr-ow-groups__actions">'
            f'<a class="gpr-ow-pill gpr-ow-pill--solid" href="{REGISTER_URL}">Book Your Group</a>'
            f'<a class="gpr-ow-pill" href="{PRICING_URL}">Full Pricing</a></div></div>'
            f'{visuals}')


def testimonials_html(embed_images=False):
    """The section from preview/social.html, made safe to drop into a live page.

    Scope the standalone document's reset and tokens to this section. The social
    script already scopes its cards and viewing dialog to the section root.
    """
    src = SOCIAL_HTML.read_text(encoding="utf-8")
    css = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
    section = re.search(r"<section class=\"gpr-testimonials-section\".*?</section>", src, re.S).group(0)
    script = re.search(r"<script>(.*?)</script>", src, re.S).group(1)

    font = re.search(r"@import url\('([^']+)'\);", css).group(1)
    scope = ".gpr-testimonials-section"
    swaps = [
        (re.compile(r"@import url\('[^']+'\);"), ""),
        (re.compile(r"\*, \*::before, \*::after \{"),
         f"{scope}, {scope} *, {scope} *::before, {scope} *::after {{"),
        (re.compile(r"html, body \{.*?\}", re.S), ""),
        (re.compile(r":root \{"), f"{scope} {{"),
    ]
    for pattern, repl in swaps:
        css, n = pattern.subn(repl, css, count=1)
        assert n == 1, f"social.html CSS changed shape; update testimonials_html() ({pattern.pattern})"
    if embed_images:
        background = (HERE / "preview" / "assets" / "background image.jpeg").read_bytes()
        css = css.replace("assets/background%20image.jpeg",
                          "data:image/jpeg;base64," + base64.b64encode(background).decode("ascii"))

    return (f'<link rel="stylesheet" href="{html.escape(font)}">'
            f"<style>{css}</style>{section}<script>{script}</script>")

def motion_html():
    """Animate elements as they enter view; content stays visible without JS support."""
    return r"""<script>
(function () {
    'use strict';
    var root = (document.currentScript && document.currentScript.closest('[data-elementor-type="wp-page"]'))
        || document.querySelector('.elementor-PAGE_ID');
    if (!root || root.dataset.gprMotionReady || !window.matchMedia
        || !('IntersectionObserver' in window) || !Element.prototype.animate) return;
    root.dataset.gprMotionReady = 'true';
    var preference = window.matchMedia('(prefers-reduced-motion: reduce)');
    var active = new Set();
    var observer;
    var selectors = '.gpr-ow-hero__content > .elementor-widget, .gpr-ow-hero__meta, '
        + '.gpr-ow-events__header > .gpr-ow-head, .gpr-ow-countdown, .gpr-ow-event, '
        + '.gpr-ow-groups .gpr-ow-head, .gpr-ow-tier, .gpr-ow-pillars__media, .gpr-ow-pillars__text';
    function stop() {
        if (observer) observer.disconnect();
        active.forEach(function (animation) { animation.cancel(); });
        active.clear();
    }
    function start() {
        if (preference.matches) return;
        observer = new IntersectionObserver(function (entries) {
            var order = 0;
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                observer.unobserve(entry.target);
                if (preference.matches || entry.target.dataset.gprRevealed) return;
                entry.target.dataset.gprRevealed = 'true';
                if (entry.target.contains(document.activeElement)) return;
                var animation = entry.target.animate([
                    { opacity: 0, transform: 'translateY(14px)' },
                    { opacity: 1, transform: 'translateY(0)' }
                ], {
                    duration: 550, delay: (order++ % 3) * 70,
                    easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'backwards'
                });
                active.add(animation);
                animation.onfinish = animation.oncancel = function () { active.delete(animation); };
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -24px 0px' });
        root.querySelectorAll(selectors).forEach(function (element) {
            if (!element.dataset.gprRevealed) observer.observe(element);
        });
    }
    root.addEventListener('focusin', function (event) {
        active.forEach(function (animation) {
            if (animation.effect.target.contains(event.target)) animation.cancel();
        });
    });
    function changed() { stop(); start(); }
    if (preference.addEventListener) preference.addEventListener('change', changed);
    start();
})();
</script>""".replace("PAGE_ID", str(PAGE_ID))


# ---------------------------------------------------------------- element tree

_ids = iter(f"0w{n:05x}" for n in range(1, 999))


def container(classes, children, boxed=False, inner=False):
    return {"id": next(_ids), "elType": "container", "isInner": inner,
            "settings": {"content_width": "boxed" if boxed else "full", "css_classes": classes},
            "elements": children}


def widget(kind, classes, **settings):
    settings["_css_classes"] = classes
    return {"id": next(_ids), "elType": "widget", "widgetType": kind, "settings": settings, "elements": []}


def section_head(eyebrow, title, lede):
    return container("gpr-ow-head", inner=True, children=[
        widget("heading", "gpr-ow-eyebrow", title=eyebrow, header_size="p"),
        widget("heading", "gpr-ow-head__title", title=html.escape(title), header_size="h2"),
        widget("text-editor", "gpr-ow-head__lede", editor=f"<p>{html.escape(lede)}</p>"),
    ])


TREE = [
    container("gpr-ow-hero", boxed=True, children=[
        widget("html", "gpr-ow-hero__media", html=HERO_IMG),
        container("gpr-ow-hero__content", inner=True, children=[
            widget("heading", "gpr-ow-eyebrow", title=EYEBROW, header_size="p"),
            widget("heading", "gpr-ow-title", title=TITLE, header_size="h1"),
            widget("text-editor", "gpr-ow-lede", editor=f"<p>{html.escape(LEDE)}</p>"),
            container("gpr-ow-hero__meta", inner=True, children=[
                widget("heading", "gpr-ow-status", title=STATUS, header_size="p"),
                widget("button", "gpr-ow-button", text=BUTTON["text"], size="sm",
                       link={"url": BUTTON["url"], "is_external": "", "nofollow": ""}),
            ]),
        ]),
    ]),
    container("gpr-ow-events", boxed=True, children=[
        container("gpr-ow-events__header", inner=True, children=[
            section_head(EVENTS_EYEBROW, EVENTS_TITLE, EVENTS_LEDE),
            widget("html", "gpr-ow-events__countdown", html=countdown_html()),
        ]),
        widget("html", "gpr-ow-events__list", html=events_html()),
    ]),
    container("gpr-ow-testimonials", children=[
        widget("html", "gpr-ow-testimonials__embed", html=testimonials_html()),
    ]),
    container("gpr-ow-groups", boxed=True, children=[
        section_head(GROUPS_EYEBROW, GROUPS_TITLE, GROUPS_LEDE),
        widget("html", "gpr-ow-groups__body", html=groups_html()),
    ]),
    container("gpr-ow-pillars", children=[
        widget("html", "gpr-ow-pillars__media", html=PILLARS_IMG),
        container("gpr-ow-pillars__text", inner=True, children=[
            widget("heading", "gpr-ow-eyebrow", title=PILLARS_EYEBROW, header_size="p"),
            widget("heading", "gpr-ow-pillars__title", title=PILLARS_TITLE_HTML, header_size="h2"),
            widget("text-editor", "gpr-ow-pillars__copy", editor=f"<p>{html.escape(PILLARS_COPY)}</p>"),
            widget("html", "gpr-ow-motion", html=motion_html()),
        ]),
    ]),
]

# ---------------------------------------------------------------- render (mirrors Elementor 4.x frontend markup)


def render(el):
    s = el["settings"]
    if el["elType"] == "container":
        kind = "e-con-boxed" if s["content_width"] == "boxed" else "e-con-full"
        role = "e-child" if el["isInner"] else "e-parent"
        kids = "".join(render(c) for c in el["elements"])
        if kind == "e-con-boxed":
            kids = f'<div class="e-con-inner">{kids}</div>'
        return (f'<div class="elementor-element elementor-element-{el["id"]} {kind} e-flex e-con {role} {s["css_classes"]}" '
                f'data-id="{el["id"]}" data-element_type="container">{kids}</div>')
    w = el["widgetType"]
    if w == "heading":
        tag = s["header_size"]
        body = f'<{tag} class="elementor-heading-title elementor-size-default">{s["title"]}</{tag}>'
    elif w == "text-editor":
        body = s["editor"]
    elif w == "html":
        body = s["html"]
    elif w == "button":
        body = ('<div class="elementor-button-wrapper">'
                f'<a class="elementor-button elementor-button-link elementor-size-{s["size"]}" href="{s["link"]["url"]}">'
                f'<span class="elementor-button-content-wrapper"><span class="elementor-button-text">{html.escape(s["text"])}</span></span></a></div>')
    return (f'<div class="elementor-element elementor-element-{el["id"]} elementor-widget elementor-widget-{w} {s["_css_classes"]}" '
            f'data-id="{el["id"]}" data-element_type="widget" data-widget_type="{w}.default">'
            f'<div class="elementor-widget-container">{body}</div></div>')


def build_template(css):
    content = copy.deepcopy(TREE)
    for section in content:
        for element in section["elements"]:
            if element["settings"].get("_css_classes") == "gpr-ow-events__list":
                element["settings"]["html"] = events_html(embed_images=True)
            elif element["settings"].get("_css_classes") == "gpr-ow-testimonials__embed":
                element["settings"]["html"] = testimonials_html(embed_images=True)
    return {
        "version": "0.4",
        "title": "Our World — Landing Page",
        "type": "page",
        "page_settings": {
            "template": "elementor_header_footer",  # same Full Width template as Gala Dinner
            "hide_title": "yes",
            "custom_css": css,
        },
        "content": content,
    }


def build_preview(shell_path, css):
    shell = Path(shell_path).read_text(encoding="utf-8")
    # \s+ also matches a shell that has been through Prettier (attributes on their own lines)
    start = re.search(r'<div\s+data-elementor-type="wp-page"', shell).start()
    # find the matching </div> for the wp-page wrapper
    depth, i = 0, start
    for m in re.finditer(r"<div\b|</div>", shell[start:]):
        depth += 1 if m.group(0) == "<div" else -1
        if depth == 0:
            end = start + m.end()
            break
    page = (f'<div data-elementor-type="wp-page" data-elementor-id="{PAGE_ID}" '
            f'class="elementor elementor-{PAGE_ID}" data-elementor-post-type="page">'
            + "".join(render(e) for e in TREE) + "</div>")
    out = shell[:start] + page + shell[end:]
    out = re.sub(r"<title>[^<]*</title>", "<title>Our World - GP REFRESH Conference</title>", out, count=1)
    style = f'<style id="gpr-our-world-css">\n{css}\n</style>'
    # Re-running on an existing preview replaces its page CSS instead of adding a second copy
    out, n = re.subn(r'<style id="gpr-our-world-css">.*?</style>', lambda _: style, out, count=1, flags=re.S)
    if not n:
        out = out.replace("</head>", f"{style}\n</head>", 1)
    return out


def main():
    css = (HERE / "our-world.css").read_text(encoding="utf-8")
    (HERE / "our-world-elementor-template.json").write_text(
        json.dumps(build_template(css), indent=2, ensure_ascii=False), encoding="utf-8")
    if len(sys.argv) > 1:
        (HERE / "preview").mkdir(exist_ok=True)
        (HERE / "preview" / "our-world.html").write_text(build_preview(sys.argv[1], css), encoding="utf-8")
    print("built")


if __name__ == "__main__":
    main()
