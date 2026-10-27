import pygame
from player import Player
from voiture import Voiture
from train import Train
import random



class Monde:
    noir = (0, 0, 0)
    rouge = (255, 0, 0)
    vert = (0, 255, 0)

    avatar = pygame.Rect(200, 400, 40, 40)
    carrosserie1 = pygame.Rect(0, 240, 40, 40)
    carrosserie2 = pygame.Rect(0, 120, 40, 40)
    wagon = pygame.Rect(0, 60, 200, 40)

    joueur = Player(40,avatar)
    voiture1  = Voiture(1, carrosserie1)
    voiture2  = Voiture(2, carrosserie2)
    train1 = Train(4, wagon)
    liste_vehicules=[voiture1,voiture2,train1]

    liste_arbres=[]
    for i in range (0,10):
        rng=random.randint(0,4)
        if rng==2:
            liste_arbres.append(pygame.Rect(0,i*40,40,40))

    def __init__(self,ecran,graine):
        self.ecran=ecran
        self.graine=graine

    def dessine_objet(self,couleur,objet):
        pygame.draw.rect(self.ecran, couleur, objet.rectangle)

    def dessine_decor(self,couleur,objet):
        pygame.draw.rect(self.ecran, couleur , objet)