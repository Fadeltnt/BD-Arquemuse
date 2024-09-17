import os, datetime
import pymysql
from dotenv import load_dotenv
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from functools import wraps


auth = Blueprint('auth', __name__)

# Configuration de la connexion à labase de données MySQL
load_dotenv()
host = os.environ.get("HOST")
port = int(os.environ.get("PORT"))
database = os.environ.get("DATABASE")
user = os.environ.get("USER")
password = os.environ.get("PASSWORD")
migration_counter = 0

db_config = {
    'host': host,
    'user': user,
    'password': password,
    'database': database,
}


class User(UserMixin):
    # Définit une classe User qui hérite de UserMixin. UserMixin fournit des implémentations par défaut pour les méthodes liées à la gestion de l'utilisateur, telles que is_authenticated, is_active, etc.

    def __init__(self, user_id, email, nom, prenom, role):
        self.id = user_id
        self.email = email
        self.nom = nom
        self.prenom = prenom
        self.role = role


# Définit une variable globale current_user_role pour stocker le rôle actuel de l'utilisateur.

current_user_role = None


def get_user_role(email):
    # Définit une fonction pour récupérer le rôle de l'utilisateur à partir de la base de données en utilisant son adresse e-mail.
    conn = pymysql.connect(**db_config)
    cur = conn.cursor()
    # Recherche dans la table des étudiants
    cur.execute("SELECT role FROM Utilisateurs WHERE courriel = %s", (email,))
    student_role = cur.fetchone()
    if student_role:
        return student_role[0]

    cur.execute("SELECT role FROM Professeurs WHERE courriel = %s", (email,))
    professor_role = cur.fetchone()
    if professor_role:
        print(professor_role[0])
        return professor_role[0]

    # Recherche dans la table des administrateurs
    cur.execute("SELECT role FROM Administrateurs WHERE courriel = %s", (email,))
    admin_role = cur.fetchone()
    if admin_role:
        return admin_role[0]
    return None

# Vérifie si l'utilisateur actuel a le rôle d'étudiant avant d'exécuter la fonction décorée.
def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        role = session.get('role')
        print(role)  # Vérifiez la
        if role != 'Etudiant':
            flash('Accès non autorisé.', category='error')
            return redirect(url_for('auth.logout'))  # Rediriger vers la page d'accueil ou une autre page appropriée
        return f(*args, **kwargs)

    return decorated_function


# Les fonctions professor_required et admin_required fonctionnent de la même manière, mais pour les rôles de professeur et d'administrateur respectivement.
def professor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        role = session.get('role')
        print(role)  # Vérifiez la
        if role != 'Professeur':
            flash('Accès non autorisé.', category='error')
            return redirect(url_for('auth.logout'))  # Rediriger vers la page d'accueil ou une autre page appropriée
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        role = session.get('role')
        print(role)  # Vérifiez la valeur de current_user_role
        if role != 'Administrateur':
            flash('Accès non autorisé.', category='error')
            return redirect(url_for('auth.logout'))  # Rediriger vers la page d'accueil ou une autre page appropriée
        return f(*args, **kwargs)

    return decorated_function


