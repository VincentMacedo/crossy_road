class Train:
    def __init__(self, vitesse, rectangle, couleur=(90, 110, 200)):
        self.vitesse = vitesse
        self.rectangle = rectangle
        self.couleur = couleur

    def deplacer(self):
        self.rectangle.x += self.vitesse