from django import forms
from movies.models import MovieReview


class MovieReviewForm(forms.ModelForm):
    class Meta:
        model = MovieReview
        fields = ['title', 'rating', 'review']
        labels = {
            'title': 'Título',
            'rating': 'Calificación (1-5)',
            'review': 'Reseña'
        }
        widgets = {
            'title': forms.TextInput(attrs={
                "class": "block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6"
            }),
            'rating': forms.Select(attrs={
                "class": "rounded-md bg-white py-1.5 pl-3 pr-2 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6"
            }, choices=[(i, f'{i} estrella{"s" if i != 1 else ""}') for i in range(1, 6)]),
            'review': forms.Textarea(attrs={
                "class": "block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6",
                "rows": 5
            })
        }