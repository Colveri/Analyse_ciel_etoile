### Importation des modules ###

import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, Text, Button
from PIL import Image, ImageTk
import cv2
import numpy as np
import webbrowser


### Variables globales ###

seuilLst= [100,99,98,97,96,95,94,93,92,91,90,
           89,88,87,86,85,84,83,82,81,80,
           79,78,77,76,75,74,73,72,71,70,
           69,68,67,66,65,64,63,62,61,60,
           59,58,57,56,55,54,53,52,51,50,
           49,48,47,46,45,44,43,42,41,40,
           39,38,37,36,35,34,33,32,31,30,
           29,28,27,26,25,24,23,22,21,20,
           19,18,17,16,15,14,13,12,11,10,
                          9,8,7,6,5,4,3,2,1,0]
tolerance = seuilLst[100-60]


### Vérification des modules ###
if int(str(sys.version_info[0]) + str(sys.version_info[1])) <= 311:
    try:
        import cv2
    except Exception as e:
        if messagebox.askyesno('Erreur',
                               f'Une erreur est survenue: {e}\n Tout les modules ne sont pas installés, voulez vous '
                               f'les installer? (Cela devrait prendre quelques minutes)'):
            import subprocess

            messagebox.showinfo('Téléchargement', 'Le téléchargement commencera quand vous aurez fermé la fenêtre. Le programme va '
                                               'redémarrer une fois le téléchargement terminé.')
            subprocess.call(['python3', '-m', 'pip', 'install','-r', 'requirements.txt'])
            import cv2
        else:
            exit()





### Fonctions de l'interface ###



def select_image():
    global img, file_path, tolerance
    file_path = filedialog.askopenfilename()
    img = cv2.imread(file_path, cv2.IMREAD_COLOR)
    analyze_image()


def analyze_image():
    global img, file_path
    # Convertir l'image en niveaux de gris
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Récupérer la valeur de la tolérance
    tolerance = tolerance_scale.get()
    
    # Définir la plage de valeurs
    lower = np.array([tolerance])
    upper = np.array([255])

    # Extraire les pixels dans la plage de valeurs
    mask = cv2.inRange(gray, lower, upper)

    # Trouver les contours dans le masque
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    console.insert(tk.END, f'Nombre d\'étoiles: {len(contours)}\n')

    # Parcourir tous les contours
    for i, contour in enumerate(contours):
        # Calculer le moment du contour
        M = cv2.moments(contour)

        # Calculer le centre de masse du contour
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            # Calculer la couleur moyenne de l'étoile
            mask = np.zeros(img.shape[:2], dtype="uint8")
            cv2.drawContours(mask, [contour], -1, 255, -1)
            moy_color_bgr = cv2.mean(img, mask=mask)[:3]

            # Arrondir les valeurs de couleur
            moy_color_bgr = tuple(round(val) for val in moy_color_bgr)

        else:
            if M["m00"] == 0 or M["m00"] == 0.0:
                M["m00"] = 1
            if M["m10"] == 0 or M["m10"] == 0.0:
                M["m10"] = 1
            if M["m01"] == 0 or M["m01"] == 0.0:
                M["m01"] = 1

            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            moy_color_bgr = img[cY, cX]

        cv2.drawContours(img, [contour], -1, (0, 255, 0), 2)
        cv2.putText(img, str(i+1), (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Convertir BGR à RGB
        moy_color_rgb = moy_color_bgr[::-1]


        console.insert(tk.END, f'Etoile {i+1} - Couleur moyenne RGB: {moy_color_rgb}\n')
        
    # Affiche la tolérance selectionnée
    console.insert(tk.END, f'Valeur de la tolérance: {tolerance}\n')


def download_image():
    global img, file_path
    # Convertir l'image numpy.ndarray en une image PIL
    img_pil = Image.fromarray(img)
    # Enregistrer l'image analysée
    img_pil.save(os.path.splitext(file_path)[0] + '_analysé.png')
    console.insert(tk.END, "Image analysée téléchargée.\n")


def show_about():
    messagebox.showinfo('A propos', 'Analyse d\'image de ciel étoilé\n\nLa valeur de tolérance par défaut est de 60 %\n\nProgramme fait par Coleen - TG08.\n')


def show_help():
    messagebox.showinfo('Comment utiliser', "Veuillez selectionner une tolérance avant de séléctionner l'image.\nLa valeur est prise en compte une fois l'image selectionnée.\nVous trouverez l'image analysée dans le même répertoire que l'image d'origine.\nSi l'analyse manque des étoiles, veuillez revoir la tolérance et reselectionner l'image originale.")


# Fonction pour mettre en mémoire la valeur de la tolérance
def memorize_tolerance():
    tolerance_value = tolerance_scale.get()
    print(f"La valeur de la tolérance {tolerance_value} a été mise en mémoire.")
    tolerance_value = seuilLst[tolerance_value] # vu que la tolérance est inversée,
                                                # on fait comme on peut...
    print(f"La vraie valeur de la tolérance {tolerance_scale.get()} a été mise en mémoire.")
    # Plus c'est haut, plus la sensibilité est grande
    # Plus c'est bas, plus la sensibilité est petite
    # Car avant, 100% de tolérance = 0% de sensibilité à la couleur
    # Et maintenant, 100% de tolérance = 100% de sensibilité à la couleur

def link_To_GitHub():
    if messagebox.askyesno('Mise à jour', 'Voulez-vous être redirigé vers la page GitHub du programme?'):
        webbrowser.open("https://github.com/Colveri/Analyse_ciel_etoile")
    else:
        messagebox.showinfo('Mise à jour', "Vous pouvez retrouver le programme sur GitHub: https://github.com/Colveri/Analyse_ciel_etoile") # Je sais pas si c'est utile mais bon

### Interface ###

root = tk.Tk()
root.title("Analyse d'image de ciel étoilé")




### Création des widgets ###

# Créer une barre de menu (la barre en haut de la fenêtre)
menubar = tk.Menu(root)

# Créer un menu Fichier
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Ouvrir", command=select_image)
filemenu.add_command(label="Enregistrer l'analyse", command=download_image)
filemenu.add_separator()
filemenu.add_command(label="Quitter", command=root.quit)
menubar.add_cascade(label="Fichier", menu=filemenu)

# Créer un menu Aide
helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="A propos", command=show_about)
helpmenu.add_command(label="Comment utiliser", command=show_help)
helpmenu.add_command(label="Mise à jour", command=link_To_GitHub)
menubar.add_cascade(label="Aide", menu=helpmenu)

# Ajouter la barre de menu à la fenêtre
root.config(menu=menubar)

# Widget Curseur pour la tolérance
tolerance_label = tk.Label(root, text="Tolérance :")
tolerance_label.pack()
tolerance_scale = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL)
tolerance_scale.set(60)  # Valeur par défaut
tolerance_scale.pack()

# Bouton pour mettre en mémoire la valeur de la tolérance
memorize_button = tk.Button(root, text="Mémoriser la tolérance", command=memorize_tolerance)
memorize_button.pack()

# Widget Text pour afficher le texte de la console
console = Text(root)
console.pack()

console.insert(tk.END, "C'est ici que vous trouverez les informations sur l'image analysée.\nBonne utilisation.\n")


root.mainloop()