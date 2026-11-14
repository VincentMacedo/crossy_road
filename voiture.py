class Voiture:
    """Véhicule d'une route : petite voiture, voiture ou camion (selon `genre`)."""

    def __init__(self, vitesse, rectangle, couleur=(220, 60, 60), genre="voiture",
                 couleur_remorque=(235, 235, 240)):
        self.vitesse_base = vitesse     # vitesse voulue (propre à ce véhicule)
        self.vitesse = vitesse          # vitesse actuelle (réduite s'il suit un véhicule plus lent)
        self.rectangle = rectangle      # la largeur du rectangle dépend du genre
        self.couleur = couleur
        self.genre = genre              # "petite", "voiture" ou "camion"
        self.couleur_remorque = couleur_remorque
        self.x_reel = float(rectangle.x)   # position précise (les vitesses ne sont pas entières)

    def deplacer(self):
        self.x_reel += self.vitesse
        self.rectangle.x = round(self.x_reel)