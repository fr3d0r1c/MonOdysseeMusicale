import streamlit as st
import pandas as pd
import json
import requests
import wikipedia
import time
from datetime import date, datetime
from streamlit_calendar import calendar
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. CONFIGURATION & DESIGN "CULTURE FUSION"
# ==========================================
st.set_page_config(
    page_title="My Music 2026", 
    page_icon="🎵", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Avancé : Mode Sombre, Dégradés France/CIV, Cartes modernes
st.markdown("""
    <style>
        /* FOND & STRUCTURE */
        .stApp { background-color: #0E1117; }
        .block-container { padding-top: 1rem !important; padding-bottom: 3rem !important; }

        /* TITRE PRINCIPAL (Gradient Fusion : Orange CIV -> Blanc -> Bleu FR) */
        h1 {
            background: linear-gradient(to right, #FF8200, #FFFFFF, #0055A4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
            text-align: center;
            margin-bottom: 0px;
        }
        
        /* SOUS-TITRES & TEXTES */
        h2, h3, h4 { color: #F0F2F6; text-align: center; }
        p { font-size: 1.1rem; }

        /* CARTE "PROCHAIN ALBUM" (Style Kita-Moderne) */
        .next-album-card {
            background: linear-gradient(145deg, #1E1E1E, #25262B);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin-top: 30px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
            border-left: 5px solid #009A44;  /* Vert CIV */
            border-right: 5px solid #EF4135; /* Rouge FR */
            border-top: 1px solid #333;
            border-bottom: 1px solid #333;
            transition: transform 0.3s;
        }
        .next-album-card:hover { transform: translateY(-5px); }
        
        .next-album-cover {
            width: 120px; 
            border-radius: 8px; 
            margin: 15px auto; 
            display: block;
            border: 2px solid #FF8200; /* Touche Orange */
            box-shadow: 0 5px 15px rgba(0,0,0,0.5);
        }

        /* BOUTONS (Dégradé Action) */
        div.stButton > button {
            background: linear-gradient(90deg, #FF8200 0%, #EF4135 100%);
            color: white; border: none; font-weight: bold; width: 100%;
            border-radius: 8px;
            height: 50px;
        }
        div.stButton > button:hover {
            box-shadow: 0 0 15px rgba(255, 130, 0, 0.4);
            color: white;
        }
        
        /* BARRE DE PROGRESSION */
        .stProgress > div > div > div > div { background-color: #FF8200; }
        
        /* DIVERS UI */
        .stImage { display: flex; justify_content: center; }
        .fc { height: 600px !important; min-height: 600px !important; }
        
        /* Badge style pour les cartes galerie */
        .badge-status {
            font-size: 0.8em;
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. GESTION DES DONNÉES (ROBUSTE)
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    """Charge les données, gère les types et initialise les colonnes manquantes."""
    try:
        df = conn.read(worksheet="Database", ttl=0)
        
        # 1. Initialisation si vide (Fallback JSON)
        if df.empty or len(df) < 10:
            try:
                with open("journal_musical_ULTIMATE.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                df = pd.DataFrame.from_dict(data, orient='index').reset_index().rename(columns={'index': 'date'})
                conn.update(worksheet="Database", data=df)
                st.cache_data.clear()
            except FileNotFoundError:
                st.error("Fichier JSON introuvable. Veuillez vérifier le dépôt.")
                return pd.DataFrame()
        
        # 2. Vérification et Création des colonnes
        expected_cols = {
            'ecoute': False, 
            'note': 0, 
            'avis': "", 
            'deja_connu': False, 
            'pays': "🌍"
        }
        updated = False
        for col, default_val in expected_cols.items():
            if col not in df.columns:
                df[col] = default_val
                updated = True
        
        # 3. Nettoyage strict des types (Anti-Bug Pandas)
        df['ecoute'] = df['ecoute'].fillna(False).infer_objects(copy=False).astype(bool)
        df['deja_connu'] = df['deja_connu'].fillna(False).infer_objects(copy=False).astype(bool)
        df['note'] = pd.to_numeric(df['note'], errors='coerce').fillna(0).astype(int)
        
        # Conversion texte sécurisée
        if 'avis' in df.columns:
            df['avis'] = df['avis'].astype(str).replace('nan', '')
        if 'pays' in df.columns:
            df['pays'] = df['pays'].astype(str).replace('nan', '🌍')

        # 4. Sauvegarde si structure modifiée
        if updated:
            conn.update(worksheet="Database", data=df)
            st.cache_data.clear()
            
        return df
    except Exception as e:
        st.error(f"Erreur critique lors du chargement : {e}")
        return pd.DataFrame()

def save_data(df):
    """Sauvegarde les données dans Google Sheets."""
    try:
        conn.update(worksheet="Database", data=df)
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Erreur de sauvegarde : {e}")

@st.cache_data
def get_album_infos(artiste, album):
    """Récupère pochette et année via iTunes API avec image par défaut."""
    # Image par défaut (Vinyle propre)
    default_cover = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/12in-Vinyl-LP-Record-Angle.jpg/640px-12in-Vinyl-LP-Record-Angle.jpg"
    infos = {"cover": default_cover, "year": ""}
    
    try:
        # Recherche iTunes
        term = f"{artiste} {album}"
        url = f"https://itunes.apple.com/search?term={term}&entity=album&limit=1"
        res = requests.get(url, timeout=3).json()
        
        if res['resultCount'] > 0:
            data = res['results'][0]
            # On prend la grande image (600x600)
            infos["cover"] = data.get('artworkUrl100', default_cover).replace("100x100", "600x600")
            infos["year"] = data.get('releaseDate', "")[:4]
    except:
        pass # En cas d'erreur (pas de réseau, etc), on garde l'image par défaut
        
    return infos

# ==========================================
# 3. LOGIQUE & INTERFACE
# ==========================================
df = load_data()

if not df.empty:
    
    # --- HEADER & KPI ---
    nb_valide = df[df['ecoute'] == True].shape[0]
    total = len(df)
    
    # Stats détaillées
    nb_decouvertes = df[(df['ecoute'] == True) & (df['deja_connu'] == False)].shape[0]
    nb_classiques = df[(df['ecoute'] == True) & (df['deja_connu'] == True)].shape[0]
    
    st.title("🎹 Odyssée Musicale 2026")
    
    # Barre de progression
    if total > 0:
        st.progress(nb_valide / total)
    else:
        st.progress(0)
    
    # Métriques
    c1, c2, c3 = st.columns(3)
    c1.metric("🏆 Global", f"{int((nb_valide/total)*100)}%" if total > 0 else "0%")
    c2.metric("🟢 Découvertes", nb_decouvertes)
    c3.metric("🔵 Classiques", nb_classiques)

    # --- SIDEBAR (Recherche Avancée) ---
    with st.sidebar:
        st.header("🔍 Rechercher & Noter")
        st.caption("Accès rapide pour noter un album.")
        
        # Création d'une liste formatée pour le menu
        # On stocke l'index original pour le retrouver facilement
        options_dict = {f"{r['pays']} {r['artiste']} - {r['album']}": i for i, r in df.iterrows()}
        
        choix = st.selectbox("Choisir un album", ["-- Sélectionner --"] + list(options_dict.keys()))
        
        if choix != "-- Sélectionner --":
            # On récupère l'index direct via le dictionnaire (Plus robuste que le split string)
            idx_sel = options_dict[choix]
            row_sel = df.loc[idx_sel]
            
            st.divider()
            st.write(f"**{row_sel['album']}**")
            
            with st.form(f"sidebar_form_{idx_sel}"):
                # Pré-remplissage intelligent
                current_note = int(row_sel['note']) if row_sel['note'] > 0 else 5
                
                s_note = st.slider("Note", 1, 5, current_note)
                s_avis = st.text_area("Avis", value=row_sel['avis'])
                s_connu = st.checkbox("Déjà connu (Classique)", value=row_sel['deja_connu'])
                s_pays = st.text_input("Drapeau", value=row_sel['pays'])
                
                if st.form_submit_button("💾 Enregistrer"):
                    df.at[idx_sel, 'ecoute'] = True
                    df.at[idx_sel, 'note'] = s_note
                    df.at[idx_sel, 'avis'] = s_avis
                    df.at[idx_sel, 'deja_connu'] = s_connu
                    df.at[idx_sel, 'pays'] = s_pays
                    save_data(df)
                    st.toast("Modifications enregistrées !", icon="✅")
                    time.sleep(1)
                    st.rerun()

    # --- NAVIGATION ---
    tab1, tab2, tab3, tab4 = st.tabs(["🎧 À l'écoute", "📅 Calendrier", "🏆 Découvertes", "🔄 Classiques"])

    # ==========================================
    # TAB 1 : LE PLAYER
    # ==========================================
    with tab1:
        df_todo = df[df['ecoute'] == False].sort_values('date')
        
        if not df_todo.empty:
            current = df_todo.iloc[0]
            # Récupération de l'index réel dans le dataframe principal
            real_idx = df[df['date'] == current['date']].index[0]
            
            # Infos API
            infos = get_album_infos(current['artiste'], current['album'])
            
            # Affichage Principal
            st.markdown(f"## {current['pays']} {current['artiste']}")
            st.markdown(f"#### *{current['album']}* ({infos['year']})")
            
            # Image + Cadre
            st.image(infos["cover"], width=320)
            
            # Wikipédia (Replié)
            with st.expander("📖 Histoire & Anecdotes"):
                try:
                    wikipedia.set_lang("fr")
                    res_wiki = wikipedia.search(f"{current['album']} {current['artiste']}")
                    if res_wiki:
                        page = wikipedia.page(res_wiki[0])
                        st.info("💡 **Le saviez-vous ?**")
                        st.write(page.summary[:700] + "...")
                        st.markdown(f"[Lire l'article complet]({page.url})")
                    else:
                        st.warning("Pas d'article Wikipédia trouvé.")
                except:
                    st.write("Connexion Wikipédia indisponible.")

            st.divider()

            # Zone de Notation
            with st.container(border=True):
                with st.form("main_notation_form"):
                    st.write("### 🎙️ Ton verdict")
                    
                    c_note, c_pays = st.columns([3, 1])
                    with c_note:
                        val_note = st.feedback("stars")
                    with c_pays:
                        val_pays = st.text_input("Pays", value=current['pays'], help="Mets un emoji drapeau ici !")
                    
                    val_avis = st.text_area("Ta critique", height=100, placeholder="Production, flow, émotion...")
                    val_connu = st.checkbox("Je connaissais déjà cet album (Classique)")
                    
                    submit = st.form_submit_button("✅ Valider l'écoute")
                    
                    if submit:
                        df.at[real_idx, 'ecoute'] = True
                        df.at[real_idx, 'note'] = (val_note + 1) if val_note is not None else 3
                        df.at[real_idx, 'avis'] = val_avis
                        df.at[real_idx, 'deja_connu'] = val_connu
                        df.at[real_idx, 'pays'] = val_pays
                        save_data(df)
                        
                        st.toast("Album validé avec succès !", icon="🎉")
                        st.balloons()
                        time.sleep(1.5)
                        st.rerun()
            
            # TEASING DU LENDEMAIN
            if len(df_todo) > 1:
                next_up = df_todo.iloc[1]
                next_infos = get_album_infos(next_up['artiste'], next_up['album'])
                
                st.markdown(f"""
                <div class='next-album-card'>
                    <p style='color:#FF8200; margin:0; font-weight:bold; letter-spacing: 2px; font-size: 0.8em;'>🔜 DEMAIN</p>
                    <img src='{next_infos['cover']}' class='next-album-cover'>
                    <h3 style='margin:5px 0; font-size: 1.2em;'>{next_up['pays']} {next_up['artiste']}</h3>
                    <p style='color:#aaa; font-style:italic; margin:0;'>{next_up['album']}</p>
                </div>
                """, unsafe_allow_html=True)
                
        else:
            st.success("🏆 INCROYABLE ! Tu as terminé le challenge 2026 !")
            st.balloons()

    # ==========================================
    # TAB 2 : CALENDRIER & GALERIE
    # ==========================================
    with tab2:
        view_mode = st.radio("Vue :", ["Liste 📱", "Grille 🖥️", "Galerie 🖼️"], horizontal=True, label_visibility="collapsed")
        
        if view_mode == "Galerie 🖼️":
            st.caption("Ta collection classée par mois.")
            # Conversion date pour tri
            df['dt_obj'] = pd.to_datetime(df['date'])
            # On parcourt les mois de 1 à 12
            for month_num in range(1, 13):
                df_month = df[df['dt_obj'].dt.month == month_num]
                
                if not df_month.empty:
                    month_name = df_month.iloc[0]['dt_obj'].strftime('%B %Y').capitalize()
                    
                    with st.expander(f"📅 {month_name}", expanded=(month_num == date.today().month)):
                        cols = st.columns(4)
                        for i, (_, row) in enumerate(df_month.iterrows()):
                            with cols[i % 4]:
                                info_art = get_album_infos(row['artiste'], row['album'])
                                with st.container(border=True):
                                    st.image(info_art['cover'], use_container_width=True)
                                    st.markdown(f"**{row['pays']} {row['artiste']}**")
                                    # Badge Statut
                                    if row['ecoute']:
                                        if row['deja_connu']:
                                            st.markdown("<span class='badge-status' style='background:#17a2b8; color:white'>Classique</span>", unsafe_allow_html=True)
                                        else:
                                            st.markdown("<span class='badge-status' style='background:#28a745; color:white'>Découverte</span>", unsafe_allow_html=True)
                                    else:
                                        st.caption(f"📅 {row['date']}")
        else:
            # Mode Calendrier (Liste/Grille)
            events = []
            today_iso = str(date.today())
            
            for _, r in df.iterrows():
                evt_title = f"{r['pays']} {r['artiste']}"
                
                if r['ecoute']:
                    if r['deja_connu']:
                        color, title = "#17a2b8", f"🔄 {evt_title}" # Bleu
                    else:
                        color, title = "#28a745", f"✅ {evt_title}" # Vert
                elif str(r['date']) < today_iso:
                    color, title = "#dc3545", f"⚠️ {evt_title}" # Rouge
                else:
                    color, title = "#6c757d", f"🎵 {evt_title}" # Gris
                
                events.append({
                    "title": title, 
                    "start": str(r['date']), 
                    "allDay": True, 
                    "backgroundColor": color, 
                    "borderColor": color
                })
            
            cal_mode = "listMonth" if "Liste" in view_mode else "dayGridMonth"
            calendar(events=events, options={
                "initialDate": "2026-01-01",
                "locale": "fr",
                "headerToolbar": {"left": "prev,next", "center": "title", "right": ""},
                "initialView": cal_mode,
                "height": "600px"
            }, key=f"cal_{view_mode}")

    # ==========================================
    # TAB 3 : TIER LIST (DÉCOUVERTES - VERT)
    # ==========================================
    with tab3:
        st.caption("🟢 Tes nouvelles découvertes de l'année.")
        df_green = df[(df['ecoute'] == True) & (df['deja_connu'] == False)]
        
        if df_green.empty:
            st.info("Aucune découverte validée pour l'instant.")
        else:
            tiers = [(5, "S-TIER", "🚨"), (4, "A-TIER", "🟠"), (3, "B-TIER", "🟡"), (2, "C-TIER", "🟢"), (1, "D-TIER", "🟤")]
            for note, label, icon in tiers:
                sub_df = df_green[df_green['note'] == note]
                if not sub_df.empty:
                    st.subheader(f"{icon} {label}")
                    for _, row in sub_df.iterrows():
                        r_idx = df[df['date'] == row['date']].index[0]
                        with st.expander(f"{row['pays']} {row['artiste']} - {row['album']}"):
                            c_img, c_txt = st.columns([1, 3])
                            with c_img:
                                inf = get_album_infos(row['artiste'], row['album'])
                                st.image(inf['cover'], width=100)
                            with c_txt:
                                st.write(f"**Avis :** {row['avis']}")
                                if st.button("Passer en 'Classique' (Bleu)", key=f"btn_blue_{r_idx}"):
                                    df.at[r_idx, 'deja_connu'] = True
                                    save_data(df)
                                    st.rerun()

    # ==========================================
    # TAB 4 : CLASSIQUES (RELECTURES - BLEU)
    # ==========================================
    with tab4:
        st.caption("🔵 Tes classiques et relectures.")
        df_blue = df[(df['ecoute'] == True) & (df['deja_connu'] == True)]
        
        if df_blue.empty:
            st.info("Rien ici.")
        else:
            # Tri par note décroissante
            for _, row in df_blue.sort_values('note', ascending=False).iterrows():
                r_idx = df[df['date'] == row['date']].index[0]
                with st.expander(f"🔵 {row['pays']} {'⭐'*row['note']} | {row['artiste']} - {row['album']}"):
                    c_img, c_txt = st.columns([1, 3])
                    with c_img:
                        inf = get_album_infos(row['artiste'], row['album'])
                        st.image(inf['cover'], width=100)
                    with c_txt:
                        st.write(f"**Avis :** {row['avis']}")
                        if st.button("Passer en 'Découverte' (Vert)", key=f"btn_green_{r_idx}"):
                             df.at[r_idx, 'deja_connu'] = False
                             save_data(df)
                             st.rerun()