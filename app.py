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

    # ==========================================
    # 🔴 LE BATCH DE SYNCHRONISATION (VERSION OVERDRIVE)
    # ==========================================
    
    # --- 📅 DÉFINITION DE LA DATE ---
    today_iso = date.today().isoformat()
    
    # --- 🧮 CALCULS AVANCÉS ---
    # On compte TOUS les albums écoutés (Officiels + Hors-Série)
    nb_valide = df[df['ecoute'] == True].shape[0]
    
    # La cible reste 365 (ton objectif de base)
    cible_odyssee = 365
    
    # Calcul du pourcentage réel (peut dépasser 100%)
    progress_val = nb_valide / cible_odyssee
    # Sécurité pour la barre visuelle uniquement (max 1.0)
    progress_bar_display = min(progress_val, 1.0)
    
    # Calcul du retard (uniquement sur les albums programmés)
    if 'type' in df.columns:
        df_retard = df[(df['ecoute'] == False) & (df['date'] < today_iso) & (df['type'] != 'HORS-SÉRIE')]
    else:
        df_retard = df[(df['ecoute'] == False) & (df['date'] < today_iso)]
    nb_retard = len(df_retard)
    
    # Calcul du Streak (Série)
    df_sorted = df.sort_values('date', ascending=False)
    ecoutes_serie = df_sorted[df_sorted['date'] < today_iso]['ecoute'].tolist()
    streak = 0
    for e in ecoutes_serie:
        if e: streak += 1
        else: break

    # --- 🎨 DESIGN DU HEADER ---
    st.markdown(f"""
        <div style="background: linear-gradient(90deg, #FF8200 0%, #FF4500 100%); padding: 2px; border-radius: 15px; margin-bottom: 20px;">
            <div style="background: #0E1117; padding: 20px; border-radius: 13px; text-align: center;">
                <h1 style="margin: 0; font-size: 2.5em; letter-spacing: -1px;">🎹 ODYSSÉE MUSICALE <span style="color: #FF8200;">2026</span></h1>
                <p style="color: gray; margin: 5px 0 15px 0;">Objectif 365 albums... et plus si affinités !</p>
                <div style="display: flex; justify-content: center; gap: 40px; margin-top: 10px; flex-wrap: wrap;">
                    <div>
                        <span style="display: block; font-size: 0.8em; color: gray; text-transform: uppercase;">Total Écoutés</span>
                        <span style="font-size: 1.5em; font-weight: bold; color: #FF8200;">{nb_valide} / {cible_odyssee}</span>
                    </div>
                    <div>
                        <span style="display: block; font-size: 0.8em; color: gray; text-transform: uppercase;">Score de l'Année</span>
                        <span style="font-size: 1.5em; font-weight: bold; color: #FF8200;">{int(progress_val*100)}%</span>
                    </div>
                    <div>
                        <span style="display: block; font-size: 0.8em; color: gray; text-transform: uppercase;">Série Actuelle</span>
                        <span style="font-size: 1.5em; font-weight: bold; color: #FF8200;">🔥 {streak} Jours</span>
                    </div>
                    <div>
                        <span style="display: block; font-size: 0.8em; color: gray; text-transform: uppercase;">Statut</span>
                        <span style="font-size: 1.5em; font-weight: bold; color: {'#009A44' if nb_retard == 0 else '#EF4135'};">
                            {'✅ À JOUR' if nb_retard == 0 else f'🚨 -{nb_retard}'}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.progress(progress_bar_display)

    # ==========================================
    # ⚙️ BARRE LATÉRALE : CENTRE DE CONTRÔLE
    # ==========================================
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #FF8200;'>🛠️ Centre de Contrôle</h2>", unsafe_allow_html=True)
        st.write("")

        st.subheader("🔍 Édition Rapide")
        st.caption("Modifie un album déjà écouté ou rattrape un retard facilement.")

        # Tri alphabétique pour retrouver plus facilement les albums
        df_sorted_alpha = df.sort_values(by="artiste")
        options_dict = {f"{r.get('pays', '')} {r['artiste']} - {r['album']}": i for i, r in df_sorted_alpha.iterrows()}
        
        choix = st.selectbox("Rechercher un album :", ["-- Sélectionner --"] + list(options_dict.keys()))

        if choix != "-- Sélectionner --":
            idx_sel = options_dict[choix]
            row_sel = df.loc[idx_sel]

            # --- 🖼️ MINI-CARTE DE L'ALBUM ---
            with st.container(border=True):
                c_img, c_txt = st.columns([1, 2.5])
                with c_img:
                    st.image(row_sel.get('cover_url', 'https://placehold.co/150x150/1E1E1E/FF8200?text=Musique'), use_container_width=True)
                with c_txt:
                    st.markdown(f"<b style='font-size:1.1em;'>{row_sel['artiste']}</b>", unsafe_allow_html=True)
                    st.markdown(f"<i style='font-size:0.9em; color:gray;'>{row_sel['album']}</i>", unsafe_allow_html=True)
                    
                    if row_sel['ecoute']:
                        st.markdown(f"<span style='color:#009A44; font-size:0.85em; font-weight:bold;'>✅ Fait ({row_sel['note']}/5)</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span style='color:#EF4135; font-size:0.85em; font-weight:bold;'>⏳ En attente</span>", unsafe_allow_html=True)

            # --- 🎛️ LOGIQUE DU SLIDER (Max 5, sauf si déjà élu GOAT/AOTY) ---
            try: note_actuelle = int(row_sel['note']) 
            except: note_actuelle = 0

            # Si l'album a été couronné 6 ou 7 dans la cérémonie, le slider s'adapte pour ne pas casser la note
            note_max_sb = max(5, note_actuelle)
            val_defaut = note_actuelle if note_actuelle > 0 else 4

            with st.form(f"sidebar_form_{idx_sel}"):
                s_note = st.slider("Note de l'album", 1, note_max_sb, val_defaut)
                s_avis = st.text_area("Ton avis", value=str(row_sel.get('avis', '')))
                
                c_pays, c_connu = st.columns([1.5, 1])
                with c_pays:
                    s_pays = st.text_input("Drapeau / Pays", value=str(row_sel.get('pays', '')))
                with c_connu:
                    st.write("") # Petit espace pour aligner la case à cocher avec le texte
                    st.write("")
                    s_connu = st.checkbox("Classique", value=bool(row_sel.get('deja_connu', False)))

                if st.form_submit_button("💾 Sauvegarder", use_container_width=True):
                    df.at[idx_sel, 'ecoute'] = True
                    df.at[idx_sel, 'note'] = s_note
                    df.at[idx_sel, 'avis'] = s_avis
                    df.at[idx_sel, 'deja_connu'] = s_connu
                    df.at[idx_sel, 'pays'] = s_pays
                    save_data(df)
                    st.success("Modifications enregistrées !")
                    time.sleep(1)
                    st.rerun()
              
        st.divider()

        # --- ⚙️ OUTILS D'ADMINISTRATION ---
        with st.expander("⚙️ Outils d'Administration", expanded=False):
            st.caption("Télécharge les pochettes et années manquantes depuis Spotify.")
            if st.button("🔄 Lancer l'aspirateur Spotify", use_container_width=True):
                # On cible les cases vides OU les fausses pochettes générées par défaut
                mask = (df['cover_url'] == "") | (df['cover_url'].str.contains("placehold.co", na=False)) | (df['cover_url'].isnull())
                nb_a_faire = mask.sum()

                if nb_a_faire > 0:
                    barre = st.progress(0)
                    status_text = st.empty() # Création d'une zone de texte dynamique
                    
                    for i, idx in enumerate(df[mask].index):
                        status_text.text(f"Recherche : {df.at[idx, 'artiste']}...") # Affiche l'album en cours
                        infos = get_album_infos(df.at[idx, 'artiste'], df.at[idx, 'album'])
                        df.at[idx, 'cover_url'] = infos['cover']
                        df.at[idx, 'annee'] = infos['year']
                        barre.progress((i + 1) / nb_a_faire)

                    save_data(df)
                    status_text.empty() # On efface le texte dynamique
                    st.success(f"✅ {nb_a_faire} pochettes mises à jour !")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.info("✨ Ton odyssée est parfaite, tout est à jour !")
                

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🎧 À l'écoute", "📊 Bilan", "📅 Calendrier", "🏆 Tier List", "🗄️ Archives", "🎁 Cérémonie", "➕ Hors-Série"
    ])

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
            st.balloons()
        else:
            # --- 🌟 HEADER DYNAMIQUE ---
            st.markdown(f"<h2 style='text-align:center; color:#FF8200;'>🎧 Aujourd'hui : {current.get('album', 'Inconnu')}</h2>", unsafe_allow_html=True)

            c_img, c_details = st.columns([1.2, 2])

            with c_img:
                # Affichage de la pochette avec le style "Glow"
                cover_url = current.get('cover_url', 'https://placehold.co/600x600/1E1E1E/FF8200?text=Musique')
                st.markdown(f'<div class="cover-glow"><img src="{cover_url}" width="100%" style="border-radius:15px;"></div>', unsafe_allow_html=True)

                # --- 🔊 PLAYER EMBARQUÉ (GOAT FEATURE) ---
                try:
                    search_res = sp.search(q=f"album:{current.get('album', '')} artist:{current.get('artiste', '')}", type='album', limit=1)
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

                # --- 🚀 HUB D'ÉCOUTE (Raccourcis) ---
                query = f"{current.get('artiste', '')} {current.get('album', '')}".replace(" ", "%20")
                spot_url = f"https://open.spotify.com/search/{query}/albums"
                yt_url = f"https://www.youtube.com/results?search_query={query}+full+album"
                genius_url = f"https://genius.com/search?q={query}"

                st.markdown(f"""
                <div style="display: flex; gap: 10px; margin-top: 10px; margin-bottom: 15px; flex-wrap: wrap;">
                    <a href="{spot_url}" target="_blank" style="text-decoration: none;">
                        <div style="background-color: #1DB954; color: white; padding: 6px 12px; border-radius: 5px; font-weight: bold; font-size: 0.85em;">🎧 Spotify</div>
                    </a>
                    <a href="{yt_url}" target="_blank" style="text-decoration: none;">
                        <div style="background-color: #FF0000; color: white; padding: 6px 12px; border-radius: 5px; font-weight: bold; font-size: 0.85em;">📺 YouTube</div>
                    </a>
                    <a href="{genius_url}" target="_blank" style="text-decoration: none;">
                        <div style="background-color: #FFFF64; color: black; padding: 6px 12px; border-radius: 5px; font-weight: bold; font-size: 0.85em;">🎤 Paroles</div>
                    </a>
                </div>
                """, unsafe_allow_html=True)

                st.divider()

                # --- 📚 LE SAVIEZ-VOUS ? ---
                with st.expander("📖 Un peu de culture (Wikipedia)", expanded=True):
                    try:
                        wiki_summary = wikipedia.summary(f"Album {current.get('album', '')} {current.get('artiste', '')}", sentences=3, lang="fr")
                        st.write(wiki_summary)
                    except:
                        st.write("Pas d'anecdote trouvée pour cet album, concentre-toi sur la musique !")

            st.write("")

            # --- 📝 LA ZONE DE NOTATION ---
            with st.container(border=True):
                st.info("⭐ La note maximale au quotidien est de **5/5**. Le GOAT (6/6) sera élu à la fin du mois dans la Cérémonie !")

                with st.form("main_notation_form"):
                    st.write("### 🎙️ Ton verdict")
                    c_note, c_pays = st.columns([3, 1])
                    with c_note: 
                        val_note = st.slider("⭐ Note (5 = Classique Absolu 🔥)", 1, 5, 4)
                    with c_pays:
                        val_pays = st.text_input("Pays / Drapeau", value=current.get('pays', ''))

                    val_avis = st.text_area("Ta critique", height=100)
                    val_connu = st.checkbox("Je connaissais déjà cet album", value=bool(current.get('deja_connu', False)))

                    submit = st.form_submit_button("✅ Valider l'écoute", width='stretch')

                    if submit:
                        df.at[real_idx, 'ecoute'] = True
                        df.at[real_idx, 'note'] = val_note
                        df.at[real_idx, 'avis'] = val_avis
                        df.at[real_idx, 'deja_connu'] = val_connu
                        df.at[real_idx, 'pays'] = val_pays
                        save_data(df)
                        st.balloons()
                        time.sleep(1.5)
                        st.rerun()

    # --- TAB 2 : STATS & RATTRAPAGE ---
    with tab2:
        st.markdown("<h1 style='text-align:center; color:#FF8200;'>📊 Le Bilan de l'Odyssée</h1>", unsafe_allow_html=True)

        df_ecoutes = df[df['ecoute'] == True].copy()

        # --- 🚀 LA BARRE DE PROGRESSION ---
        total_albums = len(df)
        nb_ecoutes = len(df_ecoutes)
        if total_albums > 0:
            progress_pct = nb_ecoutes / total_albums
            st.progress(progress_pct)
            st.markdown(f"<p style='text-align:center; color:gray; font-size:1.1em;'>Progression : <b>{nb_ecoutes} / {total_albums}</b> albums écoutés ({int(progress_pct*100)}%)</p>", unsafe_allow_html=True)
        
        st.write("")

        # --- 🏆 PARTIE 1 : LES STATS CLÉS (KPIs) ---
        if not df_ecoutes.empty:
            c1, c2, c3, c4 = st.columns(4)
            
            # CORRECTION : On affiche la moyenne sur 5
            c1.metric("⭐ Moyenne Globale", f"{round(df_ecoutes['note'].mean(), 2)} / 5")
            
            nb_decouvertes = len(df_ecoutes[df_ecoutes['deja_connu'] == False])
            c2.metric("🟢 Découvertes", nb_decouvertes)
            
            nb_pays = df_ecoutes['pays'].nunique()
            c3.metric("🌍 Pays Explorés", nb_pays)
            
            nb_goats = len(df_ecoutes[df_ecoutes['note'] >= 6])
            c4.metric("👑 GOATs Couronnés", f"{nb_goats} albums")
            
        st.divider()

        # --- 🚨 PARTIE 2 : LE RATTRAPAGE INTELLIGENT ---
        df['dt_obj'] = pd.to_datetime(df['date'], errors='coerce')
        today = pd.Timestamp.today().normalize()
        df_retard = df[(df['dt_obj'] < today) & (df['ecoute'] == False)].copy()

        if df_retard.empty:
            st.markdown("""
                <div style="background-color: rgba(0, 154, 68, 0.1); border: 1px solid #009A44; padding: 20px; border-radius: 10px; text-align: center;">
                    <h2 style="margin:0;">🎉 Zéro retard !</h2>
                    <p style="margin:0; color:#009A44;">Tu es parfaitement à jour dans ton calendrier. Le boss !</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="background-color: rgba(239, 65, 53, 0.1); border: 1px solid #EF4135; padding: 20px; border-radius: 10px; text-align: center;">
                    <h2 style="margin:0; color:#EF4135;">🚨 ALERTE ROUGE : {len(df_retard)} album(s) en retard !</h2>
                    <p style="margin:0;">Le programme n'attend pas. Va dans la barre latérale gauche (Édition Rapide) pour valider ces écoutes.</p>
                </div>
            """, unsafe_allow_html=True)
            st.write("")

            # Un tableau beaucoup plus propre avec le bon format de date
            st.dataframe(
                df_retard[['date', 'artiste', 'album', 'genre']], 
                column_config={
                    "date": st.column_config.DateColumn("📅 Date Prévue", format="DD/MM/YYYY"),
                    "artiste": st.column_config.TextColumn("🎤 Artiste"),
                    "album": st.column_config.TextColumn("💿 Album"),
                    "genre": st.column_config.TextColumn("🎵 Genre")
                },
                width='stretch', 
                hide_index=True
            )

        st.divider()

        # --- 📈 PARTIE 3 : L'ANALYSE DÉTAILLÉE ---
        st.markdown("<h2 style='text-align:center;'>🧠 Analyse de tes goûts</h2>", unsafe_allow_html=True)
        st.write("")

        # Sous-onglets pour ne pas surcharger la page verticalement
        tab_g, tab_a, tab_t = st.tabs(["🎵 Genres & Notes", "👑 Artistes Favoris", "⏳ Voyage Temporel"])

        with tab_g:
            c_g1, c_g2 = st.columns(2)
            with c_g1:
                st.subheader("Les Genres dominants")
                if not df_ecoutes.empty and 'genre' in df_ecoutes.columns:
                    genre_counts = df_ecoutes['genre'].value_counts().head(7)
                    st.bar_chart(genre_counts, color="#FF8200")
                else:
                    st.info("Pas encore assez de données.")
            with c_g2:
                st.subheader("Répartition des Notes")
                if not df_ecoutes.empty:
                    st.bar_chart(df_ecoutes['note'].value_counts().sort_index(), color="#009A44")

        with tab_a:
            st.subheader("Le Panthéon des Artistes (Top 10)")
            st.caption("Règle stricte : L'artiste doit avoir au moins 3 albums écoutés OU 100% de sa discographie prévue terminée.")
            if not df_ecoutes.empty:
                total_counts = df['artiste'].value_counts()
                listened_counts = df_ecoutes['artiste'].value_counts()

                artistes_valides = []
                for artiste, c_listened in listened_counts.items():
                    c_total = total_counts.get(artiste, 0)
                    if c_listened >= 3 or c_listened == c_total:
                        artistes_valides.append(artiste)

                df_filtre = df_ecoutes[df_ecoutes['artiste'].isin(artistes_valides)]

                if not df_filtre.empty:
                    # On affiche maintenant le Top 10 au lieu du Top 5
                    top_artistes = df_filtre.groupby('artiste')['note'].mean().sort_values(ascending=False).head(10)
                    st.bar_chart(top_artistes, color="#9c27b0")
                else: 
                    st.info("Aucun artiste ne remplit les critères pour le moment. Continue d'écouter !")

        with tab_t:
            st.subheader("Répartition par Décennies")
            if not df_ecoutes.empty:
                df_ecoutes['annee_propre'] = pd.to_numeric(df_ecoutes['annee'], errors='coerce').fillna(0).astype(int)
                df_annees = df_ecoutes[df_ecoutes['annee_propre'] > 1900].copy()
                if not df_annees.empty:
                    df_annees['decennie'] = (df_annees['annee_propre'] // 10) * 10
                    decennies_counts = df_annees['decennie'].value_counts().sort_index()
                    decennies_counts.index = decennies_counts.index.astype(str) + "s"
                    st.bar_chart(decennies_counts, color="#17a2b8")

    # --- TAB 3 : CALENDRIER & GALERIE ---
    with tab3:
        st.markdown("<h1 style='text-align:center; color:#FF8200;'>📅 Le Calendrier de l'Odyssée</h1>", unsafe_allow_html=True)

        view_mode = st.radio("Vue :", ["Liste 📱", "Grille 🖥️", "Galerie 🖼️"], horizontal=True, label_visibility="collapsed")
        st.write("") # Petit espace de respiration

        if view_mode == "Galerie 🖼️":
            df['dt_obj'] = pd.to_datetime(df['date'])
            # Dictionnaire robuste pour forcer le français peu importe le serveur
            mois_fr = {1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"}
            
            for month_num in range(1, 13):
                df_month = df[df['dt_obj'].dt.month == month_num]
                if not df_month.empty:
                    annee = df_month.iloc[0]['dt_obj'].year
                    month_name = f"{mois_fr[month_num]} {annee}"
                    
                    with st.expander(f"📅 {month_name}", expanded=(month_num == date.today().month)):
                        cols = st.columns(4)
                        for i, (_, row) in enumerate(df_month.iterrows()):
                            with cols[i % 4]:
                                with st.container(border=True):
                                    # Pochette avec effet Glow (réutilise le CSS du tab1)
                                    cover_url = row.get('cover_url', 'https://placehold.co/300x300/1E1E1E/FF8200?text=Musique')
                                    st.markdown(f'<div class="cover-glow"><img src="{cover_url}" width="100%" style="border-radius:10px; margin-bottom:10px;"></div>', unsafe_allow_html=True)
                                    
                                    # Informations de l'album
                                    st.markdown(f"<h4 style='text-align:center; margin-bottom:0px; line-height: 1.2;'>{row.get('album', 'Inconnu')}</h4>", unsafe_allow_html=True)
                                    st.markdown(f"<p style='text-align:center; color:#FF8200; font-weight:bold; margin-top:5px;'>{row.get('pays', '')} {row.get('artiste', 'Inconnu')}</p>", unsafe_allow_html=True)
                                    
                                    # Affichage des Notes et Statuts
                                    if row['ecoute']:
                                        note = row.get('note', 0)
                                        # Affichage dynamique de la note
                                        if note == 7: stars = "🌟 <b>AOTY</b> 🌟"
                                        elif note == 6: stars = "👑 <b>GOAT</b>"
                                        else: stars = "⭐" * int(note)
                                        
                                        st.markdown(f"<p style='text-align:center; margin-bottom:5px; font-size:1.1em;'>{stars}</p>", unsafe_allow_html=True)
                                        
                                        # Badge de découverte
                                        badge_color = "#17a2b8" if row['deja_connu'] else "#28a745"
                                        badge_text = "Classique" if row['deja_connu'] else "Découverte"
                                        st.markdown(f"<div style='text-align:center;'><span style='background:{badge_color}; color:white; padding: 4px 10px; border-radius: 12px; font-size: 0.8em; font-weight:bold;'>{badge_text}</span></div>", unsafe_allow_html=True)
                                    else:
                                        date_str = row['dt_obj'].strftime('%d/%m')
                                        if str(row['date']) < today_iso:
                                            st.markdown(f"<div style='text-align:center;'><span style='background:#EF4135; color:white; padding: 4px 10px; border-radius: 12px; font-size: 0.8em; font-weight:bold;'>⚠️ Retard ({date_str})</span></div>", unsafe_allow_html=True)
                                        else:
                                            st.markdown(f"<div style='text-align:center;'><span style='background:#6c757d; color:white; padding: 4px 10px; border-radius: 12px; font-size: 0.8em; font-weight:bold;'>⏳ Prévu le {date_str}</span></div>", unsafe_allow_html=True)
        else:
            events = []
            for _, r in df.iterrows():
                # On ajoute ENFIN le nom de l'album dans le calendrier !
                evt_title = f"{r.get('pays', '')} {r.get('artiste', '')} - {r.get('album', '')}"

                if r['ecoute']: 
                    # Si c'est un GOAT ou AOTY, on le met en orange bien visible dans le calendrier !
                    if r.get('note', 0) >= 6:
                        color = "#FF8200"
                        icon = "🌟" if r.get('note', 0) == 7 else "👑"
                    else:
                        color = "#17a2b8" if r['deja_connu'] else "#28a745"
                        icon = "🔄" if r['deja_connu'] else "✅"
                    title = f"{icon} {evt_title}"
                elif str(r['date']) < today_iso:
                    color, title = "#EF4135", f"⚠️ {evt_title}"
                else: 
                    color, title = "#6c757d", f"🎵 {evt_title}"

                events.append({"title": title, "start": str(r['date']), "allDay": True, "backgroundColor": color, "borderColor": color})

            cal_mode = "listMonth" if "Liste" in view_mode else "dayGridMonth"
            # initialDate paramétrée sur le jour actuel (today_iso) ! Et bouton "today" rajouté dans la toolbar.
            calendar(events=events, options={"initialDate": today_iso, "locale": "fr", "headerToolbar": {"left": "prev,next today", "center": "title", "right": ""}, "initialView": cal_mode, "height": "750px"}, key=f"cal_{view_mode}")

    # --- 🛠️ FONCTION DE RENDU TIER LIST AMÉLIORÉE ---
    def render_tier_list_pro(df_filtre, tiers, key_prefix):
        if df_filtre.empty:
            st.info("📭 Aucun album ne correspond à ces critères.")
            return
        
        for note, label, icon in tiers:
            sub_df = df_filtre[df_filtre['note'] == note]
            if not sub_df.empty:
                st.markdown(f"#### {icon} {label} ({len(sub_df)})")

                # Grille de 5 colonnes pour un rendu compact
                cols = st.columns(5)
                for i, (idx, row) in enumerate(sub_df.iterrows()):
                    with cols[i % 5]:
                        with st.container(border=True):
                            # Affichage Image
                            cover = row.get('cover_url', 'https://placehold.co/300x300/1E1E1E/FF8200?text=Musique')
                            st.markdown(f'<div class="cover-glow"><img src="{cover}" width="100%" style="border-radius:8px;"></div>', unsafe_allow_html=True)
                            
                            # Infos Textuelles
                            st.markdown(f"<p style='text-align:center; font-size:0.85em; margin-top:5px; line-height:1.2;'><b>{row['artiste']}</b><br><i style='color:gray;'>{row['album']}</i></p>", unsafe_allow_html=True)
                            st.markdown(f"<p style='text-align:center; font-size:0.8em;'>{row['pays']} | {row['genre']}</p>", unsafe_allow_html=True)
                            
                            # Actions rapides
                            with st.expander("⚙️ Action"):
                                nouveau_statut = "Découverte" if row['deja_connu'] else "Classique"
                                if st.button(f"➡️ En {nouveau_statut}", key=f"swap_{key_prefix}_{idx}"):
                                    df.at[idx, 'deja_connu'] = not row['deja_connu']
                                    save_data(df)
                                    st.rerun()
                st.divider()
    
    # --- 🏗️ STRUCTURE DES ONGLETS ---

    # Définition des Tiers (on ajoute le 7 pour l'AOTY et le 6 pour le GOAT)
    tiers_definitions = [
        (7, "AOTY (L'Élu de l'Année, Légendaire)", "🌟"),
        (6, "GOAT-TIER (Le Trône est pris, Maîtrise totale)", "🐐"),
        (5, "S-TIER (Gros Boucan, L'enjaillement est versé)", "🏆"), 
        (4, "A-TIER (Le goût de ça, C'est trop kpata)", "🔥"), 
        (3, "B-TIER (Y a pas drap, On gère tranquille)", "😌"), 
        (2, "C-TIER (Yako pour mes tympans, C'est un peu scié)", "😬"), 
        (1, "D-TIER (Vrai Brouteur, Faut laisser ça)", "📉")
    ]

    # --- TAB 4 : LA GRANDE TIER LIST UNIVERSELLE ---
    with tab4:
        st.markdown("<h1 style='text-align:center; color:#FF8200;'>🏆 La Grande Tier List</h1>", unsafe_allow_html=True)

        df_filtre = df[df['ecoute'] == True].copy()

        # --- 🎛️ PANNEAU DE CONTRÔLE DES FILTRES ---
        with st.container(border=True):
            st.markdown("### 🎛️ Filtres Avancés")
            c_type, c_gen, c_pays, c_tri = st.columns(4)
            
            with c_type:
                type_choix = st.selectbox("📌 Type d'album", ["Tous 🌍", "🟢 Découvertes", "🔵 Classiques"])
            with c_gen:
                genres_dispo = sorted(df_filtre['genre'].dropna().unique())
                sel_genres = st.multiselect("🎵 Genre", genres_dispo, placeholder="Tous les genres")
            with c_pays:
                pays_dispo = sorted(df_filtre['pays'].dropna().unique())
                sel_pays = st.multiselect("🌍 Pays", pays_dispo, placeholder="Tous les pays")
            with c_tri:
                ordre = st.selectbox("⬇️ Tri des notes", ["Décroissant (Meilleurs en haut)", "Croissant (Pires en haut)"])
                
        # --- ⚙️ APPLICATION DES FILTRES ---
        if type_choix == "🟢 Découvertes":
            df_filtre = df_filtre[df_filtre['deja_connu'] == False]
        elif type_choix == "🔵 Classiques":
            df_filtre = df_filtre[df_filtre['deja_connu'] == True]
            
        if sel_genres:
            df_filtre = df_filtre[df_filtre['genre'].isin(sel_genres)]
        if sel_pays:
            df_filtre = df_filtre[df_filtre['pays'].isin(sel_pays)]
            
        tiers_a_afficher = tiers_definitions if "Décroissant" in ordre else tiers_definitions[::-1]
        
        st.write("")
        # On utilise ta fonction render_tier_list_pro existante
        render_tier_list_pro(df_filtre, tiers_a_afficher, "global")

    # --- TAB 5 : LE MOTEUR DE RECHERCHE (ARCHIVES) ---
    with tab5:
        st.markdown("<h1 style='text-align:center; color:#17a2b8;'>🗄️ Les Archives de l'Odyssée</h1>", unsafe_allow_html=True)
        st.write("Une base de données complète pour retrouver rapidement n'importe quel album prévu dans ton année.")

        recherche = st.text_input("🔍 Rechercher un artiste, un album ou un pays...", placeholder="Ex: Kanye West, Illmatic, 🇨🇮...")

        df_display = df.copy()

        # Filtre de recherche textuelle
        if recherche:
            mask = df_display['artiste'].str.contains(recherche, case=False, na=False) | \
                   df_display['album'].str.contains(recherche, case=False, na=False) | \
                   df_display['pays'].str.contains(recherche, case=False, na=False)
            df_display = df_display[mask]
            
        st.write("")
        # Tableau de données interactif
        st.dataframe(
            df_display[['date', 'artiste', 'album', 'genre', 'pays', 'note', 'ecoute']],
            column_config={
                "date": st.column_config.DateColumn("📅 Date Prévue", format="DD/MM/YYYY"),
                "artiste": st.column_config.TextColumn("🎤 Artiste"),
                "album": st.column_config.TextColumn("💿 Album"),
                "genre": st.column_config.TextColumn("🎵 Genre"),
                "pays": st.column_config.TextColumn("🌍 Pays"),
                "note": st.column_config.NumberColumn("⭐ Note"),
                "ecoute": st.column_config.CheckboxColumn("✅ Fait")
            },
            width='stretch',
            hide_index=True,
            height=600
        )

    with tab6:
        # ==========================================
        # 🏆 LA CÉRÉMONIE DES GOATs
        # ==========================================
        st.markdown("<h1 style='text-align:center; color:#FF8200;'>🏆 La Cérémonie des GOATs</h1>", unsafe_allow_html=True)
        st.write("")

        with st.container(border=True):
            mois_noms = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
            mois_actuel_num = date.today().month
            
            c_m1, c_m2 = st.columns([1, 2])
            with c_m1:
                mois_choisi_num = st.selectbox("📅 Mois de l'élection :", range(1, 13), index=mois_actuel_num-1, format_func=lambda x: mois_noms[x-1])
            
            df['mois_calcul'] = pd.to_datetime(df['date'], errors='coerce').dt.month
            candidats = df[(df['mois_calcul'] == mois_choisi_num) & (df['note'] >= 5) & (df['ecoute'] == True)]
            
            if candidats.empty:
                st.info(f"🤷‍♂️ Aucun candidat (5/5) trouvé pour le mois de {mois_noms[mois_choisi_num-1]}.")
            else:
                goat_deja_elu = candidats[candidats['note'] >= 6]
                
                if not goat_deja_elu.empty:
                    roi = goat_deja_elu.iloc[0]
                    st.markdown(f"""
                        <div style="background: linear-gradient(135deg, rgba(255, 130, 0, 0.2), rgba(0,0,0,0)); padding: 30px; border-radius: 20px; text-align: center; border: 2px solid #FF8200; box-shadow: 0 0 20px rgba(255,130,0,0.3);">
                            <h2 style="margin-bottom: 10px;">👑 LE GOAT DE {mois_noms[mois_choisi_num-1].upper()}</h2>
                            <img src="{roi['cover_url']}" width="200" style="border-radius: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.5);">
                            <h1 style="color: #FF8200; margin-top: 15px; margin-bottom: 0px;">{roi['album']}</h1>
                            <h3 style="margin-top: 5px; color: white;">{roi['artiste']}</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    st.write("")
                    if st.button("🔄 Annuler l'élection (Libérer le trône)", key=f"reset_goat_{mois_choisi_num}"):
                        df.at[roi.name, 'note'] = 5
                        save_data(df)
                        st.rerun()
                else:
                    st.markdown(f"### 🗳️ Les Nominés de {mois_noms[mois_choisi_num-1]} :")
                    # Affichage des pochettes des nominés
                    cols_nom = st.columns(min(len(candidats), 5))
                    for i, (idx, row) in enumerate(candidats.iterrows()):
                        with cols_nom[i % 5]:
                            st.image(row['cover_url'], use_container_width=True)
                            st.caption(f"**{row['artiste']}**")

                    choix_goat = st.selectbox(
                        "Qui mérite de gâter le coin ce mois-ci ?", 
                        candidats.index, 
                        format_func=lambda idx: f"💿 {df.loc[idx, 'artiste']} - {df.loc[idx, 'album']}"
                    )
                    
                    if st.button("👑 COURONNER CET ALBUM", type="primary", use_container_width=True):
                        df.at[choix_goat, 'note'] = 6
                        save_data(df)
                        st.balloons()
                        time.sleep(1)
                        st.rerun()

        # --- 🌟 LIGUE DES CHAMPIONS (AOTY) ---
        st.write("")
        st.markdown("<h1 style='text-align:center; color:#EF4135;'>🌟 L'Album de l'Année (AOTY)</h1>", unsafe_allow_html=True)
        
        goats_annuels = df[(df['note'] >= 6) & (df['ecoute'] == True)]
        
        if goats_annuels.empty:
            st.info("Les GOATs mensuels n'ont pas encore été élus. L'arène AOTY est fermée.")
        else:
            aoty = goats_annuels[goats_annuels['note'] == 7]
            if not aoty.empty:
                dieu = aoty.iloc[0]
                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #EF4135, #7A1A14); padding: 40px; border-radius: 25px; text-align: center; border: 4px solid #white; box-shadow: 0 0 50px rgba(239, 65, 53, 0.6);">
                        <h1 style="font-size: 3.5em; margin-bottom: 0px;">👑 LÉGENDE 2026 👑</h1>
                        <img src="{dieu['cover_url']}" width="300" style="border-radius: 20px; border: 5px solid white; margin: 20px 0;">
                        <h1 style="color: white; font-size: 3em; margin: 0;">{dieu['album']}</h1>
                        <h2 style="color: #FFD700; margin-top: 0;">{dieu['artiste']}</h2>
                        <p style="font-size: 2.5em; letter-spacing: 10px;">🌟🌟🌟🌟🌟🌟🌟</p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("🔄 Remettre le titre en jeu"):
                    df.at[dieu.name, 'note'] = 6
                    save_data(df)
                    st.rerun()
            else:
                with st.expander("⚔️ Entrer dans l'Arène Finale (Ligue des Champions)"):
                    st.write("Voici tes 12 (ou moins) GOATs mensuels. Un seul deviendra éternel.")
                    choix_aoty = st.radio("Sélectionne le Dieu de la Musique 2026 :", goats_annuels.index, 
                                        format_func=lambda idx: f"🐐 {df.loc[idx, 'artiste']} - {df.loc[idx, 'album']}")
                    
                    if st.button("🌟 SACRER L'ALBUM DE L'ANNÉE", type="primary", use_container_width=True):
                        df.at[choix_aoty, 'note'] = 7
                        save_data(df)
                        st.balloons()
                        time.sleep(1)
                        st.rerun()

        # ==========================================
        # 🎁 LE WRAPPED MUSICAL
        # ==========================================
        # ==========================================
        # 🎁 LE WRAPPED MUSICAL (VERSION INFOGRAPHIE)
        # ==========================================
        st.divider()
        st.markdown("<h1 style='text-align:center; color:#1DB954;'>🎁 Ton Wrapped Musical</h1>", unsafe_allow_html=True)

        df_ecoutes_wrap = df[df['ecoute'] == True].copy()

        if df_ecoutes_wrap.empty:
            st.info("Continue ton voyage pour débloquer ton Wrapped !")
        else:
            df_ecoutes_wrap['dt_obj'] = pd.to_datetime(df_ecoutes_wrap['date'])
            cw1, cw2 = st.columns(2)
            with cw1:
                period_type = st.segmented_control("Période", ["Mensuel", "Annuel"], default="Mensuel")
            
            df_cible = df_ecoutes_wrap
            titre_wrap = "Bilan Annuel 2026"

            if period_type == "Mensuel":
                with cw2:
                    mois_wrap = st.selectbox("Choisir le mois :", mois_noms, index=mois_actuel_num-1)
                m_idx = mois_noms.index(mois_wrap) + 1
                df_cible = df_ecoutes_wrap[df_ecoutes_wrap['dt_obj'].dt.month == m_idx]
                titre_wrap = f"Bilan de {mois_wrap}"

            if st.button(f"✨ GÉNÉRER LE WRAPPED : {titre_wrap.upper()} ✨", use_container_width=True):
                if df_cible.empty:
                    st.warning("Aucune donnée pour cette période. Il faut écouter de la musique !")
                else:
                    st.balloons()
                    
                    # --- 🧮 CALCUL DES NOUVELLES STATS ---
                    nb_albums = len(df_cible)
                    note_moy = round(df_cible['note'].mean(), 2)
                    top_art = df_cible['artiste'].value_counts().idxmax()
                    top_pay = df_cible['pays'].value_counts().idxmax()
                    
                    # Sécurisation du genre au cas où il serait vide
                    try: top_genre = df_cible['genre'].value_counts().idxmax()
                    except: top_genre = "Inconnu"
                    
                    # Calcul Découvertes vs Classiques
                    nb_decouvertes = len(df_cible[df_cible['deja_connu'] == False])
                    nb_classiques = nb_albums - nb_decouvertes
                    
                    best_alb = df_cible.sort_values(['note', 'date'], ascending=False).iloc[0]

                    # --- 🎨 LA CARTE WRAPPED ULTRA-STYLISÉE ---
                    html_wrapped = f"""
<div style="background: linear-gradient(135deg, #1DB954 0%, #128238 100%); padding: 40px; border-radius: 30px; color: white; font-family: sans-serif; box-shadow: 0 20px 40px rgba(29, 185, 84, 0.3);">
<div style="text-align: center; margin-bottom: 30px;">
<h4 style="margin:0; color: #b3ffcc; text-transform: uppercase; letter-spacing: 3px;">{titre_wrap}</h4>
<h1 style="font-size: 4.5em; margin: 10px 0; line-height: 1.1; font-weight: 900;">MON WRAPPED<br>ODYSSÉE</h1>
</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
<div style="background: rgba(0,0,0,0.2); padding: 20px; border-radius: 20px; text-align: center;">
<p style="margin:0; color: #b3ffcc; font-size: 0.9em; font-weight: bold; letter-spacing: 1px;">ALBUMS ÉCOUTÉS</p>
<h2 style="margin:10px 0 0 0; font-size: 4em;">{nb_albums}</h2>
</div>
<div style="background: rgba(0,0,0,0.2); padding: 20px; border-radius: 20px; text-align: center;">
<p style="margin:0; color: #b3ffcc; font-size: 0.9em; font-weight: bold; letter-spacing: 1px;">NOTE MOYENNE</p>
<h2 style="margin:10px 0 0 0; font-size: 4em;">{note_moy}<span style="font-size: 0.5em; color: rgba(255,255,255,0.6);">/5</span></h2>
</div>
</div>
<div style="display: flex; justify-content: space-between; background: rgba(0,0,0,0.2); padding: 20px; border-radius: 20px; margin-bottom: 30px; text-align: center; flex-wrap: wrap; gap: 10px;">
<div style="flex: 1; min-width: 100px;">
<p style="margin:0; color: #b3ffcc; font-size: 0.8em; font-weight: bold;">🎤 TOP ARTISTE</p>
<h3 style="margin: 5px 0 0 0; font-size: 1.3em;">{top_art}</h3>
</div>
<div style="flex: 1; min-width: 100px; border-left: 1px solid rgba(255,255,255,0.2); border-right: 1px solid rgba(255,255,255,0.2);">
<p style="margin:0; color: #b3ffcc; font-size: 0.8em; font-weight: bold;">🎵 TOP GENRE</p>
<h3 style="margin: 5px 0 0 0; font-size: 1.3em;">{top_genre}</h3>
</div>
<div style="flex: 1; min-width: 100px;">
<p style="margin:0; color: #b3ffcc; font-size: 0.8em; font-weight: bold;">🌍 TOP PAYS</p>
<h3 style="margin: 5px 0 0 0; font-size: 1.3em;">{top_pay}</h3>
</div>
</div>
<div style="background: rgba(0,0,0,0.2); padding: 20px; border-radius: 20px; margin-bottom: 30px; display: flex; justify-content: space-around; text-align: center;">
<div>
<h3 style="margin:0; font-size: 2.5em; color: #fff;">{nb_decouvertes}</h3>
<p style="margin:0; color: #b3ffcc; font-size: 0.8em; font-weight: bold; text-transform: uppercase;">Nouvelles Pépites 🟢</p>
</div>
<div>
<h3 style="margin:0; font-size: 2.5em; color: #fff;">{nb_classiques}</h3>
<p style="margin:0; color: #b3ffcc; font-size: 0.8em; font-weight: bold; text-transform: uppercase;">Classiques Révisés 🔵</p>
</div>
</div>
<div style="background: white; padding: 20px; border-radius: 20px; display: flex; align-items: center; gap: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.2); flex-wrap: wrap;">
<img src="{best_alb['cover_url']}" width="120" style="border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.3);">
<div style="flex: 1; min-width: 200px;">
<p style="margin:0; font-weight: 900; color: #1DB954; letter-spacing: 1px; font-size: 0.9em;">🏆 ALBUM PRÉFÉRÉ</p>
<h2 style="margin:5px 0; color: black; font-size: 1.8em; line-height: 1.1;">{best_alb['album']}</h2>
<p style="margin:0; color: gray; font-size: 1.1em; font-weight: bold;">{best_alb['artiste']}</p>
</div>
<div style="text-align: right;">
<h1 style="margin:0; color: #FF8200; font-size: 2.5em;">{best_alb['note']}⭐</h1>
</div>
</div>
</div>
"""
                    st.markdown(html_wrapped, unsafe_allow_html=True)
    # ==========================================
    # ➕ TAB 7 : AJOUTER UN HORS-SÉRIE
    # ==========================================
    with tab7:
        st.markdown("<h1 style='text-align:center; color:#FF8200;'>➕ Ajouter un Hors-Série</h1>", unsafe_allow_html=True)
        
        search_query = st.text_input("🔍 Rechercher l'album sur Spotify :", placeholder="Artiste - Album...")

        if search_query:
            results = sp.search(q=search_query, type='album', limit=5)
            albums = results['albums']['items']

            if albums:
                options = {f"{a['artists'][0]['name']} - {a['name']} ({a['release_date'][:4]})": i for i, a in enumerate(albums)}
                selection = st.selectbox("Sélectionne l'album :", options.keys())
                selected_album = albums[options[selection]]

                st.write("---")
                c_img, c_info = st.columns([1, 2])
                with c_img:
                    st.image(selected_album['images'][0]['url'], use_container_width=True)
                with c_info:
                    st.markdown(f"### {selected_album['name']}")
                    st.markdown(f"**{selected_album['artists'][0]['name']}**")
                    # On ajoute le choix de la date d'écoute
                    hs_date_ecoute = st.date_input("📅 Quand as-tu écouté cet album ?", value=date.today())

                with st.form("form_hors_serie"):
                    c_n, c_p = st.columns([2, 1])
                    with c_n: hs_note = st.slider("Ta Note (Max 5)", 1, 5, 4)
                    with c_p: hs_pays = st.text_input("Drapeau / Pays", placeholder="ex: 🇫🇷")
                    
                    hs_genre = st.text_input("Genre musical", value="")
                    hs_avis = st.text_area("Ton avis")
                    hs_connu = st.checkbox("Je connaissais déjà cet album")

                    if st.form_submit_button("💾 Enregistrer dans l'Odyssée", use_container_width=True):
                        new_row = {
                            'date': hs_date_ecoute.isoformat(), # On utilise la date choisie !
                            'artiste': selected_album['artists'][0]['name'],
                            'album': selected_album['name'],
                            'genre': hs_genre,
                            'annee': selected_album['release_date'][:4],
                            'pays': hs_pays,
                            'cover_url': selected_album['images'][0]['url'],
                            'type': "HORS-SÉRIE",
                            'ecoute': True,
                            'note': hs_note,
                            'avis': hs_avis,
                            'deja_connu': hs_connu
                        }
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        save_data(df)
                        st.balloons()
                        st.success("Album ajouté ! Ton score de l'année vient d'augmenter.")
                        time.sleep(1.5)
                        st.rerun()