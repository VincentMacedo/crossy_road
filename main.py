import pygame
from monde import Monde

pygame.init()

# Fenêtre
largeur, hauteur = 800, 600
ecran = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("Carré rouge")

#monde
World = Monde(ecran, 67123)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        #touches
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                World.joueur.deplacer_haut()
            if event.key == pygame.K_s:
                World.joueur.deplacer_bas()
            if event.key == pygame.K_d:
                World.joueur.deplacer_droite()
            if event.key == pygame.K_q:
                World.joueur.deplacer_gauche()
            

    World.voiture1.rectangle.x+=World.voiture1.vitesse
    if World.voiture1.rectangle.x>600:
        World.voiture1.rectangle.x=0

    World.voiture2.rectangle.x+=World.voiture2.vitesse
    if World.voiture2.rectangle.x>600:
        World.voiture2.rectangle.x=0

    if World.joueur.contact(World.liste_vehicules) == True:
        print("contact!!!")

    World.train1.deplacer()

    ecran.fill(World.noir)
    for i in range (len(World.liste_vehicules)):
        World.dessine_objet(World.rouge,World.liste_vehicules[i])

    for i  in range (len(World.liste_arbres)):
        World.dessine_decor(World.vert,World.liste_arbres[i])
    
    World.dessine_objet(World.rouge, World.joueur)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()