import streamlit as st
import pandas as pd
import os
import pickle

# Konfiguration
st.set_page_config(page_title="Kursbyggare", layout="wide")
st.title("📚 Kursbyggare")

DATA_FILE = "kursdata.pkl"

# Spara / ladda funktioner
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'rb') as f:
            return pickle.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, 'wb') as f:
        pickle.dump(data, f)

# Formulär
with st.form("kurs_form"):
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("Kursinfo")
        kursnamn = st.text_input("Kursnamn")
        skola = st.text_input("Skola")
        poäng = st.number_input("Antal poäng", min_value=0)
        timmar_vecka = st.number_input("Timmar/vecka", min_value=0)
        dagar = st.number_input("Antal dagar", min_value=0)
        tid = st.selectbox("Tid", ["Förmiddag", "Eftermiddag", "Kväll"])
        fil = st.file_uploader("Ladda upp fil", type=["pdf", "docx", "xlsx"])

        st.markdown("### Ämnen (SoU)")
        ämnen = ["Ledarskap", "Kommunikation", "Organisation", "Etik", "Arbetsmiljö", "Konflikthantering"]
        valda_ämnen = [ämne for ämne in ämnen if st.checkbox(ämne)]

    with col2:
        st.header("Planering")
        tidsperiod = st.radio("Välj planeringstyp", ["Månad", "Vecka", "Dag"])
        planering = st.select_slider(f"Välj {tidsperiod.lower()}:", options=[f"{i}" for i in range(1, 32)])

        gruppuppgift = st.text_input("Gruppuppgift / Lämning")
        tenta_antal = st.number_input("Tenta – Träffar (antal)", min_value=0, step=1)

        st.subheader("POP – Förslag / Arbetsmaterial")
        pop_vals = []
        for i in range(6):
            pop_vals.append(st.text_input(f"POP-förslag {i+1}", key=f"pop{i}"))

    submitted = st.form_submit_button("💾 Spara kurs")

    if submitted:
        kurs = {
            "Kursnamn": kursnamn,
            "Skola": skola,
            "Poäng": poäng,
            "Timmar/vecka": timmar_vecka,
            "Dagar": dagar,
            "Tid": tid,
            "Tidsperiod": tidsperiod,
            "Planering": planering,
            "Ämnen": valda_ämnen,
            "Gruppuppgift": gruppuppgift,
            "Tenta antal": tenta_antal,
            "POP-förslag": [p for p in pop_vals if p]
        }
        data = load_data()
        data.append(kurs)
        save_data(data)
        st.success("Kursen sparades!")

# Visa sparade kurser
st.markdown("---")
st.header("📂 Sparade kurser")
all_data = load_data()
if all_data:
    df = pd.DataFrame(all_data)
    st.dataframe(df)
else:
    st.info("Inga kurser har sparats än.")
