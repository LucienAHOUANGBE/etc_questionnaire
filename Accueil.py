"""
@auteur: Vignawou Lucien AHOUANGBE
@affiliation: Excellent Treaning Center (ETC)
@date: Saturday 15 Nov 2025 19:49
@update: 
    - 22/11/2025

"""

import streamlit as st
from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime, timezone, date
import dropbox
import smtplib
from email.message import EmailMessage
import re
import phonenumbers
import time

# l'initialisation



MAINTENANCE_MODE = st.secrets.get("MAINTENANCE_MODE", False)

if MAINTENANCE_MODE:
    st.error("🚧 Site en maintenance. Réessayez plus tard.")
    st.stop()


# les controles

datelimit = datetime(2025, 11, 26, 23, 59, 0,  tzinfo = timezone.utc)

if datetime.now(timezone.utc) > datelimit:
    st.error(f"""
            La date limite pour ce questionnaire est {datelimit.strftime("%Y-%m-%d %H:%M:%S")}. Le questionnaire n'est plus d'actualité. Veuillez attendre la prochaine session de formation.
            """)
    st.stop()



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
   'LATEX1': "Latex 1"
}


logicielDefinition = {
    'PYTHON1': "Python 1 : Introduction à python",
    'R1': "R 1 : Introduction à R + Analyse de données",
    'LATEX1': "Latex 1 : Introduction au Latex et au Beamer"
}


