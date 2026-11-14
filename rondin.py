class Rondin:
    """Tronc flottant qui suit le courant d'une ligne d'eau."""

    def __init__(self, vitesse, rectangle):
        self.vitesse = vitesse
        self.rectangle = rectangle
        self.x_reel = float(rectangle.x)   # position précise (vitesses non entières)

    def deplacer(self):
        self.x_reel += self.vitesse
        self.rectangle.x = round(self.x_reel)