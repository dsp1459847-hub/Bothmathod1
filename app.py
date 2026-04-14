import streamlit as st
import pandas as pd
from collections import Counter
from itertools import combinations
import numpy as np

# Page Config
st.set_page_config(page_title="Super-AI Total Predictor", layout="wide")

st.title("🛡️ Super-AI: Total Combination Predictor")
st.write("सभी 6 तरीकों (Patterns, Sequences, Trends, Bar, Multi-Shift) का निचोड़।")

# 1. Master Configurations
master_patterns = [0, -18, -16, -26, -32, -1, -4, -11, -15, -10, -51, -50, 15, 5, -5, -55, 1, 10, 11, 51, 55, -40]
shifts = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG']

# 2. File Upload
uploaded_file = st.sidebar.file_uploader("Upload Data File", type=['csv', 'xlsx'])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    for col in shifts:
        if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Pre-Processing
    st.sidebar.success("डेटा लोड हो गया है!")
    
    # Get Latest Numbers
    today_nums = df.iloc[-1][shifts].dropna().to_dict()
    yesterday_nums = df.iloc[-2][shifts].dropna().to_dict() if len(df) > 1 else {}

    # --- THE SUPER SCORING ENGINE ---
    scores = np.zeros(100) # 0 to 99 scores

    # A. Method 1: Master Pattern Score (Weight: 1 per hit)
    for val in today_nums.values():
        for p in master_patterns:
            res = int((val + p) % 100)
            scores[res] += 1

    # B. Method 2: History Transition (Jyoti Style - Weight: 3)
    # What usually follows these specific numbers?
    for s_name, s_val in today_nums.items():
        # Find matches in history for this specific shift and number
        history_hits = df[df[s_name] == s_val].index
        next_vals = []
        for idx in history_hits:
            if idx + 1 < len(df):
                v_next = df.loc[idx+1, s_name]
                if not pd.isna(v_next): next_vals.append(int(v_next))
        
        # Give points to top 2 most frequent next numbers
        top_next = [n for n, c in Counter(next_vals).most_common(2)]
        for tn in top_next:
            scores[tn] += 3

    # C. Method 3: Weekly & Monthly Trend (Weight: 2)
    flat_7d = []
    flat_30d = []
    for i in range(len(df)-1, max(0, len(df)-31), -1):
        day_ps = [p for v in df.iloc[i-1][shifts].dropna() for p in master_patterns if (v+p)%100 in set(df.iloc[i][shifts].dropna())]
        if i >= len(df)-7: flat_7d.extend(day_ps)
        flat_30d.extend(day_ps)
    
    top_7d = [p for p, c in Counter(flat_7d).most_common(5)]
    top_30d = [p for p, c in Counter(flat_30d).most_common(5)]
    
    for v in today_nums.values():
        for p in set(top_7d + top_30d):
            scores[int((v+p)%100)] += 2

    # D. Method 4: Sequence Logic (Weight: 2)
    # Today's Pattern -> Next Pattern
    for s_name, t_val in today_nums.items():
        if s_name in yesterday_nums:
            curr_p = int((t_val - yesterday_nums[s_name]) % 100)
            # Find what pattern usually follows this pattern
            # (Simplified: using the Rulebook logic we built earlier)
            if curr_p == 84: # -16
                scores[int((t_val + 0)%100)] += 2 # -16 -> 0
            elif curr_p == 89: # -11
                scores[int((t_val - 4)%100)] += 2 # -11 -> -4

    # --- DISPLAY FINAL RESULTS ---
    st.header("🎯 Combined Super Prediction")
    
    # Calculate Probability (Approx)
    final_results = []
    for num in range(100):
        if scores[num] > 0:
            final_results.append({
                "Number": num,
                "Total Score": scores[num],
                "Confidence": f"{min(95, scores[num]*5):.1f}%"
            })
    
    final_df = pd.DataFrame(final_results).sort_values(by="Total Score", ascending=False)

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🏆 Top Recommended Numbers (All Methods Combined)")
        st.table(final_df.head(10))
        
    with col2:
        st.subheader("💡 Logic Used")
        st.write("- **Pattern Hits:** Points for 22 master patterns.")
        st.write("- **Number Transition:** Points for what usually follows today's number.")
        st.write("- **Trend Weight:** Extra points for Weekly/Monthly hot patterns.")
        st.write("- **Sequence Logic:** Points for pattern-to-pattern history.")

    st.divider()
    st.header("🔍 Shift-wise Deep Analysis")
    st.write("प्रत्येक शिफ्ट के लिए सबसे मजबूत प्रेडिक्शन:")
    shift_res = []
    for s_name, s_val in today_nums.items():
        # Get highest score specifically for numbers derived from this shift
        shift_specific = []
        for p in master_patterns:
            n = int((s_val + p) % 100)
            shift_specific.append({"Number": n, "Score": scores[n]})
        best_n = sorted(shift_specific, key=lambda x: x['Score'], reverse=True)[0]
        shift_res.append({"Shift": s_name, "Today": s_val, "Best Prediction": best_n['Number'], "Power": best_n['Score']})
    
    st.dataframe(shift_res)

else:
    st.info("Sidebar में अपनी Excel/CSV फाइल अपलोड करें। यह सिस्टम आपके पुराने डेटा को खुद ही समझ लेगा।")
        
