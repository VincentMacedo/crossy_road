class Train:
    def __init__(self,vitesse,rectangle):
        self.vitesse=vitesse
        self.rectangle=rectangle

    def deplacer(self):
        self.rectangle.x+=self.vitesse
        