import random
import pygame
from monde import Monde


mode_de_jeu = int(input("Entre 1 pour jouer 2 pour faire jouer l'IA : "))
pygame.init()
graine = random.randint(0, 10000)  # graine de génération du monde
cooldown = 100  # temps de rafraichissement du calcul du bot
dernier_deplacement = 0

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


monde = Monde(ecran, graine)
score = 0
game_over = False
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
            elif mode_de_jeu == 1:
                # touches (les arbres et les rochers bloquent le joueur)
                if event.key == pygame.K_z:
                    monde.deplacer_joueur(0, -1)
                if event.key == pygame.K_s:
                    monde.deplacer_joueur(0, 1)
                if event.key == pygame.K_d:
                    monde.deplacer_joueur(1, 0)
                if event.key == pygame.K_q:
                    monde.deplacer_joueur(-1, 0)

    # actions du bot
    if mode_de_jeu == 2 and not game_over:
        temps_actuel = pygame.time.get_ticks()
        if temps_actuel - dernier_deplacement >= cooldown:

            col, ligne = monde.case_visee(0, 0)
            liste_liste_chemin = monde.analyse(10, ligne, col)     # x = ligne, y = colonne
            best = monde.meilleur_chemin(liste_liste_chemin)

            if best is not None:                    # sinon : aucun chemin, le bot attend
                premier = best[1][1]                # première action du chemin
                dligne = premier[0] - ligne         # -1 = devant, +1 = derrière
                dcol = premier[1] - col             # -1 = gauche, +1 = droite
                monde.deplacer_joueur(dcol, dligne)
                dernier_deplacement = temps_actuel
            

            

    if not game_over:
        monde.mettre_a_jour()

        score = max(score, (400 - monde.joueur.rectangle.y) // monde.TAILLE_LIGNE)

        if monde.joueur.contact(monde.liste_vehicules):
            game_over = True
            cause = "Écrasé !"
        elif monde.emporte:
            game_over = True
            cause = "Emporté par le courant !"
        elif monde.joueur_pose() and monde.joueur_dans_eau():
            game_over = True
            cause = "Tu t'es noyé !"

    
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