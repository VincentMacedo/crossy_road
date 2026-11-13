import math
import random
import pygame
from player import Player
from voiture import Voiture
from train import Train


def assombrir(couleur, facteur):
    return tuple(int(c * facteur) for c in couleur)


def eclaircir(couleur, ajout):
    return tuple(min(255, c + ajout) for c in couleur)


class Decor:
    """Arbre ou rocher posé sur une case d'herbe (créé à la volée pour le dessin)."""

    def __init__(self, genre, col, taille_case):
        self.genre = genre
        self.col = col
        self.x = col * taille_case


class Monde:
    # --- Monde (en "pixels de monde") ---
    TAILLE_LIGNE = 40
    LARGEUR = 800                       # zone jouable : x de 0 à LARGEUR
    NB_COLONNES = LARGEUR // TAILLE_LIGNE
    MARGE = 400                         # largeur de la forêt de chaque côté (sol en herbe)
    NB_COLONNES_FORET = MARGE // TAILLE_LIGNE
    MARGE_VEHICULES = 160               # les véhicules disparaissent/apparaissent dans la forêt

    # --- Réglages du jeu ---
    VOITURES_MIN = 4
    VOITURES_MAX = 8
    DENSITE_ARBRES = 0.18               # arbres/rochers dans la zone jouable
    DISTANCE_SECURITE = 100             # une voiture ralentit si elle s'approche trop de celle de devant
    VITESSES_VOITURES = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]

    # --- Projection ---
    ZOOM = 1.5
    ROTATION = 15      # degrés : petite valeur = on avance surtout vers le haut, un peu vers la droite
    ELEVATION = 55     # degrés : angle de la caméra (90 = vue de dessus, petit = vue plus rasante)
    COS_ROT = math.cos(math.radians(ROTATION))
    SIN_ROT = math.sin(math.radians(ROTATION))
    SIN_ELEV = math.sin(math.radians(ELEVATION))

    # --- Couleurs ---
    FOND = (30, 30, 40)
    BLANC = (245, 245, 245)
    CRETE = (220, 40, 40)
    COULEURS_VOITURES = [
        (230, 70, 60), (240, 190, 50), (70, 150, 230),
        (120, 200, 120), (200, 100, 220), (240, 240, 240),
    ]

    # type de ligne : (couleur, hauteur du sol)
    STYLES = {
        "herbe": ((110, 200, 80), 12),
        "route": ((70, 70, 78), 0),
        "chemin_de_fer": ((150, 135, 120), 0),
        "eau": ((70, 150, 230), -6),
    }
    EPAISSEUR = 10  # épaisseur visible sous chaque ligne

    def __init__(self, ecran, graine):
        self.ecran = ecran
        self.graine = graine
        self.lignes = {}

        largeur_ecran, hauteur_ecran = ecran.get_size()
        self.centre_x = largeur_ecran // 2
        self.centre_y = int(hauteur_ecran * 0.68)

        self.joueur = Player(40, pygame.Rect(200, 400, 40, 40))

        # caméra centrée sur le joueur (en coordonnées de monde)
        self.camera_x = self.joueur.rectangle.centerx
        self.camera_y = self.joueur.rectangle.centery
        self.z_joueur = self.STYLES["herbe"][1]

    # ------------------------------------------------------------------
    # Génération des lignes (déterministe : même graine = même monde)
    # ------------------------------------------------------------------
    def colonne_passage(self, indice):
        """Colonne qui reste praticable entre la ligne `indice` et la suivante
        (évite qu'un lac ou une rangée d'arbres bloque complètement la partie)."""
        rng = random.Random(f"{self.graine}:passage:{indice}")
        return rng.randrange(1, self.NB_COLONNES - 1)

    def generer_ligne(self, indice):
        rng = random.Random(f"{self.graine}:{indice}")

        if indice > 5:
            type_ligne = "herbe"
        else:
            types = ["herbe", "route", "eau", "chemin_de_fer"]
            poids = [4, 3, 2, 1]
            type_ligne = rng.choices(types, weights=poids)[0]

        t = self.TAILLE_LIGNE
        rect = pygame.Rect(0, indice * t, self.LARGEUR, t)
        ligne = {
            "type": type_ligne,
            "rect": rect,
            "indice": indice,
            "vehicules": [],   # voitures ou train de cette ligne
            "decor": {},       # colonne -> "arbre" / "rocher" / "nenuphar"
        }

        if type_ligne == "herbe":
            self.remplir_herbe(ligne, rng)
        elif type_ligne == "route":
            self.remplir_route(ligne, rng)
        elif type_ligne == "chemin_de_fer":
            self.remplir_rail(ligne, rng)
        elif type_ligne == "eau":
            self.remplir_eau(ligne, rng)

        self.remplir_foret(ligne)
        return ligne

    def remplir_foret(self, ligne):
        """Forêt dense de chaque côté de la zone jouable, sur toutes les lignes."""
        for k in range(1, self.NB_COLONNES_FORET + 1):
            ligne["decor"][-k] = "arbre"
            ligne["decor"][self.NB_COLONNES - 1 + k] = "arbre"

    def remplir_herbe(self, ligne, rng):
        indice = ligne["indice"]
        g1 = self.colonne_passage(indice - 1)
        g2 = self.colonne_passage(indice)
        libres = set(range(min(g1, g2), max(g1, g2) + 1))   # couloir toujours dégagé

        for col in range(self.NB_COLONNES):
            if col in libres:
                continue
            if 9 <= indice <= 11 and 4 <= col <= 6:
                continue            # zone de départ du joueur
            if rng.random() < self.DENSITE_ARBRES:
                ligne["decor"][col] = "rocher" if rng.random() < 0.3 else "arbre"

    def remplir_route(self, ligne, rng):
        y = ligne["rect"].y
        nb = rng.randint(self.VOITURES_MIN, self.VOITURES_MAX)
        sens = rng.choice([-1, 1])
        # chaque voiture a sa propre vitesse (toutes différentes sur une même route)
        vitesses = rng.sample(self.VITESSES_VOITURES, nb)
        boucle = self.LARGEUR + 2 * self.MARGE_VEHICULES + 40
        for k in range(nb):
            x = -self.MARGE_VEHICULES - 40 + (k * boucle) // nb + rng.randint(0, 60)
            couleur = rng.choice(self.COULEURS_VOITURES)
            ligne["vehicules"].append(
                Voiture(sens * vitesses[k], pygame.Rect(x, y, 40, 40), couleur))

    def remplir_rail(self, ligne, rng):
        y = ligne["rect"].y
        sens = rng.choice([-1, 1])
        vitesse = sens * rng.randint(5, 8)
        x = rng.randint(-self.MARGE_VEHICULES, self.LARGEUR)
        ligne["vehicules"].append(Train(vitesse, pygame.Rect(x, y, 200, 40)))

    def remplir_eau(self, ligne, rng):
        indice = ligne["indice"]
        g1 = self.colonne_passage(indice - 1)
        g2 = self.colonne_passage(indice)
        # chemin de nénuphars entre les deux colonnes de passage
        for col in range(min(g1, g2), max(g1, g2) + 1):
            ligne["decor"][col] = "nenuphar"
        # quelques nénuphars en plus
        for col in range(self.NB_COLONNES):
            if rng.random() < 0.25:
                ligne["decor"][col] = "nenuphar"

    # ------------------------------------------------------------------
    # Mise à jour
    # ------------------------------------------------------------------
    @property
    def liste_vehicules(self):
        """Tous les véhicules des lignes actuellement chargées."""
        return [v for ligne in self.lignes.values() for v in ligne["vehicules"]]

    def deplacer_vehicules(self):
        boucle = self.LARGEUR + 2 * self.MARGE_VEHICULES + 40
        for ligne in self.lignes.values():
            vehicules = ligne["vehicules"]

            # vitesse du moment : celle de la voiture, ou celle de la voiture de devant
            # si elle est plus lente et trop proche (pas de dépassement ni de superposition)
            nouvelles = {}
            for v in vehicules:
                sens = 1 if v.vitesse_base > 0 else -1
                vitesse = v.vitesse_base
                for autre in vehicules:
                    if autre is v:
                        continue
                    ecart = ((autre.x_reel - v.x_reel) * sens) % boucle
                    if ecart < self.DISTANCE_SECURITE and abs(autre.vitesse) < abs(vitesse):
                        vitesse = autre.vitesse
                nouvelles[id(v)] = vitesse

            for v in vehicules:
                v.vitesse = nouvelles[id(v)]
                v.deplacer()

                # sortie par un côté (dans la forêt) -> réapparition de l'autre côté
                largeur = v.rectangle.width
                trajet = self.LARGEUR + 2 * self.MARGE_VEHICULES + largeur
                if v.x_reel > self.LARGEUR + self.MARGE_VEHICULES:
                    v.x_reel -= trajet
                elif v.x_reel < -self.MARGE_VEHICULES - largeur:
                    v.x_reel += trajet
                v.rectangle.x = round(v.x_reel)

    def peut_aller(self, dcol, dlig):
        """False si la case visée est hors zone ou occupée par un arbre / un rocher.
        L'eau n'est pas bloquée : on peut y sauter, et on s'y noie s'il n'y a pas de nénuphar."""
        t = self.TAILLE_LIGNE
        r = self.joueur.rectangle
        col = r.x // t + dcol
        indice = r.y // t + dlig
        if col < 0 or col >= self.NB_COLONNES:
            return False
        ligne = self.lignes.get(indice)
        if ligne is None:
            return True
        return ligne["decor"].get(col) not in ("arbre", "rocher")

    def joueur_dans_eau(self):
        """True si le joueur est sur une case d'eau sans nénuphar."""
        t = self.TAILLE_LIGNE
        r = self.joueur.rectangle
        ligne = self.lignes.get(r.y // t)
        if ligne is None or ligne["type"] != "eau":
            return False
        return ligne["decor"].get(r.x // t) != "nenuphar"

    def joueur_pose(self):
        """True quand le joueur a fini son saut (position affichée = position logique)."""
        j = self.joueur
        return abs(j.x_visuel - j.rectangle.x) < 1 and abs(j.y_visuel - j.rectangle.y) < 1

    def mettre_a_jour(self):
        joueur = self.joueur
        r = joueur.rectangle

        # le joueur reste dans la zone jouable
        r.x = max(0, min(r.x, self.LARGEUR - r.width))

        joueur.animer()

        # la caméra suit le joueur (position visuelle, donc suit aussi le saut)
        cible_x = joueur.x_visuel + r.width / 2
        cible_y = joueur.y_visuel + r.height / 2
        self.camera_x += (cible_x - self.camera_x) * 0.12
        self.camera_y += (cible_y - self.camera_y) * 0.12

        # génération des lignes autour de la caméra
        ligne_cam = int(self.camera_y // self.TAILLE_LIGNE)
        for indice in range(ligne_cam - 12, ligne_cam + 13):
            if indice not in self.lignes:
                self.lignes[indice] = self.generer_ligne(indice)

        self.lignes = {
            i: l for i, l in self.lignes.items()
            if ligne_cam - 17 <= i <= ligne_cam + 17
        }

        self.deplacer_vehicules()

    def hauteur_sol(self, indice):
        ligne = self.lignes.get(indice)
        if ligne is None:
            return 0
        return self.STYLES[ligne["type"]][1]

    # ------------------------------------------------------------------
    # Projection et primitives de dessin
    # ------------------------------------------------------------------
    def projeter(self, x, y, z=0):
        """Coordonnées de monde (x, y, z) -> coordonnées écran."""
        dx = x - self.camera_x
        dy = y - self.camera_y
        # rotation du monde autour de la verticale
        a = dx * self.COS_ROT - dy * self.SIN_ROT   # axe horizontal de l'écran
        b = dx * self.SIN_ROT + dy * self.COS_ROT   # profondeur (plus grand = plus proche)
        sx = self.centre_x + a * self.ZOOM
        sy = self.centre_y + b * self.SIN_ELEV * self.ZOOM - z * self.ZOOM
        return (sx, sy)

    def dessine_dalle(self, x, y, largeur, profondeur, z, couleur):
        """Rectangle plat posé à la hauteur z."""
        p = self.projeter
        points = [p(x, y, z), p(x + largeur, y, z),
                  p(x + largeur, y + profondeur, z), p(x, y + profondeur, z)]
        pygame.draw.polygon(self.ecran, couleur, points)

    def dessine_disque(self, cx, cy, rayon, z, couleur, n=14):
        """Disque plat (nénuphar) posé à la hauteur z."""
        points = [
            self.projeter(cx + rayon * math.cos(2 * math.pi * i / n),
                          cy + rayon * math.sin(2 * math.pi * i / n), z)
            for i in range(n)
        ]
        pygame.draw.polygon(self.ecran, couleur, points)

    def dessine_boite(self, x, y, largeur, profondeur, z, hauteur, couleur):
        """Pavé : dessus + les deux faces visibles (côté +y et côté +x)."""
        p = self.projeter
        x2, y2, z2 = x + largeur, y + profondeur, z + hauteur

        if hauteur > 0:
            face_y = [p(x, y2, z2), p(x2, y2, z2), p(x2, y2, z), p(x, y2, z)]
            face_x = [p(x2, y, z2), p(x2, y2, z2), p(x2, y2, z), p(x2, y, z)]
            pygame.draw.polygon(self.ecran, assombrir(couleur, 0.82), face_y)
            pygame.draw.polygon(self.ecran, assombrir(couleur, 0.62), face_x)

        dessus = [p(x, y, z2), p(x2, y, z2), p(x2, y2, z2), p(x, y2, z2)]
        pygame.draw.polygon(self.ecran, couleur, dessus)

    # ------------------------------------------------------------------
    # Dessin des lignes (sol + motifs + nénuphars)
    # ------------------------------------------------------------------
    def dessine_damier_herbe(self, ligne, col_debut, col_fin):
        t = self.TAILLE_LIGNE
        couleur, hauteur = self.STYLES["herbe"]
        clair = eclaircir(couleur, 18)
        y = ligne["rect"].y
        for col in range(col_debut, col_fin):
            if (col + ligne["indice"]) % 2 == 0:
                self.dessine_dalle(col * t, y, t, t, hauteur, clair)

    def dessine_ligne(self, ligne):
        t = self.TAILLE_LIGNE
        type_ligne = ligne["type"]
        indice = ligne["indice"]
        couleur, hauteur = self.STYLES[type_ligne]
        herbe_couleur, herbe_hauteur = self.STYLES["herbe"]
        y = ligne["rect"].y

        # colonnes visibles autour de la caméra
        col_min = max(-self.MARGE // t, int(self.camera_x // t) - 12)
        col_max = min((self.LARGEUR + self.MARGE) // t, int(self.camera_x // t) + 12)
        zone_min = max(col_min, 0)
        zone_max = min(col_max, self.NB_COLONNES)

        if type_ligne == "herbe":
            self.dessine_boite(-self.MARGE, y, self.LARGEUR + 2 * self.MARGE, t,
                               -self.EPAISSEUR, herbe_hauteur + self.EPAISSEUR, herbe_couleur)
            self.dessine_damier_herbe(ligne, col_min, col_max)
            return

        # forêt à gauche (plus loin), puis la ligne, puis forêt à droite (plus près)
        self.dessine_boite(-self.MARGE, y, self.MARGE, t,
                           -self.EPAISSEUR, herbe_hauteur + self.EPAISSEUR, herbe_couleur)
        self.dessine_boite(0, y, self.LARGEUR, t, -self.EPAISSEUR, hauteur + self.EPAISSEUR, couleur)
        self.dessine_boite(self.LARGEUR, y, self.MARGE, t,
                           -self.EPAISSEUR, herbe_hauteur + self.EPAISSEUR, herbe_couleur)
        self.dessine_damier_herbe(ligne, col_min, min(col_max, 0))
        self.dessine_damier_herbe(ligne, max(col_min, self.NB_COLONNES), col_max)

        if type_ligne == "route":
            for col in range(zone_min, zone_max):
                if col % 2 == 0:
                    self.dessine_dalle(col * t + 6, y + t / 2 - 2, 28, 4, hauteur, (230, 230, 220))

        elif type_ligne == "chemin_de_fer":
            for col in range(zone_min, zone_max):
                self.dessine_dalle(col * t + 14, y + 2, 12, t - 4, hauteur, (110, 80, 55))
            for decalage in (8, 27):
                self.dessine_boite(zone_min * t, y + decalage, (zone_max - zone_min) * t, 4,
                                   hauteur, 2, (170, 170, 180))

        elif type_ligne == "eau":
            clair = eclaircir(couleur, 40)
            for col in range(zone_min, zone_max):
                if (col + indice) % 3 == 0:
                    self.dessine_dalle(col * t + 6, y + 14, 28, 5, hauteur, clair)
            # nénuphars
            for col, genre in ligne["decor"].items():
                if genre == "nenuphar" and zone_min <= col < zone_max:
                    cx, cy = col * t + t / 2, y + t / 2
                    self.dessine_disque(cx, cy, 16, hauteur + 0.5, (60, 165, 90))
                    self.dessine_disque(cx, cy, 10, hauteur + 0.6, (90, 200, 115))

    # ------------------------------------------------------------------
    # Dessin des objets (triés par ligne puis par x)
    # ------------------------------------------------------------------
    def dessine_voiture(self, v, base):
        r = v.rectangle
        x, y, l, p = r.x, r.y + 6, r.width, r.height - 12
        self.dessine_dalle(x, y, l, p, base, assombrir(self.STYLES["route"][0], 0.6))
        self.dessine_boite(x, y, l, p, base + 2, 12, v.couleur)
        self.dessine_boite(x + 8, y + 3, l - 16, p - 6, base + 14, 9, (235, 240, 245))

    def dessine_train(self, t, base):
        r = t.rectangle
        x, y, l, p = r.x, r.y + 2, r.width, r.height - 4
        self.dessine_boite(x, y, l, p, base + 2, 30, t.couleur)
        self.dessine_boite(x + 4, y + 4, l - 8, p - 8, base + 32, 4, eclaircir(t.couleur, 50))

    def dessine_joueur(self, j):
        x = j.x_visuel + 8
        y = j.y_visuel + 8
        # ombre au sol (reste au sol pendant le saut)
        self.dessine_dalle(x, y, 24, 24, self.z_joueur, assombrir(self.STYLES["herbe"][0], 0.55))
        z = self.z_joueur + j.hauteur_saut
        self.dessine_boite(x, y, 24, 24, z, 24, self.BLANC)
        self.dessine_boite(x + 9, y + 8, 6, 8, z + 24, 7, self.CRETE)

    def dessine_arbre(self, x, y, base):
        ombre = assombrir(self.STYLES["herbe"][0], 0.7)
        self.dessine_dalle(x + 4, y + 4, 32, 32, base, ombre)
        self.dessine_boite(x + 15, y + 15, 10, 10, base, 14, (110, 75, 45))           # tronc
        self.dessine_boite(x + 6, y + 6, 28, 28, base + 14, 22, (60, 150, 70))        # feuillage
        self.dessine_boite(x + 11, y + 11, 18, 18, base + 36, 8, (85, 175, 90))       # cime

    def dessine_rocher(self, x, y, base):
        ombre = assombrir(self.STYLES["herbe"][0], 0.7)
        self.dessine_dalle(x + 5, y + 6, 30, 28, base, ombre)
        self.dessine_boite(x + 7, y + 9, 26, 22, base, 12, (135, 135, 145))
        self.dessine_boite(x + 13, y + 13, 14, 13, base + 12, 6, (165, 165, 175))

    def hors_zone(self, col):
        return col < 0 or col >= self.NB_COLONNES

    def dessine_objet(self, objet, indice):
        base = self.hauteur_sol(indice)
        y = indice * self.TAILLE_LIGNE
        if isinstance(objet, Player):
            self.dessine_joueur(objet)
        elif isinstance(objet, Train):
            self.dessine_train(objet, base)
        elif isinstance(objet, Decor):
            if self.hors_zone(objet.col):
                base = self.STYLES["herbe"][1]   # la forêt pousse sur de l'herbe
            if objet.genre == "arbre":
                self.dessine_arbre(objet.x, y, base)
            else:
                self.dessine_rocher(objet.x, y, base)
        else:
            self.dessine_voiture(objet, base)

    def cle_x(self, objet):
        if isinstance(objet, Player):
            return objet.x_visuel
        if isinstance(objet, Decor):
            # la forêt est dessinée par-dessus les véhicules qui y entrent
            if objet.col < 0:
                return -0.5 + objet.col * 0.001
            if objet.col >= self.NB_COLONNES:
                return 10000 + objet.col
            return objet.x
        return objet.rectangle.x

    # ------------------------------------------------------------------
    # Dessin complet : lignes de l'arrière vers l'avant (algorithme du peintre)
    # ------------------------------------------------------------------
    def dessiner(self):
        t = self.TAILLE_LIGNE
        self.ecran.fill(self.FOND)
        largeur_ecran = self.ecran.get_width()

        # objets rangés par ligne
        par_ligne = {}
        for vehicule in self.liste_vehicules:
            par_ligne.setdefault(vehicule.rectangle.centery // t, []).append(vehicule)

        indice_joueur = int((self.joueur.y_visuel + self.joueur.rectangle.height / 2) // t)
        par_ligne.setdefault(indice_joueur, []).append(self.joueur)

        # le joueur monte/descend en douceur d'une ligne à l'autre (et se pose sur un nénuphar)
        cible_z = self.hauteur_sol(indice_joueur)
        ligne_joueur = self.lignes.get(indice_joueur)
        col_joueur = int((self.joueur.x_visuel + self.joueur.rectangle.width / 2) // t)
        if ligne_joueur and ligne_joueur["decor"].get(col_joueur) == "nenuphar":
            cible_z += 1
        self.z_joueur += (cible_z - self.z_joueur) * 0.35

        ligne_cam = int(self.camera_y // t)
        for indice in range(ligne_cam - 11, ligne_cam + 12):
            ligne = self.lignes.get(indice)
            if ligne is None:
                continue
            self.dessine_ligne(ligne)

            objets = par_ligne.get(indice, [])
            for col, genre in ligne["decor"].items():
                if genre == "nenuphar":
                    continue
                sx, _ = self.projeter(col * t + t / 2, indice * t + t / 2)
                if -90 <= sx <= largeur_ecran + 90:      # on ne dessine que les arbres visibles
                    objets.append(Decor(genre, col, t))

            objets.sort(key=self.cle_x)  # x plus grand = plus proche, dessiné en dernier
            for objet in objets:
                self.dessine_objet(objet, indice)