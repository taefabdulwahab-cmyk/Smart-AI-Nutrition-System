
import streamlit as st

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Smart AI Nutrition",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

defaults = {
    "page": "Overview",
    "diabetes": False,
    "hypertension": False,
    "allergies": [],
    "carb_limit": 45,
    "sodium_limit": 600,
    "ingredients": [],
    "recipe_method": "Prompt-only",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --------------------------------------------------
# CUSTOM DESIGN
# --------------------------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #F7F9F6;
    color: #294D3A;
}

.block-container {
    max-width: 1180px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

[data-testid="stHeader"] {
    background: transparent;
}

h1, h2, h3 {
    color: #294D3A;
}

p, label {
    color: #596D60;
}

.nav-brand {
    color: #294D3A;
    font-size: 23px;
    font-weight: 750;
    padding-top: 7px;
}

.eyebrow {
    color: #66846D;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
}

.hero-title {
    color: #294D3A;
    font-size: 48px;
    line-height: 1.15;
    font-weight: 750;
    margin-top: 15px;
}

.hero-description {
    color: #647568;
    font-size: 17px;
    line-height: 1.8;
    max-width: 700px;
}

.info-card {
    background: #FFFFFF;
    border: 1px solid #E3EAE2;
    border-radius: 16px;
    padding: 24px;
    min-height: 170px;
}

.info-card h3 {
    font-size: 19px;
    margin-bottom: 10px;
}

.info-card p {
    font-size: 14px;
    line-height: 1.7;
}

.soft-panel {
    background: #EAF1E9;
    border-radius: 16px;
    padding: 25px;
}

.metric-card {
    background: white;
    border: 1px solid #E3EAE2;
    padding: 20px;
    border-radius: 14px;
}

.stButton > button {
    background-color: #557B61;
    color: white;
    border: 1px solid #557B61;
    border-radius: 9px;
    min-height: 42px;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #3F624A;
    color: white;
    border-color: #3F624A;
}

.stTextInput input,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 9px;
}

