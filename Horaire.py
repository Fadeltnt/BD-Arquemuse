from tkinter import *

# Fenetre generer selon la grosseur de votre ecran
window = Tk()
window.title('Horaire')
window_width = int(window.winfo_screenwidth())
window_height = int(window.winfo_screenheight())
window.geometry("%dx%d+0+0" % (window_width, window_height))
window.state('zoomed')
frame1 = Frame(window)
frame1.pack()

#Canvas pour la taille de l'horaire
nb_lignes = 31
schedule_height = window_height - 300
schedule_width = window_width - 500
case_height = schedule_height / nb_lignes
case_width = schedule_width / 8
canvas = Canvas(frame1, bg='#E0CFFF', height=schedule_height, width=schedule_width)
canvas.pack(expand=True)


# Dessiner les lignes du canvas
def canvas_lignes(lignes):

    y = 0
    for i in range(window_width):
        x = 0
        grosseur = 2
        if i % 2 == 0:
            grosseur = 1
        canvas.create_line(x, y, schedule_width, y, width=grosseur)
        y = y + case_height
    x = 0
    for j in range(window_height):
        y = 0
        canvas.create_line(x, y, x, window_height, width=2)
        x = x + case_width


# Les heures de la journée sur le canvas
def canvas_heure(lignes):
    x = 0
    texte = 7
    for i in range(lignes//2):
        x = x + 2
        texte = texte + 1
        display = str(texte) + ':00'
        canvas.create_text(case_width / 2, (case_height * x - case_height / 2), text=display, anchor=CENTER)


# Les jours de la semaine sur le canvas
def canvas_jour():

    x = 1

    for j in range(7):
        x = x + 1
        if j == 0:
            display = 'LUNDI'
        elif j == 1:
            display = 'MARDI'
        elif j == 2:
            display = 'MERCREDI'
        elif j == 3:
            display = 'JEUDI'
        elif j == 4:
            display = 'VENDREDI'
        elif j == 5:
            display = 'SAMEDI'
        else:
            display = 'DIMANCHE'

        canvas.create_text((case_width * x - case_width / 2), case_height / 2, text=display, anchor=CENTER)


# Convertion de jour en point X
def jour_position(jour):

    if jour == "lundi":
        return case_width
    if jour == "mardi":
        return case_width * 2
    if jour == "mercredi":
        return case_width * 3
    if jour == "jeudi":
        return case_width * 4
    if jour == "vendredi":
        return case_width * 5
    if jour == "samedi":
        return case_width * 6
    if jour == "dimanche":
        return case_width * 7


# Conversion de heure en point Y
def heure_position(heure):

    return case_height * ((heure - 7.5) * 2)


# Afficher un cours en fonction du nom de l'eleve. le jour, l'heure et la duree du cours.
# Le statut signifie si l'eleve est confirmee ou en processus de...
def affichage_cours(nom, jour, heure, duree, statut):

    x = jour_position(jour)
    y_1 = heure_position(heure)
    texte = nom
    couleur = '#C6FF94'

    if statut == "En traitement":
        couleur = '#FFFEAD'

    if duree == 30:
        y_2 = y_1 + case_height
    elif duree == 45:
        y_2 = y_1 + case_height + (case_height/2)
    else:
        y_2 = y_1 + case_height * 2

    canvas.create_rectangle(x, y_1, x + case_width, y_2, fill=couleur)
    canvas.create_text(x + 2, y_1, text=texte, anchor='nw')


# Afficher les disponibilites
def affichage_dispos(jour, de, a):

    x = jour_position(jour)
    y_1 = heure_position(de)
    y_2 = heure_position(a)

    canvas.create_rectangle(x, y_1, x + case_width, y_2, fill='#BABABA')

#Les fonctions sont appelles pour creer l'horaire
affichage_dispos("mardi", 9, 19,)
affichage_dispos("lundi", 8, 17)
affichage_dispos("samedi", 14, 19)

affichage_cours("Robert Pelletier", "mardi", 19, 60, "En traitement")
affichage_cours("Sonia Vachon", "mardi", 17, 60, "confirmé")

canvas_lignes(nb_lignes)
canvas_jour()
canvas_heure(nb_lignes)

window.mainloop()