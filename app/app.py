import streamlit as st
import re
import pandas as pd
from docx import Document
from docx.shared import Pt
from io import BytesIO
import PyPDF2

st.set_page_config(page_title="Kingpolis Verlengingsmail Generator", page_icon="🚲")

def get_premie(postcode, verzekerde_waarde, type_fiets, betaling="jaar"):
    try:
        postcode_num = int(re.search(r'\d{4}', postcode).group())
        regio = 3 if (postcode_num >= 7000 and postcode_num < 8000) else 1 
        if regio == 3 and type_fiets == "E-bike" and verzekerde_waarde <= 4000:
            return "197,85"
        return "Onbekend - Controleer handmatig"
    except:
        return "Onbekend"

st.image("https://www.kingpolis.nl/wp-content/uploads/2021/04/Kingpolis-logo-2.png", width=200)
st.title("Automatische Verlengingsbrief")

uploaded_file = st.file_uploader("Sleep hier het polisblad (PDF) in", type="pdf")

if uploaded_file is not None:
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
        
    with st.expander("Klik hier om de ruwe tekst uit de PDF te zien (handig voor controle)"):
        st.text(text)
        
    try:
        polis_match = re.search(r'(Po-\d+)', text)
        # Hier plakken we direct de 'v' achter het polisnummer
        polisnummer_v = polis_match.group(1) + "v" if polis_match else "[Polisnummer]v"
        
        pc_match = re.search(r'(\d{4})\s?[A-Z]{2}', text)
        postcode = pc_match.group(1) if pc_match else "0000"
        
        naam_match = re.search(r'([A-Z]\.\s*[A-Za-z\s]+?)\n', text)
        naam = naam_match.group(1).split()[-1] if naam_match else "[Naam]"
        
        eind_match = re.search(r'Einddatum[\s\S]*?(\d{2}-\d{2}-\d{4})', text, re.IGNORECASE)
        einddatum = eind_match.group(1) if eind_match else "[Datum]"
        
        waarde_match = re.search(r'EUR\s*([\d\.,]+)', text)
        waarde = float(waarde_match.group(1).replace('.', '').replace(',', '.')) if waarde_match else 0.0
        
        type_fiets = "E-bike" if "Garantie" in text or "e-bike" in text.lower() else "Fiets" 
        premie = get_premie(postcode, waarde, type_fiets)
        
        st.success(f"Gegevens uitgelezen:\nNaam: {naam} | Polis: {polisnummer_v} | Waarde: €{waarde} | Type: {type_fi