yes_no = {
    'O': 'Oui',
    'N' : 'Non'
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


@st.cache_resource
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
    except gspread.exceptions.APIError as e:
        st.error(f"Erreur API Google : {e}")
        return None, None, None
    except Exception as e:
        st.error(f"Erreur connexion : {e}")
        st.stop()

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


def check_all_duplicates(email, telephone, data):
    """Vérifie email ET téléphone sur TOUTES les formations en une seule connexion"""
    _, gsht, _ = connect_to_server()
    
    if gsht is None:
        return None, None
    
    try:
        email_col = list(data.keys()).index('email') + 1
        tel_col = list(data.keys()).index('telephone') + 1
    except ValueError:
        return None, None
    
    for formation in listOfLogicielInit.keys():
        try:
            wsht = gsht.worksheet(formation)
            
            # Vérifier email
            emails = [e.lower().strip() for e in wsht.col_values(email_col)[1:]]
            if email.strip().lower() in emails:
                return formation, 'email'
            
            # Vérifier téléphone
            telephones = [t.strip() for t in wsht.col_values(tel_col)[1:]]
            if telephone.strip() in telephones:
                return formation, 'telephone'
        
        except gspread.exceptions.WorksheetNotFound:
            continue
    
    return None, None




    
# ActualEnrolledNumber = {f: get_total_enrole(f) for f in listOfLogicielInit.keys()}
# Calculer les codate
@st.cache_data(ttl=30)  # Cache 60 secondes
def get_quotas_restant():
    return {f: MaxPlace[f] - get_total_enrolled(f) 
            for f in listOfLogicielInit.keys()}

quotasRestant = get_quotas_restant()



# update softward list to display
listOfLogiciel = {}
for i, j in listOfLogicielInit.items(): 
    if quotasRestant[i]>0:
        listOfLogiciel[i]= j

def validate_phone(phone):
    try:
        parsed = phonenumbers.parse(phone, None)
        return phonenumbers.is_valid_number(parsed)
    except:
        return False
    


@st.cache_data
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
        "Economie",
        "Education et sciences de l’éducation",
        "Electronique et électrotechnique",
        "Energies renouvelables et environnement",
        "Enseignement (primaire, secondaire, supérieur)",
        "Entrepreneuriat et innovation",
        "Etudes en gouvernance et institutions publiques",
        "Etudes sur le genre et inclusion sociale",
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




@st.cache_data
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

# ce qu'il faut faire si toutes les formations sont rempit



# Vérifier disponibilité
formations_disponibles = {k: v for k, v in listOfLogiciel.items() if quotasRestant[k] > 0}


if not formations_disponibles:
    total_places = sum(MaxPlace.values())
    
    st.markdown("---")
    # Version avec colonnes Streamlit (plus simple)
    st.error("### 🚫 Toutes les formations sont complètes")
    
    total_places = sum(MaxPlace.values())

    st.markdown(f"""
        <style>
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .closing-message {{
            animation: fadeIn 1s ease-out;
        }}
        </style>
        
        <div class="closing-message" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 4rem 2rem; border-radius: 25px; 
                    text-align: center; box-shadow: 0 20px 60px rgba(0,0,0,0.3); margin: 1em;">
            <h1 style="font-size: 4em; margin: 0;">🎓</h1>
            <h1 style="margin: 1rem 0;">Vague 1 : Complète !</h1>
            <p style="font-size: 1.3em; margin: 2rem 0; line-height: 1.6;">
                Merci pour votre intérêt ! Les <strong>{total_places} places</strong> ont trouvé preneurs.
            </p>
            
        </div>
    """, unsafe_allow_html=True)
    
    st.write()
    
    st.write()
    
    st.info("""
    ### 📅 Prochainement
    
    Une nouvelle vague de formations sera bientôt annoncée.
    Restez connecté(e) pour ne pas manquer l'ouverture des inscriptions !
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.link_button(
            "💬 Rejoindre WhatsApp",
            "https://chat.whatsapp.com/KR0tQBivH8u4hwgRWb61pw",
            use_container_width=True
        )
    
    with col2:
        st.link_button(
            "✉️ Nous contacter",
            "mailto:contact.training.etc@gmail.com",
            use_container_width=True
        )
    
    st.markdown("---")
    
    with st.expander("🔔 Comment être informé(e) de la prochaine session ?"):
        st.write("""
        1. Rejoignez notre communauté WhatsApp (lien ci-dessus)
        2. Suivez notre site web : https://sites.google.com/view/etc-site
        3. Envoyez-nous un email pour être sur notre liste de diffusion
        """)
    
    st.stop()



##### Debut de la page de formation
st.markdown(f"""
<p class="header-title">
    Première Vague - Inscriptions jusqu'au {datelimit.strftime("%Y-%m-%d %H:%M:%S")}
</p>
""", unsafe_allow_html=True)

st.markdown("""
<p class="header-title">
    Parrainé par <a href="https://sites.google.com/view/etc-site">ETC</a> - Programme EcoDA - Association Future Leaders
</p>
""", unsafe_allow_html=True)



st.markdown("---")


st.markdown("""
        <div class="section-title">
            ⚠️ Information importante - Condition d'éligibilité
        </div>
    """, unsafe_allow_html=True)



# Si des places sont disponibles
places_totales_restantes = sum(quotasRestant.values())

if places_totales_restantes <= 10:
    st.warning(f"⚠️ **ATTENTION :** Plus que {places_totales_restantes} place(s) disponible(s) au total !")
else:
    st.success(f"✅ {places_totales_restantes} place(s) encore disponible(s) !")

# Afficher quelles formations sont complètes
formations_completes = [logicielDefinition[k] for k in listOfLogicielInit.keys() if quotasRestant[k] <= 0]
if formations_completes:
    st.markdown(f"""
        <div class="warning-box">
            ⚠️ <strong>Formations complètes :</strong> {', '.join(formations_completes)}
        </div>
    """, unsafe_allow_html=True)


st.markdown(
    """
    <div class="warning-box">
        <ol>
            <li>Cette section est exclusivement en français.</li>
            <li>Avoir au minimum un niveau Bac + 2. Ne vous inquiétez pas, une autre session plus large sera lancée prochainement.</li>
            <li>📅 <strong>Calendrier</strong> : 7 séances, les samedis de 8h30 à 11h30 (GMT, heure officielle). 
                Les horaires peuvent être adaptés en fonction de la disponibilité du formateur.</li>
            <li>Veuillez vérifier votre disponibilité avant de vous inscrire. 
                Les formations se dérouleront principalement les samedis matin, mais les horaires peuvent être ajustés si le formateur est indisponible.</li>
            <li>La durée des formations est de 21 heures, sauf la formation LaTeX qui durera 15 heures.</li>
        </ol>       
    </div>
    """,
    unsafe_allow_html=True
)






# informations sur les place disponibles
col1, col2, col3 = st.columns(3)
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

with col3:
    st.markdown(f"""
    <div class="quota-card">
        <h3 style="color: black;">📊 Latex</h3>
        <p style="color: black;"><strong>Niveau 1</strong></p>
        <h2 style="color: red;">{quotasRestant['LATEX1']}/{MaxPlace['LATEX1']}</h2>
        <p style="color: black;">places disponibles</p>
    </div>
    """, unsafe_allow_html=True)
    r_pct = (quotasRestant['LATEX1'] / MaxPlace['LATEX1']) * 100
    st.progress(r_pct / 100)

st.markdown("---")

# Debut du formulaire
with st.form('formIncription'):

    st.markdown("""
        <div class="warning-box">
            ⚠️ <strong>Information :</strong> Les places affichées peuvent changer pendant que vous remplissez ce formulaire.
            Nous vérifierons la disponibilité au moment de votre soumission.
        </div>
    """, unsafe_allow_html=True)
     
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
        telephone = st.text_input("Téléphone (Whatsapp) *", placeholder="+228 XX XX XX XX")


    with col2:
        date_naissance = st.date_input(
            "Date de naissance *",
            min_value= date(1970, 1, 1),
            max_value=date.today(),
            value=date(2000, 1, 1)
        )

    # st.markdown(
    #     """
    #         <div class="warning-box">
    #             ⚠️ Veuillez fournir les informations sur une pièces d'identité en cours de validité.
    #         </div>
    #     """, unsafe_allow_html=True
    # )


    # col1, col2, col3 = st.columns(3)
    # with col1:
    #     id_type = st.selectbox(
    #         "Type de pièce d'identité *",
    #         ["CNI","Passeport", "Permis de conduire", "Autre"],
    #         index=None,
    #         placeholder="Selectionner un type"
    #     )

    id_type = "NA"

    # with col2:
    #     id_num = st.text_input(
    #         "N° pièce *",
    #         placeholder="AB 123456"
    #     )

    id_num = "NA"

    # with col3:
    #     id_enddate = st.date_input("Date d'expiration *")

    id_enddate = "NA"
    
    st.markdown("""
        <div class="section-title">
            🎓 Formation académique
        </div>
    """, unsafe_allow_html=True)

    current_active_etudiant_educ = st.radio(
        "Etes-vous toujours étudiant ? *",
        yes_no.keys(),
        captions = yes_no.values(),
        horizontal=True,
        index=None,
    )

    domaine_educ = st.selectbox(
        "Votre domaine *",
        getListOfDomaine(),
        index=None,
        placeholder="Ex. Economie"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        niveau_educ = st.selectbox(
            "Niveau d'étude *",
            [f"Bac +{i}" for i in range(2, 9)],
            placeholder="Plus haut niveau",
            index=None
        )

    with col2:
        diplome_educ = st.text_input(
            "Dernier diplôme obtenu *",
            placeholder="Ex: Licence en informatique"
        )

    with col3:
        etablissement_educ = st.text_input(
            "Établissement *",
            placeholder="Ex: Université de lomé"
        )

    specialite_educ = st.text_input(
        "Quelle est votre spécialité exacte ou votre filière *",
        placeholder='Ex. Microéconomie comportementale'
    )

    st.markdown("""
        <div class="section-title">
            💼 Expérience professionnelles
        </div>
    """, unsafe_allow_html=True)

    activite_pro = st.radio(
        "Exercez vous une activité professionnelle ? *",
        yes_no.keys(),
        captions = yes_no.values(),
        horizontal=True,
        index=None,
    )

    domaine_pro = st.selectbox(
        "Quel est votre domaine d'activités principal ? *",
        getListOfDomaine(),
        index=None,
        placeholder="Ex. Economie"
    )

    specialite_pro = st.text_input(
        "Quelle est votre spécialité ou votre rôle principal dans ce domaine ? *",
        placeholder="Ex: Consultant en analyse de données"
    )

    current_active_pro = st.radio(
        "Travaillez-vous actuellement dans ce domaine ? *",
        yes_no.keys(),
        captions = yes_no.values(),
        horizontal=True,
        index=None,
    )

    experience_year = st.number_input(
        "Depuis combien de temps travaillez-vous dans ce domaine (en année) ? *",
        value = 0.0,
        min_value = 0.0,
        max_value = 50.0,
        step = 0.5,
        format="%.2f"
    )
    
    st.markdown("""
        <div class="section-title">
            🎯 Motivation et Objectifs
        </div>
    """, unsafe_allow_html=True)

    formation_pourquoi = st.text_area(
        "Pourquoi souhaitez-vous suivre cette formation ? *",
        max_chars=1000,
        placeholder="Minimum 50 caractères."
    )

    formation_utilite = st.text_area(
        "Comment pensez-vous utiliser les compétences acquises après cette formation ? *",
        max_chars=1000,
        placeholder="Minimum 50 caractères."
    )

    formation_comment = st.text_area(
        "Commentaire ?",
        max_chars=1000,
        placeholder="Votre commentaire."
    )
 
    st.markdown("""
        <div class="section-title">
            ✅ Engagement et conditions
        </div>
    """, unsafe_allow_html=True)
    
    confirme_presence = st.checkbox(
        "Je m'engage à être présent(e) à TOUTES les séances. Les absences non justifiées entraînent une exclusion automatique. *"
    )
    
    confirme_connexion = st.checkbox(
        "Je confirme disposer d'ordinateur et d'une bonne connexion Internet pour suivre les sessions en ligne. *"
    )
    

    submitted = st.form_submit_button("🚀 Envoyer mon inscription", width='stretch')

    if submitted:
        
        pattern_email = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

        

        # Champs obligatoires de base
        if not all([formation, genre, nom, prenom, nationnalite, email, pays, ville, 
                    quartier, telephone, date_naissance, domaine_educ, niveau_educ, 
                    diplome_educ, etablissement_educ, specialite_educ, activite_pro, 
                    formation_pourquoi, formation_utilite]):
            st.markdown('<div class="error-box">❌ Veuillez remplir tous les champs obligatoires.</div>', unsafe_allow_html=True)
        
        # Validation email
        elif not re.match(pattern_email, email.strip()):
            st.markdown('<div class="error-box">❌ Le format email est incorrect. Ex: abc@def.ghf</div>', unsafe_allow_html=True)
        
        # Validation téléphone
        elif not validate_phone(telephone):
            st.markdown('<div class="error-box">❌ Numéro invalide. Exemple : +228 90 12 34 56</div>', unsafe_allow_html=True)
        
        # Validation activité professionnelle
        elif activite_pro == 'O' and not all([domaine_pro, specialite_pro, current_active_pro]):
            st.markdown('<div class="error-box">❌ Veuillez remplir tous les champs obligatoires de vos activités professionnelles.</div>', unsafe_allow_html=True)
        
        # Validation expérience
        elif activite_pro == 'O' and current_active_pro == 'O' and experience_year <= 0:
            st.markdown('<div class="error-box">❌ Veuillez indiquer votre expérience professionnelle (minimum 0.5 an).</div>', unsafe_allow_html=True)
        
        # Validation longueur motivation
        elif len(formation_pourquoi.strip()) < 50:
            st.markdown('<div class="error-box">❌ Veuillez détailler votre motivation (minimum 50 caractères).</div>', unsafe_allow_html=True)
        
        elif len(formation_utilite.strip()) < 50:
            st.markdown('<div class="error-box">❌ Veuillez détailler comment vous utiliserez la formation (minimum 50 caractères).</div>', unsafe_allow_html=True)
        
        # Validation conditions
        elif not all([confirme_presence, confirme_connexion]):
            st.markdown('<div class="error-box">❌ Veuillez accepter toutes les conditions obligatoires.</div>', unsafe_allow_html=True)
        
        # Vérification places disponibles
        elif get_total_enrolled(formation) >= MaxPlace[formation]:
            st.error("❌ Il n'y a plus de places disponibles pour cette formation.")
            time.sleep(4)
            st.rerun()
        else:

            # Préparer les données
            data = {
                "ID": f"{formation}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                "date_submitted": f'{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}',
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
                "current_active_etudiant_educ": current_active_etudiant_educ,
                "domaine_educ": domaine_educ,
                "niveau_educ": niveau_educ,
                "diplome_educ": diplome_educ.strip(),
                "etablissement_educ": etablissement_educ.strip(),
                "specialite_educ": specialite_educ.strip(),
                "activite_pro": activite_pro,
                "domaine_pro": domaine_pro if activite_pro == 'O' else "N/A",
                "specialite_pro": specialite_pro.strip() if activite_pro == 'O' else "N/A",
                "current_active_pro": current_active_pro if activite_pro == 'O' else "N/A",
                "experience_year": experience_year if activite_pro == 'O' else 0,
                "formation_pourquoi": formation_pourquoi.strip(),
                "formation_utilite": formation_utilite.strip(),
                "formation_comment": formation_comment.strip()
            }

           
            # Utilisation
            duplicate_formation, duplicate_field = check_all_duplicates(email, telephone, data)

            if duplicate_formation:
                st.markdown(
                    f'<div class="error-box">❌ Ce {duplicate_field} est déjà inscrit à <strong>{logicielDefinition[duplicate_formation]}</strong>.</div>',
                    unsafe_allow_html=True
                )
                st.stop()

            # ✅ VÉRIFICATION FINALE JUSTE AVANT INSERTION
            places_actuelles = get_total_enrolled(formation)
            if places_actuelles >= MaxPlace[formation]:
                st.error("❌ Formation complète ! Un autre utilisateur a pris la dernière place pendant votre inscription.")
                time.sleep(3)
                st.rerun()
                st.stop()
            
            try:
                send_to_sheet(data, shtname=formation)

                titres = {'M': "Monsieur ", 'F': "Madame "}
                msg = EmailMessage()
                msg['From'] = smtp_user
                msg['To'] = email.strip()
                msg["Subject"] = "Programme EcoDA Vague 1 Gratuit"
                msg.set_content(f"""
Bonjour {titres.get(genre, '')}{prenom.strip()} {nom.strip()},

Votre candidature a bien été reçue.
Votre ID : {data.get('ID', "Non Connu")}

Rejoignez notre communauté WhatsApp :
https://chat.whatsapp.com/KR0tQBivH8u4hwgRWb61pw

Cordialement,
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

                st.markdown("""
                    <div class="success-box">✅ Candidature envoyée. Surveillez vos mails (SPAM) et vos messages WhatsApp.</div>
                """, unsafe_allow_html=True)

                st.balloons()  # Animation de succès
                st.success(f"✅ Inscription validée ! Bienvenu à bord {titres.get(genre, '')}{prenom.strip()} {nom.strip()} !")
                time.sleep(10)
                st.rerun()  # Recharger pour vider le formulaire


            except Exception as e:
                st.error(f"Problème d'envoi de vos données. Vérifiez votre connexion. Erreur : {e}")

            


# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem;">
    <p><strong>📅 Calendrier :</strong> 7 séances les samedis 8h30-11h30 GMT</p>
    <p><strong>📞 Contact :</strong> Pour toute question, <a href="mailto:contact.training.etc@gmail.com
">contactez-nous</a></p>
    <p>Formation | Analyse de données | Conseil économique</p>
    <p style="margin-top: 1rem; opacity: 0.8;">© 2025 <a href="https://sites.google.com/view/etc-site">ETC</a> Programme EcoDA - Tous droits réservés</p>
</div>
""", unsafe_allow_html=True)
