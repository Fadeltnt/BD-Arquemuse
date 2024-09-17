import os
from auth import *
from turtle import pd
import pymysql
from dotenv import load_dotenv
import random
from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

#Connection a la bd
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

""" CREATION DE TABLES"""

# /// CREATION DE LA BD ///
create_table1 = "CREATE DATABASE IF NOT EXISTS bd_arquemuse;"

# /// SESSIONS ///
create_table2 = ("CREATE TABLE IF NOT EXISTS Sessions(session_id int auto_increment,nom_session varchar(20) NOT NULL,"
                 "date_debut DATE NOT NULL, date_fin DATE NOT NULL, nb_semaines int(2),"
                 "PRIMARY KEY(session_id));")
# /// UTILISATEURS ///

create_table3 = ("CREATE TABLE IF NOT EXISTS Utilisateurs(utilisateur_id int auto_increment,prenom varchar(20) NOT NULL,"
                 " nom varchar(20) NOT NULL,telephone varchar(14) NOT NULL, courriel varchar(30) NOT NULL, "
                 "mot_de_passe varchar(200) NOT NULL, role varchar(15) DEFAULT 'Etudiant',"
                 "PRIMARY KEY(utilisateur_id));")

# /// ETUDIANTS ///

create_table4 = ("CREATE TABLE IF NOT EXISTS  Etudiants(etudiant_id int auto_increment, utilisateur_id int,"
                 "prenom varchar(20) NOT NULL, nom char(20) NOT NULL, age int(2) NOT NULL,"
                 "instrument varchar(25) NOT NULL, duree int(2), traitee varchar(3) DEFAULT 'non',"
                 "PRIMARY KEY (etudiant_id),"
                 "FOREIGN KEY (utilisateur_id) REFERENCES Utilisateurs(utilisateur_id));")

# /// PROFESSEURS ///

create_table5 = ("CREATE TABLE IF NOT EXISTS Professeurs(professeur_id int auto_increment,prenom varchar(20) NOT NULL, "
                 "nom varchar(20) NOT NULL, courriel varchar(30) NOT NULL,telephone varchar(12), "
                 "mot_de_passe varchar(200), role varchar(15) DEFAULT 'Professeur',"
                 "PRIMARY KEY (professeur_id));")

# /// COURS ///

create_table6 = ("CREATE TABLE IF NOT EXISTS Cours(cours_id int auto_increment,etudiant_id int NOT NULL, "
                 "professeur_id int NOT NULL, instrument varchar(20) NOT NULL,jour varchar(8) NOT NULL, "
                 "heure TIME NOT NULL, duree int(2) NOT NULL, session_id int,"
                 "PRIMARY KEY(cours_id),"
                 "FOREIGN KEY(etudiant_id) REFERENCES Etudiants(etudiant_id),"
                 "FOREIGN KEY(professeur_id) REFERENCES Professeurs(professeur_id),"
                 "FOREIGN KEY(session_id) REFERENCES sessions(session_id));")

# /// DISPOS ETUDIANTS ///

create_table7 = ("CREATE TABLE IF NOT EXISTS Dispos_etudiant(dispo_id int auto_increment, utilisateur_id int, "
                 "Jour varchar(8),heure_debut time, heure_fin time,"
                 "PRIMARY KEY(dispo_id),"
                 "FOREIGN KEY(utilisateur_id) REFERENCES Utilisateurs(utilisateur_id));")

# /// DISPOS PROFESSEURS ///

create_table8 = ("CREATE TABLE IF NOT EXISTS Dispos_professeur(dispo_id int auto_increment, professeur_id int, "
                 "Jour varchar(8),heure_debut time, heure_fin time,"
                 "PRIMARY KEY(dispo_id),"
                 "FOREIGN KEY(professeur_id) REFERENCES professeurs(professeur_id));")

# /// ADMINISTRATEURS ///

create_table9 = ("CREATE TABLE IF NOT EXISTS Administrateurs(admin_id int auto_increment, prenom varchar(20) NOT NULL,"
                 "nom varchar(20) NOT NULL, courriel varchar(30) NOT NULL,mot_de_passe varchar(200) NOT NULL, "
                 "role varchar(15) DEFAULT 'Administrateur', "
                 "PRIMARY KEY(Admin_id));")

