from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class UserProfile(models.Model):
    """Stores all the general account information."""
    user = models.OneToOneField(User)                   # Käyttäjä, jonka profiili tämä on
    isDeveloper = models.BooleanField(default=False)    # Onko käyttäjä gamer vai developer
    picture = models.URLField(null=True, blank=True)    # Profiilikuva
    regDate = models.DateField(auto_now=False, auto_now_add=True)  # käyttäjän rekisteröinti
    fbReg = models.BooleanField(default=False)          # Onko käyttäjä rekisteröitynyt Facebookin kautta vai normaalisti

    def __str__(self):
        return self.user.username


class GameGenre(models.Model):
    """Stores the available game genres. The superuser should create these beforehand."""
    genre = models.CharField(null=False, blank=False, max_length=255, unique=True)  # Genren nimi
    desc = models.TextField(null=False, blank=False, unique=True)  # Genren kuvaus

    def __str__(self):
        return self.genre


class StoreGame(models.Model):
    """Represents a game available in the store."""
    # Tämä Model on peliobjekti verkkokaupassa

    title = models.CharField(null=False, blank=False, max_length=255, unique=True)  # Pelin nimi
    desc = models.TextField(null=False, blank=False)                        # Pelin kuvaus
    author = models.ForeignKey(User)                                        # Tekijän nimi
    relDate = models.DateField(auto_now=False, auto_now_add=True)           # Julkaisuaika
    lastUpdate = models.DateField(auto_now=True, auto_now_add=True)         # Milloin päivitetty
    price = models.DecimalField(null=False, blank=False, max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])  # hinta
    genre = models.ForeignKey(GameGenre, related_name="games_by_genre")     # Pelin genre hakua varten
    avgRate = models.DecimalField(null=True, max_digits=2, decimal_places=1)
    url = models.URLField(null=False, blank=False, unique=True)             # Pelin osoite
    imageUrl = models.URLField(null=True, blank=True)                       # Pelin kansikuva

    def __str__(self):
        return self.title


class UserGame(models.Model):
    """Information about which users own which games."""
    game = models.ForeignKey(StoreGame, related_name="+")           # Verkkokaupan peli
    owner = models.ForeignKey(User, related_name="owned_games")    # Pelin ostaja
    purDate = models.DateField(auto_now=False, auto_now_add=True)   # Ostopäivä
    lastPlayed = models.DateField(blank=True, null=True, auto_now=False, auto_now_add=False)  # Viimeksi pelattu
    rating = models.PositiveSmallIntegerField(null=True)            # Annettu arvosana

    def __str__(self):
        return self.game.title + ", Rating: " + str(self.rating)

    class Meta:
        get_latest_by = "purDate"


class GameScore(models.Model):
    """All the game scores for every game are stored here. This model is used
    to populate the user highscores and global highscores. This will get big
    soon, in a real application we  should probably limit the history to 5
    games per user...
    """
    game = models.ForeignKey(StoreGame, related_name="high_scores")         # peli johon score liittyy
    player = models.ForeignKey(User, related_name="user_scores")            # pelaaja
    score = models.PositiveIntegerField()                                   # pisteet
    date = models.DateField(auto_now=False, auto_now_add=True, null=True)   # käyttäjän rekisteröinti

    def __str__(self):
        return self.game.title + ", " + str(self.score)

    class Meta:
        ordering = ['score']


class GameSave(models.Model):
    """Stores the game save data. Can only have one save file per game."""
    game = models.ForeignKey(StoreGame)
    user = models.ForeignKey(User)
    saveData = models.TextField(null=True, blank=True)
    saveDate = models.DateTimeField(auto_now=True, auto_now_add=True)

    class Meta:
        unique_together = ("game", "user")  # Game and user form a unique key
