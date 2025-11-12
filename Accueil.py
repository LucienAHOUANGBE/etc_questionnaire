import streamlit as st

CONFIG = {
    'PythonMaxPlace': 30,
    'RMaxPlace': 30,
}

domaineList = [
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
    "Autre"
]

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
        color: white;
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
            
    label div p {
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
            
</style>
""", unsafe_allow_html=True
)


st.title("🎓 Formation Gratuite ETC")

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
        <h2 style="color: red;">15/{CONFIG['PythonMaxPlace']}</h2>
        <p style="color: black;">places disponibles</p>
    </div>
    """, unsafe_allow_html=True)

    python_pct = (15/CONFIG['PythonMaxPlace']) * 100
    st.progress(python_pct / 100)

with col2:
    st.markdown(f"""
    <div class="quota-card">
        <h3 style="color: black;">📊 R - Analyse de données</h3>
        <h2 style="color: red;">15/{CONFIG['PythonMaxPlace']}</h2>
        <p style="color: black;">places disponibles</p>
    </div>
    """, unsafe_allow_html=True)
    r_pct = (15 / CONFIG['RMaxPlace']) * 100
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
        ["Python", "R"],
        placeholder="Choisissez une formation",
        index=None,
        format_func=lambda x: {
            "Python": "Introduction à python",
            "R": "R - introduction à R et à l'analyse de données"
        }[x]
    )

    st.markdown('<div class="section-title">👤 Informations personnelles</div>', unsafe_allow_html=True)

    genre = st.radio(
        "Genre *",
        ["F", "M"], 
        captions=["Feminin", 'Masculin'], 
        index=None, 
        horizontal=True
    )


    col1, col2 = st.columns(2)
    with col1:
        nom = st.text_input("Nom *", placeholder="Votre nom")
    with col2:
        prenom = st.text_input("Prénom *", placeholder="Votre prénom")


    email = st.text_input("Email *", placeholder="votre.email@exemple.com")
    
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
            placeholder="EB787878"
        )

    with col3:
        id_enddate = st.date_input("Date d'expiration*")



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
            "Niveau d'étude*",
            [f"Bac +{i}" for i in range(3, 9)],
            placeholder="Plus haut niveau",
            index=None
        )

    with col2:
        diplome = st.text_input(
            "Dernier diplôme obtenu*",
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


# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: white; padding: 2rem;">
    <p><strong>📅 Calendrier :</strong> 7 séances les samedis 8h30-11h30 GMT</p>
    <p><strong>📞 Contact :</strong> Pour toute question, contactez-nous</p>
    <p style="margin-top: 1rem; opacity: 0.8;">© 2024 ETC Formation - Tous droits réservés</p>
</div>
""", unsafe_allow_html=True)
