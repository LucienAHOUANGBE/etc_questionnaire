"""
@auteur: Vignawou Lucien AHOUANGBE
@affiliation: Excellent Treaning Center (ETC)
@date: Saturday 15 Nov 2025 19:49
"""

import streamlit as st
from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime
import dropbox
import smtplib
from email.message import EmailMessage
import re




# Les configurations ---------------------------------------------------------


# ----------- Debut de la page
st.set_page_config(
    page_title="Inscription ETC Formation",
    page_icon= "🎓",
    layout='centered'
)



CONFIG = {
    'PYTHON1': 30,
    'RMaxPlace': 30,
    "spreadSheetID": st.secrets.get("SPREADSHEET_ID"),
    "driveFolderID": st.secrets.get("DRIVE_FOLDER_ID")
}

listOfLogicielInit = {
   'PYTHON1' :  'Python 1',
   'R1' :  'R 1',
}

logicielDefinition = {
    'PYTHON1': "Python 1 : Introduction à python",
    'R1': "R 1 : Introduction à R + Analyse de données"
}

MaxPlace = {f: 30 for f in listOfLogicielInit.keys()}

smtp_user = st.secrets.Mails['SMTP_USER']
smtp_pass = st.secrets.Mails['SMTP_PASS']

# Mise à jours tu CSS


st.markdown("""
<style>

    /* ---------- BACKGROUND ---------- */

    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: transparent;
    }


    /* ---------- HEADER ---------- */

    .header-title {
        text-align: center;
        font-size: 3em;
        margin-bottom: 0.5rem;
        /* color: black;*/
        text-shadow: 2px 2px 4px rgba(0,0,0,0.35);
    }


    /* ---------- FORMULAIRE ---------- */

    div[data-testid="stForm"] {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        backdrop-filter: blur(6px);
    }

   


    /* ---------- CARDS ---------- */

    .quota-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.10);
        text-align: center;
        margin: 1rem 0;
    }
            
    /* Forcer la couleur du texte des labels des checkboxes */
    label p {
        color: black;
    }
    
    
           


    /* ---------- TITRES DE SECTION ---------- */

    .section-title {
        color: #667eea;
        font-size: 1.5em;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
        font-weight: 600;
    }


    /* ---------- WARNING BOX ---------- */

    .warning-box {
        background: #fff8e1;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 8px;
        color: #856404;
        margin-bottom: 1rem;
        box-shadow: 0 3px 8px rgba(0,0,0,0.1);
    }


    /* ---------- ERROR BOX ---------- */

    .error-box {
        background: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1.5rem;
        border-radius: 10px;
        color: #721c24;
        box-shadow: 0 3px 8px rgba(0,0,0,0.15);
    }


    /* ---------- SUCCESS BOX (ETC DESIGN) ---------- */

    .success-box {
        background: #f4eaff;
        border-left: 5px solid #6f42c1;
        padding: 1.5rem;
        border-radius: 10px;
        color: #3c1c6f;
        box-shadow: 0 4px 12px rgba(111, 66, 193, 0.18);
    }
            
    /* On centre la zone image et on limite la largeur max */
    div[data-testid="stImage"] {
        max-width: 900px;
        width: 90%;
        margin: 15px auto;
    }

    /* L'image s'adapte à la taille de la zone */
    div[data-testid="stImage"] img {
        width: 100% !important;
        height: auto !important;
        border-radius: 16px !important;
        object-fit: contain !important;
    }

    /* Mobile : quasi plein écran */
    @media (max-width: 600px) {
        div[data-testid="stImage"] {
            width: 98%;
        }
    }


</style>
""", unsafe_allow_html=True)



# Les connexions serveur ---------------------------------------------------
# Google sheets


