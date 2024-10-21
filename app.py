from flask import Flask, render_template, request
import itertools

app = Flask(__name__)

# Points des lettres au Scrabble français
valeurs_lettres = {
    'e': 1, 'a': 1, 'i': 1, 'n': 1, 'o': 1, 'r': 1, 's': 1, 't': 1, 'u': 1, 'l': 1,
    'd': 2, 'g': 2, 'm': 2,
    'b': 3, 'c': 3, 'p': 3,
    'f': 4, 'h': 4, 'v': 4,
    'j': 8, 'q': 8,
    'k': 10, 'w': 10, 'x': 10, 'y': 10, 'z': 10
}

# Charger la liste officielle du scrabble (ODS6)
def charger_liste_scrabble(fichier):
    with open(fichier, 'r', encoding='utf-8') as file:
        mots = {ligne.strip().lower() for ligne in file}
    return mots

# Calculer les points d'un mot en excluant le joker (*)
def calculer_points(mot):
    return sum(valeurs_lettres[lettre] for lettre in mot if lettre != '*')

# Générer tous les mots possibles à partir des lettres de la réglette, joker et des lettres du plateau
def generer_mots_possibles(lettres_reglette, lettres_plateau, mots_scrabble, longueur_mot=None):
    lettres_reglette = lettres_reglette.lower()
    lettres_total = lettres_reglette + lettres_plateau.lower()  # Ajouter les lettres du plateau
    mots_possibles = set()

    # Identifier si un joker (*) est présent dans les lettres de la réglette
    if '*' in lettres_total:
        # Remplacer le joker par toutes les lettres de l'alphabet
        lettres_sans_joker = lettres_total.replace('*', '')
        alphabet = 'abcdefghijklmnopqrstuvwxyz'

        # Générer des combinaisons avec chaque possible substitution du joker
        for remplacement in alphabet:
            lettres_avec_remplacement = lettres_sans_joker + remplacement
            for longueur in range(2, len(lettres_avec_remplacement) + 1):
                combinaisons = itertools.permutations(lettres_avec_remplacement, longueur)
                for combinaison in combinaisons:
                    mot = ''.join(combinaison)
                    if mot in mots_scrabble:
                        if not longueur_mot or len(mot) == longueur_mot:
                            mots_possibles.add(mot)
    else:
        # Si pas de joker, générer normalement
        for longueur in range(2, len(lettres_total) + 1):
            combinaisons = itertools.permutations(lettres_total, longueur)
            for combinaison in combinaisons:
                mot = ''.join(combinaison)
                if mot in mots_scrabble:
                    if not longueur_mot or len(mot) == longueur_mot:
                        mots_possibles.add(mot)

    return mots_possibles

# Charger le dictionnaire (à exécuter une fois)
mots_scrabble = charger_liste_scrabble('ods6.txt')

@app.route('/', methods=['GET', 'POST'])
def index():
    mots_trouves = []
    lettres_reglette = ""
    lettres_plateau = ""
    longueur_mot = None
    ordre_points = "aucun"
    lettre_debut = ""

    if request.method == 'POST':
        lettres_reglette = request.form['lettres_reglette']
        lettres_plateau = request.form.get('lettres_plateau', '')
        longueur_mot = request.form.get('longueur_mot', '')

        # Convertir la longueur du mot si renseignée
        if longueur_mot:
            longueur_mot = int(longueur_mot)

        # Générer les mots possibles
        mots_possibles = generer_mots_possibles(lettres_reglette, lettres_plateau, mots_scrabble, longueur_mot)

        # Calculer les points des mots trouvés
        mots_trouves = [(mot, calculer_points(mot)) for mot in sorted(mots_possibles)]

        # Appliquer les filtres de tri
        ordre_points = request.form.get('ordre_points', 'aucun')

        # Filtrer par lettre de départ
        if lettre_debut:
            mots_trouves = [mot for mot in mots_trouves if mot[0] == lettre_debut.lower()]

        # Trier par points ou par ordre alphabétique
        if ordre_points == "croissant":
            mots_trouves.sort(key=lambda x: x[1])  # Tri par points croissants
        elif ordre_points == "decroissant":
            mots_trouves.sort(key=lambda x: x[1], reverse=True)  # Tri par points décroissants
        else:
            mots_trouves.sort(key=lambda x: x[0])  # Tri par ordre alphabétique

    return render_template('index.html', 
                           mots_trouves=mots_trouves, 
                           lettres_reglette=lettres_reglette, 
                           lettres_plateau=lettres_plateau, 
                           longueur_mot=longueur_mot, 
                           ordre_points=ordre_points, 
                           lettre_debut=lettre_debut)

if __name__ == '__main__':
    app.run(debug=True)
