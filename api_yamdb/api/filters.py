from django_filters import filters
from django_filters.rest_framework import FilterSet
from reviews.models import Title


class TitleFilter(FilterSet):
    name = filters.CharFilter(field_name='name')
    genre = filters.CharFilter(field_name='genre__slug')
    category = filters.CharFilter(field_name='category__slug')
    year = filters.NumberFilter(field_name='year')

    class Mets:
        model = Title
        fields = ('name', 'category', 'genre', 'year')
