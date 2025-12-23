import streamlit as st
import pandas as pd
import json
import requests
import wikipedia
from datetime import date, datetime, timedelta
from streamlit_calendar import calendar

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="My Music 2026", page_icon="🎵", layout="wide")

# --- FONCTIONS DE GESTION DES DONNÉES ---
FILE_PATH = "journal_musical_ULTIMATE.json"

def load_data():
    """Charge les données du JSON dans un DataFrame Pandas"""
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame.from_dict(data, orient='index')
        df.index.name = 'date'
        df = df.reset_index()
        return df
    except FileNotFoundError:
        st.error(f"Le fichier {FILE_PATH} n'existe pas. Lance le script 'generateur_json.py' d'abord !")
        return pd.DataFrame()
    
def save_data(df):
    """Sauvegarde les modifications dans le JSON"""
    df_to_save = df.set_index('date').to_dict(orient='index')
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(df_to_save, f, indent=4, ensure_ascii=False)

@st.cache_data 
def get_album_infos(artiste, album):
    """Récupère Cover + Année (iTunes) et Histoire (Wikipédia)"""
    infos = {
        "cover": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/12in-Vinyl-LP-Record-Angle.jpg/640px-12in-Vinyl-LP-Record-Angle.jpg",
        "year": "Année Inconnue",
        "copyright": "",
        "summary": "Pas d'infos Wikipédia trouvées pour cet album.",
        "url_wiki": "#"
    }

    try:
        term = f"{artiste} {album}"
        url = f"https://itunes.apple.com/search?term={term}&entity=album&limit=1"
        res = requests.get(url, timeout=5).json()
        if res['resultCount'] > 0:
            data = res['results'][0]
            infos["cover"] = data['artworkUrl100'].replace("100x100", "600x600")
            infos["year"] = data['releaseDate'][:4]
            infos["copyright"] = data.get('copyright', '')
    except:
        pass

    try:
        wikipedia.set_lang("fr")
        search_query = f"{album} ({artiste})"
        results = wikipedia.search(search_query)
        if results:
            page = wikipedia.page(results[0])
            infos["summary"] = page.summary[:600] + "..."
            infos["url_wiki"] = page.url
    except:
        pass
        
    return infos

# --- INTERFACE UTILISATEUR ---

# 1. Header et Statistiques
st.title("🎹 Mon Odyssée Musicale")
df = load_data()

if not df.empty:
    total_albums = len(df)
    nb_ecoutes = df[df['ecoute'] == True].shape[0]
    progression = nb_ecoutes / total_albums if total_albums > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Albums Écoutés", f"{nb_ecoutes} / {total_albums}")
    col2.metric("Progression", f"{progression:.1%}")
    if nb_ecoutes > 0:
        moyenne = df[df['ecoute'] == True]['note'].mean()
        col3.metric("Note Moyenne", f"{moyenne:.2f}/5 ⭐")

    st.progress(progression)
    st.divider()

    with st.sidebar:
        st.header("🔮 Et juste après...")

        df_a_faire = df[df['ecoute'] == False]

        if len(df_a_faire) >= 2:
            row_next = df_a_faire.iloc[1]

            next_date = row_next['date']
            next_art = row_next['artiste']
            next_alb = row_next['album']
            next_genre = row_next['genre']

            infos_next = get_album_infos(next_art, next_alb)

            st.image(infos_next['cover'], use_container_width=True)
            st.caption(f"📅 Prévu pour le : {next_date}")
            st.markdown(f"**{next_art}**")
            st.write(f"*{next_alb}*")
            st.info(f"{next_genre}")

        elif len(df_a_faire) == 1:
            st.write("C'est le tout dernier album de la liste !")
        else:
            st.write("Liste terminée !")

        st.divider()
        st.write("🌟 **Objectif Ultimate**")

    st.header("🎧 Ton Prochain Objectif")

    df_todo = df[df['ecoute'] == False]

    if not df_todo.empty:
        row_active = df_todo.iloc[0]
        index_active = df_todo.index[0]

        date_prevue = row_active['date']
        artiste = row_active['artiste']
        album = row_active['album']
        genre = row_active['genre']
        tag = row_active['tag']

        infos_album = get_album_infos(artiste, album)

        c1, c2 = st.columns([1, 2])

        with c1:
            st.image(infos_album["cover"], width=350)
            st.caption(f"📅 Sortie : **{infos_album['year']}**")
            st.caption(f"📅 Prévu le : **{date_prevue}**")

            if tag == "INTEGRALE":
                st.warning(f"🔥 **Défi Intégrale**")
            elif "Afro" in tag:
                st.success(f"🌍 **Vibe Afro**")
            else:
                st.info(f"🎧 **{tag}**")

        with c2:
            st.markdown(f"# {artiste}")
            st.markdown(f"## *{album}*")
            st.caption(f"Genre : {genre} | {infos_album['copyright']}")

            with st.expander("📖 **Contexte & Histoire (Wikipédia)**", expanded=True):
                st.write(infos_album["summary"])
                st.markdown(f"[Lire la suite sur Wikipédia]({infos_album['url_wiki']})")
                st.info("💡 Regarde la première phrase pour savoir si c'est une mixtape ou un album studio !")
            
            st.divider()

            with st.form("form_notation"):
                st.write("### 📝 Valider l'écoute")
                note_input = st.feedback("stars")
                new_avis = st.text_area("Ton avis", height=100, placeholder="Qu'est-ce qui t'a marqué ?")
                submitted = st.form_submit_button("✅ J'ai écouté cet album")

                if submitted:
                    final_note = (note_input + 1) if note_input is not None else 3
                    df.at[index_active, 'ecoute'] = True
                    df.at[index_active, 'note'] = final_note
                    df.at[index_active, 'avis'] = new_avis
                    save_data(df)
                    st.balloons()
                    st.success("Bravo ! Album validé.")
                    st.rerun()

    else:
        st.success("🎉 INCROYABLE ! Tu as écouté TOUS les albums de la liste ! Rendez-vous en 2027 ?")

    st.divider()
    st.header("📅 Ton Calendrier")

    events = []
    for index, row in df.iterrows():
        today_str = str(date.today())

        if row['ecoute']:
            color = "#28a745" # Vert
            title = f"✅ {row['artiste']}"
        elif row['date'] < today_str:
            color = "#dc3545" # Rouge
            title = f"⚠️ {row['artiste']}"
        else:
            color = "#6c757d" # Gris
            title = f"🎵 {row['artiste']}"

        event = {
            "title": title,
            "start": row['date'],
            "allDay": True,
            "backgroundColor": color,
            "borderColor": color
        }
        events.append(event)

    calendar_options = {
        "headerToolbar": {"left": "today prev,next", "center": "title", "right": "dayGridMonth,listWeek"},
        "initialDate": "2026-01-01",
        "locale": "fr"
    }

    custom_css = ".fc-event-title { font-size: 0.8rem !important; white-space: normal !important; }"
    calendar(events=events, options=calendar_options, custom_css=custom_css)
    st.caption("Légende : 🟩 Écouté | 🟥 En retard | ⬜ À venir")