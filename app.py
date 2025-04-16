import os
import streamlit as st
from PyPDF2 import PdfReader
import docx

def extract_text_from_pdf(pdf_path):
    """Extrait le texte d'un fichier PDF"""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Erreur lors de la lecture du PDF {pdf_path}: {e}")
        return ""

def extract_text_from_docx(docx_path):
    """Extrait le texte d'un fichier DOCX"""
    try:
        doc = docx.Document(docx_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        st.error(f"Erreur lors de la lecture du DOCX {docx_path}: {e}")
        return ""

def file_contains_text(file_path, search_text):
    """Retourne True si le fichier contient le texte recherché, False sinon"""
    search_text = search_text.lower()
    ext = os.path.splitext(file_path)[1].lower()
    content = ""
    
    if ext == ".pdf":
        content = extract_text_from_pdf(file_path)
    elif ext in [".docx"]:
        content = extract_text_from_docx(file_path)
    
    return search_text in content.lower()

def scan_files(directory, search_text):
    """Parcourt un dossier et ses sous-dossiers pour chercher dans les fichiers PDF et DOCX le texte donné"""
    matched_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in [".pdf", ".docx"]:
                file_path = os.path.join(root, file)
                if file_contains_text(file_path, search_text):
                    matched_files.append(file_path)
    return matched_files

# Interface Streamlit
st.title("Recherche de texte dans PDF et DOCX")

# Saisie du répertoire et du texte de recherche
search_text = st.text_input("Texte de recherche:")
directory = st.text_input("Chemin du dossier à scanner:")

if st.button("Lancer la recherche"):
    if not search_text:
        st.error("Veuillez saisir le texte à rechercher.")
    elif not directory or not os.path.isdir(directory):
        st.error("Veuillez saisir un chemin de dossier valide.")
    else:
        st.info(f"Recherche de '{search_text}' dans le dossier {directory} en cours...")
        matched_files = scan_files(directory, search_text)
        
        if matched_files:
            st.success(f"Trouvé {len(matched_files)} fichier(s) contenant le texte recherché :")
            for file in matched_files:
                st.write(file)
        else:
            st.warning("Aucun fichier ne correspond à la recherche.")
