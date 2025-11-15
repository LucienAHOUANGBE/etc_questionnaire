import streamlit as st
from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError
import io
import dropbox



# Les configurations ---------------------------------------------------------


# ----------- Debut de la page
st.set_page_config(
    page_title="Inscription ETC Formation",
    page_icon= "🎓",
    layout='centered'
)


# Mise à jours tu CSS

st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: transparent;
    }   
            
    .header-title {
        text-align: center;
        font-size: 3em;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
            
    div[data-testid="stForm"] {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
            
    p {
        color: black;
    }
            
    .quota-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        text-align: center;
        margin: 1rem 0;
    }
            
    .section-title {
        color: #667eea;
        font-size: 1.5em;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
    }

    .warning-box {
        background: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        border-radius: 8px;
        color: #856404;
        margin-bottom: 1rem;
    }

    .error-box {
        background: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1.5rem;
        border-radius: 10px;
        color: #721c24;
    }
    .success-box {
        background: ##bcf5c1;
        border-left: 5px solid #dc3545;
        padding: 1.5rem;
        border-radius: 10px;
        color: #0ff523;
    }      
</style>
""", unsafe_allow_html=True
)


CONFIG = {
    'PythonMaxPlace': 30,
    'RMaxPlace': 30,
    "spreadSheetID": st.secrets.get("SPREADSHEET_ID"),
    "driveFolderID": st.secrets.get("DRIVE_FOLDER_ID")
}


# Les connexions serveur ---------------------------------------------------
# Google sheets

print(st.secrets["gcp_service_account"]["project_id"])

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


def send_to_dropbox(entry_file, dest_files_name, dest_folder="/ETCquestionnaire"):
    _, _, dbx= connect_to_server()
    file_bytes = entry_file.read()
    dest_path = f"{dest_folder}/{dest_files_name}"
    dbx.files_upload(file_bytes, dest_path)
    
    
# def send_to_drive(file_bytes, name_on_server):
#     try:
#         _, _, gdrv = connect_to_server()
#         if gdrv is None:
#             raise Exception("Impossible de récupérer le fichier Google drive.")
            
#         try:
#             # Si la drive existe
#             # creer le nom de fichier et le dossier sur serveur drive
#             file_metadata = {
#                 'name': name_on_server,
#                 'parents': [CONFIG["driveFolderID"]]
#             }

#             # information du media en local
#             media_a_charger = MediaIoBaseUpload(
#                 io.BytesIO(file_bytes),
#                 mimetype="application/pdf"
#             )

#             # chargement du fichier vers drive
#             file = gdrv.files().create(
#                 body = file_metadata,
#                 media_body = media_a_charger, 
#                 fields = "id, name",
#                 supportsAllDrives=True
#             ).execute()

#             return file

#         except Exception as e:
#             raise Exception(f"Erreur sauvegarde vers Drive: {e}")
            
#     except Exception as e:     
#         raise Exception(f"Erreur connexion à Drive: {e}")
    
# def send_to_drive(file_bytes, name_on_server):
#     try:
#         _, _, gdrv = connect_to_server()
#         if gdrv is None:
#             raise Exception("Impossible de se connecter à Google Drive.")

#         try:
#             file_metadata = {
#                 "name": name_on_server,
#                 "parents": [CONFIG["driveFolderID"]]   # dossier PARTAGÉ
#             }

#             media = MediaIoBaseUpload(
#                 io.BytesIO(file_bytes),
#                 mimetype="application/pdf",
#                 resumable=True
#             )

#             file = gdrv.files().create(
#                 body=file_metadata,
#                 media_body=media,
#                 fields="id, name",
#                 supportsAllDrives=True   # OBLIGATOIRE
#             ).execute()

#             return file

#         except Exception as e:
#             raise Exception(f"Erreur sauvegarde vers Drive : {e}")

#     except Exception as e:
#         raise Exception(f"Erreur connexion à Drive : {e}")
# def send_to_drive(file_bytes, name_on_server):
#     try:
#         _, _, gdrv = connect_to_server()
#         if gdrv is None:
#             raise Exception("Impossible de se connecter à Google Drive.")

#         folder_id = CONFIG.get("driveFolderID")
        
#         if not folder_id:
#             raise Exception("driveFolderID non configuré dans CONFIG")
        
#         file_metadata = {
#             "name": name_on_server,
#             "parents": [folder_id]
#         }

#         media = MediaIoBaseUpload(
#             io.BytesIO(file_bytes),
#             mimetype="application/pdf",
#             resumable=True
#         )

#         file = gdrv.files().create(
#             body=file_metadata,
#             media_body=media,
#             fields="id, name",
#             supportsAllDrives=True  # ← Gardez seulement celui-ci
#         ).execute()

#         return file

#     except HttpError as e:
#         raise Exception(f"Erreur Google Drive API : {e}")
#     except Exception as e:
#         raise Exception(f"Erreur lors de l'upload : {e}")
    

# def test_drive_access():
#     _, _, gdrv = connect_to_server()
#     results = gdrv.files().list(
#         q=f"'{CONFIG['driveFolderID']}' in parents",
#         fields="files(id, name)",
#         supportsAllDrives=True
#     ).execute()

#     return results

# print(test_drive_access())

ActualEnrolledNumber = {
    'python': 15,
    'r': 15
}

# def test_folder_rights():
#     _, _, gdrv = connect_to_server()

#     folder = gdrv.files().get(
#         fileId=CONFIG['driveFolderID'],
#         fields="id, name, permissions",
#         supportsAllDrives=True
#     ).execute()

#     return folder

# print(test_folder_rights())

# def test_drive_type():
#     _, _, gdrv = connect_to_server()

#     folder = gdrv.files().get(
#         fileId=CONFIG['driveFolderID'],
#         fields="id, name, driveId, parents",
#         supportsAllDrives=True
#     ).execute()

#     return folder

# print(test_drive_type())



quotas = {
    'python': CONFIG['PythonMaxPlace'] - ActualEnrolledNumber['python'],
    'r': CONFIG['RMaxPlace'] - ActualEnrolledNumber['r']
}





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






#st.title("🎓 Formation Gratuite ETC")
st.markdown("<h1 style='text-align: center;'>🎓 Formation Gratuite ETC</h1>", unsafe_allow_html=True)

st.markdown("""
<p class="header-title">
    Première Vague - Inscriptions jusqu'au 15 novembre
</p>
""", unsafe_allow_html=True)

st.markdown("""
<p class="header-title">
    Parrainer par <a href="https://sites.google.com/view/etc-site">ETC</a> - Programe EcoDA - Association Future Leaders
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
            <p>1. Avoir au minimum BAC+3 </p>
            <p>2. 📅 Calendrier : 7 séances les samedis 8h30-11h30 GMT</p>
        </div>
    """, unsafe_allow_html=True
)



col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    <div class="quota-card">
        <h3 style="color: black;">🐍 Python</h3>
        <h2 style="color: red;">{quotas['python']}/{CONFIG['PythonMaxPlace']}</h2>
        <p style="color: black;">places disponibles</p>
    </div>
    """, unsafe_allow_html=True)

    python_pct = (quotas['python']/CONFIG['PythonMaxPlace']) * 100
    st.progress(python_pct / 100)

