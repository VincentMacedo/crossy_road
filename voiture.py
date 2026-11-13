class Voiture:
    def __init__(self, vitesse, rectangle, couleur=(220, 60, 60)):
        self.vitesse_base = vitesse     # vitesse voulue (propre à cette voiture)
        self.vitesse = vitesse          # vitesse actuelle (réduite si elle suit une voiture plus lente)
        self.rectangle = rectangle
        self.couleur = couleur
        self.x_reel = float(rectangle.x)   # position précise (les vitesses ne sont pas entières)

    def deplacer(self):
        self.x_reel += self.vitesse
        self.rectangle.x = round(self.x_reel)