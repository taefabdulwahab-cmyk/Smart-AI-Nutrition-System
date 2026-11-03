import base64
import copy
import hashlib
import os

import streamlit as st
from PIL import Image

from ingredient_detector import detect_ingredients

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Smart AI Nutrition",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PAGES = ["Overview", "Dietary profile", "Ingredient scan", "Evaluation"]
HERO_IMAGE_PATH = "images/sss.jpeg"  # put your food photo here (images/hero.jpg next to this file)


# ==================================================
# SESSION STATE
# ==================================================

defaults = {
    "page": "Overview",
    "diabetes": False,
    "hypertension": False,
    "allergies": [],
    "carb_limit": 45,      # fixed value (no longer editable in the UI)
    "sodium_limit": 600,   # fixed value (no longer editable in the UI)
    "ingredients": [],
    "manual_ingredients": [],
    "detected_confidence": {},
    "last_image_hash": None,
    "annotated_image": None,
    "recipe_results": {"Prompt-only": [], "RAG-assisted": []},
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = copy.deepcopy(value)


# ==================================================
# HELPERS
# ==================================================

def html(block: str):
    """Render an HTML block (strips indentation so Markdown doesn't treat it as code)."""
    cleaned = "\n".join(line.strip() for line in block.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


def go(page: str):
    st.session_state.page = page


def run_generation():
    """
    Hook for the team's modules.
    Fill st.session_state.recipe_results with:
      {"Prompt-only": [recipe, ...], "RAG-assisted": [recipe, ...]}
    where each recipe is a dict with: name, description, servings, time_min,
    ingredients (list of {"name","amount"} or strings), steps (list[str]),
    nutrition {carbohydrates_g, sodium_mg}, allergen_warnings, status,
    rejection_reasons, guidelines (list[str]).
    """
    pass


def reset_all():
    for k, v in defaults.items():
        st.session_state[k] = copy.deepcopy(v)
    st.session_state.page = "Overview"


def toggle(key):
    st.session_state[key] = not st.session_state[key]


def toggle_allergy(name):
    if name in st.session_state.allergies:
        st.session_state.allergies.remove(name)
    else:
        st.session_state.allergies.append(name)


def hero_image_html():
    if os.path.exists(HERO_IMAGE_PATH):
        with open(HERO_IMAGE_PATH, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f'<img src="data:image/jpeg;base64,{b64}" class="hero-img"/>'
    return '<div class="hero-img hero-img-fallback">🥗</div>'


# ==================================================
# STYLE
# ==================================================

STATIC_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;1,9..144,400&family=Inter:wght@400;500;600&display=swap');

:root{
  --bg:#FAF9F6; --ink:#1F3A2E; --ink-soft:#5E6B63; --line:#E8E5DD;
  --accent:#B5673F; --card:#FFFFFF; --chip:#F3F1EA;
}

.stApp{ background:var(--bg); font-family:'Inter',sans-serif; color:var(--ink); }
[data-testid="stHeader"]{ display:none; }
[data-testid="stToolbar"], #MainMenu, footer{ display:none; }
.block-container{ max-width:1200px; padding-top:0.6rem; padding-bottom:3rem; }

h1,h2,h3,.serif{ font-family:'Fraunces',serif !important; color:var(--ink) !important; font-weight:400 !important; letter-spacing:-0.01em; }
p,label,span{ font-family:'Inter',sans-serif; }

.eyebrow{ font-size:11px; letter-spacing:.18em; text-transform:uppercase; color:var(--ink-soft); margin:0 0 14px 0; }
.muted{ color:var(--ink-soft); font-size:14px; line-height:1.7; }

/* ---------- top nav ---------- */
.brand{ display:flex; align-items:center; gap:12px; padding-top:6px; }
.brand-logo{ width:38px; height:38px; border-radius:50%; background:var(--ink); color:#fff;
  display:flex; align-items:center; justify-content:center; font-size:16px; }
.brand-name{ font-family:'Fraunces',serif; font-size:17px; color:var(--ink); line-height:1.1; }
.brand-sub{ font-size:9px; letter-spacing:.2em; color:var(--ink-soft); text-transform:uppercase; }

[class*="st-key-nav_"] button{ background:transparent !important; border:none !important; border-radius:0 !important;
  box-shadow:none !important; color:var(--ink-soft) !important; font-size:14px; font-weight:400; min-height:40px; padding:0 4px; }
[class*="st-key-nav_"] button:hover{ color:var(--ink) !important; }
.st-key-nav_start button{ background:var(--ink) !important; color:#fff !important; border-radius:999px !important;
  font-weight:500; padding:0 22px; }

/* ---------- buttons ---------- */
.stButton > button{ border-radius:999px; border:1px solid var(--line); background:#fff; color:var(--ink);
  font-weight:500; min-height:44px; padding:0 22px; transition:.15s; }
.stButton > button:hover{ border-color:var(--ink); color:var(--ink); background:#fff; }
.stButton > button[kind="primary"]{ background:var(--ink); color:#fff; border-color:var(--ink); }
.stButton > button[kind="primary"]:hover{ background:#14291F; color:#fff; }
.st-key-link_btn button, [class*="st-key-ghost_"] button{ background:transparent !important; border:none !important;
  color:var(--ink-soft) !important; font-size:13px; padding:0; min-height:30px; }

/* ---------- hero ---------- */
.hero-title{ font-family:'Fraunces',serif; font-size:64px; line-height:1.02; color:var(--ink); margin:6px 0 22px 0; }
.hero-title em{ color:#46604F; font-style:italic; }
.hero-desc{ color:var(--ink-soft); font-size:16px; line-height:1.8; max-width:520px; }
.hero-tags{ margin-top:34px; font-size:11px; letter-spacing:.16em; text-transform:uppercase; color:var(--ink-soft); }
.hero-tags span{ margin-right:22px; }
.hero-wrap{ position:relative; padding-bottom:40px; }
.hero-img{ width:78%; margin-left:auto; display:block; height:460px; object-fit:cover;
  border-radius:200px 200px 24px 24px; }
.hero-img-fallback{ background:linear-gradient(160deg,#DDE7D8,#B9CDB4); display:flex; align-items:center;
  justify-content:center; font-size:120px; }
.val-card{ position:absolute; left:0; bottom:0; width:285px; background:#fff; border-radius:16px;
  padding:16px 18px; box-shadow:0 18px 40px rgba(31,58,46,.12); border:1px solid var(--line); }
.val-card .t{ font-size:10px; letter-spacing:.16em; color:var(--ink-soft); text-transform:uppercase; margin-bottom:10px; }
.val-row{ display:flex; gap:10px; margin-bottom:9px; }
.tick{ width:16px; height:16px; border-radius:50%; background:var(--chip); color:var(--ink); font-size:10px;
  display:flex; align-items:center; justify-content:center; flex-shrink:0; margin-top:2px; }
.val-row b{ font-weight:500; font-size:13px; display:block; color:var(--ink); }
.val-row small{ color:var(--ink-soft); font-size:11px; }
.val-foot{ border-top:1px solid var(--line); padding-top:10px; font-size:10px; letter-spacing:.14em;
  color:var(--accent); text-transform:uppercase; }

/* ---------- how it works ---------- */
.step-col{ border-top:1px solid var(--line); padding-top:18px; }
.step-num{ font-family:'Fraunces',serif; color:var(--accent); font-size:13px; margin-bottom:22px; }
.step-col h4{ font-family:'Fraunces',serif; font-size:17px; font-weight:500; margin:0 0 8px 0; color:var(--ink); }
.step-col p{ color:var(--ink-soft); font-size:13px; line-height:1.7; }
.section-title{ font-family:'Fraunces',serif; font-size:38px; line-height:1.15; color:var(--ink); }

.st-key-cta_box{ background:var(--ink); border-radius:24px; padding:52px 56px; margin-top:40px; position:relative; overflow:hidden; }
.st-key-cta_box::after{ content:""; position:absolute; right:-60px; top:-60px; width:260px; height:260px; border-radius:50%;
  background:radial-gradient(circle,rgba(255,255,255,.12),transparent 70%); pointer-events:none; }
.st-key-cta_box .eyebrow{ color:#A9BCB0; }
.st-key-cta_box h2{ color:#fff !important; font-size:38px; line-height:1.2; margin:0 0 16px 0; }
.st-key-cta_box .cta-text{ color:#C9D6CD; font-size:14px; max-width:560px; line-height:1.7; }
.st-key-cta_begin button{ background:#fff !important; border-color:#fff !important; margin-top:8px; }
.st-key-cta_begin button p{ color:var(--ink) !important; }

.site-footer{ border-top:1px solid var(--line); margin-top:60px; padding-top:30px; display:flex; justify-content:space-between; gap:40px; }
.site-footer .l{ max-width:460px; }
.site-footer .r{ text-align:right; color:var(--ink-soft); font-size:12px; line-height:2; }
.site-footer .r .e{ font-size:10px; letter-spacing:.2em; text-transform:uppercase; }

/* ---------- stepper ---------- */
.stepper{ display:flex; align-items:center; gap:14px; font-size:12px; color:var(--ink-soft); margin:10px 0 34px 0; }
.stepper .dot{ width:22px; height:22px; border-radius:50%; border:1px solid var(--line); display:inline-flex;
  align-items:center; justify-content:center; font-size:11px; margin-right:8px; }
.stepper .on .dot{ background:var(--ink); color:#fff; border-color:var(--ink); }
.stepper .on{ color:var(--ink); font-weight:500; }
.stepper .done .dot{ background:#F4E7DE; border-color:#EBD3C3; color:var(--accent); }
.stepper .bar{ width:36px; height:1px; background:var(--line); }

/* ---------- panels ---------- */
.panel-title{ font-family:'Fraunces',serif; letter-spacing:.14em; font-size:11px; text-transform:uppercase; color:var(--ink-soft); margin-bottom:4px; }
.note-box{ border:1px solid var(--line); border-radius:14px; padding:16px 18px; background:#fff; margin-top:26px; }
.note-box .t{ font-size:10px; letter-spacing:.16em; color:var(--ink-soft); text-transform:uppercase; margin-bottom:6px; }
.note-box p{ font-size:12px; color:var(--ink-soft); line-height:1.6; margin:0; }

[data-testid="stVerticalBlockBorderWrapper"]{ background:#fff; border-radius:22px !important; border-color:var(--line) !important;
  box-shadow:0 10px 30px rgba(31,58,46,.05); }

/* selectable cards */
[class*="st-key-card_"] button{ height:auto; width:100%; border-radius:16px; justify-content:flex-start; text-align:left;
  padding:16px 18px; background:#fff; border:1px solid var(--line); align-items:flex-start; }
[class*="st-key-card_"] button p{ text-align:left; font-size:12px; color:var(--ink-soft); line-height:1.5; margin:0; }
[class*="st-key-card_"] button p strong{ font-size:14px; color:var(--ink); font-weight:500; display:block; margin-bottom:4px; }

/* uploader */
[data-testid="stFileUploader"] section{ background:#F5F3EE; border:1px dashed #CFCBBF; border-radius:18px; padding:48px 16px; }

/* ingredient rows */
.ing-row{ display:flex; gap:18px; padding:12px 0; border-bottom:1px solid var(--line); align-items:center; }
.ing-idx{ font-family:'Fraunces',serif; font-size:11px; color:var(--ink-soft); width:20px; }
.ing-name{ font-size:14px; color:var(--ink); }
.ing-bar{ height:3px; width:80px; background:var(--chip); border-radius:2px; margin-top:6px; display:inline-block; }
.ing-bar i{ display:block; height:3px; background:#C58E6B; border-radius:2px; }
.ing-pct{ font-size:10px; color:var(--ink-soft); margin-left:10px; }
.count-pill{ background:var(--chip); border-radius:50%; width:28px; height:28px; display:inline-flex;
  align-items:center; justify-content:center; font-size:11px; float:right; }

/* recipe cards */
.draft-label{ font-size:11px; letter-spacing:.16em; text-transform:uppercase; color:var(--ink-soft); }
.draft-dot{ display:inline-block; width:6px; height:6px; border-radius:50%; margin-right:8px; background:var(--ink); }
.draft-dot.rag{ background:var(--accent); }
.pill{ float:right; font-size:10px; letter-spacing:.12em; padding:4px 10px; border-radius:999px; text-transform:uppercase; }
.pill.ok{ background:#E7EFE7; color:#2F5B41; } .pill.bad{ background:#F6E3DC; color:#9A4A2A; }
.recipe-name{ font-family:'Fraunces',serif; font-size:26px; line-height:1.15; color:var(--ink); margin:20px 0 8px 0; }
.meta{ font-size:10px; letter-spacing:.14em; color:var(--ink-soft); text-transform:uppercase; margin:12px 0 18px 0; }
.ing-line{ display:flex; justify-content:space-between; padding:7px 0; border-bottom:1px solid var(--line); font-size:13px; }
.ing-line span:last-child{ color:var(--ink-soft); }
.method-step{ display:flex; gap:14px; margin-bottom:12px; font-size:13px; color:var(--ink); line-height:1.6; }
.method-step b{ font-family:'Fraunces',serif; color:var(--accent); font-weight:400; font-size:12px; padding-top:2px; }
.val-panel{ background:#FAF9F6; border:1px solid var(--line); border-radius:14px; padding:16px 18px; margin-top:18px; }
.val-panel .h{ font-size:10px; letter-spacing:.16em; color:var(--ink-soft); text-transform:uppercase; margin-bottom:12px; }
.chk{ display:flex; gap:10px; margin-bottom:12px; }
.chk .tick.bad{ background:#F6E3DC; color:#9A4A2A; }
.chk .row{ flex:1; display:flex; justify-content:space-between; }
.chk b{ font-weight:500; font-size:13px; } .chk small{ display:block; color:var(--ink-soft); font-size:11px; margin-top:2px; }
.chk .v{ font-size:11px; color:var(--ink-soft); }
.tags{ margin-top:14px; } .tags .e{ font-size:10px; letter-spacing:.16em; color:var(--ink-soft); text-transform:uppercase; margin-bottom:8px; }
.tag{ display:inline-block; border:1px solid #E7CDBE; color:var(--accent); background:#FDF6F1; border-radius:999px;
  font-size:11px; padding:4px 11px; margin:0 6px 6px 0; }
.summary-chip{ display:inline-block; border:1px solid var(--line); border-radius:999px; font-size:11px; padding:5px 12px; margin:0 8px 8px 0; background:#fff; color:var(--ink-soft); }
.summary-chip.hl{ background:#F9EBE2; color:var(--accent); border-color:#EBD3C3; }
.disclaimer{ font-size:12px; color:var(--ink-soft); margin-top:26px; max-width:760px; }
</style>
"""

st.markdown(STATIC_CSS, unsafe_allow_html=True)


def dynamic_css():
    """Active states that depend on session state."""
    rules = []
    active = st.session_state.page
    rules.append(
        f".st-key-nav_{active.replace(' ', '_')} button"
        "{ color:#1F3A2E !important; border-bottom:2px solid #B5673F !important; }"
    )
    selected_cards = []
    if st.session_state.diabetes:
        selected_cards.append("diabetes")
    if st.session_state.hypertension:
        selected_cards.append("hypertension")
    for a in st.session_state.allergies:
        selected_cards.append(f"allergy_{a.lower()}")
    for c in selected_cards:
        rules.append(
            f".st-key-card_{c} button"
            "{ background:#F1F2EC !important; border-color:#1F3A2E !important;"
            " box-shadow:0 8px 20px rgba(31,58,46,.08); }"
        )
    st.markdown("<style>" + "\n".join(rules) + "</style>", unsafe_allow_html=True)


# ==================================================
# TOP NAVIGATION
# ==================================================

cols = st.columns([2.6, 0.9, 1.3, 1.3, 1.0, 0.9], vertical_alignment="center")

with cols[0]:
    html("""
    <div class="brand">
      <div class="brand-logo">🌱</div>
      <div>
        <div class="brand-name">Smart AI Nutrition</div>
        <div class="brand-sub">Research prototype</div>
      </div>
    </div>
    """)

for col, name in zip(cols[1:5], PAGES):
    with col:
        st.button(name, key=f"nav_{name.replace(' ', '_')}", use_container_width=True,
                  on_click=go, args=(name,))

with cols[5]:
    st.button("Start", key="nav_start", use_container_width=True, on_click=go, args=("Dietary profile",))

dynamic_css()
st.markdown("<hr style='border:none;border-top:1px solid #E8E5DD;margin:8px 0 28px 0'>", unsafe_allow_html=True)


def stepper(active: int):
    labels = ["Dietary profile", "Ingredient scan", "Generate & review"]
    parts = []
    for i, label in enumerate(labels, start=1):
        cls = "on" if i == active else ("done" if i < active else "")
        dot = "✓" if i < active else str(i)
        parts.append(f'<span class="{cls}"><span class="dot">{dot}</span>{label}</span>')
        if i < len(labels):
            parts.append('<span class="bar"></span>')
    html(f'<div class="stepper">{"".join(parts)}</div>')


# ==================================================
# OVERVIEW
# ==================================================

if st.session_state.page == "Overview":

    left, right = st.columns([1.15, 1], gap="large")

    with left:
        html("""
        <div class="hero-title">Cook what<br>you have.<br><em>Stay inside<br>your limits.</em></div>
        <div class="hero-desc">
        Smart AI Nutrition reads a photo of your ingredients, drafts a recipe around your health
        conditions and allergies, then checks the carbohydrate, sodium and allergen numbers
        before you turn on the stove.
        </div>
        """)
        st.write("")
        b1, b2, _ = st.columns([1, 1, 0.8])
        with b1:
            st.button("Get started  →", type="primary", use_container_width=True,
                      key="hero_start", on_click=go, args=("Dietary profile",))
        with b2:
            st.button("See the evaluation", use_container_width=True,
                      key="hero_eval", on_click=go, args=("Evaluation",))
        html("""
        <div class="hero-tags">
          <span>Ingredient vision</span><span>Guideline retrieval</span><span>Rule-based validation</span>
        </div>
        """)

    with right:
        html(f"""
        <div class="hero-wrap">
          {hero_image_html()}
          <div class="val-card">
            <div class="t">Validation · per serving</div>
            <div class="val-row"><div class="tick">✓</div><div><b>Allergens clear</b><small>no egg, no banana</small></div></div>
            <div class="val-row"><div class="tick">✓</div><div><b>Carbohydrate</b><small>38 g · limit 45 g</small></div></div>
            <div class="val-row"><div class="tick">✓</div><div><b>Sodium</b><small>540 mg · limit 600 mg</small></div></div>
            <div class="val-foot">3 of 3 constraints met</div>
          </div>
        </div>
        """)

    st.write("")
    h1, h2 = st.columns([1.4, 1], vertical_alignment="bottom")
    with h1:
        html("""
        <div class="eyebrow">How it works</div>
        <div class="section-title">Four steps from a fridge<br>photo to a checked recipe.</div>
        """)
    with h2:
        html('<p class="muted" style="text-align:right">Nothing is assumed about your ingredients, and nothing is taken on trust from the model.</p>')

    st.write("")
    steps = [
        ("01", "Dietary profile", "Declare diabetes or high blood pressure, and any egg or banana allergy."),
        ("02", "Ingredient scan", "Photograph what you have. Each ingredient is listed with a confidence score, and you can remove anything that was detected wrongly."),
        ("03", "Generate & validate", "The model drafts the recipe twice — with and without retrieved guidelines — and the validator recomputes every number."),
        ("04", "Review", "Compare both drafts side by side, see which constraints held, and keep the one that fits your day."),
    ]
    for col, (n, t, d) in zip(st.columns(4, gap="large"), steps):
        with col:
            html(f'<div class="step-col"><div class="step-num">{n}</div><h4>{t}</h4><p>{d}</p></div>')

    st.write("")
    with st.container(key="cta_box"):
        html("""
        <div class="eyebrow">Start with your profile</div>
        <h2>A recipe is only useful if<br>it fits the person eating it.</h2>
        <p class="cta-text">Set your restrictions once, then scan whatever is in the kitchen. Both drafts and their
        validation arrive together, so you can see the difference retrieval makes.</p>
        """)
        st.button("Begin the profile  →", key="cta_begin", on_click=go, args=("Dietary profile",))


# ==================================================
# DIETARY PROFILE
# ==================================================

elif st.session_state.page == "Dietary profile":

    stepper(1)
    left, right = st.columns([0.9, 1.25], gap="large")

    with left:
        html("""
        <div class="eyebrow">Step 1 · Dietary profile</div>
        <div class="section-title" style="font-size:46px">Tell us about<br>your health needs.</div>
        <p class="muted" style="margin-top:18px">These inputs drive both the recipe and the validator.
        The model is told what to avoid; the validator independently checks whether it did.</p>
        <div class="note-box">
          <div class="t">🔒 Kept in this browser</div>
          <p>Your profile lives only in the current session — it travels with the generation request that needs it.</p>
        </div>
        """)
        st.button("← Back to overview", key="ghost_back", on_click=go, args=("Overview",))

    with right:
        with st.container(border=True):
            html('<div class="panel-title">Health conditions</div><p class="muted" style="font-size:13px">Select all that apply.</p>')
            c1, c2 = st.columns(2)
            with c1:
                st.button("**Diabetes**  \nKeep glycaemic load low and carbohydrate portions controlled.",
                          key="card_diabetes", on_click=toggle, args=("diabetes",), use_container_width=True)
            with c2:
                st.button("**High blood pressure**  \nKeep sodium low and favour potassium-rich whole foods.",
                          key="card_hypertension", on_click=toggle, args=("hypertension",), use_container_width=True)

            st.divider()
            html('<div class="panel-title">Food allergies</div><p class="muted" style="font-size:13px">Any selected allergen found in the recipe raises a warning.</p>')
            a1, a2 = st.columns(2)
            with a1:
                st.button("**Egg allergy**  \nNo whole eggs, mayonnaise, meringue or egg-based binders.",
                          key="card_allergy_egg", on_click=toggle_allergy, args=("Egg",), use_container_width=True)
            with a2:
                st.button("**Banana allergy**  \nNo banana or plantain, including in smoothies and bakes.",
                          key="card_allergy_banana", on_click=toggle_allergy, args=("Banana",), use_container_width=True)

            st.divider()
            n_sel = int(st.session_state.diabetes) + int(st.session_state.hypertension) + len(st.session_state.allergies)
            f1, f2 = st.columns([2, 1], vertical_alignment="center")
            with f1:
                st.caption(f"{n_sel} restriction(s) selected.")
            with f2:
                st.button("Continue  →", type="primary", use_container_width=True,
                          key="profile_continue", on_click=go, args=("Ingredient scan",))


# ==================================================
# INGREDIENT SCAN
# ==================================================

elif st.session_state.page == "Ingredient scan":

    stepper(2)
    html("""
    <div class="eyebrow">Step 2 · Ingredient recognition</div>
    <div class="section-title" style="font-size:46px">What's in your kitchen?</div>
    <p class="muted" style="margin:14px 0 28px 0">Upload a photo and remove anything the detector got wrong.</p>
    """)

    image_col, ing_col = st.columns([1.05, 1], gap="large")

    # ---------- LEFT: upload ----------
    with image_col:
        with st.container(border=True):
            uploaded_image = st.file_uploader(
                "Drop a photo of your ingredients",
                type=["png", "jpg", "jpeg"],
                key="ingredient_image",
            )

            if uploaded_image is not None:
                image_hash = hashlib.md5(uploaded_image.getvalue()).hexdigest()

                if image_hash != st.session_state.last_image_hash:
                    for item in list(st.session_state.detected_confidence.keys()):
                        if item not in st.session_state.manual_ingredients and item in st.session_state.ingredients:
                            st.session_state.ingredients.remove(item)

                    st.session_state.detected_confidence = {}
                    st.session_state.annotated_image = None
                    st.session_state.last_image_hash = image_hash

                    try:
                        image = Image.open(uploaded_image).convert("RGB")
                        detections, annotated = detect_ingredients(image)
                        st.session_state.annotated_image = annotated[:, :, ::-1]

                        for det in detections:
                            name = det["name"].title()
                            conf = float(det["confidence"])
                            if conf > st.session_state.detected_confidence.get(name, 0):
                                st.session_state.detected_confidence[name] = conf
                            if name not in st.session_state.ingredients:
                                st.session_state.ingredients.append(name)
                    except Exception as e:
                        st.session_state.last_image_hash = None
                        st.error(f"Ingredient detection failed: {e}")

                if st.session_state.annotated_image is not None:
                    st.image(st.session_state.annotated_image, caption="AI ingredient recognition",
                             use_container_width=True)

            st.caption("A top-down photo on a plain surface gives the most reliable detection.")

    # ---------- RIGHT: list (remove only) ----------
    with ing_col:
        with st.container(border=True):
            html(f"""
            <span class="count-pill">{len(st.session_state.ingredients)}</span>
            <div class="panel-title">Detected ingredients</div>
            <p class="muted" style="font-size:13px">Remove anything the detector got wrong.</p>
            """)

            if not st.session_state.ingredients:
                st.info("No ingredients yet. Upload an image to detect them.")

            for idx, item in enumerate(list(st.session_state.ingredients), start=1):
                conf = st.session_state.detected_confidence.get(item)
                r1, r2 = st.columns([10, 1], vertical_alignment="center")
                with r1:
                    if conf is not None:
                        pct = int(round(conf * 100))
                        bar = f'<span class="ing-bar"><i style="width:{pct}%"></i></span><span class="ing-pct">{pct}%</span>'
                    else:
                        bar = ""
                    html(f"""
                    <div class="ing-row" style="border:none;padding:8px 0">
                      <div class="ing-idx">{idx:02d}</div>
                      <div><div class="ing-name">{item}</div>{bar}</div>
                    </div>
                    """)
                with r2:
                    if st.button("✕", key=f"ghost_rm_{item}"):
                        if item in st.session_state.ingredients:
                            st.session_state.ingredients.remove(item)
                        st.session_state.detected_confidence.pop(item, None)
                        st.rerun()

    st.write("")
    f1, f2 = st.columns([3, 1.1], vertical_alignment="center")
    with f1:
        st.button("← Edit dietary profile", key="ghost_edit_profile", on_click=go, args=("Dietary profile",))
    with f2:
        st.button("Generate recipe  →", type="primary", use_container_width=True, key="generate",
                  disabled=not st.session_state.ingredients,
                  on_click=lambda: (run_generation(), go("Evaluation")))


# ==================================================
# EVALUATION  (Generate & review)
# ==================================================

elif st.session_state.page == "Evaluation":

    stepper(3)
    s = st.session_state
    html("""
    <div class="eyebrow">Step 3 · Recipe generation & validation</div>
    <div class="section-title" style="font-size:46px">Two drafts, measured<br>against one ruler.</div>
    <p class="muted" style="margin:16px 0 18px 0;max-width:680px">Both recipes were generated from the same
    ingredients and the same restrictions. The validator then recalculated allergens, carbohydrate and
    sodium independently of the model.</p>
    """)

    chips = [f'<span class="summary-chip">{len(s.ingredients)} ingredients</span>']
    if s.diabetes:
        chips.append('<span class="summary-chip">Diabetes</span>')
    if s.hypertension:
        chips.append('<span class="summary-chip">High blood pressure</span>')
    for a in s.allergies:
        chips.append(f'<span class="summary-chip hl">{a} allergy</span>')
    chips.append(f'<span class="summary-chip">≤ {s.carb_limit} g carbs</span>')
    chips.append(f'<span class="summary-chip">≤ {s.sodium_limit} mg sodium</span>')
    html("".join(chips))
    st.write("")

    def render_column(method, blurb, dot_cls):
        recipes = s.recipe_results.get(method, [])
        with st.container(border=True):
            html(f"""
            <div class="draft-label"><span class="draft-dot {dot_cls}"></span>{blurb[0]}</div>
            <p class="muted" style="font-size:13px;margin-top:6px">{blurb[1]}</p>
            """)
            if not recipes:
                st.info("No result yet. Recipe generation will appear here once connected to the team's modules.")
                return

            for recipe in recipes:
                accepted = str(recipe.get("status", "")).lower() == "accepted"
                pill = '<span class="pill ok">✓ Passed</span>' if accepted else '<span class="pill bad">✕ Rejected</span>'

                ing = recipe.get("ingredients", [])
                ing_rows = ""
                for x in (ing if isinstance(ing, list) else [ing]):
                    if isinstance(x, dict):
                        ing_rows += f'<div class="ing-line"><span>{x.get("name","")}</span><span>{x.get("amount","")}</span></div>'
                    else:
                        ing_rows += f'<div class="ing-line"><span>{x}</span><span></span></div>'

                steps = recipe.get("steps") or recipe.get("method") or []
                step_rows = "".join(
                    f'<div class="method-step"><b>{i:02d}</b><div>{t}</div></div>' for i, t in enumerate(steps, start=1)
                )

                meta_bits = []
                if recipe.get("servings"):
                    meta_bits.append(f'{recipe["servings"]} servings')
                if recipe.get("time_min"):
                    meta_bits.append(f'{recipe["time_min"]} min')
                if isinstance(ing, list):
                    meta_bits.append(f"{len(ing)} ingredients")
                meta = " · ".join(meta_bits)

                nut = recipe.get("nutrition", {}) or {}
                carbs, sodium = nut.get("carbohydrates_g"), nut.get("sodium_mg")
                warnings = recipe.get("allergen_warnings", []) or []

                def row(ok, title, sub, val=""):
                    cls = "" if ok else "bad"
                    mark = "✓" if ok else "✕"
                    return (f'<div class="chk"><div class="tick {cls}">{mark}</div><div class="row"><div>'
                            f'<b>{title}</b><small>{sub}</small></div><span class="v">{val}</span></div></div>')

                checks = row(
                    not warnings, "Allergen check",
                    "No selected allergen found in the ingredients or method." if not warnings else ", ".join(warnings),
                    "Clear" if not warnings else "Found",
                )
                if carbs is not None:
                    checks += row(carbs <= s.carb_limit, "Carbohydrate limit",
                                  f"{carbs} g per serving against your {s.carb_limit} g limit.",
                                  f"{carbs} / {s.carb_limit} g")
                if sodium is not None:
                    checks += row(sodium <= s.sodium_limit, "Sodium limit",
                                  f"{sodium} mg per serving against your {s.sodium_limit} mg limit.",
                                  f"{sodium} / {s.sodium_limit} mg")

                reasons = recipe.get("rejection_reasons", []) or []
                reasons_html = "".join(f'<div class="muted" style="font-size:12px">• {r}</div>' for r in reasons)

                guidelines = recipe.get("guidelines", []) or []
                tags = ""
                if guidelines:
                    tags = (f'<div class="tags"><div class="e">Guidelines retrieved · {len(guidelines)}</div>'
                            + "".join(f'<span class="tag">{g}</span>' for g in guidelines) + "</div>")

                html(f"""
                <div style="margin-top:10px">{pill}</div>
                <div class="recipe-name">{recipe.get("name", "Recipe")}</div>
                <p class="muted" style="font-size:13px">{recipe.get("description", "")}</p>
                <div class="meta">{meta}</div>
                """)
                i_col, m_col = st.columns([1, 1.3])
                with i_col:
                    html(f'<div class="draft-label" style="margin-bottom:8px">Ingredients</div>{ing_rows}')
                with m_col:
                    html(f'<div class="draft-label" style="margin-bottom:8px">Method</div>{step_rows}')
                html(f"""
                <div class="val-panel">
                  <div class="h">Rule-based validation
                    <span class="pill {'ok' if accepted else 'bad'}" style="letter-spacing:.08em">
                    {'All checks passed' if accepted else 'Checks failed'}</span></div>
                  {checks}
                  {reasons_html}
                </div>
                {tags}
                """)

    left, right = st.columns(2, gap="large")
    with left:
        render_column("Prompt-only", ("Prompt-only", "Ingredients and restrictions go straight into the prompt, with no external guidance."), "")
    with right:
        render_column("RAG-assisted", ("Guidelines (RAG)", "Relevant dietary guidelines are retrieved first, then given to the model with your inputs."), "rag")

    # ---------- researcher comparison ----------
    all_pairs = [(m, r) for m, rs in s.recipe_results.items() for r in rs]
    if all_pairs:
        with st.expander("Researcher view · generation comparison"):
            def count(method, status):
                return sum(str(r.get("status", "")).lower() == status for r in s.recipe_results.get(method, []))
            st.table({
                "Metric": ["Total generated", "Accepted", "Rejected"],
                "Prompt-only": [len(s.recipe_results.get("Prompt-only", [])), count("Prompt-only", "accepted"), count("Prompt-only", "rejected")],
                "RAG-assisted": [len(s.recipe_results.get("RAG-assisted", [])), count("RAG-assisted", "accepted"), count("RAG-assisted", "rejected")],
            })

    st.divider()
    b1, b2, b3 = st.columns([1.1, 1.1, 3], vertical_alignment="center")
    with b1:
        st.button("⟳  Regenerate both", key="regen", on_click=run_generation, use_container_width=True)
    with b2:
        st.button("✎  Edit ingredients", key="edit_ing", on_click=go, args=("Ingredient scan",), use_container_width=True)
    with b3:
        st.button("Start over", key="ghost_startover", on_click=reset_all)

    html('<div class="disclaimer">Nutritional estimates are derived from USDA FoodData Central reference values for matched ingredients and are indicative only. This prototype is not medical or dietary advice.</div>')


# ==================================================
# FOOTER
# ==================================================

html("""
<div class="site-footer">
  <div class="l">
    <div class="serif" style="font-size:17px;margin-bottom:10px">Smart AI Nutrition System</div>
    <p class="muted" style="font-size:12px">An educational research prototype that evaluates AI-based recipe generation
    against rule-based dietary constraint checking. It is not intended to replace professional medical or nutritional advice.</p>
  </div>
  <div class="r">
    <div class="e">Pipeline</div>
    Vision recognition · LLM generation<br>
    Guideline retrieval · Rule-based validation<br>
    USDA FoodData Central reference values
  </div>
</div>
""")