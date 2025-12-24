import streamlit as st
import pandas as pd
import json
import requests
import wikipedia
import time
from datetime import date, datetime, timedelta
from streamlit_calendar import calendar
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURATION & STYLE MOBILE ---
st.set_page_config(
    page_title="My Music 2026", 
    page_icon="🎵", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        /* Mobile : Marges réduites */
        .block-container { padding-top: 1rem !important; padding-bottom: 3rem !important; }
        /* Images centrées */
        .stImage { display: flex; justify_content: center; }
        /* Titres centrés */
        h1, h2, h3, h4 { text-align: center; }
        /* Calendrier Mobile */
        .fc { height: 600px !important; min-height: 600px !important; }
        /* Style des cartes "Next Album" */
        .next-album-card {
            background-color: #262730;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #4F4F4F;
            text-align: center;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. CONNEXION & DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(worksheet="Database", ttl=0)
        if df.empty or len(df) < 10:
            with open("journal_musical_ULTIMATE.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame.from_dict(data, orient='index')
            df.index.name = 'date'
            df = df.reset_index()

            for col in ['ecoute', 'note', 'avis']:
                if col not in df.columns:
                    df[col] = False if col == 'ecoute' else (0 if col == 'note' else "")
            
            conn.update(worksheet="Database", data=df)
            st.cache_data.clear()

        if 'avis' in df.columns:
            df['avis'] = df['avis'].astype(str).replace('nan', '')
            
        return df
    except Exception as e:
        st.error(f"Erreur connexion : {e}")
        return pd.DataFrame()

def save_data(df):
    conn.update(worksheet="Database", data=df)
    st.cache_data.clear()

@st.cache_data
def get_album_infos(artiste, album):
    infos = {
        "cover": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/12in-Vinyl-LP-Record-Angle.jpg/640px-12in-Vinyl-LP-Record-Angle.jpg",
        "year": "",
        "url_wiki": "#"
    }
    try:
        term = f"{artiste} {album}"
        res = requests.get(f"https://itunes.apple.com/search?term={term}&entity=album&limit=1", timeout=3).json()
        if res['resultCount'] > 0:
            data = res['results'][0]
            infos["cover"] = data['artworkUrl100'].replace("100x100", "600x600")
            infos["year"] = data['releaseDate'][:4]
    except: pass
    return infos

# --- 3. APP PRINCIPALE ---
df = load_data()

if not df.empty:
    df['ecoute'] = df['ecoute'].fillna(False).astype(bool)
    df['note'] = pd.to_numeric(df['note'], errors='coerce').fillna(0).astype(int)
    
    # Header Gamifié
    nb_ecoutes = df[df['ecoute'] == True].shape[0]
    total = len(df)
    st.title("🎹 Odyssée 2026")
    st.progress(nb_ecoutes / total)
    st.caption(f"Progression : {nb_ecoutes}/{total} albums")

    # ==========================================
    # SIDEBAR : RECHERCHE RAPIDE (NOUVEAU !)
    # ==========================================
    with st.sidebar:
        st.header("🔍 Rechercher & Noter")
        st.caption("Note un album en avance.")

        # Liste de tous les albums
        all_albums = df.apply(lambda x: f"{x['artiste']} - {x['album']}", axis=1).tolist()

        # Menu déroulant
        choix_search = st.selectbox("Choisir un album", ["-- Sélectionner --"] + all_albums)
        
        if choix_search != "-- Sélectionner --":
            try:
                # On sépare l'artiste et l'album
                search_artiste, search_album = choix_search.split(" - ", 1)

                # On cherche l'index qui correspond À LA FOIS à l'artiste ET à l'album
                mask = (df['artiste'] == search_artiste) & (df['album'] == search_album)

                if mask.any():
                    idx_search = df[mask].index[0] # On récupère le bon index unique
                    row_search = df.loc[idx_search]

                    st.divider()
                    st.write(f"**{row_search['album']}**")

                    # Formulaire de notation
                    with st.form(key=f"search_form_{idx_search}"):
                        # On pré-remplit avec les valeurs existantes s'il y en a
                        val_note = int(row_search['note']) if row_search['note'] > 0 else 5
                        s_note = st.slider("Note", 1, 5, val_note)
                        s_avis = st.text_area("Avis", value=row_search['avis'])

                        if st.form_submit_button("💾 Enregistrer la note"):
                            df.at[idx_search, 'ecoute'] = True
                            df.at[idx_search, 'note'] = s_note
                            df.at[idx_search, 'avis'] = s_avis
                            save_data(df)
                            st.toast(f"C'est bon ! {row_search['album']} a été noté.", icon="✅")
                            time.sleep(1)
                            st.rerun()

                else:
                    st.error("Erreur : Album introuvable dans la base.")
            except Exception as e:
                st.error(f"Erreur de sélection : {e}")


    # Navigation
    tab1, tab2, tab3 = st.tabs(["🎧 À l'écoute", "📅 Calendrier", "🏆 Tier List"])

    # ==========================================
    # ONGLET 1 : L'EXPÉRIENCE D'ÉCOUTE
    # ==========================================
    with tab1:
        # On récupère les albums non écoutés
        df_todo = df[df['ecoute'] == False].sort_values('date')

        if not df_todo.empty:
            # --- L'ALBUM DU JOUR ---
            current = df_todo.iloc[0]
            idx = df[df['date'] == current['date']].index[0]
            infos = get_album_infos(current['artiste'], current['album'])

            st.markdown(f"## {current['artiste']}")
            st.markdown(f"#### *{current['album']}* ({infos['year']})")

            st.image(infos["cover"], width=300)

            # BLOC 1 : CONTEXTE & ANECDOTE
            with st.expander("📖 Histoire & Anecdotes (Wikipédia)", expanded=False):
                try:
                    wikipedia.set_lang("fr")
                    # On cherche la page précise
                    wiki_res = wikipedia.search(f"{current['album']} {current['artiste']}")
                    if wiki_res:
                        page = wikipedia.page(wiki_res[0])
                        st.info("💡 **Le savais-tu ?**")
                        st.write(page.summary[:800] + " [...]")
                        st.markdown(f"👉 [Lire l'article complet]({page.url})")
                    else:
                        st.warning("Pas d'anecdote trouvée pour cet album.")
                except:
                    st.write("Connexion Wikipédia impossible.")

            st.divider()

            with st.container(border=True):
                with st.form("notation_form"):
                    st.write("### 🎙️ Ton verdict")
                    note_val = st.feedback("stars")
                    avis_val = st.text_area("Ta critique", placeholder="Ambiance, production, coup de cœur...", height=100)

                    if st.form_submit_button("✅ Valider et passer au suivant", use_container_width=True):
                        df.at[idx, 'ecoute'] = True
                        df.at[idx, 'note'] = (note_val + 1) if note_val is not None else 3
                        df.at[idx, 'avis'] = avis_val
                        save_data(df)
                        st.toast("Album validé !", icon="🎉")
                        time.sleep(1)
                        st.rerun()

            # BLOC 3 : TEASING (LE PROCHAIN ALBUM)
            if len(df_todo) > 1:
                next_up = df_todo.iloc[1] # Le suivant dans la liste
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="next-album-card">
                    <p style='color: #888; margin:0;'>🔜 PROCHAINEMENT</p>
                    <h3 style='margin:5px 0;'>{next_up['artiste']}</h3>
                    <p style='margin:0;'>{next_up['album']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("🏆 Tu as terminé ton voyage musical !")
            st.balloons()

    # ==========================================
    # ONGLET 2 : CALENDRIER
    # ==========================================
    with tab2:
        vue = st.radio("Vue :", ["Liste 📱", "Grille 🖥️"], horizontal=True, label_visibility="collapsed")

        events = []
        today_str = str(date.today())
        for _, r in df.iterrows():
            try: d_str = pd.to_datetime(r['date']).strftime("%Y-%m-%d")
            except: continue

            if r['ecoute']: color, title = "#28a745", f"✅ {r['artiste']}"
            elif d_str < today_str: color, title = "#dc3545", f"⚠️ {r['artiste']}"
            else: color, title = "#6c757d", f"🎵 {r['artiste']}"
            events.append({"title": title, "start": d_str, "allDay": True, "backgroundColor": color, "borderColor": color})

        mode = "listMonth" if "Liste" in vue else "dayGridMonth"
        calendar(events=events, options={"initialDate": "2026-01-01", "locale": "fr", "headerToolbar": {"left": "prev,next", "center": "title", "right": ""}, "initialView": mode, "height": "600px"}, key=f"cal_{mode}")

    # ==========================================
    # ONGLET 3 : TIER LIST & LÉGENDE
    # ==========================================
    with tab3:
        # LÉGENDE EXPLICATIVE
        with st.expander("ℹ️ Comprendre le classement", expanded=True):
            st.markdown("""
            | Note | Rang | Signification |
            | :---: | :--- | :--- |
            | ⭐⭐⭐⭐⭐ | **S-Tier** | **Masterclass.** Un album qui change la vie. |
            | ⭐⭐⭐⭐ | **A-Tier** | **Excellent.** Très solide, je réécouterai. |
            | ⭐⭐⭐ | **B-Tier** | **Bon.** Un moment sympa, sans plus. |
            | ⭐⭐ | **C-Tier** | **Moyen.** Quelques bons sons, mais ennuyeux. |
            | ⭐ | **D-Tier** | **Déception.** Pas pour moi / À éviter. |
            """)

        st.divider()

        df_ranked = df[df['ecoute'] == True]
        if df_ranked.empty:
            st.info("Ta Tier List est vide pour le moment. Commence à écouter !")
        else:
            tiers = [(5, "S-TIER", "🚨"), (4, "A-TIER", "🟠"), (3, "B-TIER", "🟡"), (2, "C-TIER", "🟢"), (1, "D-TIER", "🟤")]
            for note, label, icon in tiers:
                sub_df = df_ranked[df_ranked['note'] == note]
                if not sub_df.empty:
                    st.subheader(f"{icon} {label}")
                    for _, row in sub_df.iterrows():
                        real_idx = df[df['date'] == row['date']].index[0]
                        with st.expander(f"{row['artiste']} - {row['album']}"):
                            c1, c2 = st.columns([1, 2])
                            with c1:
                                inf = get_album_infos(row['artiste'], row['album'])
                                st.image(inf['cover'], width=100)
                            with c2:
                                with st.form(key=f"edit_{real_idx}"):
                                    new_n = st.slider("Note", 1, 5, int(row['note']))
                                    new_a = st.text_area("Avis", value=row['avis'])
                                    if st.form_submit_button("💾 Mettre à jour"):
                                        df.at[real_idx, 'note'] = new_n
                                        df.at[real_idx, 'avis'] = new_a
                                        save_data(df)
                                        st.rerun()