st.cache_resource()
def connect_to_server():

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    Credentials_dict = {
    "type": st.secrets["gcp_service_account"]["type"],
    "project_id": st.secrets["gcp_service_account"]["project_id"],
    "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
    "private_key": st.secrets["gcp_service_account"]["private_key"],
    "client_email": st.secrets["gcp_service_account"]["client_email"],
    "client_id": st.secrets["gcp_service_account"]["client_id"],
    "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
    "token_uri": st.secrets["gcp_service_account"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"],
    "universe_domain": st.secrets["gcp_service_account"]["universe_domain"]
    }



    creds = Credentials.from_service_account_info(
        Credentials_dict,
        scopes=SCOPES
    )

    
    try:
        client = gspread.authorize(creds)
        sht = client.open_by_key(CONFIG["spreadSheetID"])
        #drv = build(serviceName='drive', version='v3', credentials=creds)
        dbx = dropbox.Dropbox(st.secrets['dropbox']['token'])
        return client, sht, dbx
    
    except:
        st.error(
            "Connexion serveur impossible !", icon="❌"
        )
        return None, None, None





def send_to_sheet(data, shtname):
    
    try:
        _, gsht,_ = connect_to_server()
        if gsht is None:
            raise Exception("Impossible de récupérer le fichier Google Sheets.")
        
        try:
            # Si la feuille existe
            wsht = gsht.worksheet(shtname)
            wsht.append_row(list(data.values()))

        except gspread.exceptions.WorksheetNotFound:

            # Créer la feuille si elle n'existe pas
            wsht = gsht.add_worksheet(title=shtname, rows=100, cols=30)
            wsht.append_row(list(data.keys()))
            wsht.append_row(list(data.values()))

    except Exception as e:
        raise Exception(f"Erreur sauvegarde Sheets: {e}")


def send_to_dropbox(entry_file, dest_files_name, dest_folder="/Formation/Vague1"):
    _, _, dbx= connect_to_server()
    file_bytes = entry_file.read()
    dest_path = f"{dest_folder}/{dest_files_name}"
    dbx.files_upload(file_bytes, dest_path)
    
    

# ontenir le nombre actuel

# calculer le cota actuelle




def get_total_enrolled(formation):
    _, gsht, _ = connect_to_server()

    nb = 0
    if gsht is None:
        raise Exception("Impossible de récupérer le fichier Google Sheets.")
    try:
        # Si la feuille existe
        wsht = gsht.worksheet(formation)
        nb = len(wsht.get_all_values()) - 1
    except:
        pass
    return nb
    
# ActualEnrolledNumber = {f: get_total_enrole(f) for f in listOfLogicielInit.keys()}
# Calculer les codate
quotasRestant = {f: MaxPlace[f] - get_total_enrolled(f) for f in listOfLogicielInit.keys()}


# update softward list to display
listOfLogiciel = {}
for i, j in listOfLogicielInit.items(): 
    if quotasRestant[i]>0:
        listOfLogiciel[i]= j




st.cache_data()
def getListOfDomaine():
    return [
        "Agronomie",
        "Anthropologie",
        "Arts plastiques et visuels",
        "Banque et assurance",
        "Bâtiment et travaux publics (BTP)",
        "Biologie",
        "Blockchain et fintech",
        "Chimie",
        "Cinéma et audiovisuel",
        "Communication, journalisme et médias",
        "Comptabilité et finance",
        "Couture, hôtellerie et restauration",
        "Criminologie",
        "Cybersécurité",
        "Data science et big data",
        "Design et architecture",
        "Développement durable et climat",
        "Développement rural",
        "Droit international",
        "Droit privé (civil, commercial, pénal, etc.)",
        "Droit public (administratif, constitutionnel, fiscal…)",
        "Économie",
        "Éducation et sciences de l’éducation",
        "Électronique et électrotechnique",
        "Énergies renouvelables et environnement",
        "Enseignement (primaire, secondaire, supérieur)",
        "Entrepreneuriat et innovation",
        "Études en gouvernance et institutions publiques",
        "Études sur le genre et inclusion sociale",
        "Foresterie",
        "Formation professionnelle et technique",
        "Géographie",
        "Gestion de l’environnement",
        "Gestion des entreprises",
        "Histoire",
        "Informatique et intelligence artificielle",
        "Intelligence artificielle appliquée",
        "Kinésithérapie et rééducation",
        "Littérature et langues",
        "Logistique et transport",
        "Maintenance industrielle",
        "Management des ressources humaines",
        "Marketing et commerce international",
        "Mathématiques et statistiques",
        "Mécanique automobile et industrielle",
        "Médecine",
        "Métiers du numérique (web, graphisme, réseaux, etc.)",
        "Musique, théâtre et danse",
        "Nutrition et diététique",
        "Odontologie (chirurgie dentaire)",
        "Orientation scolaire et professionnelle",
        "Patrimoine et culture",
        "Pêche et aquaculture",
        "Pédagogie et andragogie",
        "Pharmacie",
        "Philosophie",
        "Physique",
        "Psychologie",
        "Santé publique",
        "Sciences cognitives",
        "Sciences de l’ingénieur (mécanique, électrique, civil, industriel, etc.)",
        "Sciences infirmières",
        "Sciences politiques et relations internationales",
        "Sécurité alimentaire",
        "Sociologie",
        "Technologies de l’information et de la communication (TIC)",
        "Autre"]

domaineList = getListOfDomaine()


st.cache_resource()
def getListOfCountryName():
    import pycountry
    from babel import Locale

    local = Locale("fr")
    pays_fr = {}
    
    for country in pycountry.countries:
        try:  
            # recupérer le code pays iso3 et le nom du pays à partir du code iso2  
            pays_fr[f'{country.alpha_3}'] = local.territories[country.alpha_2]
        except KeyError:
            pass
    return(pays_fr)


paysList = getListOfCountryName()



col1, col2, col3, col4, col5 = st.columns([1,2,1,2,1])
with col2:
    st.image("statics/ETC Slogan.png", width='stretch')


with col4:
    st.image("statics/Future Learders.jpg", width='stretch')
    

st.markdown("<h1 style='text-align: center;'>🎓 Formation Programme EcoDA</h1>", unsafe_allow_html=True)

st.markdown("""
<p class="header-title">
    Première Vague - Inscriptions jusqu'au 22 novembre
</p>
""", unsafe_allow_html=True)

st.markdown("""
<p class="header-title">
    Parrainé par <a href="https://sites.google.com/view/etc-site">ETC</a> - Programe EcoDA - Association Future Leaders
</p>
""", unsafe_allow_html=True)

st.markdown("""
        <div class="section-title">
            ⚠️ Information importante - Condition d'éligibilité
        </div>
    """, unsafe_allow_html=True)

st.markdown(
    """
        <div class="warning-box">
            <p>1. Avoir au minimum BAC+3. Ne vous inquiétez pas, une autre session plus large se lancer </p>
            <p>2. 📅 Calendrier : 7 séances les samedis 8h30-11h30 GMT. Disponibilité pouvant être adapter avec </p>
        </div>
    """, unsafe_allow_html=True
)



col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    <div class="quota-card">
        <h3 style="color: black;">🐍 Python</h3>
        <p style="color: black;"><strong>Niveau 1</strong></p>
        <h2 style="color: red;">{quotasRestant['PYTHON1']}/{MaxPlace['PYTHON1']}</h2>
        <p style="color: black;">places disponibles</p>
    </div>
    """, unsafe_allow_html=True)

    python_pct = (quotasRestant['PYTHON1']/MaxPlace['PYTHON1']) * 100
    st.progress(python_pct / 100)

with col2:
    st.markdown(f"""
    <div class="quota-card">
        <h3 style="color: black;">📊 R</h3>
        <p style="color: black;"><strong>Niveau 1</strong></p>
        <h2 style="color: red;">{quotasRestant['R1']}/{MaxPlace['PYTHON1']}</h2>
        <p style="color: black;">places disponibles</p>
    </div>
    """, unsafe_allow_html=True)
    r_pct = (quotasRestant['R1'] / MaxPlace['R1']) * 100
    st.progress(r_pct / 100)

st.markdown("---")


with st.form('formIncription'):
    st.markdown("""
        <div class="section-title">
            📝 Choix de formation
        </div>
    """, unsafe_allow_html=True)


    formation = st.selectbox(
        "Formation souhaitée*",
        listOfLogiciel.keys(),
        placeholder="Choisissez une formation. Attention aux accents. Ex: Économie",
        index=None,
        format_func=lambda x: logicielDefinition[x]
    )

    st.markdown('<div class="section-title">👤 Informations personnelles</div>', unsafe_allow_html=True)

    genre = st.radio(
        "Genre *",
        ["F", "M"], 
        captions=['Feminin', 'Masculin'], 
        index=None, 
        horizontal=True
    )


    col1, col2 = st.columns(2)
    with col1:
        nom = st.text_input("Nom *", placeholder="Votre nom")
    with col2:
        prenom = st.text_input("Prénom *", placeholder="Votre prénom")


    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input("Email *", placeholder="votre.email@exemple.com")
    with col2:
        nationnalite = st.selectbox(
            "Nationalité *",
            paysList.keys(),
            index=None,
            placeholder="Selectionner un pays",
            format_func= lambda x: paysList.get(x, "")
        )
    
    pays = st.selectbox(
            "Pays de résidence *",
            paysList.keys(),
            index=None,
            placeholder="Selectionner un pays",
            format_func= lambda x: paysList.get(x, "") 
        )
    
    col1, col2 = st.columns(2)
    with col1:
        ville = st.text_input(
            "Ville de résidence *",
            placeholder="Ex: Lomé"
        )
    with col2: 
        quartier = st.text_input(
            "Quartier de résidence *",
            placeholder="Ex: Agoè-Cacavéli"
        )


    col1, col2 = st.columns(2)
    with col1:
        telephone = st.text_input("Téléphone (Whatsapp)*", placeholder="+228 XX XX XX XX")
    with col2:
        date_naissance = st.date_input("Date de naissance *")

    st.markdown(
        """
            <div class="warning-box">
                ⚠️ Veuillez fournir les informations sur une pièces d'identité en cours de validité.
            </div>
        """, unsafe_allow_html=True
    )


    col1, col2, col3 = st.columns(3)
    with col1:
        id_type = st.selectbox(
            "Type de pièce d'identité *",
            ["CNI","Passeport", "Permis de conduire", "Autre"],
            index=None,
            placeholder="Selectionner un type"
        )

    with col2:
        id_num = st.text_input(
            "N° pièce *",
            placeholder="AB 123456"
        )

    with col3:
        id_enddate = st.date_input("Date d'expiration *")

    
    st.markdown("""
        <div class="section-title">
            🎓 Formation académique
        </div>
    """, unsafe_allow_html=True)


    domaine = st.selectbox(
        "Votre domaine *",
        domaineList,
        index=None,
        placeholder="Selectionner un domaine"
    )


    col1, col2, col3 = st.columns(3)
    with col1:
        educ_niveau = st.selectbox(
            "Niveau d'étude *",
            [f"Bac +{i}" for i in range(3, 9)],
            placeholder="Plus haut niveau",
            index=None
        )

    with col2:
        diplome = st.text_input(
            "Dernier diplôme obtenu *",
            placeholder="Ex: Licence en informatique"
        )

    with col3:
        etablissement = st.text_input(
            "Établissement *",
            placeholder="Ex: Université de lomé"
        )



    st.markdown("""
        <div class="section-title">
            📄 Documents justificatifs
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="warning-box">
            <p>⚠️ <strong>Important :</strong> Les fichiers doivent être au format PDF et ne pas dépasser 10 MB chacun.</p>
            <p>Pour des raisons de sécurités, vos documents fournis seront détruits une fois les informations validées.</p>
        </div>
    """, unsafe_allow_html=True)

    diplome_pdf = st.file_uploader("Copie du diplôme (PDF) *", type=['pdf'], key="diplome")
    piece_identite_pdf = st.file_uploader("Pièce d'identité (PDF) *", type=['pdf'], key="piece_identite")

    st.markdown("""
        <div class="section-title">
            ✅ Engagement et conditions
        </div>
    """, unsafe_allow_html=True)

    accepte_conditions = st.checkbox(
        "J'accepte que mes documents soient vérifiés et je comprends que toute fausse déclaration entraînera une exclusion définitive. *"
    )
    
    confirme_presence = st.checkbox(
        "Je m'engage à être présent(e) à TOUTES les séances. Les absences non justifiées entraînent une exclusion automatique. *"
    )
    
    confirme_connexion = st.checkbox(
        "Je confirme disposer d'une bonne connexion Internet pour suivre les sessions en ligne. *"
    )
    

    submitted = st.form_submit_button("🚀 Envoyer mon inscription", width='stretch')

    if submitted:
        
        pattern_email = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        pattern_tel = r"^\+[1-9]\d{1,3}(\s?\d{2,4}){2,5}$"

        if not all([formation, genre, nom, prenom, nationnalite, email, pays, ville, quartier, telephone, date_naissance, id_type, id_num, id_enddate, domaine, educ_niveau, diplome, etablissement]):
            st.markdown('<div class="error-box">❌ Veuillez remplir tous les champs obligatoires.</div>', unsafe_allow_html=True)
        elif not re.match(pattern_email, email.strip()):
            st.markdown('<div class="error-box">❌ Le format email est incorrect. Ex: abc@def.ghf</div>', unsafe_allow_html=True)
        elif not re.match(pattern_tel, telephone.strip()):
            st.markdown('<div class="error-box">❌ Numéro invalide. Exemple : +228 90 12 34 56</div>', unsafe_allow_html=True)
        elif not diplome_pdf or not piece_identite_pdf:
            st.markdown('<div class="error-box">❌ Veuillez charger vos documents justificatifs.</div>', unsafe_allow_html=True)
        elif (diplome_pdf.name[-4:].lower() != ".pdf") or (piece_identite_pdf.name[-4:].lower() != ".pdf"):
            st.markdown('<div class="error-box">❌ Veuillez charger vos documents justificatifs en <strong>PDF</strong>.</div>', unsafe_allow_html=True)
        elif diplome_pdf.size > 10 * 1024 * 1024 or piece_identite_pdf.size > 10 * 1024 * 1024:
            st.markdown('<div class="error-box">❌ Les fichiers ne doivent pas dépasser 10 MB chacun.</div>', unsafe_allow_html=True)
        elif not all([accepte_conditions, confirme_presence, confirme_connexion]):
            st.markdown('<div class="error-box">❌ Veuillez accepter toutes les conditions obligatoires.</div>', unsafe_allow_html=True)
        else:
            data = {
                #"formation": formation,
                "ID": f"{formation}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "date_submitted": f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}',
                "genre": genre,
                "nom": nom.strip(),
                "prenom": prenom.strip(),
                "nationnalite": nationnalite,
                "email": email.strip(),
                "pays": pays,
                "ville": ville.strip(),
                "quartier": quartier.strip(),
                "telephone": telephone.strip(),
                "date_naissance": f'{date_naissance}',
                "id_type": id_type,
                "id_num": id_num.strip(),
                "id_enddate": f'{id_enddate}',
                "domaine": domaine,
                "educ_niveau": educ_niveau,
                "diplome": diplome.strip(),
                "etablissement": etablissement.strip()
            }

            # Envoi du diplome à dropbox
            send_to_dropbox(diplome_pdf, dest_files_name=f"{data.get('ID', '')}_Diplome.pdf")
            send_to_dropbox(piece_identite_pdf, dest_files_name=f"{data.get('ID', '')}_IDProof.pdf")


            send_to_sheet(data, shtname=formation)

            titres = {'M': "Monsieur ", 'F': "Madame "}
            msg = EmailMessage()
            msg['From'] = smtp_user
            msg['To'] = email.strip()
            msg["Subject"] = "Programme EcoDA Vague 1 Gratuit"
            msg.set_content(f"""
            Bonjour {titres.get(genre, '')}{prenom.strip()} {nom.strip()},
            
            Votre candidature a bien été reçu.

            Notre équipe a bien recu les fichiers et reviendra vers vous prochainement.
            Si vous n'etes pas encore dans la communauté ETC, nous vous invitons à la rejoindre sur WhatsApp afin de rester informé(e) des prochaines activités et formations :

            👉 [https://chat.whatsapp.com/KR0tQBivH8u4hwgRWb61pw]



            Excellent Training Center
            L'excellence au service du développement

            Formation | Analyse de données | Conseil économique
            🌐 https://sites.google.com/view/etc-site
            📩 contact.training.etc@gmail.com
            """)

            with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                smtp.starttls()
                smtp.login(smtp_user, smtp_pass)
                smtp.send_message(msg)

            st.markdown(
                """
                <div class="success-box"> ✅ Candidature envoyé. Surveillez vos mails (SPAM) et vos messages whatsapp.</div>
                """, unsafe_allow_html=True
            )



# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem;">
    <p><strong>📅 Calendrier :</strong> 7 séances les samedis 8h30-11h30 GMT</p>
    <p><strong>📞 Contact :</strong> Pour toute question, <a href="mailto:contact.training.etc@gmail.com
">contactez-nous</a></p>
    <p style="margin-top: 1rem; opacity: 0.8;">© 2025 <a href="https://sites.google.com/view/etc-site">ETC</a> Programme EcoDA - Tous droits réservés</p>
</div>
""", unsafe_allow_html=True)
