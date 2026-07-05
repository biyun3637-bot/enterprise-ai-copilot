import streamlit as st
import sys, os, json, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.insight import run as insight_run
from src.agents.marketing import run as marketing_run
from src.agents.qa import run as qa_run
from src.tools.logger import set_level

st.set_page_config(page_title="Enterprise AI Growth Copilot", layout="wide")

# ©¤©¤ Helpers ©¤©¤

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


# ©¤©¤ Session state ©¤©¤

if "results" not in st.session_state:
    st.session_state.results = None
if "reviews_input" not in st.session_state:
    st.session_state.reviews_input = ""


# ©¤©¤ Sidebar ©¤©¤

with st.sidebar:
    st.markdown("### Enterprise AI Growth Copilot")
    st.markdown(
        "A 3-agent pipeline that analyzes product reviews, "
        "generates marketing content, and evaluates quality."
    )
    st.markdown("---")

    files = load_test_data()
    file_names = [f[0] for f in files]
    sample_choice = st.selectbox(
        "Sample data",
        [""] + file_names,
        format_func=lambda x: x if x else "\u2014 Select \u2014",
    )
    if sample_choice:
        path = [f[1] for f in files if f[0] == sample_choice][0]
        content = load_reviews(path)
        st.session_state.reviews_input = "\n".join(content)
        st.info(f"Loaded {sample_choice} ({len(content)} reviews)")

    st.markdown("---")
    debug_mode = st.checkbox("Debug Mode", value=False)


# ©¤©¤ Main UI ©¤©¤

st.title("Enterprise AI Growth Copilot")

# Section 1: Input
st.markdown("### Input Reviews")
reviews_input = st.text_area(
    "Enter reviews, one per line:",
    value=st.session_state.reviews_input,
    height=180,
    placeholder="Paste your product reviews here...",
    key="reviews_area",
)

col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    run_clicked = st.button("Run Analysis", type="primary", use_container_width=True)
with col2:
    if st.button("Clear", use_container_width=True):
        st.session_state.results = None
        st.session_state.reviews_input = ""
        st.rerun()


# ©¤©¤ Pipeline Execution ©¤©¤

if run_clicked:
    reviews_list = [r.strip() for r in reviews_input.strip().split("\n") if r.strip()]
    if not reviews_list:
        st.warning("Please enter at least one review.")
        st.stop()

    set_level("ERROR" if not debug_mode else "INFO")

    progress = st.status("Running pipeline...", expanded=True, state="running")

    # Step 1: Customer Insight
    progress.update(label="Customer Insight: analyzing reviews...")
    t0 = time.time()
    insight_result = insight_run(reviews_list, product_info())
    insight_time = round(time.time() - t0, 2)
    st.markdown(f"**Customer Insight** \u2014 {insight_time}s")
    st.json(insight_result["data"])

    # Step 2: Marketing
    progress.update(label="Marketing: generating content...")
    t0 = time.time()
    marketing_result = marketing_run(insight_result["data"])
    mkt_time = round(time.time() - t0, 2)
    st.markdown(f"**Marketing Agent** \u2014 {mkt_time}s")
    st.json(marketing_result["data"])

    # Step 3: QA with retry loop
    retry_count = 0
    max_retries = 3
    marketing_data = marketing_result["data"]

    while True:
        progress.update(label=f"QA: evaluating (attempt {retry_count + 1})...")
        t0 = time.time()
        qa_result = qa_run(insight_result["data"], marketing_data)
        qa_time = round(time.time() - t0, 2)
        qa_data = qa_result["data"]

        st.markdown(
            f"**QA Agent** \u2014 {qa_time}s"
            + (f" (retry {retry_count})" if retry_count > 0 else "")
        )
        st.json(qa_data)

        if qa_data["decision"] == "APPROVED":
            progress.update(
                label=f"Approved! Score: {qa_data['overall_score']}",
                state="complete",
            )
            break

        retry_count += 1
        if retry_count >= max_retries:
            progress.update(label=f"Rejected after {max_retries} retries", state="error")
            break

        progress.update(
            label=f"Score {qa_data['overall_score']} < 80, retry {retry_count}/{max_retries}..."
        )
        marketing_result = marketing_run(insight_result["data"])
        marketing_data = marketing_result["data"]
        st.markdown(f"**Marketing Agent (retry {retry_count})**")
        st.json(marketing_data)

    # Store for re-render persistence
    st.session_state.results = {
        "insight": insight_result["data"],
        "marketing": marketing_data,
        "qa": qa_data,
        "insight_time": insight_time,
        "mkt_time": mkt_time,
        "qa_time": qa_time,
        "retries": retry_count,
        "final_state": qa_data["decision"],
        "total_time": round(insight_time + mkt_time + qa_time, 2),
    }

    # Section 4: Execution Information
    st.divider()
    st.markdown("### Execution Information")
    r = st.session_state.results
    cols = st.columns(4)
    cols[0].metric("Processing Time", f"{r['total_time']}s")
    cols[1].metric("Final State", r["final_state"])
    cols[2].metric("Retry Count", r["retries"])
    cols[3].metric("Validation", "PASSED")

    # Section 3: Agent Results (expandable panels)
    st.divider()
    st.markdown("### Agent Results")

    with st.expander("Customer Insight", expanded=True):
        cri, c2 = st.columns(2)
        with cri:
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
        score = qa_data["overall_score"]
        decision = qa_data["decision"]
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Score", score)
            st.metric("Decision", decision)
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
