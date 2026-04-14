import streamlit as st
import pandas as pd
from collections import Counter
import numpy as np
from datetime import timedelta

# Page Setup
st.set_page_config(page_title="Confidence AI Predictor", layout="wide")

st.title("🛡️ Super-AI: Confidence-Based Predictor")
st.write("प्रत्येक नंबर के साथ उसका 'Confidence %' और स्कोर देखें।")

# 1. Master Patterns
master_patterns = [0, -18, -16, -26, -32, -1, -4, -11, -15, -10, -51, -50, 15, 5, -5, -55, 1, 10, 11, 51, 55, -40]
shifts = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG']

uploaded_file = st.sidebar.file_uploader("Data File Upload", type=['csv', 'xlsx'])

if uploaded_file:
    try:
        # File handling
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Date processing
        if 'DATE' in df.columns:
            df['DATE'] = pd.to_datetime(df['DATE']).dt.date
            available_dates = df['DATE'].dropna().unique()
            selected_date = st.sidebar.selectbox("तारीख चुनें:", options=reversed(available_dates))
            base_idx = df[df['DATE'] == selected_date].index[0]
            tomorrow = selected_date + timedelta(days=1)
        else:
            base_idx = len(df) - 1
            tomorrow = "Next Day"

        # Numeric check
        for s in shifts:
            if s in df.columns:
                df[s] = pd.to_numeric(df[s], errors='coerce')

        # --- SCORING ENGINE ---
        scores = np.zeros(100)
        today_nums = df.loc[base_idx, [s for s in shifts if s in df.columns]].dropna().to_dict()
        
        for val in today_nums.values():
            for p in master_patterns:
                scores[int((val + p) % 100)] += 1

        # --- DISPLAY RESULTS ---
        st.info(f"📅 **Base Date:** {selected_date} | 🎯 **Prediction for:** {tomorrow}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.header("✅ Top Winners")
            # Logic: Convert Score to Confidence % (Max Score is usually around 10-12)
            winners = []
            for n in range(100):
                if scores[n] >= 3:
                    conf = min(98, (scores[n] / 8) * 100) # 8 hits = 100% (Approx)
                    winners.append({"Number": n, "Score": int(scores[n]), "Confidence %": f"{conf:.1f}%"})
            
            if winners:
                winners_df = pd.DataFrame(winners).sort_values(by="Score", ascending=False)
                st.table(winners_df.head(12))
            else:
                st.write("अभी कोई मजबूत नंबर (3+ Hits) नहीं मिला।")

        with col2:
            st.header("❌ 60-70 Losers (Not Coming)")
            losers = [n for n in range(100) if scores[n] <= 1]
            st.error(f"इन {len(losers)} नंबरों के आने का चांस 1% से कम है:")
            st.write(sorted(losers))

        # --- SHIFT-WISE ANALYSIS ---
        st.divider()
        st.header("🎰 Shift-Wise Analysis")
        valid_shifts = [s for s in shifts if s in df.columns]
        if valid_shifts:
            tabs = st.tabs(valid_shifts)
            for i, s_name in enumerate(valid_shifts):
                with tabs[i]:
                    s_val = today_nums.get(s_name)
                    if s_val is not None:
                        st.subheader(f"{s_name} (Today: {int(s_val)})")
                        s_preds = []
                        for p in master_patterns:
                            num = int((s_val + p)%100)
                            s_preds.append({"Number": num, "Confidence %": f"{min(98, (scores[num]/8)*100):.1f}%"})
                        
                        s_df = pd.DataFrame(s_preds).sort_values("Confidence %", ascending=False).drop_duplicates('Number')
                        st.table(s_df.head(5))

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Sidebar में अपनी Excel/CSV फाइल अपलोड करें।")
    
