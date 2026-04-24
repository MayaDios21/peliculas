from django.urls import path
from .views import *


urlpatterns = [
    path('all/', all_movies),
    path('search/', search_movies, name='search_movies'),
    path('actor/<int:person_id>/', person_detail, name='person_detail'),
    path('random', random_movies, name='random_movies'),
    path('<int:movie_id>/', movie, name='movie'),
    path('movie_review/add/<int:movie_id>/', add_review),
    path('movie_reviews/<int:movie_id>/', movie_reviews, name='movie_reviews'),
    path('review/edit/<int:review_id>/', edit_review, name='edit_review'),
    path('review/delete/<int:review_id>/', delete_review, name='delete_review'),
    path('user/<int:user_id>/reviews/', user_reviews, name='user_reviews'),
    path('user/<int:user_id>/favorites/', user_favorites, name='user_favorites'),
    path('my-favorites/', my_favorites, name='my_favorites'),
    path('favorite/add/<int:movie_id>/', add_favorite, name='add_favorite'),
    path('favorite/remove/<int:movie_id>/', remove_favorite, name='remove_favorite'),
    path('favorite/count/', favorite_count, name='favorite_count'),
    path('', index)
]
