import streamlit as st
import pandas as pd
import json
import requests
import wikipedia
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import date, datetime
from streamlit_calendar import calendar
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. CONFIGURATION & CLÉS API
# ==========================================
st.set_page_config(page_title="My Music 2026", page_icon="🎵", layout="wide", initial_sidebar_state="collapsed")

# 🔴 METS TES CLÉS SPOTIFY ICI
SPOTIFY_CLIENT_ID = "c77eed1362374a16894808dab3b0a1a1"
SPOTIFY_CLIENT_SECRET = "af4297e71fb44875ab939ef9311c48fa"

auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager, retries=0, status_retries=0)

# ==========================================
# 2. DESIGN & DICTIONNAIRES
# ==========================================
st.markdown("""
    <style>
        .stApp { background-color: #0E1117; }
        .block-container { padding-top: 1rem !important; padding-bottom: 3rem !important; }
        h1 { background: linear-gradient(to right, #FF8200, #FFFFFF, #0055A4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800 !important; text-align: center; margin-bottom: 0px; }
        h2, h3, h4 { color: #F0F2F6; text-align: center; }
        .next-album-card { background: linear-gradient(145deg, #1E1E1E, #25262B); padding: 20px; border-radius: 15px; text-align: center; margin-top: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); border-left: 5px solid #009A44; border-right: 5px solid #EF4135; border-top: 1px solid #333; border-bottom: 1px solid #333; transition: transform 0.3s; }
        .next-album-card:hover { transform: translateY(-5px); }
        .next-album-cover { width: 120px; border-radius: 8px; margin: 15px auto; display: block; border: 2px solid #FF8200; box-shadow: 0 5px 15px rgba(0,0,0,0.5); }
        div.stButton > button { background: linear-gradient(90deg, #FF8200 0%, #EF4135 100%); color: white; border: none; font-weight: bold; width: 100%; border-radius: 8px; height: 50px; }
        div.stButton > button:hover { box-shadow: 0 0 15px rgba(255, 130, 0, 0.4); color: white; }
        .stProgress > div > div > div > div { background-color: #FF8200; }
        .badge-status { font-size: 0.8em; padding: 2px 8px; border-radius: 12px; font-weight: bold; }
        .badge-alert { background-color: #dc3545; color: white; padding: 4px 10px; border-radius: 8px; font-weight: bold; font-size: 0.9em; }
    </style>
""", unsafe_allow_html=True)

