import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from calendar import monthrange

# =====================================
# CONFIGURAZIONE
# =====================================

FILE_DATI = "classifica_mensile.xlsx"
FILE_HALL_OF_FAME = "hall_of_fame.xlsx"

ADMIN_PASSWORD = "Sales2026!"

TARGET_TEAM_CHIAMATE = 2500

VENDITORI = [
    "Eleonora",
    "Emma",
    "Laura",
    "Mara"
]

st.set_page_config(
    page_title="Sales Championship",
    page_icon="🏆",
    layout="wide"
)

# =====================================
# STILE
# =====================================

st.markdown("""
<style>

.stApp {
    background-color: #F8FAFC;
}

div[data-testid="metric-container"]{
    background-color:white;
    border:1px solid #E2E8F0;
    border-radius:15px;
    padding:10px;
}

</style>
""", unsafe_allow_html=True)

st.title("🏆 Sales Championship")

# =====================================
# FUNZIONI
# =====================================

def livello(punti):

    if punti >= 80:
        return "👑 Legend"

    elif punti >= 60:
        return "💎 Platinum"

    elif punti >= 40:
        return "🥇 Gold"

    elif punti >= 20:
        return "🥈 Silver"

    return "🥉 Bronze"


def badge(chiamate, preventivi, ordini):

    badges = []

    if chiamate >= 500:
        badges.append("☎️ Call Machine")

    if preventivi >= 30:
        badges.append("📄 Proposal Master")

    if ordini >= 10:
        badges.append("💰 Deal Closer")

    if not badges:
        return "Nessuno"

    return " | ".join(badges)


def calcola_performance(
    chiamate,
    preventivi,
    ordini
):

    if chiamate <= 0:
        return 0

    return round(
        (
            (
                (preventivi * 1)
                + (ordini * 3)
            )
            / chiamate
        ) * 100,
        2
    )


def bonus_volume(chiamate):

    if chiamate >= 1000:
        return 30

    elif chiamate >= 750:
        return 20

    elif chiamate >= 500:
        return 10

    return 0


def bonus_ordini(ordini):

    if ordini >= 8:
        return 20

    elif ordini >= 5:
        return 10

    elif ordini >= 3:
        return 5

    return 0


# =====================================
# CREAZIONE FILE
# =====================================

if not Path(FILE_DATI).exists():

    df_iniziale = pd.DataFrame({
        "Venditore": VENDITORI,
        "Chiamate": [0, 0, 0, 0],
        "Preventivi": [0, 0, 0, 0],
        "Ordini": [0, 0, 0, 0]
    })

    df_iniziale.to_excel(
        FILE_DATI,
        index=False
    )

if not Path(FILE_HALL_OF_FAME).exists():

    pd.DataFrame(
        columns=[
            "Mese",
            "Vincitrice",
            "Punti"
        ]
    ).to_excel(
        FILE_HALL_OF_FAME,
        index=False
    )

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
# ADMIN
# =====================================

if is_admin:

    st.sidebar.markdown("---")
    st.sidebar.header("📥 Aggiorna Dati")

    venditore = st.sidebar.selectbox(
        "Venditore",
        VENDITORI
    )

    record = df[
        df["Venditore"] == venditore
    ].iloc[0]

    chiamate = st.sidebar.number_input(
        "Chiamate",
        min_value=0,
        value=int(record["Chiamate"])
    )

    preventivi = st.sidebar.number_input(
        "Preventivi",
        min_value=0,
        value=int(record["Preventivi"])
    )

    ordini = st.sidebar.number_input(
        "Ordini",
        min_value=0,
        value=int(record["Ordini"])
    )

    # =====================================
    # SALVA DATI
    # =====================================

    if st.sidebar.button("💾 Salva"):

        df.loc[
            df["Venditore"] == venditore,
            "Chiamate"
        ] = chiamate

        df.loc[
            df["Venditore"] == venditore,
            "Preventivi"
        ] = preventivi

        df.loc[
            df["Venditore"] == venditore,
            "Ordini"
        ] = ordini

        df.to_excel(
            FILE_DATI,
            index=False
        )

        st.sidebar.success(
            "✅ Dati salvati"
        )

        st.rerun()

    # =====================================
    # NUOVO MESE
    # =====================================

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚠️ Gestione Contest")

    conferma_reset = st.sidebar.checkbox(
        "Confermo di voler azzerare il contest"
    )

if st.sidebar.button("🔄 Nuovo Mese"):

    if conferma_reset:

        hall = pd.read_excel(
            FILE_HALL_OF_FAME
        )

        vincitrice = df.iloc[0]

        mese_corrente = datetime.today().strftime(
            "%m/%Y"
        )

        nuovo_record = pd.DataFrame([{
            "Mese": mese_corrente,
            "Vincitrice": vincitrice["Venditore"],
            "Punti": round(
                vincitrice["Punti"],
                1
            )
        }])

        hall = pd.concat(
            [hall, nuovo_record],
            ignore_index=True
        )

        hall.to_excel(
            FILE_HALL_OF_FAME,
            index=False
        )

        df_reset = pd.DataFrame({
            "Venditore": VENDITORI,
            "Chiamate": [0] * len(VENDITORI),
            "Preventivi": [0] * len(VENDITORI),
            "Ordini": [0] * len(VENDITORI)
        })

        df_reset.to_excel(
            FILE_DATI,
            index=False
        )

        st.sidebar.success(
            "✅ Contest archiviato e azzerato"
        )

        st.rerun()

    else:

        st.sidebar.error(
            "⚠️ Seleziona la conferma prima di azzerare il contest"
        )

