"""
streamlit_app.py — AI Research Assistant (Premium UI)
"""
import streamlit as st
import requests, json, time
from datetime import datetime

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_URL = "https://intelligraph-ai.onrender.com"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif; }

.stApp {
    background: #0a0a0f;
    color: #e2e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d0d18 !important;
    border-right: 1px solid #1a1a2e !important;
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }
[data-testid="stSidebar"] h3 { color: #e2e8f0 !important; }

/* Hero */
.hero-wrap {
    text-align: center;
    padding: 3rem 0 2rem 0;
}
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #818cf8 0%, #38bdf8 50%, #34d399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.6rem;
}
.hero-sub {
    color: #64748b;
    font-size: 1.05rem;
    font-weight: 400;
    margin-bottom: 0;
}

/* Input box */
.stTextArea textarea {
    background: #111827 !important;
    color: #e2e8f0 !important;
    border: 1.5px solid #1e293b !important;
    border-radius: 14px !important;
    font-size: 1rem !important;
    padding: 14px !important;
    transition: border-color 0.2s !important;
}
.stTextArea textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px #6366f115 !important;
}

/* Submit button */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.7rem 2.5rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #4f46e5, #4338ca) !important;
    box-shadow: 0 8px 25px #6366f140 !important;
    transform: translateY(-1px) !important;
}