DRAPEAUX = {
    # 🇺🇸 ÉTATS-UNIS
    "Kendrick Lamar": "🇺🇸", "JID": "🇺🇸", "Kanye West": "🇺🇸", "Ariana Grande": "🇺🇸",
    "Doja cat": "🇺🇸", "Lauryn Hill": "🇺🇸", "Biggie": "🇺🇸", "Notorious B.I.G.": "🇺🇸",
    "Nas": "🇺🇸", "Tupac": "🇺🇸", "Travis Scott": "🇺🇸", "Mac Miller": "🇺🇸",
    "Asap Rocky": "🇺🇸", "A$AP Rocky": "🇺🇸", "Denzel Curry": "🇺🇸", "J. Cole": "🇺🇸",
    "Taylor Swift": "🇺🇸", "Jay-Z": "🇺🇸", "Prince": "🇺🇸", "Beyoncé": "🇺🇸",
    "Billie Eilish": "🇺🇸", "Tyler, The Creator": "🇺🇸", "Michael Jackson": "🇺🇸",
    "Freddie Gibbs": "🇺🇸", "SZA": "🇺🇸", "Aretha Franklin": "🇺🇸", "De La Soul": "🇺🇸",
    "Frank Ocean": "🇺🇸", "The Doors": "🇺🇸", "OutKast": "🇺🇸", "Clipse": "🇺🇸",
    "Dr. Dre": "🇺🇸", "Stevie Wonder": "🇺🇸", "Nirvana": "🇺🇸", "Marvin Gaye": "🇺🇸",
    "Etta James": "🇺🇸", "Miles Davis": "🇺🇸", "Snoop Dogg": "🇺🇸", "Tracy Chapman": "🇺🇸",
    "Playboi Carti": "🇺🇸", "Jimi Hendrix": "🇺🇸", "Mobb Deep": "🇺🇸", "Wu-Tang Clan": "🇺🇸",
    "D'angelo": "🇺🇸",

    # 🇫🇷 FRANCE / 🇧🇪 BELGIQUE
    "Daft Punk": "🇫🇷", "Booba": "🇫🇷", "Kaaris": "🇫🇷", "Lunatic": "🇫🇷", "Laylow": "🇫🇷",
    "PNL": "🇫🇷", "Nekfeu": "🇫🇷", "Alpha Wann": "🇫🇷", "SCH": "🇫🇷", "Justice": "🇫🇷",
    "La Fève": "🇫🇷", "Damso": "🇧🇪", "Hamza": "🇧🇪",

    # 🇬🇧 ROYAUME-UNI / 🇮🇪 IRLANDE
    "Pink Floyd": "🇬🇧", "The Beatles": "🇬🇧", "The Bee Gees": "🇬🇧", "Queen": "🇬🇧",
    "Radiohead": "🇬🇧", "Amy Winehouse": "🇬🇧", "The Smiths": "🇬🇧", "Fleetwood Mac": "🇬🇧",
    "Joy Division": "🇬🇧", "Portishead": "🇬🇧", "Sade": "🇬🇧", "Massive Attack": "🇬🇧",
    "Gorillaz": "🇬🇧", "Led Zeppelin": "🇬🇧", "David Bowie": "🇬🇧",

    # 🇨🇦 CANADA
    "The Weeknd": "🇨🇦", "Drake": "🇨🇦",

    # 🌍 AFRO / CARAÏBES / LATINO / RESTE DU MONDE
    "Burna Boy": "🇳🇬", "Rema": "🇳🇬", "Wizkid": "🇳🇬", "Asake": "🇳🇬", "Tems": "🇳🇬", 
    "Omah Lay": "🇳🇬", "Davido": "🇳🇬", "Fireboy DML": "🇳🇬", "Fela Kuti": "🇳🇬",
    "Tyla": "🇿🇦", "Miriam Makeba": "🇿🇦", "Uncle Waffles": "🇿🇦",
    "Magic System": "🇨🇮", "Ali Farka Touré": "🇲🇱", "Salif Keita": "🇲🇱",
    "Koffi Olomidé": "🇨🇩", "Fally Ipupa": "🇨🇩", "Franco": "🇨🇩",
    "Youssou N'Dour": "🇸🇳", "Orchestra Baobab": "🇸🇳",
    "Manu Dibango": "🇨🇲", "Angelique Kidjo": "🇧🇯", "Amaarae": "🇬🇭",
    "Cesária Évora": "🇨🇻", "Rihanna": "🇧🇧", "Bob Marley": "🇯🇲",
    "Kali Uchis": "🇨🇴", "Bad Bunny": "🇵🇷", "Tame Impala": "🇦🇺"
}

def auto_assigner_drapeau(artiste, pays_actuel):
    if pays_actuel != "🌍" and pays_actuel != "" and str(pays_actuel) != "nan": return pays_actuel
    for nom, drapeau in DRAPEAUX.items():
        if nom.lower() in str(artiste).lower(): return drapeau
    return "🌍"

# ==========================================
# 3. GESTION DES DONNÉES & API SPOTIFY
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(show_spinner=False, ttl=86400)
def get_album_infos(artiste, album):
    """Interroge Spotify uniquement si l'image n'est pas déjà dans le GSheet."""
    exceptions = {
        "SZA Z": {"cover": "https://s1.qwant.com/thumbr/474x474/3/f/7c5800a088894e92b8b2495bd952ed946ffe16a6ec17b2492dd7e4c7e0281f/OIP.IbApnBFqvx_z3SMX5CZ59AHaHa.jpg?u=https%3A%2F%2Ftse.mm.bing.net%2Fth%2Fid%2FOIP.IbApnBFqvx_z3SMX5CZ59AHaHa%3Fpid%3DApi&q=0&b=1&p=0&a=0", "year": "2014"},
        "Lunatic Mauvais Oeil": {"cover": "https://s1.qwant.com/thumbr/474x474/9/d/90a015b95874dec8271f6ac9f3d052c109d8c8c2bd06399388e3fc62cfa316/OIP.mec-8rKWmdDgRr8afO3l2QHaHa.jpg?u=https%3A%2F%2Ftse.mm.bing.net%2Fth%2Fid%2FOIP.mec-8rKWmdDgRr8afO3l2QHaHa%3Fr%3D0%26pid%3DApi&q=0&b=1&p=0&a=0", "year": "2000"},
        "The Doors The Doors": {"cover": "https://upload.wikimedia.org/wikipedia/en/9/98/TheDoorsTheDoorsalbumcover.jpg", "year": "1967"}
    }
    
    requete = f"{artiste} {album}"
    for cle, valeurs in exceptions.items():
        if cle.lower() in requete.lower(): return valeurs

    infos = {"cover": "https://placehold.co/600x600/1E1E1E/FF8200?text=Cover+Introuvable", "year": ""}
    try:
        time.sleep(0.4) # Sécurité anti-spam
        res = sp.search(q=requete, type='album', limit=1)
        if res['albums']['items']:
            item = res['albums']['items'][0]
            if item['images']: infos["cover"] = item['images'][0]['url']
            if item['release_date']: infos["year"] = item['release_date'][:4]
    except: pass 
    return infos