cursor.execute(create_table1)
cursor.execute(create_table2)
cursor.execute(create_table3)
cursor.execute(create_table4)
cursor.execute(create_table5)
cursor.execute(create_table6)
cursor.execute(create_table7)
cursor.execute(create_table8)
cursor.execute(create_table9)


# // SELECT TOUS LES COURS POUR ADMIN //
def select_cours():
    request = ("SELECT C.session_id, C.cours_id, C.jour, C.instrument, C.duree, C.heure, E.prenom, P.prenom FROM Cours C,"
               " Etudiants E, Professeurs P WHERE E.etudiant_id = C.etudiant_id AND P.professeur_id = C.professeur_id"
               " ORDER BY C.session_id DESC, C.cours_id;")
    cursor.execute(request)

    cours = cursor.fetchall()

    return cours

# // SELECTION DES COURS D'UN ETUDIANT //
def select_cours_etudiant(user_id):
    request = (f"SELECT C.cours_id, C.jour, C.instrument, C.duree, C.heure, E.prenom, P.prenom FROM Cours C, Etudiants E,"
               f"Professeurs P, Utilisateurs U WHERE U.utilisateur_id = ('{user_id}') AND P.professeur_id = C.professeur_id AND "
               f"E.etudiant_id = C.etudiant_id AND U.utilisateur_id = E.utilisateur_id;")
    cursor.execute(request)

    cours_etudiant = cursor.fetchall()

    return cours_etudiant

# // SELECTION DES COURS D'UN PROF //
def select_cours_prof(user_id):
    request = (f"SELECT C.jour, C.heure, C.instrument, C.duree, E.prenom FROM Cours C, Etudiants E, Professeurs P WHERE "
               f"P.professeur_id = ('{user_id}') AND P.professeur_id = C.professeur_id AND E.etudiant_id = C.etudiant_id;")
    cursor.execute(request)

    cours_etudiant = cursor.fetchall()

    return cours_etudiant

# // SELECTION DES ELEVES DANS LA BASE DE DONNÉ //
def select_eleves():
    request = (
        "SELECT E.etudiant_id, E.prenom, E.nom, U.courriel, E.age, E.instrument, E.duree, E.traitee FROM Etudiants E, "
        "Utilisateurs U WHERE U.utilisateur_id = E.utilisateur_id ORDER BY E.etudiant_id DESC;")
    cursor.execute(request)

    eleves = cursor.fetchall()

    return eleves

# // SELECTION DES PROFESSEURS DANS LA BASE DE DONNÉ //
def select_professeurs():
    request = "SELECT professeur_id, prenom, nom, courriel, telephone FROM Professeurs ORDER BY professeur_id DESC;"
    cursor.execute(request)

    prof = cursor.fetchall()

    return prof

# // SELECTION DES SESSIONS DANS LA BASE DE DONNÉ //
def select_sessions():
    request = "SELECT session_id, nom_session, date_debut, date_fin, nb_semaines FROM Sessions ORDER BY session_id DESC;"
    cursor.execute(request)

    session = cursor.fetchall()

    return session

# // SELECTION DES ELEVES POUR UN PROFESSEUR //
def select_eleves_from_prof(user_id):
    request_prof = (f"SELECT E.prenom, E.nom, E.age, E.instrument, U.courriel, U.telephone FROM Etudiants E, Cours C, "
                    f"Utilisateurs U WHERE professeur_id = ('{user_id}') AND E.etudiant_id = C.etudiant_id AND "
                    f"E.utilisateur_id = U.utilisateur_id;")
    cursor.execute(request_prof)

    session = cursor.fetchall()

    return session

# // SELECTION DES DISPONIBILITÉ D'UN PROFESSEUR //
def select_dispos_from_prof(user_id):
    request_dispos_prof = f"SELECT D.jour, D.heure_debut, D.heure_fin FROM Dispos_professeur D WHERE professeur_id = ('{user_id}');"
    cursor.execute(request_dispos_prof)

    dispos = cursor.fetchall()

    return dispos

# // SELECTION DES DISPONIBILITÉ POUR UN ELEVE //
def select_dispos_from_etudiant(user_id):
    request_dispos_etudiant = f"SELECT D.jour, D.heure_debut, D.heure_fin FROM Dispos_etudiant D WHERE utilisateur_id = ('{user_id}');"
    cursor.execute(request_dispos_etudiant)

    dispos = cursor.fetchall()

    return dispos

