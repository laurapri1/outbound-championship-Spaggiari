import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path

# =====================================
# CONFIGURAZIONE
# =====================================

FILE_DATI = "dati.xlsx"
ADMIN_PASSWORD = "Sales2026!"
TARGET_MESE = 2500

st.set_page_config(
    page_title="Sales Championship",
    page_icon="🏆",
    layout="wide"
)

st.title("🏆 Sales Championship")

# =====================================
# FUNZIONI
# =====================================

def livello(xp):
    if xp >= 5000:
        return "👑 Legend"
    elif xp >= 3000:
        return "💎 Platinum"
    elif xp >= 1500:
        return "🥇 Gold"
    elif xp >= 500:
        return "🥈 Silver"
    else:
        return "🥉 Bronze"


def badge(chiamate, preventivi, ordini):
    badges = []

    if chiamate >= 500:
        badges.append("☎️ Call Machine")

    if preventivi >= 50:
        badges.append("📄 Proposal Master")

    if ordini >= 10:
        badges.append("💰 Deal Closer")

    if not badges:
        return "Nessuno"

    return " | ".join(badges)


# =====================================
# CREAZIONE FILE EXCEL
# =====================================

if not Path(FILE_DATI).exists():

    df_vuoto = pd.DataFrame(columns=[
        "Data",
        "Venditore",
        "Chiamate",
        "Preventivi",
        "Ordini",
        "Punti"
    ])

    df_vuoto.to_excel(FILE_DATI, index=False)

# =====================================
# LOGIN ADMIN
# =====================================

st.sidebar.header("🔐 Area Admin")

password = st.sidebar.text_input(
    "Password",
    type="password"
)

is_admin = password == ADMIN_PASSWORD

if is_admin:
    st.sidebar.success("👑 Modalità Admin")

# =====================================
# LETTURA DATI
# =====================================

df = pd.read_excel(FILE_DATI)

# =====================================
# INSERIMENTO DATI (SOLO ADMIN)
# =====================================

if is_admin:

    st.sidebar.markdown("---")
    st.sidebar.header("📥 Inserimento Attività")

    data = st.sidebar.date_input(
        "Data",
        value=date.today()
    )

    venditore = st.sidebar.selectbox(
        "Venditore",
        [
            "Eleonora",
            "Emma",
            "Laura",
            "Mara"
        ]
    )

    chiamate = st.sidebar.number_input(
        "Chiamate",
        min_value=0,
        value=0
    )

    preventivi = st.sidebar.number_input(
        "Preventivi",
        min_value=0,
        value=0
    )

    ordini = st.sidebar.number_input(
        "Ordini",
        min_value=0,
        value=0
    )

    if st.sidebar.button("💾 Salva"):

        if chiamate > 0:
            punti = (
                preventivi +
                ((ordini * 3) / chiamate) * 100
            )
        else:
            punti = 0

        nuovo_record = pd.DataFrame([{
            "Data": data,
            "Venditore": venditore,
            "Chiamate": chiamate,
            "Preventivi": preventivi,
            "Ordini": ordini,
            "Punti": round(punti, 2)
        }])

        df = pd.concat(
            [df, nuovo_record],
            ignore_index=True
        )

        df.to_excel(
            FILE_DATI,
            index=False
        )

        st.success("✅ Record salvato")

        st.rerun()

# =====================================
# RICARICA DATI
# =====================================

df = pd.read_excel(FILE_DATI)

if df.empty:
    st.info("Nessun dato disponibile.")
    st.stop()

# =====================================
# DATE
# =====================================

df["Data"] = pd.to_datetime(
    df["Data"],
    errors="coerce"
)

df = df.dropna(subset=["Data"])

if df.empty:
    st.info("Nessun dato disponibile.")
    st.stop()

mesi = sorted(
    df["Data"].dt.strftime("%Y-%m").unique(),
    reverse=True
)

mese_scelto = st.selectbox(
    "📅 Seleziona il mese",
    mesi
)

df_filtrato = df[
    df["Data"].dt.strftime("%Y-%m")
    == mese_scelto
]

if df_filtrato.empty:
    st.warning("Nessun dato disponibile per il mese selezionato.")
    st.stop()

# =====================================
# CLASSIFICA
# =====================================

classifica = (
    df_filtrato
    .groupby("Venditore")
    .agg({
        "Chiamate": "sum",
        "Preventivi": "sum",
        "Ordini": "sum",
        "Punti": "sum"
    })
    .reset_index()
)

classifica["Livello"] = classifica["Punti"].apply(
    livello
)

classifica["Badge"] = classifica.apply(
    lambda r: badge(
        r["Chiamate"],
        r["Preventivi"],
        r["Ordini"]
    ),
    axis=1
)

classifica = classifica.sort_values(
    "Punti",
    ascending=False
).reset_index(drop=True)

# =====================================
# LEADER
# =====================================

leader = classifica.iloc[0]

st.success(
    f"🔥 Leader del mese: {leader['Venditore']} con {leader['Punti']:.1f} punti"
)

# =====================================
# PODIO
# =====================================

st.subheader("🏅 Podio")

col1, col2, col3 = st.columns(3)

if len(classifica) >= 1:
    with col1:
        st.metric(
            f"🥇 {classifica.iloc[0]['Venditore']}",
            f"{classifica.iloc[0]['Punti']:.1f}"
        )

if len(classifica) >= 2:
    with col2:
        st.metric(
            f"🥈 {classifica.iloc[1]['Venditore']}",
            f"{classifica.iloc[1]['Punti']:.1f}"
        )

if len(classifica) >= 3:
    with col3:
        st.metric(
            f"🥉 {classifica.iloc[2]['Venditore']}",
            f"{classifica.iloc[2]['Punti']:.1f}"
        )

# =====================================
# TARGET
# =====================================

st.subheader("🎯 Avanzamento Target")

for riga in classifica.itertuples():

    percentuale = min(
        riga.Punti / TARGET_MESE,
        1.0
    )

    st.write(
        f"**{riga.Venditore}** - {percentuale:.0%}"
    )

   