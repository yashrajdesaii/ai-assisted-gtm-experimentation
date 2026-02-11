import streamlit as st
import pandas as pd
import sys
import os
import time

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.core.models import Lead, Hypothesis, Message, Experiment, ExperimentResult
from src.core.agents import Researcher, Strategist
from src.core.simulator import FunnelSimulator

st.set_page_config(page_title="ActivelyAI Growth Engineer", layout="wide", page_icon="rocket")

# Initialize Session State
if 'leads' not in st.session_state:
    st.session_state.leads = []
if 'experiment_results' not in st.session_state:
    st.session_state.experiment_results = []
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- Custom CSS for "Premium Feel" ---
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .metric-card {
        background-color: #262730;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar: Configuration ---
with st.sidebar:
    st.image("https://placehold.co/200x60/png?text=ActivelyAI", width=200)
    st.title("Experiment Config")
    
    st.subheader("1. Define Target Audience")
    uploaded_file = st.file_uploader("Upload CSV (Name, Company, Title)", type=['csv'])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.session_state.leads = [Lead(**row) for row in df.to_dict('records')]
        st.success(f"Loaded {len(st.session_state.leads)} leads!")
    
    st.write("--- OR ---")
    if st.button("Generate Synthetic Leads"):
        # Quick synthetic data
        st.session_state.leads = [
            Lead(name="Alice Chen", title="VP Sales", company="TechFlow", triggers=[]),
            Lead(name="Bob Smith", title="Founder", company="DataSync", triggers=[]),
            Lead(name="Charlie Davis", title="Head of Ops", company="LogiChain", triggers=[]),
            Lead(name="Diana Prince", title="CTO", company="SecureNet", triggers=[]),
            Lead(name="Evan Wright", title="Director of Growth", company="ScaleUp", triggers=[])
        ]
        st.success("Generated 5 synthetic leads.")

    st.subheader("2. Set Hypotheses")
    h1_desc = st.text_area("Variant A (Control/Logic)", "Focus on ROI and efficiency gains.", height=70)
    h2_desc = st.text_area("Variant B (Challenger/Social)", "Focus on peer validation and social proof.", height=70)

# --- Main Dashboard ---
st.title("AI-Assisted GTM Experimentation System")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Active Experiment Dashboard")
    
    if st.button("🚀 Launch Experiment", type="primary"):
        if not st.session_state.leads:
            st.warning("Please add leads first.")
        else:
            researcher = Researcher()
            strategist = Strategist()
            simulator = FunnelSimulator()
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            messages = []
            
            total = len(st.session_state.leads)
            
            for i, lead in enumerate(st.session_state.leads):
                # 1. Research
                status_text.text(f"Agent A (Researcher): Scanning {lead.company}...")
                enriched_lead = researcher.research_lead(lead)
                
                # 2. Assign Variant (A/B Split)
                variant = "A" if i % 2 == 0 else "B"
                hypothesis_desc = h1_desc if variant == "A" else h2_desc
                hypothesis = Hypothesis(
                    name=f"Hypothesis {variant}", 
                    description=hypothesis_desc,
                    experiment_variant=variant
                )
                
                # 3. Strategist
                status_text.text(f"Agent B (Strategist): Drafting message for {lead.name} using {variant} strategy...")
                msg = strategist.generate_message(enriched_lead, hypothesis, variant)
                messages.append(msg)
                
                # 4. Simulate Outcome
                res = simulator.simulate_outcome(enriched_lead, msg, hypothesis)
                results.append(res)
                
                # Update progress
                progress_bar.progress((i + 1) / total)
                time.sleep(0.5) # Simulate processing time for effect
            
            st.session_state.experiment_results = results
            st.session_state.messages = messages
            status_text.text("Experiment Complete!")
            st.balloons()

# --- Analytics Section ---
if st.session_state.experiment_results:
    st.divider()
    
    # Process Metrics
    df_res = pd.DataFrame([r.dict() for r in st.session_state.experiment_results])
    
    # Overall Funnel
    total = len(df_res)
    sent = df_res['sent'].sum()
    opened = df_res['opened'].sum()
    replied = df_res['replied'].sum()
    meetings = df_res['meeting_booked'].sum()
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Sent", sent)
    m2.metric("Opened", opened, f"{opened/sent:.1%}")
    m3.metric("Replied", replied, f"{replied/sent:.1%}")
    m4.metric("Meetings", meetings, f"{meetings/sent:.1%}")
    
    # Variant Comparison
    st.subheader("Variant Performance Analysis")
    var_perf = df_res.groupby("variant_chosen")[["opened", "replied", "meeting_booked"]].mean()
    st.table(var_perf.style.format("{:.1%}"))
    
    # Winner Declaration
    winner = var_perf['meeting_booked'].idxmax()
    st.success(f"🏆 Winning Strategy: Variant {winner}")
    st.info(f"Insight: Variant {winner} performed better. Recommendation: Scale this messaging for the next batch.")

    settings_exp = st.expander("Detailed Message Log")
    with settings_exp:
        for msg in st.session_state.messages:
            st.markdown(f"**To:** {msg.lead_id} | **Variant:** {msg.variant_type}")
            st.caption(f"Reasoning: {msg.reasoning}")
            st.text_area("Content", msg.content, height=100, key=msg.lead_id)
            st.divider()

else:
    st.info("Awaiting Experiment Launch...")
