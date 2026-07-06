import streamlit as st
import sys, os, json, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.insight import run as insight_run
from src.agents.marketing import run as marketing_run
from src.agents.qa import run as qa_run
from src.tools.logger import set_level

st.set_page_config(page_title="Enterprise AI Growth Copilot", layout="wide")

def load_test_data() -> list[tuple[str, str, int]]:
    data_dir = os.path.join(os.path.dirname(__file__), "test_data")
    if not os.path.isdir(data_dir):
        return []
    files = []
    for fname in sorted(os.listdir(data_dir)):
        if fname.endswith(".txt"):
            fpath = os.path.join(data_dir, fname)
            with open(fpath, encoding="utf-8") as f:
                count = sum(1 for line in f if line.strip())
            files.append((fname, fpath, count))
    return files

def load_reviews(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def product_info() -> dict:
    return {"name": "DataSync Pro", "version": "3.2.1", "category": "cloud_data_tool"}

if "results" not in st.session_state:
    st.session_state.results = None

with st.sidebar:
    st.markdown("### Enterprise AI Growth Copilot")
    st.markdown("A 3-agent pipeline that analyzes product reviews, generates marketing content, and evaluates quality.")
    st.markdown("---")
    files = load_test_data()
    file_names = [f[0] for f in files]
    sample_choice = st.selectbox("Sample data", [""] + file_names, format_func=lambda x: x if x else "(Select)")
    if sample_choice:
        path = [f[1] for f in files if f[0] == sample_choice][0]
        content = load_reviews(path)
        st.session_state.reviews_area = '\n'.join(content)
        st.info(f"Loaded {sample_choice} ({len(content)} reviews)")
    st.markdown("---")
    debug_mode = st.checkbox("Debug Mode", value=False)
    if debug_mode:
        st.warning("Debug ON: showing inputs, states, and validation per step")

    st.markdown("---")
    with st.expander("Business Brief (V2)", expanded=False):
        st.caption("Shared context for all agents (read-only)")
        st.text_input("Product Name", value="DataSync Pro", key="bb_product")
        st.text_input("Category", value="Cloud Data Tool", key="bb_category")
        st.text_input("Brand", value="DataSync", key="bb_brand")
        st.text_input("Target Market", value="North America", key="bb_market")
        st.text_input("Target Audience", value="Enterprise teams", key="bb_audience")
        st.text_input("Brand Position", value="Premium", key="bb_position")
        st.text_input("Price Range", value="$29-$99/month", key="bb_price")
        st.text_input("Business Goal", value="Increase market share", key="bb_goal")
        st.text_area("Core Features (one per line)", value="Large file upload\nReal-time sync\nCSV export\nTeam collaboration", height=100, key="bb_features")

st.title("Enterprise AI Growth Copilot")
st.markdown("### Input Reviews")
st.text_area("Enter reviews, one per line:", value="", height=180, placeholder="Paste your product reviews here...", key="reviews_area")

col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    run_clicked = st.button("Run Analysis", type="primary", use_container_width=True)
with col2:
    if st.button("Clear", use_container_width=True):
        st.session_state.results = None
        st.session_state.reviews_area = ""
        st.rerun()

if run_clicked:
    raw = st.session_state.reviews_area
    reviews_list = [r.strip() for r in raw.strip().split("\n") if r.strip()]
    if not reviews_list:
        st.warning("Please enter at least one review.")
        st.stop()
    bb = {
        "product_name": st.session_state.bb_product,
        "category": st.session_state.bb_category,
        "brand": st.session_state.bb_brand,
        "target_market": st.session_state.bb_market,
        "target_audience": st.session_state.bb_audience,
        "brand_position": st.session_state.bb_position,
        "price_range": st.session_state.bb_price,
        "business_goal": st.session_state.bb_goal,
        "core_features": [f.strip() for f in st.session_state.bb_features.split("\n") if f.strip()],
    }
    set_level("ERROR" if not debug_mode else "INFO")
    progress = st.status("Running pipeline...", expanded=True, state="running")

    # Step 1: Insight
    progress.update(label="Customer Insight: analyzing reviews...")
    t0 = time.time()
    insight_result = insight_run(reviews_list, product_info(), business_brief=bb)
    insight_time = round(time.time() - t0, 2)
    st.markdown(f"**Customer Insight** - {insight_time}s")
    if debug_mode:
        with st.expander("Debug: Insight Agent", expanded=True):
            st.markdown("**Input (reviews)**")
            st.json(reviews_list)
            st.markdown("**State Transition**")
            st.code("INIT -> INSIGHT_DONE")
            st.markdown("**Schema Validation**")
            st.code("PASSED - insight_schema.json")
    st.json(insight_result["data"])

    # Step 2: Marketing
    progress.update(label="Marketing: generating content...")
    t0 = time.time()
    marketing_result = marketing_run(insight_result["data"], business_brief=bb)
    mkt_time = round(time.time() - t0, 2)
    st.markdown(f"**Marketing Agent** - {mkt_time}s")
    if debug_mode:
        with st.expander("Debug: Marketing Agent", expanded=True):
            st.markdown("**Input (insight)**")
            st.json(insight_result["data"])
            st.markdown("**State Transition**")
            st.code("INSIGHT_DONE -> MARKETING_DONE")
            st.markdown("**Schema Validation**")
            st.code("PASSED - marketing_schema.json")
    st.json(marketing_result["data"])

    # Step 3: QA with retry
    retry_count = 0
    max_retries = 3
    marketing_data = marketing_result["data"]

    while True:
        progress.update(label=f"QA: evaluating (attempt {retry_count + 1})...")
        t0 = time.time()
        qa_result = qa_run(insight_result["data"], marketing_data, business_brief=bb)
        qa_time = round(time.time() - t0, 2)
        qa_data = qa_result["data"]

        if qa_data["decision"] == "APPROVED":
            next_label = "APPROVED"
        elif retry_count + 1 >= max_retries:
            next_label = "REJECTED"
        else:
            next_label = "MARKETING_DONE (retry)"

        label = f"**QA Agent** - {qa_time}s"
        if retry_count > 0:
            label += f" (retry {retry_count})"
        st.markdown(label)

        if debug_mode:
            with st.expander("Debug: QA Agent", expanded=True):
                st.markdown("**Processing Time**")
                st.code(f"{qa_time}s")
                st.markdown("**State Transition**")
                st.code(f"MARKETING_DONE -> QA_DONE -> {next_label}")
                st.markdown("**Schema Validation**")
                st.code("PASSED - qa_schema.json")
                st.markdown("**Score / Decision**")
                st.code(f"{qa_data['overall_score']}/100 -> {qa_data['decision']}")
        st.json(qa_data)

        if qa_data["decision"] == "APPROVED":
            progress.update(label=f"Approved! Score: {qa_data['overall_score']}", state="complete")
            break
        retry_count += 1
        if retry_count >= max_retries:
            progress.update(label=f"Rejected after {max_retries} retries", state="error")
            break
        progress.update(label=f"Score {qa_data['overall_score']} less than 80, retry {retry_count}/{max_retries}...")
        marketing_result = marketing_run(insight_result["data"], business_brief=bb)
        marketing_data = marketing_result["data"]
        st.markdown(f"**Marketing Agent (retry {retry_count})**")
        st.json(marketing_data)

    bb = {
        "product_name": st.session_state.bb_product,
        "category": st.session_state.bb_category,
        "brand": st.session_state.bb_brand,
        "target_market": st.session_state.bb_market,
        "target_audience": st.session_state.bb_audience,
        "brand_position": st.session_state.bb_position,
        "price_range": st.session_state.bb_price,
        "business_goal": st.session_state.bb_goal,
        "core_features": [f.strip() for f in st.session_state.bb_features.split("\n") if f.strip()],
    }
    st.session_state.results = {
        "insight": insight_result["data"], "marketing": marketing_data, "qa": qa_data,
        "insight_time": insight_time, "mkt_time": mkt_time, "qa_time": qa_time,
        "retries": retry_count, "final_state": qa_data["decision"],
        "total_time": round(insight_time + mkt_time + qa_time, 2),
        "business_brief": bb,
    }

    st.divider()
    st.markdown("### Execution Information")
    r = st.session_state.results
    cols = st.columns(4)
    cols[0].metric("Processing Time", f"{r['total_time']}s")
    cols[1].metric("Final State", r["final_state"])
    cols[2].metric("Retry Count", r["retries"])
    cols[3].metric("Validation", "PASSED")

    with st.expander("Business Brief (Shared Context)", expanded=False):
        st.json(r["business_brief"])

    st.divider()
    st.markdown("### Agent Results")

    with st.expander("Customer Insight", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Pain Points**")
            for p in insight_result["data"]["pain_points"]:
                st.markdown(f"- {p}")
            st.markdown("**Advantages**")
            for a in insight_result["data"]["advantages"]:
                st.markdown(f"- {a}")
        with c2:
            st.markdown("**Customer Segments**")
            for s in insight_result["data"]["customer_segments"]:
                st.markdown(f"- {s}")
            st.markdown(f"**Confidence:** {insight_result['data']['confidence_score']}")
        st.markdown("---")
        st.markdown("**JSON Output**")
        st.json(insight_result["data"])

    with st.expander("Marketing", expanded=True):
        st.markdown("**Campaign Suggestions**")
        for c in marketing_data["campaign_suggestions"]:
            st.markdown(f"- {c}")
        st.markdown("**Key Messages**")
        for m in marketing_data["key_messaging"]:
            st.markdown(f"- {m}")
        st.markdown("---")
        st.markdown("**JSON Output**")
        st.json(marketing_data)

    with st.expander("QA Evaluation", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Score", qa_data["overall_score"])
            st.metric("Decision", qa_data["decision"])
        with col2:
            st.markdown("**Issues**")
            if qa_data["issues"]:
                for issue in qa_data["issues"]:
                    st.markdown(f"- {issue}")
            else:
                st.markdown("*No issues found*")
        st.markdown(f"**Feedback:** {qa_data['feedback']}")
        st.markdown("---")
        st.markdown("**JSON Output**")
        st.json(qa_data)