# // SELECTION DE LA DISPONIBILITÉ DE TOUT LES PROFESSEURS //
def dispo_prof():
    request = ("SELECT P.professeur_id, P.prenom, P.nom, D.jour, D.heure_debut, D.heure_fin FROM Dispos_professeur D, "
               "Professeurs P WHERE P.professeur_id = D.professeur_id")
    cursor.execute(request)

    prof = cursor.fetchall()

    return prof

# // SELECTION ES DIPONIBILITER DES ELEVES //
def dispo_eleve():
    request = ("SELECT E.etudiant_id, E.prenom, E.nom, D.jour, D.heure_debut, D.heure_fin FROM Dispos_etudiant D, "
               "Utilisateurs U, Etudiants E WHERE U.utilisateur_id = D.utilisateur_id AND E.utilisateur_id = U.utilisateur_id "
               "ORDER BY E.etudiant_id;")
    cursor.execute(request)

    prof = cursor.fetchall()

    return prof

# // LISTE DE NOM ET PRENOM POUR CREATION DE COMPTE //
prenoms = ["Alice", "Bob", "Celine", "David", "Emma", "Francois", "Giselle", "Henry", "Irene", "Jack",
           "Karen", "Louis", "Marie", "Nathan", "Olivia", "Paul", "Quentin", "Rosa", "Simon", "Tina"]
noms = ["Dupont", "Martin", "Durand", "Petit", "Leroy", "Moreau", "Blanc", "lavoie", "Rousseau", "Lefevre"]
instruments = ["Accordeon", "Batterie", "Chant", "Clarinette", "Djembe", "Flute traversière", "Guitare", "Piano",
               "Saxophone", "Trompette",
               "Violon", "Violoncelle", "Ukulele"]

# // GENERATION D'ETUDIANT //
def generer_etudiants(nombre):
    for _ in range(nombre):
        utilisateur_id = random.randint(1, 100)
        prenom = random.choice(prenoms)
        nom = random.choice(noms)
        age = random.randint(10, 70)
        instrument = random.choice(instruments)
        duree = random.choice([30, 60])
        print(f"({utilisateur_id}, '{prenom}', '{nom}', {age}, '{instrument}', {duree}),")


#generer_etudiants(150)

# // LISTE DE TELEPHONE POUR GÉNÉRATION D'UTILISATEUR //
telephonelist = numeros_telephone_canadiens = [
    "613-555-1234", "416-555-9876", "905-555-4567", "514-555-7890", "604-555-2345",
    "902-555-6789", "306-555-3456", "204-555-8901", "709-555-4567", "902-555-7890",
    "506-555-1234", "403-555-8765", "867-555-2345", "204-555-7890", "902-555-3456",
    "819-555-6789", "438-555-9012", "450-555-3456", "506-555-7890", "709-555-2345"
]

# // GENERATION DE CHIFFRE A AJOUTER AU COURRIEL //
def generer_trois_chiffres():
    return random.randint(100, 999)

# // GENERATION D'UTTILISATEUR //
def generer_utilisateur(nombre):
    for _ in range(nombre):
        prenom = random.choice(prenoms)
        nom = random.choice(noms)
        courriel = f"{prenom}.{nom}{str(random.randint(1, 100))}@gmail.com"
        telephone = random.choice(telephonelist)
        mot_de_passe = f"{prenom}{generer_trois_chiffres()}"
        mot_de_passe_hache = generate_password_hash(mot_de_passe, method='scrypt')
        print(f"('{prenom}', '{nom}', '{telephone}', '{courriel}', '{mot_de_passe_hache}'),")

#generer_utilisateur(125)

# // GENERATION DE PROFESSEUR
def generer_professseur(nombre):
    for _ in range(nombre):
        prenom = random.choice(prenoms)
        nom = random.choice(noms)
        courriel = f"{prenom}.{nom}@gmail.com"
        telephone = random.choice(telephonelist)
        mot_de_passe = f"{prenom}{generer_trois_chiffres()}"
        mot_de_passe_hache = generate_password_hash(mot_de_passe, method='scrypt').encode('utf-8')
        print(f"('{prenom}', '{nom}', '{courriel}', '{telephone}', '{mot_de_passe_hache.decode('utf-8')}'),")

#generer_professseur(20)
