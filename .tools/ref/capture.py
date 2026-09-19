import json
from playwright.sync_api import sync_playwright

PAGES = ["index", "projects", "contact", "trips", "resume"]
BASE = "http://littlesvr.ca/{}.php"

EXTRACT_JS = r"""
() => {
  const props = ["color","backgroundColor","fontFamily","fontSize","fontWeight",
    "lineHeight","paddingTop","paddingRight","paddingBottom","paddingLeft",
    "marginTop","marginRight","marginBottom","marginLeft",
    "borderTop","borderRight","borderBottom","borderLeft",
    "maxWidth","textAlign","textDecorationLine","display","width","height",
    "backgroundImage","borderRadius"];
  function snap(el){
    if(!el) return null;
    const cs = getComputedStyle(el);
    const o = {};
    for(const p of props) o[p] = cs[p];
    const r = el.getBoundingClientRect();
    o.rect = {x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height)};
    return o;
  }
  const q = s => document.querySelector(s);
  const qa = s => Array.from(document.querySelectorAll(s));
  const out = {};
  out.viewport = {w: window.innerWidth, h: window.innerHeight};
  out.body = snap(document.body);
  out.container = snap(q("#templateo_container"));
  out.top_panel = snap(q("#templatemo_top_panel"));
  out.site_logo = snap(q("#site_logo"));
  out.site_logo_img = snap(q("#site_logo img"));
  out.header_menu_contact_a = snap(q(".contact_menu a"));
  out.menu_banner_panel = snap(q("#templatemo_menu_banner_panel"));
  out.menu_wrapper = snap(q("#templatemo_menu_wrapper"));
  out.menu = snap(q("#templatemo_menu"));
  out.menu_li = snap(q("#templatemo_menu ul li"));
  out.menu_link = snap(q("#templatemo_menu ul li a"));
  out.menu_link_current = snap(q("#templatemo_menu ul li a.current"));
  out.banner = snap(q("#templatemo_banner"));
  out.content_wrapper = snap(q("#templatemo_content_wrapper"));
  out.content = snap(q("#templatemo_content"));
  out.side_column = snap(q("#templatemo_side_column"));
  out.main_column = snap(q("#templatemo_main_content_column"));
  out.header_01 = snap(q(".header_01"));
  out.em_text = snap(q(".em_text"));
  out.p = snap(q("#templatemo_main_content_column p") || q("p"));
  out.link = snap(q("#templatemo_main_content_column a") || q("a"));
  out.footer = snap(q("#templatemo_footer"));
  out.button_01_a = snap(q(".button_01 a"));
  out.thumb_img = snap(q(".section_w280_content img"));
  out.section_w280 = snap(q(".section_w280"));
  out.news_date = snap(q(".news_date"));
  out.news_title = snap(q(".news_title"));
  out.textarea = snap(q("textarea"));
  out.input_text = snap(q('input[type="text"]'));
  out.input_submit = snap(q('input[type="submit"]'));
  // structure sketch
  function sketch(el, depth){
    if(depth > 6 || !el) return null;
    const kids = Array.from(el.children).map(c => sketch(c, depth+1)).filter(Boolean);
    let name = el.tagName.toLowerCase();
    if(el.id) name += "#" + el.id;
    if(el.className && typeof el.className === "string" && el.className.trim())
      name += "." + el.className.trim().split(/\s+/).join(".");
    const node = {el: name};
    if(kids.length) node.children = kids;
    return node;
  }
  out.structure = sketch(q("#templateo_container") || document.body, 0);
  return out;
}
"""

HOVER_JS = r"""
async () => {}
"""

tokens = {}
with sync_playwright() as pw:
    browser = pw.chromium.launch()
    for name in PAGES:
        url = BASE.format(name)
        tokens[name] = {}
        for vw, vh, tag in [(1280, 900, "1280"), (375, 800, "375")]:
            page = browser.new_page(viewport={"width": vw, "height": vh})
            page.goto(url, wait_until="networkidle")
            page.screenshot(path=f".tools/ref/shots/{name}-{tag}.png", full_page=True)
            data = page.evaluate(EXTRACT_JS)
            # hover state of first menu link (non-current)
            hover = None
            try:
                link = page.locator("#templatemo_menu ul li a:not(.current)").first
                link.hover()
                page.wait_for_timeout(150)
                hover = page.evaluate("""() => {
                  const a = document.querySelector('#templatemo_menu ul li a:not(.current)');
                  const li = a.closest('li');
                  const cs = getComputedStyle(a), ls = getComputedStyle(li);
                  return {a_color: cs.color, a_bg: ls.backgroundColor};
                }""")
            except Exception as e:
                hover = {"error": str(e)}
            data["menu_link_hover"] = hover
            tokens[name][tag] = data
            page.close()
    browser.close()

with open(".tools/ref/tokens.json", "w") as f:
    json.dump(tokens, f, indent=1)
print("done")
