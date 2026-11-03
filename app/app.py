import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
import PyPDF2
from docx import Document

# Creating a basic structure for a Python-based web app using Streamlit
app_code = """
import streamlit as st
import re
import pandas as pd
from docx import Document
from io import BytesIO
import PyPDF2

st.set_page_config(page_title="Kingpolis Verlengingsmail Generator", page_icon="🚲")

# --- Dummy Data voor Tarieven (gebaseerd op Tarievenboek 2023) ---
# In een echte app parse je de meegeleverde PDF of gebruik je een database.
def get_premie(postcode, verzekerde_waarde, type_fiets, betaling="jaar"):
    # Simpele postcode check voor regio (Regio 3: bijv 7641)
    # Dit is een vereenvoudigde weergave van de logica.
    postcode_num = int(re.search(r'\d{4}', postcode).group())
    
    # Bepaal regio (dummy logica gebaseerd op het voorbeeld)
    if postcode_num >= 7000 and postcode_num < 8000: 
        regio = 3
    else:
        regio = 1 

    # Bepaal premie op basis van regio en waarde (dummy lookup)
    # Regio 3, e-bike, t/m 4000: 197.85
    if regio == 3 and type_fiets == "E-bike" and verzekerde_waarde <= 4000:
        return "197,85"
    return "Onbekend - Controleer handmatig"

# --- UI Layout ---
st.image("https://www.kingpolis.nl/wp-content/uploads/2021/04/Kingpolis-logo-2.png", width=200)
st.title("Automatische Verlengingsbrief")

uploaded_file = st.file_uploader("Sleep hier het polisblad (PDF) in", type="pdf")

if uploaded_file is not None:
    # Lees de PDF
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
        
    st.text_area("Geëxtraheerde tekst (ter controle)", text, height=150)
    
    try:
        # Regex extractie
        polisnummer = re.search(r'Polisnummer:\s*(Po-\d+)', text).group(1)
        postcode = re.search(r'(\d{4})\s?[A-Z]{2}', text).group(1)
        naam_match = re.search(r'([A-Z]\.\s*[A-Za-z]+)\n', text)
        naam = naam_match.group(1).split()[-1] if naam_match else "Klant"
        einddatum = re.search(r'Einddatum\s*(\d{2}-\d{2}-\d{4})', text).group(1)
        waarde_match = re.search(r'Verzekerde waarde\s*EUR\s*([\d\.,]+)', text)
        waarde = float(waarde_match.group(1).replace('.', '').replace(',', '.')) if waarde_match else 0.0
        
        # Bepaal fietstype (E-bike of Fiets) obv dekkingen
        # In dit voorbeeld gebruiken we de aanwezigheid van 'Garantie' als indicatie voor e-bike
        type_fiets = "E-bike" if "Garantie" in text else "Fiets" 
        
        premie = get_premie(postcode, waarde, type_fiets)
        
        st.success(f"Gegevens succesvol ingelezen:\n- Naam: {naam}\n- Polis: {polisnummer}\n- Waarde: €{waarde}\n- Type: {type_fiets}\n- Berekende Premie: €{premie}")

        # Genereer document
        doc = Document()
        doc.add_paragraph(f"Beste meneer, mevrouw {naam},") 
        doc.add_paragraph()
        doc.add_paragraph(f"U hebt op dit moment bij Kingpolis uw fiets verzekerd. Deze fietsverzekering loopt op {einddatum} af. U moet er toch niet aan denken dat uw fiets nu gestolen wordt! Daarom bieden wij u aan uw fiets doorlopend te verzekeren tegen Casco Compleet (Dekking: diefstal, cascoschade, persoonlijke eigendommen, ongevallen en pechhulp onderweg).")
        doc.add_paragraph()
        doc.add_paragraph(f"Wilt u gebruik maken van dit aanbod dan verzoeken wij u de premie van € {premie} aan ons over te maken op rekening nummer NL57ABNA 0511 99 40 52 ten name van Stichting Betalingscentrum King onder vermelding van polisnummer {polisnummer}.")
        doc.add_paragraph()
        doc.add_paragraph("Uw fiets is bij tijdige betaling aansluitend op uw lopende verzekering doorlopend verzekerd tegen Casco Compleet.")
        doc.add_paragraph()
        doc.add_paragraph("Vertrouwende erop u hiermee voldoende te hebben geïnformeerd.")
        doc.add_paragraph()
        doc.add_paragraph("Met vriendelijke groet,")
        doc.add_paragraph("Kingpolis")
        
        # Sla op in memory buffer
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        st.download_button(
            label="Download Verlengingsbrief (Word)",
            data=buffer,
            file_name=f"Verlengingsvoorstel_{polisnummer}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        st.error(f"Er ging iets mis bij het uitlezen van het polisblad. Controleer of de PDF het juiste formaat heeft. Foutmelding: {e}")
"""

with open("app.py", "w") as f:
    f.write(app_code)
    
print("Streamlit app code written to app.py")
