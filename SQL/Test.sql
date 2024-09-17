use bd_arquemuse;

/* INDEX */

CREATE INDEX courriel ON utilisateurs(courriel);
CREATE INDEX nom_etudiant ON etudiants(prenom);
CREATE INDEX nom_prof ON professeurs(prenom);

/* VERIFICATION SI UN COURRIEL UTILISATEUR EST DEJA EXISTANT DANS LA BD ***erreur*** */

DELIMITER //

CREATE TRIGGER duplication_mail
BEFORE INSERT ON utilisateurs
FOR EACH ROW
BEGIN
    IF (SELECT COUNT(*) FROM utilisateurs WHERE courriel = NEW.courriel) >= 1
    THEN
        SIGNAL SQLSTATE "45000" SET MESSAGE_TEXT = "Utilisateur deja existant";
    END IF;
END //

DELIMITER ;

/* VERIFICATION PAS PLUS DE 5 DISPONIBILITES POUR UN PROFESSEUR */
DELIMITER //
CREATE TRIGGER dispo_max
BEFORE INSERT ON dispos_professeur
FOR EACH ROW
BEGIN
    IF (SELECT COUNT(*) FROM dispos_professeur WHERE professeur_id = NEW.professeur_id) >= 5
    THEN
        SIGNAL SQLSTATE "45000" SET MESSAGE_TEXT = "Maximum disponibilites";
    END IF;
END //
DELIMITER ;

/* VERIFICATION PAS PLUS DE 5 DISPONIBILITES POUR UN ETUDIANT */
DELIMITER //
CREATE TRIGGER dispo_max_etudiant
BEFORE INSERT ON dispos_etudiant
FOR EACH ROW
BEGIN
    IF (SELECT COUNT(*) FROM dispos_etudiant WHERE utilisateur_id = NEW.utilisateur_id) >= 5
    THEN
        SIGNAL SQLSTATE "45000" SET MESSAGE_TEXT = "Maximum disponibilites";
    END IF;
END //
DELIMITER ;


DELIMITER //

CREATE TRIGGER traitement_apres_insertion
AFTER INSERT ON Cours
FOR EACH ROW
BEGIN
    UPDATE Etudiants SET traitee = 'oui' WHERE etudiant_id = NEW.etudiant_id;
END //

DELIMITER ;

