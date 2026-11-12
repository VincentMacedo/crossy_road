class Voiture:
    def __init__(self, vitesse, rectangle, couleur=(220, 60, 60)):
        self.vitesse = vitesse
        self.rectangle = rectangle
        self.couleur = couleur

    def deplacer(self):
        self.rectangle.x += self.vitesse