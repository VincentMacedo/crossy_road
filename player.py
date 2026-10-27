import pygame

class Player:
    def __init__(self, vitesse, rectangle):
        self.vitesse = vitesse
        self.rectangle = rectangle  # Rectangle du joueur

    def deplacer_haut(self):
        self.rectangle.y -= self.vitesse

    def deplacer_bas(self):
        self.rectangle.y += self.vitesse

    def deplacer_droite(self):
        self.rectangle.x += self.vitesse

    def deplacer_gauche(self):
        self.rectangle.x -= self.vitesse

    def rect_dans_rect(self, obstacle):
        return self.rectangle.colliderect(obstacle)

    def contact(self, vehicules):
        for vehicule in vehicules:
            if self.rect_dans_rect(vehicule.rectangle):
                return True  # Il y a contact

        return False  # Aucun contact