# =====================================
# CALCOLO PUNTEGGI
# =====================================

df["Performance"] = df.apply(
    lambda x: calcola_performance(
        x["Chiamate"],
        x["Preventivi"],
        x["Ordini"]
    ),
    axis=1
)

df["Bonus Volume"] = df["Chiamate"].apply(
    bonus_volume
)

df["Bonus Ordini"] = df["Ordini"].apply(
    bonus_ordini
)

df["Punti"] = (
    df["Performance"]
    + df["Bonus Volume"]
    + df["Bonus Ordini"]
)

df["Livello"] = df["Punti"].apply(
    livello
)

df["Badge"] = df.apply(
    lambda x: badge(
        x["Chiamate"],
        x["Preventivi"],
        x["Ordini"]
    ),
    axis=1
)

df = df.sort_values(
    "Punti",
    ascending=False
).reset_index(drop=True)

# =====================================
# TARGET TEAM
# =====================================

totale_chiamate = int(df["Chiamate"].sum())

percentuale_target = min(
    totale_chiamate / TARGET_TEAM_CHIAMATE,
    1.0
)

st.subheader("🎯 Target Team")

st.write(
    f"📞 Chiamate effettuate: {totale_chiamate} / {TARGET_TEAM_CHIAMATE}"
)

st.progress(percentuale_target)

# =====================================
# COUNTDOWN
# =====================================

oggi = datetime.today()

ultimo_giorno = monthrange(
    oggi.year,
    oggi.month
)[1]

giorni_mancanti = ultimo_giorno - oggi.day

st.info(
    f"⏳ Mancano {giorni_mancanti} giorni alla fine del contest"
)

# =====================================
# LEADER
# =====================================

leader = df.iloc[0]

st.success(
    f"🔥 Leader del mese: {leader['Venditore']} ({leader['Punti']:.1f} punti)"
)

# =====================================
# PODIO
# =====================================

st.subheader("🏆 Hall of Champions")

col_sx, col_centro, col_dx = st.columns([1, 1.3, 1])

if len(df) >= 2:

    with col_sx:

        st.markdown(
            f"""
### 🥈 {df.iloc[1]['Venditore']}

**{df.iloc[1]['Punti']:.1f} punti**
"""
        )

if len(df) >= 1:

    with col_centro:

        st.success(
            f"👑 {df.iloc[0]['Venditore']} - {df.iloc[0]['Punti']:.1f} punti"
        )

if len(df) >= 3:

    with col_dx:

        st.markdown(
            f"""
### 🥉 {df.iloc[2]['Venditore']}

**{df.iloc[2]['Punti']:.1f} punti**
"""
        )

# =====================================
# QUEENS DEL MESE
# =====================================

st.subheader("👑 Queens del Mese")

c1, c2, c3 = st.columns(3)

with c1:

    call_queen = df.loc[df["Chiamate"].idxmax()]

    st.metric(
        "☎️ Call Queen",
        call_queen["Venditore"],
        f"{int(call_queen['Chiamate'])} chiamate"
    )

with c2:

    deal_queen = df.loc[df["Ordini"].idxmax()]

    st.metric(
        "💰 Deal Queen",
        deal_queen["Venditore"],
        f"{int(deal_queen['Ordini'])} ordini"
    )

with c3:

    conversion_queen = df.loc[
        df["Performance"].idxmax()
    ]

    st.metric(
        "🎯 Conversion Queen",
        conversion_queen["Venditore"],
        f"{conversion_queen['Performance']:.1f}"
    )

# =====================================
# CLASSIFICA
# =====================================

st.subheader("📊 Classifica")

st.dataframe(
    df[
        [
            "Venditore",
            "Chiamate",
            "Preventivi",
            "Ordini",
            "Performance",
            "Bonus Volume",
            "Bonus Ordini",
            "Punti",
            "Livello",
            "Badge"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

# =====================================
# RANKING
# =====================================

st.subheader("🏆 Leaderboard")

for posizione, riga in enumerate(
    df.itertuples(),
    start=1
):

    st.markdown(
        f"""
### #{posizione} - {riga.Venditore}

🏅 {riga.Livello}

⭐ Punti Totali: {riga.Punti:.1f}

🎯 Performance: {riga.Performance:.1f}

🎖️ Badge: {riga.Badge}
"""
    )

    st.progress(
        min(riga.Punti / 100, 1.0)
    )

# =====================================
# GRAFICO
# =====================================

st.subheader("📈 Classifica Grafica")

st.bar_chart(
    df.set_index("Venditore")["Punti"]
)

# =====================================
# HALL OF FAME
# =====================================

st.subheader("🏆 Hall of Fame delle Sales Queen")

hall = pd.read_excel(
    FILE_HALL_OF_FAME
)

if hall.empty:

    st.info(
        "Nessuna vincitrice registrata."
    )

else:

    hall = hall.iloc[::-1]

    for riga in hall.itertuples():

        st.success(
            f"👑 {riga.Mese} • "
            f"{riga.Vincitrice} "
            f"({riga.Punti} punti)"
        )

# =====================================
# DETTAGLIO ADMIN
# =====================================

if is_admin:

    st.subheader("📋 Dati Inseriti")

    st.dataframe(
        df.sort_values("Venditore"),
        use_container_width=True,
        hide_index=True
    )