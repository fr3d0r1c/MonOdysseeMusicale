import streamlit as st
import pandas as pd
import json
import requests
import wikipedia
from datetime import date, datetime, timedelta
from streamlit_calendar import calendar
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="My Music 2026", page_icon="🎵", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    """Charge les données depuis Google Sheets ou initialise via le JSON"""
    try:
        df = conn.read(worksheet="Database", ttl=0)

        if df.empty or len(df) < 10:
            with open("journal_musical_ULTIMATE.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame.from_dict(data, orient='index')
            df.index.name = 'date'
            df = df.reset_index()
            if 'ecoute' not in df.columns: df['ecoute'] = False
            if 'note' not in df.columns: df['note'] = 0 # On met 0 par défaut
            if 'avis' not in df.columns: df['avis'] = ""
            conn.update(worksheet="Database", data=df)
            st.cache_data.clear()
        return df
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
        return pd.DataFrame()
    
def save_data(df):
    conn.update(worksheet="Database", data=df)
    st.cache_data.clear()

@st.cache_data
def get_album_infos(artiste, album):
    """Récupère Cover + Année + Histoire"""
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

df = load_data()

if not df.empty:
    df['ecoute'] = df['ecoute'].fillna(False).astype(bool)
    df['note'] = pd.to_numeric(df['note'], errors='coerce').fillna(0).astype(int)

    st.title("🎹 Mon Odyssée Musicale 2026")

    with st.sidebar:
        st.header("🔮 À venir")
        df_todo = df[df['ecoute'] == False].sort_values('date')
        if len(df_todo) >= 2:
            next_up = df_todo.iloc[1]
            next_infos = get_album_infos(next_up['artiste'], next_up['album'])
            st.image(next_infos['cover'], use_container_width=True)
            st.markdown(f"**{next_up['artiste']}**")
            st.caption(f"{next_up['album']} ({next_up['date']})")
        st.divider()
        nb_ecoutes = df[df['ecoute'] == True].shape[0]
        st.metric("Albums validés", f"{nb_ecoutes} / {len(df)}")

    tab1, tab2, tab3 = st.tabs(["🎧 À l'écoute", "📅 Calendrier", "🏆 Tier List"])

    with tab1:
        st.header("Ton prochain objectif")
        if not df_todo.empty:
            row = df_todo.iloc[0]
            idx = df[df['date'] == row['date']].index[0]
            infos = get_album_infos(row['artiste'], row['album'])

            c1, c2 = st.columns([1, 2])
            with c1:
                st.image(infos["cover"], width=350)
                st.caption(f"📅 Sortie : **{infos['year']}** | Prévu le : **{row['date']}**")
                st.info(f"🏷️ Tag : {row['tag']}")

            with c2:
                st.markdown(f"# {row['artiste']}")
                st.markdown(f"## *{row['album']}*")
                st.caption(f"Genre : {row['genre']} | {infos['copyright']}")
                
                with st.expander("📖 Histoire & Contexte", expanded=True):
                    st.write(infos["summary"])
                    st.markdown(f"[Wiki]({infos['url_wiki']})")

                    st.divider()

                    with st.form("notation_form"):
                        st.write("### 📝 Noter cet album")
                        note_val = st.feedback("stars")
                        avis_val = st.text_area("Ton avis", placeholder="Prod, Flow, Ambiance...")

                        if st.form_submit_button("✅ Valider l'écoute"):
                            df.at[idx, 'ecoute'] = True
                            final_note = (note_val + 1) if note_val is not None else 3
                            df.at[idx, 'note'] = final_note
                            df.at[idx, 'avis'] = avis_val
                            save_data(df)
                            st.balloons()
                            st.success("Enregistré !")
                            st.rerun()
        
        else:
            st.success("🏆 Année terminée !")

    with tab2:
        st.header("📅 Planning 2026")

        events = []
        today_date = date.today()

        for _, r in df.iterrows():
            try:
                date_str = pd.to_datetime(r['date']).strftime("%Y-%m-%d")
            except:
                continue

            if r['ecoute']:
                color, title = "#28a745", f"✅ {r['artiste']}" # Vert
            elif date_str < str(today_date):
                color, title = "#dc3545", f"⚠️ {r['artiste']}" # Rouge
            else:
                color, title = "#6c757d", f"🎵 {r['artiste']}" # Gris

            events.append({
                "title": title, 
                "start": date_str,
                "allDay": True, # Force l'affichage en bandeau journée
                "backgroundColor": color, 
                "borderColor": color
            })

        calendar_options = {
            "initialDate": "2026-01-01",
            "locale": "fr",
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,listWeek"
            },
            "initialView": "dayGridMonth"
        }

        if len(events) > 0:
            calendar(events=events, options=calendar_options, key="my_calendar")
        else:
            st.warning("Aucun événement trouvé. Vérifie ton fichier Google Sheets.")

    with tab3:
        st.header("🏆 Ton Classement & Avis")
        st.caption("Clique sur un album pour relire ton avis ou modifier ta note.")

        df_ranked = df[df['ecoute'] == True]

        if df_ranked.empty:
            st.info("Note tes premiers albums pour remplir le classement !")
        else:
            tiers = [
                (5, "💎 S-TIER (Masterclass)", "🚨"),
                (4, "🔥 A-TIER (Excellent)", "🟠"),
                (3, "✅ B-TIER (Bon)", "🟡"),
                (2, "😐 C-TIER (Moyen)", "🟢"),
                (1, "💩 D-TIER (Déception)", "🟤")
            ]

            for note, label, icon in tiers:
                current_tier = df_ranked[df_ranked['note'] == note]

                if not current_tier.empty:
                    st.divider()
                    st.subheader(f"{icon} {label}")

                    for i, row in current_tier.iterrows():
                        real_idx = df[df['date'] == row['date']].index[0]

                        label_expander = f"{row['artiste']} - {row['album']}"

                        with st.expander(label_expander):
                            infos = get_album_infos(row['artiste'], row['album'])

                            col_img, col_form = st.columns([1, 2])

                            with col_img:
                                st.image(infos['cover'], width=120)
                                st.caption(f"Sortie : {infos['year']}")

                            with col_form:
                                if row['avis']:
                                    st.markdown(f"**Ton avis :**")
                                    st.info(f"_{row['avis']}_")
                                else:
                                    st.write("Pas d'avis rédigé.")

                                st.write("---")

                                with st.form(key=f"edit_form_{real_idx}"):
                                    st.write("✏️ **Modifier**")

                                    new_note = st.slider("Note", 1, 5, int(row['note']), key=f"slider_{real_idx}")

                                    new_avis = st.text_area("Mettre à jour l'avis", value=row['avis'], height=100, key=f"text_{real_idx}")

                                    if st.form_submit_button("💾 Enregistrer les changements"):
                                        df.at[real_idx, 'note'] = new_note
                                        df.at[real_idx, 'avis'] = new_avis
                                        save_data(df)
                                        st.success("Mise à jour effectuée !")
                                        st.rerun()