/* Route pill */
.pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 16px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.pill-research { background: #0f2744; color: #60a5fa; border: 1px solid #1d4ed8; }
.pill-coding   { background: #0f2d1f; color: #34d399; border: 1px solid #059669; }
.pill-chat     { background: #2d1554; color: #c084fc; border: 1px solid #7c3aed; }

/* Cards */
.metric-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 1.2rem;
    text-align: center;
}
.metric-value {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #818cf8, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-label {
    color: #475569;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-top: 2px;
}

/* Report */
.report-wrap {
    background: linear-gradient(135deg, #0f172a, #111827);
    border: 1px solid #1e293b;
    border-radius: 16px;
    padding: 2rem;
    line-height: 1.85;
    color: #cbd5e1;
}
.report-wrap h1, .report-wrap h2, .report-wrap h3 {
    color: #e2e8f0 !important;
}

/* Trace */
.trace-row {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 8px 12px;
    border-radius: 8px;
    background: #0f172a;
    border-left: 3px solid #6366f1;
    margin: 5px 0;
    font-family: 'Courier New', monospace;
    font-size: 0.82rem;
    color: #94a3b8;
}
.trace-step {
    color: #475569;
    min-width: 52px;
    font-weight: 600;
}

/* Result agent box */
.agent-box {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 1rem;
}
.agent-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: #818cf8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 10px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #111827;
    border-radius: 10px;
    padding: 4px;
    border: 1px solid #1e293b;
}
.stTabs [data-baseweb="tab"] {
    color: #64748b !important;
    border-radius: 7px !important;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: #6366f1 !important;
    color: white !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: #111827 !important;
    border: 1px solid #1e293b !important;
    border-radius: 10px !important;
}

/* Divider */
hr { border-color: #1e293b; margin: 1.5rem 0; }

/* Score color helper */
.score-hi  { color: #34d399; }
.score-mid { color: #fbbf24; }
.score-lo  { color: #f87171; }

/* History item */
.hist-item {
    padding: 10px 14px;
    border-radius: 10px;
    background: #111827;
    border: 1px solid #1e293b;
    margin-bottom: 8px;
    font-size: 0.83rem;
    color: #94a3b8;
    cursor: default;
}
.hist-user { color: #818cf8; font-weight: 600; margin-bottom: 3px; font-size: 0.78rem; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ── Helpers ───────────────────────────────────────────────────────────────────
def call_backend(query: str, endpoint="/workflow") -> dict:
    try:
        r = requests.post(
            f"{BACKEND_URL}{endpoint}",
            json={"query": query, "chat_history": st.session_state.chat_history[-6:]},
            timeout=120,
        )
        r.raise_for_status()
        return r.json()
    except requests.ConnectionError:
        return {"success": False, "error": "⚠️ Cannot connect to backend.\n\nRun:\n```\nuvicorn backend.main:app --reload\n```"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def pill_html(route):
    cfg = {
        "research":    ("🔬 Research",   "pill-research"),
        "coding":      ("💻 Coding",     "pill-coding"),
        "normal_chat": ("💬 Chat",       "pill-chat"),
    }
    label, cls = cfg.get(route, (route, "pill-research"))
    return f'<span class="pill {cls}">{label}</span>'

def score_html(s):
    cls = "score-hi" if s >= 8 else ("score-mid" if s >= 6 else "score-lo")
    return f'<span class="{cls}" style="font-size:2rem;font-weight:800">{s}</span><span style="color:#475569;font-size:0.85rem">/10</span>'

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧠 AI Research Assistant")
    st.caption("Multi-agent LangGraph system")
    st.markdown("---")

    st.markdown("**Workflow**")
    st.code("""START → Router
 ├─research→ Dispatcher
 │  ├─ Web (DuckDuckGo)
 │  ├─ Wikipedia
 │  └─ PDF Knowledge
 │       ↓
 │  Summarizer ←──┐
 │       ↓       │improve
 │  Reflection ──┘
 │       ↓finish
 │  Final Report
 ├─coding → Coding Agent
 └─chat   → Chat Agent
          ↓
         END""", language="text")

    st.markdown("---")
    st.markdown("**Route Override**")
    ep_choice = st.selectbox(
        "", ["Auto (recommended)", "Force Research", "Force Chat"],
        label_visibility="collapsed",
    )
    ep_map = {"Auto (recommended)": "/workflow", "Force Research": "/research", "Force Chat": "/chat"}
    selected_ep = ep_map[ep_choice]

    st.markdown("---")
    st.markdown("**Chat History**")
    if st.session_state.chat_history:
        for msg in reversed(st.session_state.chat_history[-8:]):
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="hist-item"><div class="hist-user">You</div>{msg["content"][:80]}{"..." if len(msg["content"])>80 else ""}</div>',
                    unsafe_allow_html=True,
                )
        if st.button("🗑 Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.last_result = None
            st.rerun()
    else:
        st.caption("No history yet.")

    st.markdown("---")
    st.markdown("""**Stack**
- LangGraph · LangChain
- Groq `llama-3.1-8b-instant`
- DuckDuckGo · Wikipedia
- FastAPI · Streamlit
""")

# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-title">AI Research & Evaluation<br>Assistant</div>
    <div class="hero-sub">Multi-agent workflow · Parallel research · Iterative reflection · Structured outputs</div>
</div>
""", unsafe_allow_html=True)

# Input
query = st.text_area(
    "Ask anything — research questions, coding problems, or general queries:",
    height=110,
    placeholder="e.g. How is AI transforming drug discovery?",
    key="q",
    label_visibility="visible",
)

col_run, col_sp = st.columns([1, 3])
with col_run:
    run_btn = st.button("⚡ Run Workflow", use_container_width=True)

# ── Execute ────────────────────────────────────────────────────────────────────
if run_btn:
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("🤖 Running AI workflow — agents working in parallel..."):
            result = call_backend(query.strip(), selected_ep)

        if result.get("error"):
            st.error(result["error"])
        else:
            st.session_state.last_result = result
            st.session_state.chat_history.append({"role": "user", "content": query.strip()})
            st.session_state.chat_history.append({"role": "assistant", "content": result.get("final_report", "")})

# ── Results ───────────────────────────────────────────────────────────────────
res = st.session_state.last_result
if res and not res.get("error"):
    st.markdown("---")

    # Metric strip
    c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1])
    with c1:
        st.markdown(
            f'{pill_html(res.get("route",""))} &nbsp; <span style="color:#475569;font-size:0.83rem">{res.get("route_reason","")[:70]}</span>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="metric-card">{score_html(res.get("reflection_score",0))}<div class="metric-label">Quality</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{res.get("iteration_count",0)}</div><div class="metric-label">Iterations</div></div>',
            unsafe_allow_html=True,
        )
    with c4:
        ms = res.get("execution_time_ms", 0)
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{ms/1000:.1f}s</div><div class="metric-label">Time</div></div>',
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{len(res.get("citations",[]))}</div><div class="metric-label">Citations</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabs
    tab_report, tab_agents, tab_trace, tab_dl = st.tabs(
        ["📊 Final Report", "🔍 Agent Outputs", "📋 Execution Trace", "📥 Download"]
    )

    with tab_report:
        st.markdown(
            f'<div class="report-wrap">{res.get("final_report","No report generated.")}</div>',
            unsafe_allow_html=True,
        )

    with tab_agents:
        route = res.get("route", "")
        if route == "research":
            col_w, col_wi, col_p = st.columns(3)
            for col, key, icon, label in [
                (col_w,  "web_results",  "🌐", "Web Search (DuckDuckGo)"),
                (col_wi, "wiki_results", "📖", "Wikipedia"),
                (col_p,  "pdf_results",  "📄", "PDF Knowledge Base"),
            ]:
                with col:
                    items = res.get(key, [])
                    st.markdown(f'<div class="agent-title">{icon} {label}</div>', unsafe_allow_html=True)
                    if items:
                        for i, r in enumerate(items):
                            with st.expander(f"Result {i+1} — {r[:50]}...", expanded=False):
                                st.write(r)
                    else:
                        st.caption("No results.")

            st.markdown("---")
            st.markdown("**📝 Aggregated Summary**")
            st.info(res.get("summary", "N/A"))

            fb = res.get("reflection_feedback", "")
            if fb:
                st.markdown("**🔁 Reflection Feedback**")
                dec = res.get("reflection_decision", "")
                icon = "✅" if dec == "finish" else "🔄"
                st.markdown(f"{icon} **Decision:** `{dec.upper()}`")
                st.caption(fb)
        else:
            st.markdown("**Direct Response**")
            st.write(res.get("final_report", ""))
            st.caption("Research agents were skipped for this route type.")

    with tab_trace:
        traces = res.get("execution_trace", [])
        st.markdown(f"**{len(traces)} steps executed**")
        for i, t in enumerate(traces, 1):
            st.markdown(
                f'<div class="trace-row"><span class="trace-step">Step {i}</span>{t}</div>',
                unsafe_allow_html=True,
            )

    with tab_dl:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_md = f"""# AI Research Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Query:** {st.session_state.chat_history[-2]["content"] if len(st.session_state.chat_history)>=2 else "N/A"}
**Route:** {res.get("route","N/A")} | **Quality Score:** {res.get("reflection_score",0)}/10 | **Iterations:** {res.get("iteration_count",0)}

---

{res.get("final_report","")}

---
## Execution Trace
{chr(10).join(f"- {t}" for t in res.get("execution_trace",[]))}

## Citations
{chr(10).join(f"- {c}" for c in res.get("citations",[]))}
"""
        st.download_button("⬇️ Download as Markdown", report_md, f"report_{ts}.md", "text/markdown", use_container_width=True)
        st.download_button("⬇️ Download as JSON", json.dumps(res, indent=2), f"report_{ts}.json", "application/json", use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align:center;color:#334155;font-size:0.78rem">'
    'AI Research Assistant &nbsp;·&nbsp; LangGraph + Groq &nbsp;·&nbsp; B.Tech Final Year Project'
    '</p>'
    '<p style="text-align:center;font-size:0.85rem;margin-top:6px;">'
    '<span style="background:linear-gradient(135deg,#818cf8,#38bdf8);-webkit-background-clip:text;'
    '-webkit-text-fill-color:transparent;font-weight:700;">Built by Anish</span> 🚀'
    '</p>',
    unsafe_allow_html=True,
)