# La route /login est configurée pour accepter les requêtes GET et POST.
# GET : Affiche la page de connexion.
# POST : Traite les données du formulaire de connexion.
@auth.route('/login', methods=['GET', 'POST'])
def login():
    global current_user_role
    global current_user_role_admin
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print("Email:", email)
        print("Password:", password)

        if email and password:
            conn = pymysql.connect(**db_config)
            cur = conn.cursor()
            print("Connected to database.")

            # Recherche de l'email dans la table des utilisateurs
            cur.execute(
                "SELECT utilisateur_id, courriel, mot_de_passe, nom, prenom, role FROM Utilisateurs WHERE courriel = %s",
                (email,))
            user_data = cur.fetchone()
            print("User data:", user_data)

            if not user_data:
                # Si l'email n'est pas trouvé dans la table des utilisateurs, recherchez-le dans la table des professeurs
                cur.execute(
                    "SELECT professeur_id, courriel, mot_de_passe, nom, prenom, role FROM Professeurs WHERE courriel = %s",
                    (email,))
                user_data = cur.fetchone()
                print("User data (professeur):", user_data)

                if not user_data:
                    # Si l'email n'est pas trouvé dans la table des professeurs, recherchez-le dans la table des administrateurs
                    cur.execute(
                        "SELECT admin_id, courriel, mot_de_passe, nom, prenom, role FROM Administrateurs WHERE courriel = %s",
                        (email,))
                    user_data = cur.fetchone()
                    print("User data (administrateur):", user_data)

            if user_data:
                print("User data found.")
                if check_password_hash(user_data[2], password) or user_data[2] == password:
                    print("Password matched.")
                    user_id, user_email, _, user_nom, user_prenom, role = user_data
                    user = User(user_id, user_email, user_nom, user_prenom,
                                role)  # Inclure le rôle lors de la création de l'utilisateur
                    session['role'] = role
                    # Mettez à jour current_user_role pour tous les types d'utilisateurs
                    current_user_role = role

                    if role == 'Etudiant':
                        # Rediriger vers la page des étudiants
                        login_user(user, remember=True)  # Se souvenir de l'utilisateur entre les sessions
                        flash('Connexion réussie !', category='success')
                        return redirect(url_for('auth.student_page'))
                    elif role == 'Professeur':
                        # Rediriger vers la page des professeurs
                        login_user(user, remember=True)  # Se souvenir de l'utilisateur entre les sessions
                        flash('Connexion réussie !', category='success')
                        return redirect(url_for('auth.professeurIndex_'))
                    elif role == 'Administrateur':
                        # Rediriger vers la page des administrateurs
                        login_user(user, remember=True)  # Se souvenir de l'utilisateur entre les sessions
                        flash('Connexion réussie !', category='success')
                        current_user_role_admin = "Administrateur"
                        print(current_user_role_admin)
                        return redirect(url_for('main.adminIndex_'))
                else:
                    print("Password didn't match.")
                    flash('Email ou mot de passe incorrect.', category='error')
            else:
                print("User data not found.")
                flash('Email ou mot de passe incorrect.', category='error')

            cur.close()
            conn.close()
            print("Database connection closed.")
        else:
            print("Email or password missing.")
            flash('Email ou mot de passe manquant.', category='error')
    return render_template('Connexion.html', user=current_user)


current_user_role_admin = None

#DECONNECTE L'UTILISATEUR
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# CREATION D'UN COMPTE UTILISATEUR
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        telephone = request.form.get('telephone')
        mot_de_passe = request.form.get('motDePasse')
        confirmation_mot_de_passe = request.form.get('confirmationMotDePasse')

        # Vérification des conditions pour l'enregistrement
        if len(email) < 4:
            flash('L\'email doit comporter au moins 4 caractères.', category='error')
        elif mot_de_passe != confirmation_mot_de_passe:
            flash('Les mots de passe ne correspondent pas.', category='error')
        elif len(mot_de_passe) < 7:
            flash('Le mot de passe doit comporter au moins 7 caractères.', category='error')
        else:
            # Connexion à la base de données
            conn = pymysql.connect(**db_config)
            cur = conn.cursor()

            # Vérification si l'email existe déjà
            cur.execute("SELECT * FROM Utilisateurs WHERE courriel = %s", (email,))
            if cur.fetchone():
                flash('Cet email existe déjà. Veuillez en choisir un autre.', category='error')
            else:
                # Hachage du mot de passe
                hashed_password = generate_password_hash(mot_de_passe, method='scrypt')

                # Insertion des données dans la base de données
                insert_query = ("INSERT INTO Utilisateurs (prenom, nom, telephone, courriel, mot_de_passe) "
                                "VALUES (%s, %s, %s, %s, %s)")

                cur.execute(insert_query, (prenom, nom, telephone, email, hashed_password))
                conn.commit()

                flash('Compte créé avec succès ! Connectez-vous maintenant.', category='success')
                return redirect(url_for('auth.login'))

            cur.close()
            conn.close()

    return render_template('EtudiantUtilisateur.html', user=current_user)

@auth.route('/ProfesseurIndex', methods=['GET'])
@login_required
@professor_required
def professeurIndex_():
    if current_user.is_authenticated:  # Assurez-vous que l'utilisateur est authentifié avant d'accéder à current_user
        return render_template('Professeurs/ProfesseurIndex.html', user=current_user)
    else:
        flash('Accès non autorisé.', category='error')
        return redirect(
            url_for('main.index'))  # Rediriger vers la page d'accueil si l'utilisateur n'est pas authentifié


