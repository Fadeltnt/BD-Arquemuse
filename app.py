from datetime import timedelta
from functools import wraps

import pymysql
from flask import Flask, redirect, url_for, flash
from flask_login import LoginManager, current_user
from auth import User, db_config, get_user_role
from dotenv import load_dotenv
import os
import pymysql

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Accéder aux variables d'environnement
DB_HOST = os.getenv('HOST')
DB_PORT = os.getenv('PORT')
DB_DATABASE = os.getenv('DATABASE')
DB_USERNAME = os.getenv('USERNAME')
DB_PASSWORD = os.getenv('PASSWORD')


def create_app():
    app = Flask(__name__)

    app.secret_key = 'votre_clé_secrète_ici'
    login_manager = LoginManager()
    login_manager.init_app(app)
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)

    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        global user_data
        conn = pymysql.connect(**db_config)
        cur = conn.cursor()

        tables = [("Utilisateurs", "utilisateur_id"), ("Professeurs", "professeur_id"), ("Administrateurs", "admin_id")]
        for table, id_field in tables:
            cur.execute(f"SELECT {id_field}, courriel, nom, prenom, role FROM {table} WHERE {id_field} = %s",
                        (user_id,))

            user_data = cur.fetchone()
            if user_data:
                break

        cur.close()
        conn.close()

        if user_data:
            user = User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4])
            user.role = get_user_role(user_data[1])
            return user

        else:
            return None

    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app


# Cette ligne est essentielle pour Gunicorn
app = create_app()
