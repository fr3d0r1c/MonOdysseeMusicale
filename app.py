import streamlit as st
import pandas as pd
import json
import requests
import wikipedia
import time
from datetime import date, datetime, timedelta
from streamlit_calendar import calendar
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURATION DE LA PAGE & CSS MOBILE ---
st.set_page_config(
    page_title="My Music 2026", 
    page_icon="🎵", 
    layout="wide",
    initial_sidebar_state="collapsed" # Masque la sidebar sur mobile par défaut
)

# CSS pour transformer le site en "App"
st.markdown("""
    <style>
        /* Réduit les marges sur mobile pour gagner de la place */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
        }
        /* Centre les images des pochettes */
        .stImage {
            display: flex;
            justify_content: center;
        }
        /* Force la hauteur du calendrier pour qu'il ne disparaisse pas sur mobile */
        .fc {
            height: 600px !important;
            min-height: 600px !important;
        }
        /* Style des titres */
        h1, h2, h3 {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. GESTION DES DONNÉES ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    """Charge les données et gère le fallback JSON si vide"""
    try:
        df = conn.read(worksheet="Database", ttl=0)
        # Sécurité : Si le sheet est vide, on recharge le JSON de secours
        if df.empty or len(df) < 10:
            with open("journal_musical_ULTIMATE.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame.from_dict(data, orient='index')
            df.index.name = 'date'
            df = df.reset_index()
            # Création des colonnes manquantes
            for col in ['ecoute', 'note', 'avis']:
                if col not in df.columns:
                    df[col] = False if col == 'ecoute' else (0 if col == 'note' else "")
            
            conn.update(worksheet="Database", data=df)
            st.cache_data.clear()
        return df
    except Exception as e:
        st.error(f"Erreur connexion : {e}")
        return pd.DataFrame()

def save_data(df):
    """Sauvegarde silencieuse"""
    conn.update(worksheet="Database", data=df)
    st.cache_data.clear()

@st.cache_data
def get_album_infos(artiste, album):
    """Récupère pochette et année via iTunes API"""
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
            infos["cover"] = data['artworkUrl100'].replace("100x100", "600x600") # Haute qualité
            infos["year"] = data['releaseDate'][:4]
    except: pass
    return infos

# --- 3. INTERFACE UTILISATEUR ---
df = load_data()

if not df.empty:
    # Nettoyage des types
    df['ecoute'] = df['ecoute'].fillna(False).astype(bool)
    df['note'] = pd.to_numeric(df['note'], errors='coerce').fillna(0).astype(int)

    # --- HEADER GAMIFIÉ ---
    nb_ecoutes = df[df['ecoute'] == True].shape[0]
    total = len(df)
    pct = nb_ecoutes / total

    # Titre et barre de progression
    st.title("🎹 Odyssée 2026")
    st.progress(pct)
    st.caption(f"Progression : **{nb_ecoutes}** albums écoutés sur **{total}** ({pct:.1%})")

    # --- NAVIGATION PRINCIPALE ---
    tab1, tab2, tab3 = st.tabs(["🎧 À l'écoute", "📅 Calendrier", "🏆 Tier List"])

    # ==========================================
    # ONGLET 1 : LE PLAYER (Design Mobile First)
    # ==========================================
    with tab1:
        df_todo = df[df['ecoute'] == False].sort_values('date')

        if not df_todo.empty:
            row = df_todo.iloc[0]
            idx = df[df['date'] == row['date']].index[0]
            infos = get_album_infos(row['artiste'], row['album'])

            # 1. La Pochette (Centrale)
            st.image(infos["cover"], width=300)

            # 2. Les Infos
            st.markdown(f"## {row['artiste']}")
            st.markdown(f"#### *{row['album']}* ({infos['year']})")
            st.caption(f"📅 Prévu pour le : {row['date']} | 🏷️ {row['genre']}")

            # 3. Contexte (Replié par défaut pour sauver de la place)
            with st.expander("📖 Lire l'histoire de l'album"):
                try:
                    wikipedia.set_lang("fr")
                    wiki_res = wikipedia.search(f"{row['album']} {row['artiste']}")
                    if wiki_res:
                        page = wikipedia.page(wiki_res[0])
                        st.write(page.summary[:600] + "...")
                        st.markdown(f"[Lire la suite sur Wikipédia]({page.url})")
                    else:
                        st.info("Pas d'article Wikipédia trouvé.")
                except:
                    st.warning("Wikipédia injoignable pour le moment.")

            st.divider()

            # 4. Zone de Notation (Encadrée)
            with st.container(border=True):
                with st.form("notation_form"):
                    st.write("### 📝 Ta critique")

                    # Note en étoiles (Feedback UI)
                    note_val = st.feedback("stars")

                    # Avis textuel
                    avis_val = st.text_area("Ton ressenti", placeholder="Prod, flow, émotion...", height=100)

                    # Bouton Large (Facile à cliquer sur mobile)
                    submit = st.form_submit_button("✅ Valider l'écoute", use_container_width=True)

                    if submit:
                        # Sauvegarde
                        df.at[idx, 'ecoute'] = True
                        df.at[idx, 'note'] = (note_val + 1) if note_val is not None else 3
                        df.at[idx, 'avis'] = avis_val
                        save_data(df)
                        
                        # Feedback utilisateur (Toast + Ballons)
                        st.toast(f"C'est noté ! {row['album']} ajouté à l'historique.", icon="💾")
                        st.balloons()
                        time.sleep(1.5) # Petite pause pour voir l'animation
                        st.rerun()

        else:
            st.success("🏆 INCROYABLE ! Tu as terminé le challenge 2026 !")
            st.balloons()

    # ==========================================
    # ONGLET 2 : CALENDRIER (Hybride PC/Mobile)
    # ==========================================
    with tab2:
        # Toggle discret pour changer de vue
        vue = st.radio("Affichage :", ["📱 Liste", "🖥️ Grille"], horizontal=True, label_visibility="collapsed")

        events = []
        today_str = str(date.today())

        for _, r in df.iterrows():
            try: d_str = pd.to_datetime(r['date']).strftime("%Y-%m-%d")
            except: continue

            if r['ecoute']: color, title = "#28a745", f"✅ {r['artiste']}"
            elif d_str < today_str: color, title = "#dc3545", f"⚠️ {r['artiste']}"
            else: color, title = "#6c757d", f"🎵 {r['artiste']}"

            events.append({"title": title, "start": d_str, "allDay": True, "backgroundColor": color, "borderColor": color})

        # Configuration selon le choix (Liste pour mobile, Grille pour PC)
        mode = "listMonth" if "Liste" in vue else "dayGridMonth"

        calendar(events=events, options={
            "initialDate": "2026-01-01",
            "locale": "fr",
            "headerToolbar": {"left": "prev,next", "center": "title", "right": ""},
            "initialView": mode,
            "height": "600px" # Force la hauteur pour mobile
        }, key=f"cal_{mode}")

    # ==========================================
    # ONGLET 3 : TIER LIST (Editable)
    # ==========================================
    with tab3:
        df_ranked = df[df['ecoute'] == True]

        if df_ranked.empty:
            st.info("Les albums notés apparaîtront ici.")
        else:
            tiers = [(5, "S-TIER", "🚨"), (4, "A-TIER", "🟠"), (3, "B-TIER", "🟡"), (2, "C-TIER", "🟢"), (1, "D-TIER", "🟤")]

            for note, label, icon in tiers:
                sub_df = df_ranked[df_ranked['note'] == note]
                if not sub_df.empty:
                    st.subheader(f"{icon} {label}")
                    for _, row in sub_df.iterrows():
                        real_idx = df[df['date'] == row['date']].index[0]

                        # Expander pour garder la liste propre
                        with st.expander(f"{row['artiste']} - {row['album']}"):
                            c1, c2 = st.columns([1, 2])
                            with c1:
                                inf = get_album_infos(row['artiste'], row['album'])
                                st.image(inf['cover'], width=100)
                            with c2:
                                with st.form(key=f"edit_{real_idx}"):
                                    # Edition de la note et de l'avis
                                    new_n = st.slider("Note", 1, 5, int(row['note']))
                                    new_a = st.text_area("Avis", value=row['avis'])
                                    if st.form_submit_button("💾 Mettre à jour"):
                                        df.at[real_idx, 'note'] = new_n
                                        df.at[real_idx, 'avis'] = new_a
                                        save_data(df)
                                        st.toast("Modification enregistrée !")
                                        st.rerun()