def load_data():
    try:
        df = conn.read(worksheet="Database", ttl=0)
        
        # 🔴 NOUVELLES COLONNES : cover_url et annee
        expected_cols = {
            'ecoute': False, 'note': 0, 'avis': "", 'deja_connu': False, 'pays': "🌍",
            'cover_url': "", 'annee': ""
        }
        updated = False
        for col, default_val in expected_cols.items():
            if col not in df.columns:
                df[col] = default_val
                updated = True
        
        df['ecoute'] = df['ecoute'].fillna(False).infer_objects(copy=False).astype(bool)
        df['deja_connu'] = df['deja_connu'].fillna(False).infer_objects(copy=False).astype(bool)
        df['note'] = pd.to_numeric(df['note'], errors='coerce').fillna(0).astype(int)
        
        if 'avis' in df.columns: df['avis'] = df['avis'].astype(str).replace('nan', '')
        if 'cover_url' in df.columns: df['cover_url'] = df['cover_url'].astype(str).replace('nan', '')
        if 'annee' in df.columns: df['annee'] = df['annee'].astype(str).replace('nan', '')
            
        if 'pays' in df.columns:
            df['pays'] = df['pays'].astype(str).replace('nan', '🌍')
            nouveaux_pays = df.apply(lambda row: auto_assigner_drapeau(row['artiste'], row['pays']), axis=1)
            if not df['pays'].equals(nouveaux_pays):
                df['pays'] = nouveaux_pays
                updated = True

        if updated:
            conn.update(worksheet="Database", data=df)
            st.cache_data.clear()
        return df
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
        return pd.DataFrame()

def save_data(df):
    conn.update(worksheet="Database", data=df)
    st.cache_data.clear()

# ==========================================
# 4. LE MOTEUR DE L'APPLICATION
# ==========================================
df = load_data()

