from flask import Blueprint, render_template, flash, redirect, url_for
import os
import pymysql
from dotenv import load_dotenv
from flask_login import login_required, current_user
from database import *

#Connection a la base de donnee
load_dotenv()
host = os.environ.get("HOST")
port = int(os.environ.get("PORT"))
database = os.environ.get("DATABASE")
user = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
migration_counter = 0

connection = pymysql.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    db=database,
    autocommit=True
)

cursor = connection.cursor()

# Initilisation de la route
main = Blueprint('main', __name__)


# ROUTES DE BASE
@main.route('/')
def index():
    return render_template('index.html')

# ROUTE PAGE DE CONNEXION
@main.route('/Connexion', methods=['GET'])
def connexion_():
    return render_template('Connexion.html')

# ROUTE POUR REVENIR PAGE ACCEUIL
@main.route('/Deconnexion', methods=['GET'])
def deconnexion_():
    return render_template('index.html')

# ROUTE POUR PAGE ACCEUIL ETUIDIANTE
@main.route('/EtudiantUtilisateur', methods=['GET'])
def etudiantUtilisateur_():
    return render_template('EtudiantUtilisateur.html')

# ROUTE POUR AFFICHER DISPONIBILITÉ DE L'ETUDIANT
@main.route('/EtudiantDispo', methods=['GET'])
@login_required
@student_required
def etudiantDispo_():
    heading = ("Jour", "Heure debut", "Heure fin")
    user_id = int(current_user.id)
    data = select_dispos_from_etudiant(user_id)
    return render_template('Etudiants/EtudiantDispo.html', heading=heading, data=data)

# ROUTE POUR L'AFFICHAGE DES COURS DE L'ETUDIANT
@main.route('/EtudiantCours', methods=['GET'])
@login_required
@student_required
def etudiantCours_():
    heading = ("Cours", "Jour", "Instrument", "Durée", "Heure", "Éleve", "Professeur",)
    user_id = int(current_user.id)
    data = select_cours_etudiant(user_id)
    return render_template('Etudiants/EtudiantCours.html', user=current_user, heading=heading, data=data)

# ROUTE POUR AFFICHER DISPONIBILTE ETUDIANT
@main.route('/EtudiantCreeDispo', methods=['GET'])
@login_required
@student_required
def etudiantCreeDispo_():
    heading = ("ID Cours", "Jour", "Instrument", "Durée", "Heure", "Nom éleve", "Nom prof", "ID Session")
    user_id = int(current_user.id)
    data = select_cours_etudiant(user_id)
    return render_template('Etudiants/EtudiantCreeDispo.html', user=current_user, heading=heading, data=data)

# ROUTES PROFESSEUR
# ROUTE POUR AFFICHER DISPONIBILTE PROFESSEUR
@main.route('/ProfesseurDispo', methods=['GET'])
@login_required
@professor_required
def professeurDispo_():
    heading = ("Jour", "Heure debut", "Heure fin")
    user_id = int(current_user.id)
    data = select_dispos_from_prof(user_id)
    return render_template('Professeurs/ProfesseurDispo.html', user=current_user, heading=heading, data=data)

# ROUTE PAGE CREATION DISPO PROFESSEUR
@main.route('/ProfesseurCreeDispo', methods=['GET'])
@login_required
@professor_required
def professeurCreeDispo_():
    return render_template('Professeurs/ProfesseurCreeDispo.html', user=current_user)

# ROUTE PAGE HORAIRE PROFESSEUR
@main.route('/ProfesseurHoraire', methods=['GET'])
@login_required
@professor_required
def professeurHoraire_():
    heading = ("Jour", "Heure", "Instrument", "Durée", "Nom élève")
    user_id = int(current_user.id)
    data = select_cours_prof(user_id)
    return render_template('Professeurs/ProfesseurHoraire.html', user=current_user, heading=heading, data=data)

# ROUTE PAGE ELEVES DU PROFESSEUR
@main.route('/ProfesseurEleves', methods=['GET'])
@login_required
@professor_required
def professeurEleves_():
    heading = ("Prenom", "Nom", "Age", "Instrument", "Courriel", "Téléphone")
    user_id = int(current_user.id)
    data = select_eleves_from_prof(user_id)
    return render_template('Professeurs/ProfesseurEleves.html', heading=heading, data=data)


# ROUTES ADMIN
# ROUTE PAGE DE COURS
@main.route('/AdminCours', methods=['GET'])
@admin_required
def adminCours_():
    heading = ("ID Session", "ID Cours", "Jour", "Instrument", "Durée", "Heure", "Nom éleve", "Nom prof")
    data = select_cours()
    return render_template('Admins/AdminCours.html', heading=heading, data=data)

# ROUTE PAGE DE CREATION DE COURS
@main.route('/AdminCreeCours', methods=['GET'])
@admin_required
def adminCreeCours_():
    return render_template('Admins/AdminCreeCours.html')

# ROUTE PAGE DE DISPONIBILITE PROF
@main.route('/AdminProfDispo', methods=['GET'])
def adminprofdispo_():
    heading = ("ID", "Prenom", "Nom", "Jour", "Heure de début", "Heure de fin")
    data = dispo_prof()
    return render_template('Admins/AdminProfDispo.html', heading=heading, data=data)

# ROUTE PAGE DISPONIBILITE ETUDIANT
@main.route('/AdminElevesDispo', methods=['GET'])
def adminelevesdispo_():
    heading = ("ID Étudiant", "Prenom", "Nom", "Jour", "Heure de début", "Heure de fin")
    data = dispo_eleve()
    return render_template('Admins/AdminElevesDispo.html', heading=heading, data=data)

# ROUTE PAGE CREATION DE PROFESSEUR
@main.route('/AdminCreeProfesseur', methods=['GET'])
@admin_required
def adminCreeProfesseur_():
    return render_template('Admins/AdminCreeProfesseur.html')

# ROUTE PAGE CREATION DE SESSION
@main.route('/AdminCreeSession', methods=['GET'])
@admin_required
def adminCreeSession_():
    return render_template('Admins/AdminCreeSession.html')

# ROUTE PAGE DES ELEVES
@main.route('/AdminEleves', methods=['GET'])
@admin_required
def adminEleves_():
    heading = ("ID Éleve", "Prenom", "Nom", "Courriel", "Age", "Instrument", "Durée", "Traitee")
    data = select_eleves()
    return render_template('Admins/AdminEleves.html', heading=heading, data=data)

# ROUTE PAGE ACCEUIL ADMIN
@main.route('/AdminIndex', methods=['GET'])
@login_required
@admin_required
def adminIndex_():
    return render_template('Admins/AdminIndex.html')

# ROUTE PAGE DES PROFESSEURS
@main.route('/AdminProfesseurs', methods=['GET'])
@admin_required
def adminProfesseurs_():
    heading = ("ID Prof", "Prenom", "Nom", "Courriel", "telephone")
    data = select_professeurs()
    return render_template('Admins/AdminProfesseurs.html', heading=heading, data=data)

# ROUTE PAGE DES SESSION
@main.route('/AdminSession', methods=['GET'])
@admin_required
def adminSession_():
    heading = ("ID Session", "Nom", "Date de début", "Date de fin", "Nombre de semaine")
    data = select_sessions()
    return render_template('Admins/AdminSession.html', heading=heading, data=data)

# ROUTE PAGE A PROPOS
@main.route('/About', methods=['GET'])
def about():
    return render_template('About.html')
