import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Test de Connexion", page_icon="🔗")

st.title("🚀 Test de connexion Google Sheets")

# 1. Tentative de connexion
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    st.success("✅ La connexion avec l'API Google Sheets est établie !")

    st.write("---")
    st.subheader("📝 Étape 1 : Envoi d'une donnée de test")

    # 2. Création de la donnée de test
    # On respecte exactement les colonnes de ton projet final
    test_df = pd.DataFrame([{
        "date": "2025-12-25",
        "artiste": "TEST_ARTISTE",
        "album": "CONNEXION_OK",
        "genre": "Test",
        "tag": "DEBUG",
        "ecoute": True,
        "note": 5,
        "avis": "Si tu vois cette ligne, c'est que ton téléphone pourra enregistrer tes notes !"
    }])

    if st.button("Envoyer la ligne de test au Google Sheet"):
        conn.update(worksheet="Database", data=test_df)
        st.balloons()
        st.info("Données envoyées ! Vérifie ton fichier Google Sheets maintenant.")

    st.write("---")
    st.subheader("📖 Étape 2 : Lecture du Google Sheet")

    # 3. Lecture pour vérification
    if st.button("Lire les données actuelles du Sheet"):
        data = conn.read(worksheet="Database", ttl=0) # ttl=0 pour forcer la lecture fraîche
        if not data.empty:
            st.write("Voici ce que contient ton Google Sheet actuellement :")
            st.dataframe(data)
        else:
            st.warning("Le Google Sheet semble vide ou l'onglet 'Database' n'existe pas.")

except Exception as e:
    st.error(f"❌ Une erreur est survenue lors de la connexion")
    st.exception(e)
    
    st.info("""
    **Checklist en cas d'erreur :**
    1. As-tu installé la bibliothèque ? (`pip install st-gsheets-connection`)
    2. Ton fichier `.streamlit/secrets.toml` contient-il l'URL du sheet ?
    3. L'onglet de ton Google Sheet s'appelle-t-il bien **Database** (avec un D majuscule) ?
    """)