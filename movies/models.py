from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone

# Create your models here.


class Genre(models.Model):
    name = models.CharField(max_length=80)
    
    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=80)
    
    def __str__(self):
        return self.name


class Studio(models.Model):
    name = models.CharField(max_length=128)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.name

    
class Person(models.Model):
    name = models.CharField(max_length=128)
    birth_date = models.DateField(blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    poster_path = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.name


class Job(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=80)
    overview = models.TextField()
    release_date = models.DateField()
    running_time = models.IntegerField()
    budget = models.IntegerField(blank=True, null=True)
    tmdb_id = models.IntegerField(blank=True, null=True)
    revenue = models.IntegerField(blank=True, null=True)
    poster_path = models.URLField(blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    studio = models.ForeignKey(Studio, on_delete=models.SET_NULL, null=True, blank=True)
    genres = models.ManyToManyField(Genre)
    credits = models.ManyToManyField(Person, through='MovieCredit')

    def __str__(self):
        return f'{self.title} {self.release_date}'


class MovieCredit(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)


class MovieReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(blank=True)
    title = models.CharField(max_length=200, blank=False, null=False, default="Reseña")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_creacion']
        unique_together = ['user', 'movie']

    def __str__(self):
        return f'{self.movie.title} - {self.user.username} ({self.rating}/5)'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favorited_by')
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'movie']
        ordering = ['-fecha_agregado']

    def __str__(self):
        return f'{self.user.username} - {self.movie.title}'


