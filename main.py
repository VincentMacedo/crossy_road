import random
import pygame
from monde import Monde

pygame.init()

# Fenêtre
largeur, hauteur = 800, 600
ecran = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("Crossy Road")

police_titre = pygame.font.SysFont(None, 110)
police_texte = pygame.font.SysFont(None, 40)

# voile sombre affiché par-dessus le jeu quand on perd
voile = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
voile.fill((0, 0, 0, 160))


def afficher_texte(texte, police, couleur, y):
    image = police.render(texte, True, couleur)
    ecran.blit(image, image.get_rect(center=(largeur // 2, y)))


monde = Monde(ecran, 67123)
score = 0
game_over = False
noyade = False          # le joueur a sauté dans l'eau : il se noie dès qu'il atterrit
cause = ""

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_over:
                # rejouer
                if event.key in (pygame.K_r, pygame.K_SPACE, pygame.K_RETURN):
                    monde = Monde(ecran, random.randint(0, 10**6))
                    score = 0
                    game_over = False
                    noyade = False
            elif not noyade:
                # touches (les arbres et les rochers bloquent le joueur)
                if event.key == pygame.K_z and monde.peut_aller(0, -1):
                    monde.joueur.deplacer_haut()
                if event.key == pygame.K_s and monde.peut_aller(0, 1):
                    monde.joueur.deplacer_bas()
                if event.key == pygame.K_d and monde.peut_aller(1, 0):
                    monde.joueur.deplacer_droite()
                if event.key == pygame.K_q and monde.peut_aller(-1, 0):
                    monde.joueur.deplacer_gauche()

                # saut dans l'eau sans nénuphar : plus de commandes, noyade à l'atterrissage
                if monde.joueur_dans_eau():
                    noyade = True

    if not game_over:
        # logique : caméra, génération des lignes, véhicules, animation du joueur
        monde.mettre_a_jour()

        # score = nombre de lignes gagnées depuis le départ
        score = max(score, (400 - monde.joueur.rectangle.y) // monde.TAILLE_LIGNE)

        if monde.joueur.contact(monde.liste_vehicules):
            game_over = True
            cause = "Écrasé !"
        elif noyade and monde.joueur_pose():
            game_over = True
            cause = "Tu t'es noyé !"

    # rendu
    monde.dessiner()

    if game_over:
        ecran.blit(voile, (0, 0))
        afficher_texte("GAME OVER", police_titre, (230, 70, 60), hauteur // 2 - 70)
        afficher_texte(cause, police_texte, (255, 255, 255), hauteur // 2 - 5)
        afficher_texte(f"Score : {score}", police_texte, (255, 255, 255), hauteur // 2 + 40)
        afficher_texte("Appuyez sur R pour rejouer", police_texte, (220, 220, 220), hauteur // 2 + 90)
    else:
        image = police_texte.render(str(score), True, (255, 255, 255))
        ecran.blit(image, (20, 15))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()