from datetime import timedelta
from functools import wraps

import pymysql
from flask import Flask, redirect, url_for, flash
from flask_login import LoginManager, current_user
from .auth import User, db_config, get_user_role


def create_app():
    app = Flask(__name__)

    app.secret_key = 'votre_clé_secrète_ici'
    login_manager = LoginManager()  # Créez une instance de LoginManager
    login_manager.init_app(app)  # Initialisez l'application avec LoginManager
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)  # Durée du cookie de rappel en jours

    login_manager.login_view = 'auth.login'  # Spécifie la vue de connexion

    # Fonction user_loader pour charger un utilisateur à partir de l'ID stocké dans la session
    @login_manager.user_loader
    def load_user(user_id):
        # Connexion à la base de données
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

        # Fermeture de la connexion à la base de données
        cur.close()
        conn.close()

        # Si l'utilisateur est trouvé, retournez une instance de la classe User avec le nom, le prénom et le rôle

        if user_data:
            user = User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4])
            # Récupérer le rôle de l'utilisateur à partir de la base de données
            # et l'attribuer à l'objet current_user
            user.role = get_user_role(user_data[1])  # Utilisez la fonction get_user_role appropriée
            return user

        else:
            return None

    # Blueprint pour les routes d'authentification dans notre application
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # Blueprint pour les parties de l'application non liées à l'authentification
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
