import streamlit as st
import pandas as pd
import json
import requests
import wikipedia
from datetime import date, datetime, timedelta
from streamlit_calendar import calendar
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="My Music 2026", page_icon="🎵", layout="wide")

# --- CONNEXION BASE DE DONNÉES (GOOGLE SHEETS) ---
# Cette connexion permet de garder en mémoire tes notes sur ton téléphone
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    """
    Tente de charger les données depuis Google Sheets. 
    Si le Sheet est vide, charge le JSON et l'envoie vers le Sheet.
    """
    try:
        # Lecture du Google Sheet
        df = conn.read(worksheet="Database", ttl="0")
        
        # Si le sheet est vide ou n'a pas les bonnes colonnes, on initialise avec le JSON
        if df.empty or "artiste" not in df.columns:
            with open("journal_musical_ULTIMATE.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame.from_dict(data, orient='index')
            df.index.name = 'date'
            df = df.reset_index()
            # Sauvegarde initiale vers Google Sheets
            conn.update(worksheet="Database", data=df)
            st.cache_data.clear()
        return df
    except Exception as e:
        st.error("Erreur de connexion au Google Sheet. Vérifie tes Secrets Streamlit.")
        return pd.DataFrame()

def save_data(df):
    """Sauvegarde les modifications dans Google Sheets"""
    conn.update(worksheet="Database", data=df)
    st.cache_data.clear() # Force Streamlit à relire les nouvelles données

@st.cache_data
def get_album_infos(artiste, album):
    """Récupère Cover + Année (iTunes) et Histoire (Wikipédia)"""
    infos = {
        "cover": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/12in-Vinyl-LP-Record-Angle.jpg/640px-12in-Vinyl-LP-Record-Angle.jpg",
        "year": "Année Inconnue",
        "copyright": "",
        "summary": "Pas d'infos Wikipédia trouvées.",
        "url_wiki": "#"
    }
    try:
        term = f"{artiste} {album}"
        res = requests.get(f"https://itunes.apple.com/search?term={term}&entity=album&limit=1", timeout=5).json()
        if res['resultCount'] > 0:
            data = res['results'][0]
            infos["cover"] = data['artworkUrl100'].replace("100x100", "600x600")
            infos["year"] = data['releaseDate'][:4]
            infos["copyright"] = data.get('copyright', '')
    except: pass
    try:
        wikipedia.set_lang("fr")
        results = wikipedia.search(f"{album} ({artiste})")
        if results:
            page = wikipedia.page(results[0])
            infos["summary"] = page.summary[:600] + "..."
            infos["url_wiki"] = page.url
    except: pass
    return infos

# --- LOGIQUE D'AFFICHAGE ---
st.title("🎹 Mon Odyssée Musicale 2026")
df = load_data()

if not df.empty:
    # On s'assure que la colonne ecoute est bien traitée comme booléen
    df['ecoute'] = df['ecoute'].astype(bool)

    # --- STATISTIQUES ---
    nb_ecoutes = df[df['ecoute'] == True].shape[0]
    total = len(df)
    col1, col2, col3 = st.columns(3)
    col1.metric("Albums Écoutés", f"{nb_ecoutes} / {total}")
    col2.metric("Progression", f"{(nb_ecoutes/total):.1%}")
    if nb_ecoutes > 0:
        moy = df[df['ecoute'] == True]['note'].mean()
        col3.metric("Note Moyenne", f"{moy:.2f}/5 ⭐")

    # --- SIDEBAR : PROCHAINEMENT ---
    with st.sidebar:
        st.header("🔮 Prochainement")
        df_todo = df[df['ecoute'] == False]
        if len(df_todo) >= 2:
            next_up = df_todo.iloc[1]
            st.image(get_album_infos(next_up['artiste'], next_up['album'])['cover'], use_container_width=True)
            st.write(f"**{next_up['artiste']}**")
            st.caption(next_up['album'])
        st.divider()
        st.write("📱 **Mode Mobile Activé**")

    # --- L'ALBUM À ÉCOUTER ---
    st.header("🎧 À écouter maintenant")
    if not df_todo.empty:
        row = df_todo.iloc[0]
        idx = df_todo.index[0]
        infos = get_album_infos(row['artiste'], row['album'])

        c1, c2 = st.columns([1, 2])
        with c1:
            st.image(infos["cover"], width=350)
            st.info(f"📅 Prévu le : {row['date']}")
        with c2:
            st.markdown(f"# {row['artiste']}")
            st.markdown(f"## *{row['album']}*")
            with st.expander("📖 Histoire & Contexte", expanded=True):
                st.write(infos["summary"])
            
            with st.form("notation"):
                note = st.feedback("stars")
                avis = st.text_area("Ton avis")
                if st.form_submit_button("✅ Valider l'étape"):
                    df.at[idx, 'ecoute'] = True
                    df.at[idx, 'note'] = (note + 1) if note is not None else 3
                    df.at[idx, 'avis'] = avis
                    save_data(df)
                    st.balloons()
                    st.rerun()

    # --- CALENDRIER ---
    st.divider()
    events = []
    for i, r in df.iterrows():
        color = "#28a745" if r['ecoute'] else ("#dc3545" if str(r['date']) < str(date.today()) else "#6c757d")
        events.append({"title": r['artiste'], "start": str(r['date']), "backgroundColor": color, "borderColor": color})
    
    calendar(events=events, options={"initialDate": "2026-01-01", "locale": "fr"})