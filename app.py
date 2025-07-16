import streamlit as st
import pandas as pd
import os
import pickle
from datetime import date
from streamlit_sortable import sortable

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
        planeringsdatum = st.date_input("Välj startdatum för veckan", value=date.today())

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
            "Planeringsdatum": str(planeringsdatum),
            "Ämnen": valda_ämnen,
            "Gruppuppgift": gruppuppgift,
            "Tenta antal": tenta_antal,
            "POP-förslag": [p for p in pop_vals if p]
        }
        data = load_data()
        data.append(kurs)
        save_data(data)
        st.success("Kursen sparades!")

# ----- Drag-and-drop planering av ämnen -----
st.markdown("---")
st.header("📅 Dra och släpp ämnen till veckodagar")

veckodagar = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]
initial_items = {dag: [] for dag in veckodagar}

if valda_ämnen:
    if "dnd_planering" not in st.session_state:
        st.session_state["dnd_planering"] = initial_items
        st.session_state["dnd_planering"]["Ämnen"] = valda_ämnen

    updated_planering = sortable(
        st.session_state["dnd_planering"],
        direction="horizontal",
        multi_containers=True,
        container_style={"minHeight": "200px", "border": "1px solid lightgray", "padding": "10px"},
        item_style={"padding": "8px", "margin": "4px", "backgroundColor": "#f0f0f0", "borderRadius": "5px"}
    )

    st.session_state["dnd_planering"] = updated_planering

    if st.button("💾 Spara vecko-planering"):
        st.success("Planering sparad!")

# ----- Visa planering i tabell -----
if "dnd_planering" in st.session_state:
    st.subheader("📊 Planeringsöversikt")
    plan_data = []
    for dag, items in st.session_state["dnd_planering"].items():
        for ämne in items:
            plan_data.append({"Dag": dag, "Ämne": ämne})
    df = pd.DataFrame(plan_data)
    st.dataframe(df)

# ----- Visa sparade kurser -----
st.markdown("---")
st.header("📂 Sparade kurser")
all_data = load_data()
if all_data:
    st.dataframe(pd.DataFrame(all_data))
else:
    st.info("Inga kurser har sparats än.")
