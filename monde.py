import random
import pygame
from player import Player
from voiture import Voiture
from train import Train


def assombrir(couleur, facteur):
    return tuple(int(c * facteur) for c in couleur)


def eclaircir(couleur, ajout):
    return tuple(min(255, c + ajout) for c in couleur)


class Monde:
    # --- Monde (en "pixels de monde", comme avant) ---
    TAILLE_LIGNE = 40
    LARGEUR = 800          # zone jouable : x de 0 à LARGEUR
    MARGE = 400            # les lignes dépassent de chaque côté (véhicules hors zone)

    # --- Projection isométrique ---
    ZOOM = 1.5
    COS = 0.866 * ZOOM
    SIN = 0.5 * ZOOM

    # --- Couleurs ---
    FOND = (30, 30, 40)
    BLANC = (245, 245, 245)
    CRETE = (220, 40, 40)
    OMBRE = (0, 0, 0)

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
        self.centre_y = int(hauteur_ecran * 0.6)

        # joueur et véhicules
        self.joueur = Player(40, pygame.Rect(200, 400, 40, 40))
        self.voiture1 = Voiture(1, pygame.Rect(0, 240, 40, 40), (230, 70, 60))
        self.voiture2 = Voiture(2, pygame.Rect(0, 120, 40, 40), (240, 190, 50))
        self.train1 = Train(4, pygame.Rect(0, 80, 200, 40))
        self.liste_vehicules = [self.voiture1, self.voiture2, self.train1]

        # caméra centrée sur le joueur (en coordonnées de monde)
        self.camera_x = self.joueur.rectangle.centerx
        self.camera_y = self.joueur.rectangle.centery
        self.z_joueur = self.STYLES["herbe"][1]

    # ------------------------------------------------------------------
    # Génération / mise à jour
    # ------------------------------------------------------------------
    def generer_ligne(self, indice):
        if indice > 5:
            type_ligne = "herbe"
        else:
            rng = random.Random(f"{self.graine}:{indice}")
            types = ["herbe", "route", "eau", "chemin_de_fer"]
            poids = [4, 3, 2, 1]
            type_ligne = rng.choices(types, weights=poids)[0]

        rect = pygame.Rect(0, indice * self.TAILLE_LIGNE, self.LARGEUR, self.TAILLE_LIGNE)
        return {"type": type_ligne, "rect": rect, "indice": indice}

    def deplacer_vehicules(self):
        for vehicule in self.liste_vehicules:
            vehicule.deplacer()
            if vehicule.rectangle.left > self.LARGEUR + self.MARGE:
                vehicule.rectangle.right = -self.MARGE

    def mettre_a_jour(self):
        joueur = self.joueur
        r = joueur.rectangle

        # le joueur reste dans la zone jouable
        r.x = max(0, min(r.x, self.LARGEUR - r.width))

        joueur.animer()
        self.deplacer_vehicules()

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
        sx = self.centre_x + (dx - dy) * self.COS
        sy = self.centre_y + (dx + dy) * self.SIN - z * self.ZOOM
        return (sx, sy)

    def dessine_dalle(self, x, y, largeur, profondeur, z, couleur):
        """Rectangle plat posé à la hauteur z."""
        p = self.projeter
        points = [p(x, y, z), p(x + largeur, y, z),
                  p(x + largeur, y + profondeur, z), p(x, y + profondeur, z)]
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
    # Dessin des lignes (décor)
    # ------------------------------------------------------------------
    def dessine_ligne(self, ligne):
        t = self.TAILLE_LIGNE
        type_ligne = ligne["type"]
        indice = ligne["indice"]
        couleur, hauteur = self.STYLES[type_ligne]
        y = ligne["rect"].y

        x_min = -self.MARGE
        longueur = self.LARGEUR + 2 * self.MARGE

        # bloc de la ligne
        self.dessine_boite(x_min, y, longueur, t, -self.EPAISSEUR,
                           hauteur + self.EPAISSEUR, couleur)

        # motifs, seulement autour de la caméra
        col_min = max(x_min // t, int(self.camera_x // t) - 12)
        col_max = min((self.LARGEUR + self.MARGE) // t, int(self.camera_x // t) + 12)

        if type_ligne == "herbe":
            clair = eclaircir(couleur, 18)
            for col in range(col_min, col_max):
                if (col + indice) % 2 == 0:
                    self.dessine_dalle(col * t, y, t, t, hauteur, clair)

        elif type_ligne == "route":
            for col in range(col_min, col_max):
                if col % 2 == 0:
                    self.dessine_dalle(col * t + 6, y + t / 2 - 2, 28, 4, hauteur, (230, 230, 220))

        elif type_ligne == "chemin_de_fer":
            for col in range(col_min, col_max):
                self.dessine_dalle(col * t + 14, y + 2, 12, t - 4, hauteur, (110, 80, 55))
            debut = col_min * t
            for decalage in (8, 27):
                self.dessine_boite(debut, y + decalage, (col_max - col_min) * t, 4,
                                   hauteur, 2, (170, 170, 180))

        elif type_ligne == "eau":
            clair = eclaircir(couleur, 40)
            for col in range(col_min, col_max):
                if (col + indice) % 3 == 0:
                    self.dessine_dalle(col * t + 6, y + 14, 28, 5, hauteur, clair)

    # ------------------------------------------------------------------
    # Dessin des objets
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

    def dessine_objet(self, objet, indice):
        base = self.hauteur_sol(indice)
        if isinstance(objet, Player):
            self.dessine_joueur(objet)
        elif isinstance(objet, Train):
            self.dessine_train(objet, base)
        else:
            self.dessine_voiture(objet, base)

    @staticmethod
    def cle_x(objet):
        if isinstance(objet, Player):
            return objet.x_visuel
        return objet.rectangle.x

    # ------------------------------------------------------------------
    # Dessin complet : lignes de l'arrière vers l'avant (algorithme du peintre)
    # ------------------------------------------------------------------
    def dessiner(self):
        t = self.TAILLE_LIGNE
        self.ecran.fill(self.FOND)

        # objets rangés par ligne
        par_ligne = {}
        for vehicule in self.liste_vehicules:
            par_ligne.setdefault(vehicule.rectangle.centery // t, []).append(vehicule)

        indice_joueur = int((self.joueur.y_visuel + self.joueur.rectangle.height / 2) // t)
        par_ligne.setdefault(indice_joueur, []).append(self.joueur)

        # le joueur monte/descend en douceur d'une ligne à l'autre
        cible_z = self.hauteur_sol(indice_joueur)
        self.z_joueur += (cible_z - self.z_joueur) * 0.35

        ligne_cam = int(self.camera_y // t)
        for indice in range(ligne_cam - 11, ligne_cam + 12):
            ligne = self.lignes.get(indice)
            if ligne is None:
                continue
            self.dessine_ligne(ligne)

            objets = par_ligne.get(indice, [])
            objets.sort(key=self.cle_x)  # x plus grand = plus proche, dessiné en dernier
            for objet in objets:
                self.dessine_objet(objet, indice)