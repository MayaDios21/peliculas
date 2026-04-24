from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from movies.models import Movie, MovieReview, Favorite
from movies.forms import MovieReviewForm

def all_movies(request):
    movies = Movie.objects.all() #Movies de la BD
    context = { 'objetos':movies, 'message':'welcom' }
    return render(request,'movies/allmovies.html', context=context )

# Create your views here.
def index(request):
    # Mostrar solo las primeras 4 películas al cargar
    movies = Movie.objects.all()[:4]
    
    # Películas recomendadas: ordenadas por cantidad de reviews y rating promedio
    from django.db.models import Avg, Count
    recommended_movies = Movie.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).filter(review_count__gt=0).order_by('-avg_rating', '-review_count')[:6]
    
    # Si no hay películas con reseñas, mostrar las más recientes
    if not recommended_movies.exists():
        recommended_movies = Movie.objects.order_by('-release_date')[:6]
    
    context = { 
        'movies': movies,
        'recommended_movies': recommended_movies,
        'message': 'welcome' 
    }
    return render(request, 'movies/index.html', context=context)
    
def movie(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    review_form = MovieReviewForm()
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, movie=movie).exists()
    context = { 
        'movie': movie, 
        'saludo': 'welcome', 
        'review_form': review_form,
        'is_favorite': is_favorite 
    }
    return render(request, 'movies/movie.html', context=context)

def movie_reviews(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    return render(request, 'movies/reviews.html', context={'movie': movie})
    
@login_required(login_url='admin:login')
def add_review(request, movie_id):
    form = None
    movie = Movie.objects.get(id=movie_id)
    
    if request.method == 'POST':
        form = MovieReviewForm(request.POST)
        if form.is_valid():
            # Verificar si el usuario ya tiene una reseña para esta película
            existing_review = MovieReview.objects.filter(user=request.user, movie=movie).first()
            if existing_review:
                # Actualizar la reseña existente
                existing_review.rating = form.cleaned_data['rating']
                existing_review.title = form.cleaned_data['title']
                existing_review.review = form.cleaned_data['review']
                existing_review.save()
            else:
                # Crear nueva reseña
                movie_review = MovieReview(
                    movie=movie,
                    rating=form.cleaned_data['rating'],
                    title=form.cleaned_data['title'],
                    review=form.cleaned_data['review'],
                    user=request.user)
                movie_review.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'listChanged'})
    else:
        # Pre-cargar reseña si existe
        existing_review = MovieReview.objects.filter(user=request.user, movie=movie).first()
        if existing_review:
            form = MovieReviewForm(instance=existing_review)
        else:
            form = MovieReviewForm()
        return render(request,
                  'movies/movie_review_form.html',
                  {'movie_review_form': form, 'movie': movie})


@login_required(login_url='admin:login')
@require_http_methods(["POST"])
def edit_review(request, review_id):
    review = get_object_or_404(MovieReview, id=review_id)
    
    # Verificar que el usuario sea el dueño de la reseña
    if review.user != request.user:
        return HttpResponse(status=403)
    
    form = MovieReviewForm(request.POST, instance=review)
    if form.is_valid():
        form.save()
        return HttpResponse(status=204, headers={'HX-Trigger': 'listChanged'})
    else:
        return render(request, 'movies/movie_review_form.html',
                  {'movie_review_form': form, 'movie': review.movie, 'review': review})


@login_required(login_url='admin:login')
@require_http_methods(["DELETE", "POST"])
def delete_review(request, review_id):
    review = get_object_or_404(MovieReview, id=review_id)
    
    # Verificar que el usuario sea el dueño de la reseña
    if review.user != request.user:
        return HttpResponse(status=403)
    
    movie_id = review.movie.id
    review.delete()
    
    if request.headers.get('HX-Request'):
        return HttpResponse(status=204, headers={'HX-Trigger': 'listChanged'})
    return redirect('movie', movie_id=movie_id)


def user_reviews(request, user_id):
    from django.contrib.auth.models import User
    user = get_object_or_404(User, id=user_id)
    reviews = MovieReview.objects.filter(user=user)
    context = {'user_profile': user, 'reviews': reviews}
    return render(request, 'movies/user_reviews.html', context=context)


@login_required(login_url='admin:login')
@require_http_methods(["POST"])
def add_favorite(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, movie=movie)
    
    if request.headers.get('HX-Request'):
        is_favorite = Favorite.objects.filter(user=request.user, movie=movie).exists()
        return render(request, 'movies/favorite_button.html', 
                     {'movie': movie, 'is_favorite': is_favorite},
                     headers={'HX-Trigger': 'favoritesUpdated'})
    return JsonResponse({'status': 'ok', 'is_favorite': True})


@login_required(login_url='admin:login')
@require_http_methods(["POST", "DELETE"])
def remove_favorite(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    Favorite.objects.filter(user=request.user, movie=movie).delete()
    
    if request.headers.get('HX-Request'):
        is_favorite = Favorite.objects.filter(user=request.user, movie=movie).exists()
        return render(request, 'movies/favorite_button.html', 
                     {'movie': movie, 'is_favorite': is_favorite},
                     headers={'HX-Trigger': 'favoritesUpdated'})
    return JsonResponse({'status': 'ok', 'is_favorite': False})


def favorite_count(request):
    """Retorna el contador de películas favoritas del usuario"""
    if request.user.is_authenticated:
        count = Favorite.objects.filter(user=request.user).count()
    else:
        count = 0
    return render(request, 'movies/favorite_badge.html', {'favorite_count': count})


def user_favorites(request, user_id):
    from django.contrib.auth.models import User
    user = get_object_or_404(User, id=user_id)
    favorites = Favorite.objects.filter(user=user).select_related('movie')
    context = {'user_profile': user, 'favorites': favorites}
    return render(request, 'movies/user_favorites.html', context=context)


@login_required(login_url='admin:login')
def my_favorites(request):
    """Redirige a las películas favoritas del usuario autenticado"""
    return user_favorites(request, request.user.id)


def search_movies(request):
    """Búsqueda de películas por título"""
    search_query = request.GET.get('search', '')
    movies = []
    
    if search_query:
        movies = Movie.objects.filter(title__icontains=search_query)
    
    context = {'movies': movies, 'search_value': search_query}
    return render(request, 'movies/search_results.html', context=context)


def person_detail(request, person_id):
    """Detalles de un actor/persona y sus películas"""
    person = get_object_or_404(Person, id=person_id)
    
    # Obtener todas las películas donde aparece esta persona
    movies = person.movie_set.all()
    
    context = {
        'person': person,
        'movies': movies
    }
    return render(request, 'movies/person_detail.html', context=context)


def random_movies(request):
    """Devuelve las siguientes 4 películas (para cargar más con HTMX)"""
    # Obtener el offset (cuántas películas ya se mostraron)
    offset = int(request.GET.get('offset', 4))
    
    # Obtener 4 películas más, comenzando desde el offset
    movies_list = Movie.objects.all()[offset:offset + 4]
    
    context = {'movies': movies_list}
    return render(request, 'movies/random_movies_fragment.html', context=context)