@auth.route('/studentPage')
@login_required
@student_required
def student_page():
    return render_template("Etudiants/EtudiantIndex.html", user=current_user)

# INSÉRATION DES DONNEES DANS LA TABLE UTILISATEUR
@auth.route('/Inscription', methods=['POST'])
@login_required
def inscription_():
    global cur, conn
    if request.method == 'POST':
        utilisateur_id = int(current_user.id)
        nom = request.form.get('Nominscription')
        prenom = request.form.get('Prenominscription')
        naissance = request.form.get('naissance')
        instrument = request.form.get('instrument')
        duree = request.form.get('DureeCours')

        try:
            conn = pymysql.connect(**db_config)
            cur = conn.cursor()

            # Insérer les informations de l'étudiant dans la table Etudiants
            insert_student_query = (
                "INSERT INTO Etudiants (utilisateur_id, prenom, nom, age, instrument, duree) "
                "VALUES (%s, %s, %s, %s, %s, %s)"
            )
            cur.execute(insert_student_query, (utilisateur_id, prenom, nom, naissance, instrument, duree))
            conn.commit()


            flash('Inscription envoyée avec succès!', category='success')
        except pymysql.MySQLError as e:
            print("Erreur MySQL: ", e)
            flash('Échec de la création du compte en raison d\'une erreur de base de données.', category='error')
        finally:
            cur.close()
            conn.close()

        return redirect(url_for('auth.etudiantCreeCours_'))

    return render_template('Etudiants/EtudiantCreeCours.html', current_user=current_user)

# ROUTES ETUDIANTS

@auth.route('/EtudiantIndex', methods=['GET'])
@login_required
@student_required
def etudiantIndex_():
    return render_template('Etudiants/EtudiantIndex.html', user=current_user)



@auth.route('/EtudiantCreeCours', methods=['GET'])
@login_required
@student_required
def etudiantCreeCours_():
    return render_template('Etudiants/EtudiantCreeCours.html', user=current_user)


# INSÉRATION DES DONNEES DANS LA TABLE PROFESSEUR
@auth.route('/ajouter_professeur', methods=['POST'])
@login_required
@admin_required
def ajouter_professeur():
    if request.method == 'POST':
        prenom = request.form['prenom']
        nom = request.form['nom']
        courriel = request.form['courriel']
        telephone = request.form.get('telephone')
        mot_de_passe = request.form['motDePasse']

        # Initialisation de la variable cur à None
        cur = None

        # Insérer les données du professeur dans la base de données
        conn = pymysql.connect(**db_config)
        try:
            cur = conn.cursor()
            insert_query = ("INSERT INTO Professeurs (prenom, nom, courriel, telephone, mot_de_passe) "
                            "VALUES (%s, %s, %s, %s, %s)")
            cur.execute(insert_query, (prenom, nom, courriel, telephone, mot_de_passe))
            conn.commit()
            flash('Professeur ajouté avec succès !', category='success')
        except pymysql.MySQLError as e:
            print("Erreur MySQL: ", e)
            flash('Échec de l\'ajout du professeur en raison d\'une erreur de base de données.', category='error')
        finally:
            # Vérification si cur est initialisé avant de le fermer
            if cur is not None:
                cur.close()
            conn.close()

    return redirect(url_for('auth.afficher_professeurs'))

# AFFICHAGE DES PROFESSEUR
@auth.route('/afficher_professeurs')
@login_required
@admin_required
def afficher_professeurs():
    # Récupérer la liste des professeurs depuis la base de données
    conn = pymysql.connect(**db_config)
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM Professeurs")
        professeurs = cur.fetchall()
    except pymysql.MySQLError as e:
        print("Erreur MySQL: ", e)
        professeurs = []
    finally:
        cur.close()
        conn.close()

    return render_template('Admins/AdminProfesseurs.html', professeurs=professeurs)