[data-testid="stFileUploader"] {
    background: white;
    border: 1px dashed #A9BDAA;
    border-radius: 14px;
    padding: 15px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

pages = [
    "Overview",
    "Dietary Profile",
    "Ingredient Scan",
    "Evaluation"
]

nav1, nav2, nav3, nav4, nav5 = st.columns(
    [2.1, 1, 1.35, 1.3, 1.1]
)

with nav1:
    st.markdown(
        '<div class="nav-brand">🌿 Smart AI Nutrition</div>',
        unsafe_allow_html=True
    )

navigation_columns = [nav2, nav3, nav4, nav5]

for column, page_name in zip(navigation_columns, pages):
    if page_name == "Overview":
        continue

    with column:
        if st.button(
            page_name,
            use_container_width=True,
            key=f"nav_{page_name}"
        ):
            st.session_state.page = page_name
            st.rerun()

with nav2:
    if st.button(
        "Overview",
        use_container_width=True,
        key="nav_overview"
    ):
        st.session_state.page = "Overview"
        st.rerun()

st.divider()


# --------------------------------------------------
# OVERVIEW PAGE
# --------------------------------------------------

if st.session_state.page == "Overview":

    st.markdown(
        '<div class="eyebrow">AI NUTRITION RESEARCH PROTOTYPE</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero-title">
            Cook what you have.<br>
            Stay inside your limits.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero-description">
            Smart AI Nutrition helps you discover recipes based on
            your available ingredients, health conditions and
            dietary restrictions. Explore personalized meals
            with nutritional information.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")
    if st.button("Get Started  →", key="overview_start"):
        st.session_state.page = "Dietary Profile"
        st.rerun()

    st.write("")
    st.write("")

    st.markdown("### How it works")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="info-card">
            <h3>🥗 Dietary Profile</h3>
            <p>
            Set your health conditions, allergies and
            nutritional limits.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="info-card">
            <h3>📸 Ingredient Scan</h3>
            <p>
            Upload a photo of your ingredients and
            manage your available food items.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="info-card">
            <h3>📊 Evaluation</h3>
            <p>
            Explore recipe suggestions and review
            their nutritional information.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.markdown("""
    <div class="soft-panel">
        <h3>Personalized nutrition starts here.</h3>
        <p>
        Make better food choices with recipes designed
        around your ingredients and dietary preferences.
        </p>
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# DIETARY PROFILE PAGE
# --------------------------------------------------

elif st.session_state.page == "Dietary Profile":

    st.markdown(
        '<div class="eyebrow">STEP 01 • PERSONALIZATION</div>',
        unsafe_allow_html=True
    )

    st.title("Your Dietary Profile")

    st.write(
        "Tell us about your health conditions and dietary needs."
    )

    st.divider()

    st.subheader("Health Conditions")

    c1, c2 = st.columns(2)

    with c1:
        st.session_state.diabetes = st.checkbox(
            "Diabetes",
            value=st.session_state.diabetes
        )

    with c2:
        st.session_state.hypertension = st.checkbox(
            "High Blood Pressure",
            value=st.session_state.hypertension
        )

    st.write("")
    st.subheader("Food Allergies")

    st.session_state.allergies = st.multiselect(
        "Select your food allergies",
        [
            "Egg",
            "Banana",
        ],
        default=st.session_state.allergies
    )

    st.write("")
    st.subheader("Nutritional Limits")

    c1, c2 = st.columns(2)

    with c1:
        st.session_state.carb_limit = st.number_input(
            "Maximum Carbohydrates (g)",
            min_value=0,
            max_value=500,
            value=int(st.session_state.carb_limit)
        )

    with c2:
        st.session_state.sodium_limit = st.number_input(
            "Maximum Sodium (mg)",
            min_value=0,
            max_value=10000,
            value=int(st.session_state.sodium_limit)
        )

    st.write("")
    st.info(
        "Your profile will be used to personalize recipe suggestions."
    )

    if st.button("Save Profile & Continue →"):
        st.session_state.page = "Ingredient Scan"
        st.rerun()


# --------------------------------------------------
# INGREDIENT SCAN PAGE
# --------------------------------------------------

elif st.session_state.page == "Ingredient Scan":

    st.markdown(
        '<div class="eyebrow">STEP 02 • INGREDIENT RECOGNITION</div>',
        unsafe_allow_html=True
    )

    st.title("Ingredient Scan")

    st.write(
        "Upload a photo of your available ingredients."
    )

    st.divider()

    uploaded_image = st.file_uploader(
        "Upload an ingredient photo",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_image is not None:
        st.image(
            uploaded_image,
            caption="Your uploaded ingredients",
            use_container_width=True
        )

        st.success("Image uploaded successfully.")

        st.caption(
            "Automatic ingredient recognition will be connected "
            "to the team's detection module later."
        )

    st.write("")
    st.subheader("Your Ingredients")

    st.write(
        "You can add or remove ingredients manually for this prototype."
    )

    new_ingredient = st.text_input(
        "Add an ingredient",
        placeholder="e.g. Tomato, Potato, Chicken"
    )

    if st.button("Add Ingredient"):
        item = new_ingredient.strip().title()

        if item and item not in st.session_state.ingredients:
            st.session_state.ingredients.append(item)
            st.rerun()

    if st.session_state.ingredients:

        st.markdown("#### Added ingredients")

        for item in st.session_state.ingredients:
            c1, c2 = st.columns([4, 1])

            with c1:
                st.markdown(f"🥬 **{item}**")

            with c2:
                if st.button(
                    "Remove",
                    key=f"remove_{item}"
                ):
                    st.session_state.ingredients.remove(item)
                    st.rerun()

    else:
        st.info("No ingredients added yet.")

    st.write("")

    if st.button("Continue to Evaluation →"):
        st.session_state.page = "Evaluation"
        st.rerun()


# --------------------------------------------------
# EVALUATION PAGE
# --------------------------------------------------

elif st.session_state.page == "Evaluation":

    st.markdown(
        '<div class="eyebrow">STEP 03 • RECIPE EVALUATION</div>',
        unsafe_allow_html=True
    )

    st.title("Recipe Evaluation")

    st.write(
        "Explore recipe generation methods and nutritional results."
    )

    st.divider()

    st.subheader("Recipe Generation Method")

    method = st.radio(
        "Choose a generation approach",
        ["Prompt-only", "RAG-assisted"],
        horizontal=True,
        index=0 if st.session_state.recipe_method == "Prompt-only" else 1
    )

    st.session_state.recipe_method = method

    st.write("")

    st.subheader("Your Current Profile")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <p>Carbohydrate Limit</p>
                <h2>{st.session_state.carb_limit} g</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <p>Sodium Limit</p>
                <h2>{st.session_state.sodium_limit} mg</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <p>Available Ingredients</p>
                <h2>{len(st.session_state.ingredients)}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")

    st.markdown("### Recipe Suggestions")

    st.info(
        f"Selected method: {method}. "
        "Recipe generation will be connected to the team's "
        "recipe generation module."
    )

    if st.session_state.ingredients:
        st.markdown("**Your ingredients:**")
        st.write(", ".join(st.session_state.ingredients))
    else:
        st.warning(
            "You have not added any ingredients yet. "
            "Go to Ingredient Scan to add them."
        )

    st.write("")

    st.markdown("### Example Recipe Cards")

    r1, r2 = st.columns(2)

    with r1:
        with st.container(border=True):
            st.markdown("#### 🥔 Potato & Tomato Bowl")
            st.write("A simple vegetable-based meal.")
            st.caption("Demo recipe • Sample nutritional values")

            st.write("Carbohydrates: 32 g")
            st.write("Sodium: 280 mg")

            st.success("Example nutritional result")

    with r2:
        with st.container(border=True):
            st.markdown("#### 🍗 Chicken & Rice Bowl")
            st.write("A balanced meal with chicken and rice.")
            st.caption("Demo recipe • Sample nutritional values")

            st.write("Carbohydrates: 40 g")
            st.write("Sodium: 420 mg")

            st.success("Example nutritional result")

    st.caption(
        "These are illustrative demo cards, not generated or "
        "validated recipes. Values are placeholders."
    )

    st.divider()

    st.markdown("### Dietary Profile Summary")

    st.write(
        "**Diabetes:**",
        "Yes" if st.session_state.diabetes else "No"
    )

    st.write(
        "**High Blood Pressure:**",
        "Yes" if st.session_state.hypertension else "No"
    )

    st.write(
        "**Allergies:**",
        ", ".join(st.session_state.allergies)
        if st.session_state.allergies else "None selected"
    )

    if st.button("Back to Overview"):
        st.session_state.page = "Overview"
        st.rerun()


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.write("")
st.divider()

st.markdown(
    """
    <p style="text-align:center; color:#819184; font-size:12px;">
        Smart AI Nutrition • Research Prototype
    </p>
    """,
    unsafe_allow_html=True
)
