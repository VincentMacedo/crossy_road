import pygame
from monde import Monde

pygame.init()

# Fenêtre
largeur, hauteur = 800, 600
ecran = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("Carré rouge")

#monde
World = Monde(ecran, 67123)
liste_sol = World.generer_sol()   

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
            
    ecran.fill(World.noir)
    
    World.mettre_a_jour(World.joueur)

    ecran.fill(World.noir)

    for ligne in World.lignes.values():
        World.dessine_decor(ligne)
    

    World.voiture1.rectangle.x+=World.voiture1.vitesse
    if World.voiture1.rectangle.x>600:
        World.voiture1.rectangle.x=0

    World.voiture2.rectangle.x+=World.voiture2.vitesse
    if World.voiture2.rectangle.x>600:
        World.voiture2.rectangle.x=0

    if World.joueur.contact(World.liste_vehicules) == True:
        print("contact!!!")

    World.train1.deplacer()

    
    for vehicule in World.liste_vehicules:
        World.dessine_objet(World.rouge, vehicule)

    World.dessine_objet(World.rouge, World.joueur)

    
    World.dessine_objet(World.rouge, World.joueur)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()