# INSÉRATION DES DONNEES DANS LA TABLE PROFESSEUR
@auth.route('/Creerprofesseur', methods=['POST'])
@login_required
@admin_required
def creerprofesseur_():
    if request.method == 'POST':
        nom = request.form.get('NomProf')
        prenom = request.form.get('PrenomProf')
        courriel = request.form.get('CourrielProf')
        mot_de_passe = request.form['motDePasse']
        telephone = request.form.get('TélProf')

        if len(courriel) < 4:
            flash('L\'email doit comporter au moins 4 caractères.', category='error')
        if len(telephone) != 12:
            flash('Le numéro de téléphone doit ressemblez à XXX-XXX-XXXX', category='error')
        if prenom == "":
            flash('La case Prenom ne peut pas être vide.', category='error')
        if len(mot_de_passe) < 8:
            flash('Le mot de passe doit comporter au moins 8 caractères.', category='error')
        if nom == "":
            flash('La case Nom ne peut pas être vide.', category='error')
        else:
            # Connexion à la base de données
            conn = pymysql.connect(**db_config)
            cur = conn.cursor()

            # Insertion des données dans la base de données
            insert_query = ("INSERT INTO Professeurs (prenom, nom, courriel, telephone, mot_de_passe) "
                            "VALUES (%s, %s, %s, %s, %s)")
            cur.execute(insert_query, (prenom, nom, courriel, telephone, mot_de_passe))
            conn.commit()
            cur.close()
            conn.close()

            flash('Compte créé avec succès !', category='success')
            return redirect(url_for('main.adminCreeProfesseur_'))

        return render_template('Admins/AdminCreeProfesseur.html', user=current_user)

# INSÉRTION DES DONNEES DANS LA TABLE COURS
@auth.route('/CreerCours', methods=['POST'])
@login_required
@admin_required
def creercours_():
    global instrument, heure, jour, durée, eleve_id, prof_id, session_id
    jour = None
    conn = pymysql.connect(**db_config)
    cur = conn.cursor()
    if request.method == 'POST':
        instrument = request.form.get('InstrumentCours')
        jour = request.form.get('JourCours')
        heure = request.form.get('HeureCours')
        durée = int(request.form.get('DureeCours'))
        eleve_id = request.form.get('eleveid')
        prof_id = request.form.get('profid')
        session_id = request.form.get('sessionid')

    if heure == "":
        flash('La case Heure ne peut pas être vide.', category='error')
        return render_template('Admins/AdminCreeCours.html', user=current_user)
    if instrument == "":
        flash('La cases Instrument ne peut pas être vide.', category='error')
        return render_template('Admins/AdminCreeCours.html', user=current_user)

    cur.execute("SELECT * FROM Etudiants WHERE etudiant_id = %s", (eleve_id,))
    if cur.fetchone() is None:
        flash("ID de l'élève n'existe pas.", category='error')
        return render_template('Admins/AdminCreeCours.html', user=current_user)

    cur.execute("SELECT * FROM Professeurs WHERE professeur_id = %s", (prof_id,))
    if cur.fetchone() is None:
        flash("ID du professeur n'existe pas.", category='error')
        return render_template('Admins/AdminCreeCours.html', user=current_user)

    cur.execute("SELECT * FROM Sessions WHERE session_id = %s", (session_id,))
    if cur.fetchone() is None:
        flash("ID de la session n'existe pas.", category='error')
        return render_template('Admins/AdminCreeCours.html', user=current_user)
    else:
        # Connexion à la base de données
        conn = pymysql.connect(**db_config)
        cur = conn.cursor()

        # Insertion des données dans la base de données
        insert_query = "INSERT INTO Cours (instrument, jour, heure, duree, etudiant_id, professeur_id, session_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"

        cur.execute(insert_query, (instrument, jour, heure, int(durée), int(eleve_id), int(prof_id), int(session_id)))
        conn.commit()
        cur.close()
        conn.close()

        flash('Cours créé avec succès !', category='success')
        return redirect(url_for('main.adminCreeCours_'))


