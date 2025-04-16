import streamlit as st
import os
import base64
from PyPDF2 import PdfReader
from docx import Document
import json

# Chemin du fichier JSON pour stocker le dernier chemin
PATH_TO_JSON = 'last_folder.json'

def load_last_folder():
    if os.path.exists(PATH_TO_JSON):
        with open(PATH_TO_JSON, 'r') as f:
            data = json.load(f)
            return data.get('last_folder', '')
    return ''

def save_last_folder(folder_path):
    with open(PATH_TO_JSON, 'w') as f:
        json.dump({'last_folder': folder_path}, f)

def search_in_pdf(file_path, keyword):
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text = page.extract_text()
            if text and keyword.lower() in text.lower():
                return True
    except Exception as e:
        print(f"Erreur PDF : {file_path} -> {e}")
    return False

def search_in_docx(file_path, keyword):
    try:
        doc = Document(file_path)
        for para in doc.paragraphs:
            if keyword.lower() in para.text.lower():
                return True
    except Exception as e:
        print(f"Erreur DOCX : {file_path} -> {e}")
    return False

def scan_folder(folder_path, keyword):
    matching_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith(".pdf"):
                if search_in_pdf(file_path, keyword):
                    matching_files.append(file_path)
            elif file.lower().endswith(".docx"):
                if search_in_docx(file_path, keyword):
                    matching_files.append(file_path)
    return matching_files

def create_download_link(file_path):
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
        b64 = base64.b64encode(file_data).decode()
        file_name = os.path.basename(file_path)
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}" target="_blank">📥 Télécharger {file_name}</a>'
        return href
    except Exception as e:
        return f"<span style='color:red;'>Erreur lors du téléchargement : {e}</span>"

# --- Streamlit App ---
st.set_page_config(page_title="Recherche dans les fichiers", layout="centered")

st.title("📁 Recherche dans les fichiers PDF et Word")

st.markdown("<hr>", unsafe_allow_html=True)

st.sidebar.image("images.png", width=200)

# Chargement du dernier chemin enregistré dans le fichier JSON
folder_path = load_last_folder()

# Texte d'entrée du chemin du dossier
folder_path_input = st.sidebar.text_input("📂 Chemin du dossier (ex: C:\\Users\\... ou /home/user/...)", value=folder_path)

# Texte d'entrée pour le mot ou l'expression à rechercher
keyword = st.chat_input("🔎 Mot ou expression à rechercher")

# Lorsque la recherche est lancée
if keyword:
    if not os.path.exists(folder_path_input):
        st.error("❌ Le chemin spécifié est invalide ou introuvable.")
    elif not keyword.strip():
        st.warning("⚠️ Veuillez entrer un mot ou une expression.")
    else:
        # Sauvegarde du chemin du dossier dans le fichier JSON
        save_last_folder(folder_path_input)

        with st.spinner("Recherche en cours..."):
            results = scan_folder(folder_path_input, keyword)
            if results:
                st.success(f"{len(results)} fichier(s) contenant « {keyword} » trouvé(s) :")
                for path in results:
                    file_name = os.path.basename(path)  # Affiche juste le nom du fichier
                    download_link = create_download_link(path)
                    st.markdown(f"""
                        <div style="margin-bottom: 10px;">
                            📄 <strong>{file_name}</strong><br>
                            {download_link}
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("🔍 Aucun fichier ne contient ce mot ou cette expression.")
