class Train:
    def __init__(self, vitesse, rectangle, couleur=(90, 110, 200)):
        self.vitesse_base = vitesse
        self.vitesse = vitesse
        self.rectangle = rectangle
        self.couleur = couleur
        self.x_reel = float(rectangle.x)

    def deplacer(self):
        self.x_reel += self.vitesse
        self.rectangle.x = round(self.x_reel)