with col2:
    st.markdown(f"""
    <div class="quota-card">
        <h3 style="color: black;">📊 R</h3>
        <h2 style="color: red;">{quotas['r']}/{CONFIG['PythonMaxPlace']}</h2>
        <p style="color: black;">places disponibles</p>
    </div>
    """, unsafe_allow_html=True)
    r_pct = (quotas['r'] / CONFIG['RMaxPlace']) * 100
    st.progress(r_pct / 100)

st.markdown("---")

# update softward list
listOfLogiciel = []
if quotas['python']>0:
    listOfLogiciel.append('Python')

if quotas['r']>0:
    listOfLogiciel.append('R')



with st.form('formIncription'):
    st.markdown("""
        <div class="section-title">
            📝 Choix de formation
        </div>
    """, unsafe_allow_html=True)


    formation = st.selectbox(
        "Formation souhaitée*",
        listOfLogiciel,
        placeholder="Choisissez une formation. Attention aux accents. Ex: Économie",
        index=None,
        format_func=lambda x: {
            "Python": "Introduction à python",
            "R": "Introduction à R et à l'analyse de données"
        }[x]
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
    

    submitted = st.form_submit_button("🚀 Envoyer mon inscription", use_container_width=True)

    if submitted:
        if not all([formation, genre, nom, prenom, nationnalite, email, pays, ville, quartier, telephone, date_naissance, id_type, id_num, id_enddate, domaine, educ_niveau, diplome, etablissement]):
            st.markdown('<div class="error-box">❌ Veuillez remplir tous les champs obligatoires.</div>', unsafe_allow_html=True)
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
                "ID": f"{formation[0]}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "date_submitted": f'{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}',
                "genre": genre,
                "nom": nom,
                "prenom": prenom,
                "nationnalite": nationnalite,
                "email": email,
                "pays": pays,
                "ville": ville,
                "quartier": quartier,
                "telephone": telephone,
                "date_naissance": f'{date_naissance}',
                "id_type": id_type,
                "id_num": id_num,
                "id_enddate": f'{id_enddate}',
                "domaine": domaine,
                "educ_niveau": educ_niveau,
                "diplome": diplome,
                "etablissement": etablissement
            }

            # Envoi du diplome
            send_to_dropbox(diplome_pdf, dest_files_name=f"Diplome_{data.get('ID', '')}.pdf")
            send_to_dropbox(piece_identite_pdf, dest_files_name=f"IDProof_{data.get('ID', '')}.pdf")
            # send_to_drive(file_bytes= diplome_pdf.read(), name_on_server=f"Diplpome_{data.get('ID', '')}")
            # send_to_drive(file_bytes= piece_identite_pdf.read(), name_on_server=f"IDProof_{data.get('ID', '')}")


            send_to_sheet(data, shtname=formation)


            st.markdown(
                """
                <div class="success-box"> ✅ Candidature envoyé. Surveillez vous mail. Et vous message whatsapp.</div>
                """, unsafe_allow_html=True
            )

            # inscription = {
            #     "formation": None,
            #     "genre": None,
            #     "nom": None,
            #     "prenom": None,
            #     "email": None,
            #     "telephone": None,
            #     "date_naissance": None,
            #     "id_type": None,
            #     "id_num": None,
            #     "id_enddate": None,
            #     "domaine": None,
            #     "educ_niveau": None,
            #     "diplome": None,
            #     "etablissement": None
            # }

            # inscription_schema = {
            #     "formation": "Module ou formation choisie",
            #     "genre": "Homme, Femme, Autre",
            #     "nom": "Nom de famille",
            #     "prenom": "Prénom",
            #     "email": "Adresse email",
            #     "telephone": "Numéro de téléphone (WhatsApp si possible)",
            #     "date_naissance": "Date de naissance (AAAA-MM-JJ)",
            #     "id_type": "Type de pièce d'identité (CNI, Passeport, Carte Étudiant...)",
            #     "id_num": "Numéro de la pièce d'identité",
            #     "id_enddate": "Date d’expiration de la pièce d'identité",
            #     "domaine": "Domaine d’activité ou secteur professionnel",
            #     "educ_niveau": "Niveau d’éducation (BAC, BAC+2, Licence, Master... )",
            #     "diplome": "Dernier diplôme obtenu",
            #     "etablissement": "Établissement ayant délivré le diplôme"
            # }

            



# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: white; padding: 2rem;">
    <p><strong>📅 Calendrier :</strong> 7 séances les samedis 8h30-11h30 GMT</p>
    <p><strong>📞 Contact :</strong> Pour toute question, <a href="mailto:contact.training.etc@gmail.com
">contactez-nous</a></p>
    <p style="margin-top: 1rem; opacity: 0.8;">© 2024 <a href="https://sites.google.com/view/etc-site">ETC</a> Formation - Tous droits réservés</p>
</div>
""", unsafe_allow_html=True)
