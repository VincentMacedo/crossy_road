import pygame
from player import Player
from voiture import Voiture
from train import Train
import random



class Monde:
    POSITION_JOUEUR_ECRAN = 400 
    noir = (0, 0, 0)
    rouge = (255, 0, 0)
    vert = (0, 255, 0)
    NB_LIGNES = 15
    TAILLE_LIGNE = 40
    LARGEUR = 800
    textures = {
        "route": pygame.transform.scale(
            pygame.image.load("textures/route.jpg"), (40, 40)
        ),
        "chemin_de_fer": pygame.transform.scale(
            pygame.image.load("textures/rail.jpg"), (40, 40)
        ),
        "herbe": pygame.transform.scale(
            pygame.image.load("textures/herbe.jpg"), (40, 40)
        ),
        "eau": pygame.transform.scale(
            pygame.image.load("textures/eau.jpg"), (40, 40)
        )
    }
    avatar = pygame.Rect(200, 400, 40, 40)
    carrosserie1 = pygame.Rect(0, 240, 40, 40)
    carrosserie2 = pygame.Rect(0, 120, 40, 40)
    wagon = pygame.Rect(0, 60, 200, 40)

    joueur = Player(40,avatar)
    voiture1  = Voiture(1, carrosserie1)
    voiture2  = Voiture(2, carrosserie2)
    train1 = Train(4, wagon)
    liste_vehicules=[voiture1,voiture2,train1]
        
        

    def __init__(self,ecran,graine):
        self.ecran = ecran
        self.graine = graine
        self.camera_y = 0
        self.lignes = {}


    def generer_ligne(self, indice):
        if indice > 5:
            type_ligne = "herbe"  
        else:
            rng = random.Random(f"{self.graine}:{indice}")   
            types = ["herbe", "route", "eau", "chemin_de_fer"]
            poids = [4, 3, 2, 1]
            type_ligne = rng.choices(types, weights=poids)[0]

        rect = pygame.Rect(0, indice * self.TAILLE_LIGNE, self.LARGEUR, self.TAILLE_LIGNE)
        return {"type": type_ligne, "rect": rect}



    def mettre_a_jour(self, joueur):
        cible = joueur.rectangle.y - self.POSITION_JOUEUR_ECRAN
        self.camera_y += (cible - self.camera_y) * 0.15

        haut = int(self.camera_y // self.TAILLE_LIGNE) - 2
        bas = int((self.camera_y + self.ecran.get_height()) // self.TAILLE_LIGNE) + 2

        for indice in range(haut, bas + 1):
            if indice not in self.lignes:
                self.lignes[indice] = self.generer_ligne(indice)

        self.lignes = {i: l for i, l in self.lignes.items() if haut - 5 <= i <= bas + 5}

    
    def generer_sol(self):
        liste_sol = []

        for i in range(self.NB_LIGNES):
            type_ligne = random.choice(list(self.textures.keys()))

            rect = pygame.Rect(
                0,
                i * self.TAILLE_LIGNE,
                self.LARGEUR,
                self.TAILLE_LIGNE
            )

            liste_sol.append({
                "type": type_ligne,
                "rect": rect
            })

        return liste_sol
    

    def dessine_objet(self, couleur, objet):
        rect = objet.rectangle.move(0, -round(self.camera_y))
        pygame.draw.rect(self.ecran, couleur, rect)

    def dessine_decor(self, ligne):
        texture = self.textures[ligne["type"]]
        y = ligne["rect"].y - round(self.camera_y)
        for x in range(0, self.LARGEUR, self.TAILLE_LIGNE):
            self.ecran.blit(texture, (x, y))