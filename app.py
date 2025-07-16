import streamlit as st
import pandas as pd
import os
import pickle

st.set_page_config(page_title="Kursbyggare", layout="wide")
st.title("📚 Kursbyggare")

DATA_FILE = "kursdata.pkl"

# ----- Hjälpfunktioner -----
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'rb') as f:
            return pickle.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, 'wb') as f:
        pickle.dump(data, f)

# ----- Formulär: Kursinformation -----
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
        planeringsruta = st.text_input(f"Ange {tidsperiod.lower()} (t.ex. Mars, V12 eller 2025-07-30)")

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
            "Planeringstid": planeringsruta,
            "Ämnen": valda_ämnen,
            "Gruppuppgift": gruppuppgift,
            "Tenta antal": tenta_antal,
            "POP-förslag": [p for p in pop_vals if p]
        }
        data = load_data()
        data.append(kurs)
        save_data(data)
        st.success("Kursen sparades!")

# ----- Schemaläggning av valda ämnen -----
st.markdown("---")
st.header("📅 Planera ämnen")

if valda_ämnen:
    ämnesplanering = {}
    for ämne in valda_ämnen:
        with st.expander(f"📘 {ämne}"):
            typ = st.selectbox("Typ av planering", ["Månad", "Vecka", "Dag"], key=ämne+"_typ")
            när = st.text_input(f"Vilken {typ.lower()}?", key=ämne+"_tid")
            kommentar = st.text_area("Kommentar / aktivitet", key=ämne+"_kommentar")
            ämnesplanering[ämne] = {"Typ": typ, "Tid": när, "Kommentar": kommentar}

    if st.button("💾 Spara ämnesplanering"):
        st.session_state["ämnesplanering"] = ämnesplanering
        st.success("Planering sparad!")

# ----- Visning av planering -----
if "ämnesplanering" in st.session_state:
    st.markdown("### 🗂️ Planeringsöversikt")
    df = pd.DataFrame.from_dict(st.session_state["ämnesplanering"], orient="index")
    st.dataframe(df)

# ----- Sparade kurser -----
st.markdown("---")
st.header("📂 Sparade kurser")
all_data = load_data()
if all_data:
    st.dataframe(pd.DataFrame(all_data))
else:
    st.info("Inga kurser har sparats än.")
