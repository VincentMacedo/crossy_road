import math
import pygame
from monde import Monde

class Bot:
    def __init__(self, vitesse, rectangle):
        self.vitesse = vitesse
        self.rectangle = rectangle  # position logique (collisions)

        # position affichée (animation de saut entre deux cases)
        self.x_visuel = float(rectangle.x)
        self.y_visuel = float(rectangle.y)
        self.hauteur_saut = 0.0

    def deplacer_haut(self):
        self.rectangle.y -= self.vitesse

    def deplacer_bas(self):
        self.rectangle.y += self.vitesse

    def deplacer_droite(self):
        self.rectangle.x += self.vitesse

    def deplacer_gauche(self):
        self.rectangle.x -= self.vitesse

    def animer(self):
        """Rapproche la position affichée de la position logique, avec un petit saut."""
        dx = self.rectangle.x - self.x_visuel
        dy = self.rectangle.y - self.y_visuel
        distance = math.hypot(dx, dy)

        if distance < 0.5:
            self.x_visuel = float(self.rectangle.x)
            self.y_visuel = float(self.rectangle.y)
            self.hauteur_saut = 0.0
            return

        self.x_visuel += dx * 0.35
        self.y_visuel += dy * 0.35
        self.hauteur_saut = 22 * math.sin(math.pi * min(distance, self.vitesse) / self.vitesse)

    def rect_dans_rect(self, obstacle):
        return self.rectangle.colliderect(obstacle)

    def contact(self, vehicules):
        # zones légèrement réduites pour que le contact soit juste visuellement
        zone = self.rectangle.inflate(-12, -12)
        for vehicule in vehicules:
            if zone.colliderect(vehicule.rectangle.inflate(-8, -12)):
                return True  # Il y a contact

        return False  # Aucun contact

    def analyse(self):
        return False