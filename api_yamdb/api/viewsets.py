from rest_framework import mixins, viewsets
from rest_framework.filters import SearchFilter

from .permissions import (IsAdminOrReadOnly)


class CreateListDeleteViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
