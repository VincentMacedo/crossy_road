import pygame
from monde import Monde

pygame.init()

# Fenêtre
largeur, hauteur = 800, 600
ecran = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("Crossy Road")

# Monde
monde = Monde(ecran, 67123)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # touches
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                monde.joueur.deplacer_haut()
            if event.key == pygame.K_s:
                monde.joueur.deplacer_bas()
            if event.key == pygame.K_d:
                monde.joueur.deplacer_droite()
            if event.key == pygame.K_q:
                monde.joueur.deplacer_gauche()

    # logique : caméra, génération des lignes, véhicules, animation du joueur
    monde.mettre_a_jour()

    if monde.joueur.contact(monde.liste_vehicules):
        print("contact!!!")

    # rendu isométrique
    monde.dessiner()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()