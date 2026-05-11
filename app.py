import streamlit as st
from trip_weaver.graph.nodes.query_parser import query_parser
from trip_weaver.graph.nodes.researcher import researcher
from trip_weaver.graph.nodes.planner import planner
from trip_weaver.graph.state import TripweverState

st.set_page_config(
    page_title="TripWeaver",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    #MainMenu, footer { visibility: hidden; }

    .hero {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 16px;
        padding: 2.5rem 2rem 2rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    .hero h1 { color: #ffffff; font-size: 2.8rem; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
    .hero p  { color: #a0aec0; font-size: 1.1rem; margin: 0.5rem 0 0; }
    .hero-icon { font-size: 3rem; margin-bottom: 0.5rem; }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #e94560, #0f3460);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        width: 100%;
        transition: opacity 0.2s;
    }
    div.stButton > button[kind="primary"]:hover { opacity: 0.88; }

    [data-testid="metric-container"] {
        background: #1e1e2e;
        border: 1px solid #2d2d44;
        border-radius: 10px;
        padding: 0.8rem 1rem;
    }

    .itinerary-body { font-size: 0.97rem; line-height: 1.75; }

    .sidebar-brand { font-size: 1.4rem; font-weight: 800; color: #e94560; letter-spacing: -0.3px; }
    .step-num {
        background: #e94560; color: white; border-radius: 50%;
        width: 20px; height: 20px;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 0.75rem; font-weight: 700; flex-shrink: 0;
    }
    .sidebar-step { display: flex; align-items: flex-start; gap: 0.6rem; margin-bottom: 0.5rem; font-size: 0.9rem; color: #cbd5e0; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">✈️ TripWeaver</div>', unsafe_allow_html=True)
    st.caption("AI-powered travel itinerary planner")
    st.divider()

    st.markdown("**How it works**")
    for i, step in enumerate([
        "Describe your trip in plain English",
        "AI parses your destination, days & preferences",
        "Researcher gathers real facts about the place",
        "Planner builds your day-by-day itinerary",
    ], 1):
        st.markdown(
            f'<div class="sidebar-step"><span class="step-num">{i}</span>{step}</div>',
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown("**Example queries**")
    for ex in [
        "5 days in Kyoto, Japan — temples & street food, $120/day",
        "3 days in Paris, France — art & cafes, relaxed pace",
        "7 days in Bali, Indonesia — beaches & culture, budget $80/day",
    ]:
        st.caption(f"• {ex}")

    st.divider()
    st.caption("Model")
    st.code("gpt-4o-mini", language=None)

# ── Hero ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-icon">🗺️</div>
  <h1>Plan Your Perfect Trip</h1>
  <p>Tell the AI where you want to go — get a complete itinerary in seconds.</p>
</div>
""", unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────
query = st.text_area(
    "query",
    placeholder=(
        "e.g. 5 days in Kyoto, Japan — I love temples, street food and hidden gardens. "
        "Budget around $120/day, moderate pace, traveling solo."
    ),
    height=110,
    label_visibility="collapsed",
)

col_btn, col_clear = st.columns([4, 1])
with col_btn:
    plan_clicked = st.button("🗺️  Plan My Trip", type="primary", use_container_width=True)
with col_clear:
    if st.button("Clear", use_container_width=True):
        st.session_state.pop("result", None)
        st.rerun()

# ── Run pipeline ───────────────────────────────────────────────────────────
if plan_clicked:
    if not query.strip():
        st.warning("Please describe your trip first.")
    else:
        with st.status("Working on your itinerary...", expanded=True) as status:
            state: TripweverState = {"query": query, "parsed_params": {}, "research": {}, "plan": ""}

            st.write("Parsing your travel request...")
            state.update(query_parser(state))

            st.write("Researching your destination...")
            state.update(researcher(state))

            st.write("Building your day-by-day itinerary...")
            state.update(planner(state))

            status.update(label="Itinerary ready!", state="complete", expanded=False)

        st.session_state["result"] = state

# ── Results ────────────────────────────────────────────────────────────────
if "result" in st.session_state:
    state = st.session_state["result"]
    parsed = state.get("parsed_params", {})
    plan = state.get("plan", "")
    clarifications = parsed.get("clarification_needed", [])

    if clarifications:
        lines = "\n".join(
            f"- **{c['field']}**: {c['reason']}"
            + (f" (e.g. {', '.join(c['example_values'])})" if c.get("example_values") else "")
            for c in clarifications
        )
        st.warning("Some details were assumed — refine your query for better results:\n\n" + lines)

    tab_itin, tab_details = st.tabs(["📋 Itinerary", "📊 Trip Details"])

    with tab_itin:
        st.markdown('<div class="itinerary-body">', unsafe_allow_html=True)
        st.markdown(plan)
        st.markdown("</div>", unsafe_allow_html=True)
        st.download_button(
            label="Download Itinerary (.md)",
            data=plan,
            file_name=f"tripweaver_{parsed.get('destination', 'trip').lower().replace(' ', '_')}.md",
            mime="text/markdown",
        )

    with tab_details:
        st.markdown("#### Trip Parameters")
        cols = st.columns(5)
        for col, label, key, fmt in zip(
            cols,
            ["Destination", "Days", "Budget/day", "Pace", "Travelers"],
            ["destination", "days", "budget_per_day_usd", "pace", "travelers"],
            ["{}", "{}", "${}", "{}", "{}"],
        ):
            val = parsed.get(key, "—")
            if key == "pace" and val != "—":
                val = val.capitalize()
            col.metric(label, fmt.format(val))

        interests = parsed.get("interests", [])
        if interests:
            st.markdown("**Interests:** " + " · ".join(interests))

        if clarifications:
            st.markdown("#### Clarifications Needed")
            for c in clarifications:
                with st.expander(f"`{c['field']}` — {c['reason']}"):
                    if c.get("example_values"):
                        st.caption("Try: " + ", ".join(c["example_values"]))

        research = state.get("research", {})
        meta = research.get("meta", {})
        if meta:
            st.markdown("#### Destination Info")
            m1, m2, m3 = st.columns(3)
            m1.metric("Currency", meta.get("currency", "—"))
            m2.metric("Language", meta.get("language", "—"))
            m3.metric("Timezone", meta.get("timezone", "—"))
            if meta.get("best_season_note"):
                st.info(meta["best_season_note"])