if not df.empty:
    
    # 🔴 LE BATCH DE SYNCHRONISATION (La Magie opère ici)
    
    # --- KPI & HEADER ---
    nb_valide = df[df['ecoute'] == True].shape[0]
    total = len(df)
    today_iso = str(date.today())
    df_retard = df[(df['ecoute'] == False) & (df['date'] < today_iso)]
    nb_retard = len(df_retard)
    
    st.title("🎹 Odyssée Musicale 2026")
    st.progress(nb_valide / total if total > 0 else 0)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏆 Global", f"{int((nb_valide/total)*100)}%" if total > 0 else "0%")
    c2.metric("🟢 Découvertes", df[(df['ecoute'] == True) & (df['deja_connu'] == False)].shape[0])
    c3.metric("🔵 Classiques", df[(df['ecoute'] == True) & (df['deja_connu'] == True)].shape[0])
    if nb_retard > 0: c4.metric("⚠️ Retard", f"{nb_retard} albums", delta=f"-{nb_retard}", delta_color="inverse")
    else: c4.metric("🔥 Retard", "0", delta="À jour !", delta_color="normal")

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("🔍 Édition Rapide")
        options_dict = {f"{r['pays']} {r['artiste']} - {r['album']}": i for i, r in df.iterrows()}
        choix = st.selectbox("Choisir un album", ["-- Sélectionner --"] + list(options_dict.keys()))
        
        if choix != "-- Sélectionner --":
            idx_sel = options_dict[choix]
            row_sel = df.loc[idx_sel]
            st.divider()
            st.image(row_sel['cover_url'], width=150)
            
            # --- 👑 LOGIQUE DU GOAT POUR LA SIDEBAR ---
            mois_sel = pd.to_datetime(row_sel['date']).month
            annee_sel = pd.to_datetime(row_sel['date']).year

            # Chercher un GOAT ce mois-ci, SAUF si c'est l'album qu'on est en train de modifier
            mask_goat_sb = (df['ecoute'] == True) & (df['note'] == 6) & (pd.to_datetime(df['date']).dt.month == mois_sel) & (pd.to_datetime(df['date']).dt.year == annee_sel) & (df.index != idx_sel)
            goat_sb_pris = not df[mask_goat_sb].empty

            note_max_sb = 5 if goat_sb_pris else 6
            note_actuelle = int(row_sel['note']) if row_sel['note'] > 0 else 5
            note_actuelle = min(note_actuelle, note_max_sb) # Sécurité

            with st.form(f"sidebar_form_{idx_sel}"):
                if goat_sb_pris:
                    st.caption("🔒 La place du GOAT de ce mois est déjà occupée !")

                s_note = st.slider("Note", 1, note_max_sb, note_actuelle)
                s_avis = st.text_area("Avis", value=row_sel['avis'])
                s_connu = st.checkbox("Déjà connu", value=row_sel['deja_connu'])
                s_pays = st.text_input("Drapeau", value=row_sel['pays'])

                if st.form_submit_button("💾 Enregistrer"):
                    df.at[idx_sel, 'ecoute'], df.at[idx_sel, 'note'], df.at[idx_sel, 'avis'], df.at[idx_sel, 'deja_connu'], df.at[idx_sel, 'pays'] = True, s_note, s_avis, s_connu, s_pays
                    save_data(df)
                    st.rerun()
                    
        st.divider()
        with st.expander("⚙️ Outils d'Administration"):
            st.caption("Télécharge les covers manquantes depuis Spotify.")
            if st.button("🔄 Lancer l'aspirateur Spotify"):
                # On cible les vides ET les fausses covers
                mask = (df['cover_url'] == "") | (df['cover_url'].str.contains("placehold.co"))
                nb_a_faire = mask.sum()

                if nb_a_faire > 0:
                    barre = st.progress(0)
                    for i, idx in enumerate(df[mask].index):
                        infos = get_album_infos(df.at[idx, 'artiste'], df.at[idx, 'album'])
                        df.at[idx, 'cover_url'] = infos['cover']
                        df.at[idx, 'annee'] = infos['year']
                        barre.progress((i + 1) / nb_a_faire)

                    save_data(df)
                    st.success(f"✅ {nb_a_faire} pochettes mises à jour !")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.info("Toutes les pochettes sont déjà à jour !")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🎧 À l'écoute", "📊 Stats & Rattrapage", "📅 Calendrier", "🏆 Découvertes", "🔄 Classiques", "🎁 Wrapped"])

    # --- 🎯 DÉFINITION DE L'ALBUM DU JOUR (LOGIQUE SMART) ---
    today_iso = date.today().isoformat()
    df_today = df[df['date'] == today_iso]

    current = None
    real_idx = None
    mission_accomplie = False

    if not df_today.empty:
        row_today = df_today.iloc[0]
        if row_today['ecoute'] == False:
            # 1. On a un album aujourd'hui et il n'est pas fait
            real_idx = df_today.index[0]
            current = df.loc[real_idx]
        else:
            # 2. L'album du jour est FAIT. Est-ce qu'il reste du retard ?
            df_retard = df[(df['date'] < today_iso) & (df['ecoute'] == False)]
            if not df_retard.empty:
                real_idx = df_retard.index[0]
                current = df.loc[real_idx]
            else:
                # 3. Tout est fini pour aujourd'hui !
                mission_accomplie = True
    else:
        # Pas d'album prévu aujourd'hui, on check quand même le retard
        df_retard = df[(df['date'] < today_iso) & (df['ecoute'] == False)]
        if not df_retard.empty:
            real_idx = df_retard.index[0]
            current = df.loc[real_idx]
        else:
            mission_accomplie = True

    # --- TAB 1 : LE PLAYER ---
    with tab1:
        # --- 🎨 STYLE CSS POUR LE GLOW DE LA POCHETTE ---
        st.markdown("""
            <style>
                .cover-glow {
                    box-shadow: 0 0 25px rgba(255, 130, 0, 0.3);
                    border-radius: 15px;
                    transition: transform 0.3s ease;
                }
                .cover-glow:hover {
                    transform: scale(1.02);
                    box-shadow: 0 0 35px rgba(255, 130, 0, 0.5);
                }
            </style>
        """, unsafe_allow_html=True)

        if mission_accomplie:
            st.write("")
            st.write("")
            st.markdown(f"""
                <div style="text-align: center; padding: 40px; border-radius: 20px; background-color: rgba(0, 154, 68, 0.1); border: 2px solid #009A44;">
                    <h1 style="font-size: 4em; margin-bottom: 20px;">🌅</h1>
                    <h2 style="color: white;">Mission accomplie pour aujourd'hui !</h2>
                    <p style="font-size: 1.3em; color: #FF8200; font-weight: bold;">
                        Pas d'album à écouter, revenez demain pour continuer votre voyage musical.
                    </p>
                    <p style="color: gray;">Profite de tes découvertes précédentes en attendant !</p>
                </div>
            """, unsafe_allow_html=True)
            st.balloons() # Optionnel : une petite fête à chaque fois que tu ouvres l'app et que c'est fini
        else:
            # --- 🌟 HEADER DYNAMIQUE ---
            st.markdown(f"<h2 style='text-align:center; color:#FF8200;'>🎧 Aujourd'hui : {current['album']}</h2>", unsafe_allow_html=True)
            
            c_img, c_details = st.columns([1.2, 2])
            
            with c_img:
                # Affichage de la pochette avec le style "Glow"
                cover_url = current.get('cover_url', 'https://placehold.co/600x600/1E1E1E/FF8200?text=Musique')
                st.markdown(f'<div class="cover-glow"><img src="{cover_url}" width="100%" style="border-radius:15px;"></div>', unsafe_allow_html=True)
                
                # --- 🔊 PLAYER EMBARQUÉ (GOAT FEATURE) ---
                # On essaie de récupérer l'ID de l'album sur Spotify pour l'embed
                try:
                    search_res = sp.search(q=f"album:{current['album']} artist:{current['artiste']}", type='album', limit=1)
                    if search_res['albums']['items']:
                        album_id = search_res['albums']['items'][0]['id']
                        st.write("")
                        st.markdown(f'<iframe src="https://open.spotify.com/embed/album/{album_id}" width="100%" height="152" frameborder="0" allowtransparency="true" allow="encrypted-media" style="border-radius:12px;"></iframe>', unsafe_allow_html=True)
                except:
                    st.caption("Lecteur Spotify indisponible")

            with c_details:
                # Infos Principales
                st.markdown(f"<h1 style='margin-bottom:0px;'>{current.get('album', 'Inconnu')}</h1>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='color:#FF8200; margin-top:0px;'>{current.get('artiste', 'Inconnu')}</h3>", unsafe_allow_html=True)
                
                # Badges sécurisés
                try: annee_val = str(int(float(current['annee'])))
                except: annee_val = "N/A"

                genre_val = current.get('genre', 'Inconnu')
                pays_val = current.get('pays', '')
                type_val = current.get('type', 'Standard')
                
                st.markdown(f"🗓️ **{annee_val}** | 🎵 **{genre_val}** | 🌍 **{pays_val}**")
                st.markdown(f"📌 *Type d'écoute : {type_val}*")
                
                st.divider()

                # --- 📚 LE SAVIEZ-VOUS ? (WIKIPEDIA CONTEXT) ---
                with st.expander("📖 Un peu de culture (Wikipedia)", expanded=True):
                    try:
                        # On cherche le résumé de l'album
                        wiki_summary = wikipedia.summary(f"Album {current.get('album', '')} {current.get('artiste', '')}", sentences=3, lang="fr")
                        st.write(wiki_summary)
                    except:
                        st.write("Pas d'anecdote trouvée pour cet album, concentre-toi sur la musique !")

            # --- 👑 LOGIQUE DU TRÔNE (GOAT DU MOIS) ---
            st.write("")
            mois_actuel = pd.to_datetime(current['date']).month
            annee_actuelle = pd.to_datetime(current['date']).year
            mask_goat = (df['ecoute'] == True) & (df['note'] == 6) & (pd.to_datetime(df['date']).dt.month == mois_actuel) & (pd.to_datetime(df['date']).dt.year == annee_actuelle)
            df_goat = df[mask_goat]
            
            if not df_goat.empty:
                roi = df_goat.iloc[0]
                st.markdown(f"""
                    <div style="background-color: rgba(255, 130, 0, 0.1); border: 1px solid #FF8200; padding: 15px; border-radius: 10px; text-align: center;">
                        🔒 <b>Le trône de Mai est pris !</b><br>
                        Le GOAT actuel est <b>{roi['artiste']}</b>. Rétrograde-le pour libérer la place.
                    </div>
                """, unsafe_allow_html=True)
                note_max = 5
            else:
                st.markdown("""
                    <div style="background-color: rgba(0, 154, 68, 0.1); border: 1px solid #009A44; padding: 15px; border-radius: 10px; text-align: center;">
                        👑 <b>La place de GOAT est libre !</b><br>
                        Est-ce que cet album va gâter le coin aujourd'hui ?
                    </div>
                """, unsafe_allow_html=True)
                note_max = 6

            # --- 🎙️ FORMULAIRE DE VERDICT ---
            with st.form("verdict_final"):
                c_n, c_p = st.columns([2, 1])
                with c_n: 
                    v_note = st.slider("Ta Note (6 = GOAT 🐐)", 1, note_max, 4)
                with c_p:
                    v_pays = st.text_input("Drapeau", value=current['pays'])
                
                v_avis = st.text_area("Ton avis (Nouchi autorisé !)", placeholder="Alors, ça dit quoi ?")
                v_connu = st.checkbox("Je connaissais déjà (Classique)", value=current['deja_connu'])
                
                if st.form_submit_button("✅ VALIDER L'ÉCOUTE", use_container_width=True):
                    df.at[real_idx, 'ecoute'], df.at[real_idx, 'note'], df.at[real_idx, 'avis'], df.at[real_idx, 'deja_connu'], df.at[real_idx, 'pays'] = True, v_note, v_avis, v_connu, v_pays
                    save_data(df)
                    st.balloons()
                    time.sleep(1)
                    st.rerun()

    # --- TAB 2 : STATS & RATTRAPAGE ---
    with tab2:
        st.markdown("<h2 style='text-align:center;'>📊 Le Bilan & 🚨 Rattrapage</h2>", unsafe_allow_html=True)

        df_ecoutes = df[df['ecoute'] == True].copy()

        # --- 🏆 PARTIE 1 : LES STATS CLÉS (KPIs) ---
        if not df_ecoutes.empty:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("💿 Écoutés", f"{len(df_ecoutes)} / 365")
            c2.metric("⭐ Moyenne", f"{round(df_ecoutes['note'].mean(), 2)} / 6")
            
            nb_decouvertes = len(df_ecoutes[df_ecoutes['deja_connu'] == False])
            c3.metric("🟢 Découvertes", nb_decouvertes)
            
            nb_pays = df_ecoutes['pays'].nunique()
            c4.metric("🌍 Pays explorés", nb_pays)
            st.divider()

        # --- 🚨 PARTIE 2 : LE RATTRAPAGE INTELLIGENT ---
        st.subheader("🚨 Zone de Rattrapage (Y a drap ?)")
        # On calcule si tu as raté des jours par rapport à la date d'aujourd'hui
        df['dt_obj'] = pd.to_datetime(df['date'], errors='coerce')
        today = pd.Timestamp.today().normalize()

        # Un album est en retard si sa date est passée ET qu'il n'est pas écouté
        df_retard = df[(df['dt_obj'] < today) & (df['ecoute'] == False)].copy()

        if df_retard.empty:
            st.success("🎉 Tu es parfaitement à jour ! Aucun album en retard, tu gères le programme comme un pro !")
        else:
            st.warning(f"⚠️ Aïe ! Tu as **{len(df_retard)} album(s)** en retard. Faut pas blaguer avec l'odyssée !")
            # On affiche un joli tableau épuré avec juste l'essentiel
            st.dataframe(
                df_retard[['date', 'artiste', 'album', 'genre', 'pays']], 
                use_container_width=True, 
                hide_index=True
            )

        st.divider()

        # --- 📈 PARTIE 3 : LES GRAPHIQUES D'ANALYSE ---
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🎵 Tes Genres Musicaux")
            if not df_ecoutes.empty and 'genre' in df_ecoutes.columns:
                # On prend les 7 genres les plus écoutés
                genre_counts = df_ecoutes['genre'].value_counts().head(7)
                st.bar_chart(genre_counts, color="#FF8200")
            else:
                st.info("Pas encore assez de données.")

            st.subheader("⭐ Répartition des Notes")
            if not df_ecoutes.empty:
                st.bar_chart(df_ecoutes['note'].value_counts().sort_index(), color="#009A44")

        with col2:
            st.subheader("👑 Artistes Favoris (Moyenne)")
            if not df_ecoutes.empty:
                # --- NOUVELLE LOGIQUE ULTRA-PRÉCISE ---
                total_counts = df['artiste'].value_counts() # Combien d'albums prévus au total
                listened_counts = df_ecoutes['artiste'].value_counts() # Combien d'albums déjà écoutés

                artistes_valides = []
                for artiste, c_listened in listened_counts.items():
                    c_total = total_counts.get(artiste, 0)
                    # Condition : Au moins 3 écoutes OU 100% des albums prévus pour cet artiste ont été écoutés
                    if c_listened >= 3 or c_listened == c_total:
                        artistes_valides.append(artiste)

                df_filtre = df_ecoutes[df_ecoutes['artiste'].isin(artistes_valides)]

                if not df_filtre.empty:
                    top_artistes = df_filtre.groupby('artiste')['note'].mean().sort_values(ascending=False).head(5)
                    st.bar_chart(top_artistes, color="#9c27b0")
                else:
                    st.info("Aucun artiste ne remplit les critères (3 albums écoutés, ou 100% de sa disco prévue terminée).")

            st.subheader("⏳ Voyage dans le Temps")
            if not df_ecoutes.empty:
                df_ecoutes['annee_propre'] = pd.to_numeric(df_ecoutes['annee'], errors='coerce').fillna(0).astype(int)
                df_annees = df_ecoutes[df_ecoutes['annee_propre'] > 1900].copy()
                if not df_annees.empty:
                    # On groupe par décennie (ex: 1990, 2000)
                    df_annees['decennie'] = (df_annees['annee_propre'] // 10) * 10
                    decennies_counts = df_annees['decennie'].value_counts().sort_index()
                    decennies_counts.index = decennies_counts.index.astype(str) + "s"
                    st.bar_chart(decennies_counts, color="#17a2b8")

    # --- TAB 3 : CALENDRIER & GALERIE ---
    with tab3:
        view_mode = st.radio("Vue :", ["Liste 📱", "Grille 🖥️", "Galerie 🖼️"], horizontal=True, label_visibility="collapsed")
        if view_mode == "Galerie 🖼️":
            df['dt_obj'] = pd.to_datetime(df['date'])
            for month_num in range(1, 13):
                df_month = df[df['dt_obj'].dt.month == month_num]
                if not df_month.empty:
                    month_name = df_month.iloc[0]['dt_obj'].strftime('%B %Y').capitalize()
                    with st.expander(f"📅 {month_name}", expanded=(month_num == date.today().month)):
                        cols = st.columns(4)
                        for i, (_, row) in enumerate(df_month.iterrows()):
                            with cols[i % 4]:
                                with st.container(border=True):
                                    st.image(row['cover_url'], width='stretch')
                                    st.markdown(f"**{row['pays']} {row['artiste']}**")
                                    if row['ecoute']:
                                        if row['deja_connu']: st.markdown("<span class='badge-status' style='background:#17a2b8; color:white'>Classique</span>", unsafe_allow_html=True)
                                        else: st.markdown("<span class='badge-status' style='background:#28a745; color:white'>Découverte</span>", unsafe_allow_html=True)
                                    else: st.caption(f"📅 {row['date']}")
        else:
            events = []
            for _, r in df.iterrows():
                evt_title = f"{r['pays']} {r['artiste']}"
                if r['ecoute']: color, title = ("#17a2b8", f"🔄 {evt_title}") if r['deja_connu'] else ("#28a745", f"✅ {evt_title}")
                elif str(r['date']) < today_iso: color, title = "#dc3545", f"⚠️ {evt_title}"
                else: color, title = "#6c757d", f"🎵 {evt_title}"
                events.append({"title": title, "start": str(r['date']), "allDay": True, "backgroundColor": color, "borderColor": color})
            cal_mode = "listMonth" if "Liste" in view_mode else "dayGridMonth"
            calendar(events=events, options={"initialDate": "2026-01-01", "locale": "fr", "headerToolbar": {"left": "prev,next", "center": "title", "right": ""}, "initialView": cal_mode, "height": "600px"}, key=f"cal_{view_mode}")

    # --- TAB 4 & 5 : TIER LISTS ---
    def render_tier_list(df_filtre, tiers, is_blue=False):
        if df_filtre.empty: st.info("Rien à afficher pour l'instant.")
        for note, label, icon in tiers:
            sub_df = df_filtre[df_filtre['note'] == note]
            if not sub_df.empty:
                st.markdown(f"### {icon} {label}")
                cols = st.columns(5)
                for i, (_, row) in enumerate(sub_df.iterrows()):
                    r_idx = df[df['date'] == row['date']].index[0]
                    with cols[i % 5]:
                        st.image(row['cover_url'], width='stretch')
                        st.markdown(f"<div style='text-align:center; font-size:0.9em; margin-bottom:5px;'><b>{row['artiste']}</b><br><i>{row['album']}</i></div>", unsafe_allow_html=True)
                        with st.expander("📝 Action"):
                            if st.button("Passer en " + ("'Découverte'" if is_blue else "'Classique'"), key=f"btn_{'g' if is_blue else 'b'}_{r_idx}"):
                                df.at[r_idx, 'deja_connu'] = not is_blue
                                save_data(df)
                                st.rerun()
                st.divider()

    with tab4:
        st.caption("🟢 Les Nouveautés : Tes découvertes évaluées sans pitié.")
        render_tier_list(df[(df['ecoute'] == True) & (df['deja_connu'] == False)], [
            (6, "GOAT-TIER (Il a gâté le coin, Maîtrise totale)", "🐐"),
            (5, "S-TIER (Gros Boucan, L'enjaillement est versé)", "🌟"), 
            (4, "A-TIER (Le goût de ça, C'est trop kpata)", "🔥"), 
            (3, "B-TIER (Y a pas drap, On gère tranquille)", "😌"), 
            (2, "C-TIER (Yako pour mes tympans, C'est un peu scié)", "😬"), 
            (1, "D-TIER (Pure Foutaise, Vrai goumin musical)", "🗑️")
        ])
    
    with tab5:
        st.caption("🔵 Les Classiques : Les vétérans qui remettent leur titre en jeu.")
        render_tier_list(df[(df['ecoute'] == True) & (df['deja_connu'] == True)], [
            (6, "GOAT-TIER (Le Vieux Père du Game, Intouchable)", "🐐"),
            (5, "S-TIER (C'est l'eau, Toujours la magie)", "🏆"), 
            (4, "A-TIER (Daba toujours, Respect au Doyen)", "💎"), 
            (3, "B-TIER (Ça dépanne, Toujours dans le mouvement)", "🚶‍♂️"), 
            (2, "C-TIER (Faut laisser ça au passé, C'est devenu chaud)", "🕰️"), 
            (1, "D-TIER (Vrai Brouteur, L'escroquerie a pris fin)", "📉")
        ], is_blue=True)

    # ==========================================
    # TAB 6 : LE MODE WRAPPED (MENSUEL & ANNUEL)
    # ==========================================
    with tab6:
        st.markdown("<h2 style='text-align:center;'>🎁 Ton Wrapped Musical</h2>", unsafe_allow_html=True)

        df_ecoutes_wrap = df[df['ecoute'] == True].copy()

        if df_ecoutes_wrap.empty:
            st.info("Valide au moins une écoute pour générer un Wrapped !")
        else:
            df_ecoutes_wrap['dt_obj'] = pd.to_datetime(df_ecoutes_wrap['date'])

            c_type, c_mois = st.columns(2)
            with c_type:
                type_wrapped = st.radio("Période :", ["Mensuel", "Annuel (Global)"], horizontal=True)
            
            df_cible = df_ecoutes_wrap
            titre_wrap = "Bilan Annuel 2026"

            if type_wrapped == "Mensuel":
                mois_noms = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
                with c_mois:
                    mois_choisi = st.selectbox("Choisis le mois :", mois_noms)
                mois_idx = mois_noms.index(mois_choisi) + 1
                df_cible = df_ecoutes_wrap[df_ecoutes_wrap['dt_obj'].dt.month == mois_idx]
                titre_wrap = f"Bilan de {mois_choisi}"
                
            st.divider()

            if st.button(f"✨ Générer mon Wrapped : {titre_wrap} ✨", width='stretch'):
                if df_cible.empty:
                    st.warning("Tu n'as écouté aucun album sur cette période !")
                else:
                    st.balloons()

                    # Calcul des stats
                    nb_albums = len(df_cible)
                    note_moyenne = round(df_cible['note'].mean(), 2)
                    top_artiste = df_cible['artiste'].value_counts().idxmax()
                    top_pays = df_cible['pays'].value_counts().idxmax()
                    
                    # Meilleur album (on prend le plus récent parmi les mieux notés)
                    meilleurs = df_cible[df_cible['note'] == df_cible['note'].max()].sort_values('date', ascending=False)
                    best_album = meilleurs.iloc[0]

                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #1E1E1E, #25262B); padding: 30px; border-radius: 20px; border: 2px solid #FF8200; box-shadow: 0 10px 20px rgba(0,0,0,0.5);'>
                        <h3 style='color:#FF8200; margin-top:0;'>🎧 {titre_wrap}</h3>
                        <p style='font-size:1.2em;'>Tu as écouté <b>{nb_albums} albums</b> avec une note moyenne de <b>{note_moyenne}/5</b> !</p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.write("")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.info(f"**🎙️ Artiste N°1**\n\n### {top_artiste}")
                    with c2:
                        st.success(f"**🌍 Région N°1**\n\n### {top_pays}")
                    with c3:
                        nb_decouvertes = df_cible[(df_cible['deja_connu'] == False)].shape[0]
                        st.warning(f"**🟢 Découvertes**\n\n### {nb_decouvertes} albums")

                    st.markdown("### 🏆 L'Album de la période")
                    c_img, c_txt = st.columns([1, 2])
                    with c_img:
                        st.image(best_album['cover_url'], width='stretch')
                    with c_txt:
                        st.markdown(f"**{best_album['pays']} {best_album['artiste']}**")
                        st.markdown(f"#### *{best_album['album']}*")
                        st.markdown(f"**Note :** {'⭐' * int(best_album['note'])}")
                        if best_album['avis']:
                            st.markdown(f"> *\"{best_album['avis']}\"*")