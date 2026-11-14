import math
import pygame


class Player:
    def __init__(self, vitesse, rectangle):
        self.vitesse = vitesse
        self.rectangle = rectangle  # position logique (collisions)

        # position affichée (animation de saut entre deux cases)
        self.x_visuel = float(rectangle.x)
        self.y_visuel = float(rectangle.y)
        self.hauteur_saut = 0.0
        self.dernier_deplacement = 0
        self.cooldown = 170

    def peut_bouger(self):
        return pygame.time.get_ticks() - self.dernier_deplacement >= self.cooldown

    def sauter_vers(self, x, y):
        """Place le joueur sur la case (x, y) si le cooldown est écoulé.
        Utilisé par Monde.deplacer_joueur (qui gère obstacles, grille et rondins)."""
        if not self.peut_bouger():
            return False
        self.rectangle.x = x
        self.rectangle.y = y
        self.dernier_deplacement = pygame.time.get_ticks()
        return True

    def deplacer_haut(self):

        temps_actuel = pygame.time.get_ticks()

        if temps_actuel - self.dernier_deplacement >= self.cooldown:

            self.rectangle.y -= self.vitesse

            self.dernier_deplacement = temps_actuel

    def deplacer_bas(self):
        temps_actuel = pygame.time.get_ticks()
        
        if temps_actuel - self.dernier_deplacement >= self.cooldown:
            self.rectangle.y += self.vitesse
            self.dernier_deplacement = temps_actuel

    def deplacer_droite(self):
        temps_actuel = pygame.time.get_ticks()
        
        if temps_actuel - self.dernier_deplacement >= self.cooldown:
            self.rectangle.x += self.vitesse
            self.dernier_deplacement = temps_actuel

    def deplacer_gauche(self):
        temps_actuel = pygame.time.get_ticks()

        if temps_actuel - self.dernier_deplacement >= self.cooldown:
            self.rectangle.x -= self.vitesse
            self.dernier_deplacement = temps_actuel

    def animer(self):
        """Rapproche la position affichée de la position logique, avec un petit saut."""
        dx = self.rectangle.x - self.x_visuel
        dy = self.rectangle.y - self.y_visuel
        distance = math.hypot(dx, dy)

        # seuil un peu tolérant : évite les petits rebonds quand un rondin porte le joueur
        if distance < 1.5:
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

    