# INSÉRATION DES DONNEES DANS LA TABLE SESSION
@auth.route('/CreerSession', methods=['POST'])
@login_required
@admin_required
def creersession_():
    global nom, datedebut, datefin, nbrsemaine
    if request.method == 'POST':
        nom = request.form.get('NomSession')
        datedebut = request.form.get('Datedébut')
        datefin = request.form.get('Datefin')
        nbrsemaine = request.form.get('NombreSemaine')

    DATE_FORMAT = "%Y-%m-%d"
    datedebuttime = datetime.strptime(datedebut, DATE_FORMAT)
    datedefintime = datetime.strptime(datefin, DATE_FORMAT)

    if nom == "":
        flash('La case Nom ne peut pas être vide.', category='error')
        return render_template('Admins/AdminCreeSession.html', user=current_user)
    if nbrsemaine == "":
        flash('La cases Nombre De semaine ne peut pas être vide.', category='error')
        return render_template('Admins/AdminCreeSession.html', user=current_user)
    if datedebut == "":
        flash('La case Date de début ne peut pas être vide.', category='error')
        return render_template('Admins/AdminCreeSession.html', user=current_user)
    if datefin == "":
        flash('La case Date de fin ne peut pas être vide.', category='error')
        return render_template('Admins/AdminCreeSession.html', user=current_user)
    if datedebuttime > datedefintime:
        flash('La date de début doit être antérieure à la date de fin.', category='error')
        return render_template('Admins/AdminCreeSession.html', user=current_user)

    else:
        # Connexion à la base de données
        conn = pymysql.connect(**db_config)
        cur = conn.cursor()

        # Insertion des données dans la base de données
        insert_query = "INSERT INTO Sessions (nom_session, date_debut, date_fin, nb_semaines) VALUES (%s, %s, %s, %s)"

        cur.execute(insert_query, (nom, datedebut, datefin, int(nbrsemaine)))
        conn.commit()
        cur.close()
        conn.close()

        flash('Session créé avec succès !', category='success')
        return redirect(url_for('main.adminCreeSession_'))


# INSÉRATION DES DISPONIBILITÉ DANS LA TABLE DISPO_PROFESSEUR
@auth.route('/add_availability', methods=['POST'])
@login_required
def add_availability():
    if request.method == 'POST':
        # Convertir l'ID du professeur en entier
        professeur_id = int(current_user.id)

        # Récupérer les données du formulaire
        jour = request.form.get('jour')
        heure_debut = request.form.get('heure_debut')
        heure_fin = request.form.get('heure_fin')
        print(professeur_id)

        if heure_debut >= heure_fin:
            flash('L\'heure de début ne peut pas être égale ou après l\'heure de fin.', category="error")
            return render_template('Professeurs/ProfesseurCreeDispo.html', user=current_user)

        # Insérer les disponibilités dans la base de données
        conn = pymysql.connect(**db_config)
        cur = conn.cursor()
        try:
            insert_query = (
                "INSERT INTO Dispos_professeur (professeur_id, Jour, heure_debut, heure_fin) "
                "VALUES (%s, %s, %s, %s)"
            )
            cur.execute(insert_query, (professeur_id, jour, heure_debut, heure_fin))
            conn.commit()
            flash('Disponibilité ajoutée avec succès !', category='success')
        except pymysql.MySQLError as e:
            print("MySQL Error: ", e)
            flash('Échec de l\'ajout de disponibilité en raison d\'une erreur de base de données.', category='error')
        finally:
            cur.close()
            conn.close()

        return redirect(url_for('main.professeurCreeDispo_'))

# INSÉRATION DES DISPONIBILITÉ DANS LA TABLE DISPO_ETUDIANT
@auth.route('/add_availability_etudiant', methods=['POST'])
@login_required
def add_availability_etudiant():
    if request.method == 'POST':
        # Convertir l'ID du professeur en entier
        etudiant_id = int(current_user.id)

        # Récupérer les données du formulaire
        jours = request.form.get('jour')
        heure_debut = request.form.get('heure_debut')
        heure_fin = request.form.get('heure_fin')
        print(etudiant_id)

        if heure_debut >= heure_fin:
            flash('L\'heure de début ne peut pas en être même temps ou après l\'heure de fin.', category="error")
            return render_template('Etudiants/EtudiantCreeDispo.html', user=current_user)

        # Insérer les disponibilités dans la base de données
        conn = pymysql.connect(**db_config)
        cur = conn.cursor()
        try:
            insert_query = (
                "INSERT INTO Dispos_etudiant(utilisateur_id, Jour, heure_debut, heure_fin) "
                "VALUES (%s, %s, %s, %s)"
            )
            cur.execute(insert_query, (etudiant_id, jours, heure_debut, heure_fin))
            conn.commit()
            flash('Disponibilité ajoutée avec succès !', category='success')
        except pymysql.MySQLError as e:
            print("MySQL Error: ", e)
            flash('Échec de l\'ajout de disponibilité en raison d\'une erreur de base de données.', category='error')
        finally:
            cur.close()
            conn.close()

        return redirect(url_for('main.etudiantCreeDispo_'))
