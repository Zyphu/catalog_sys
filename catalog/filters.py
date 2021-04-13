import django_filters

from .models import *
from django_filters import DateFilter, CharFilter


class RecordFilter(django_filters.FilterSet):
    date_start = DateFilter(field_name="date_start", lookup_expr='gte')
    date_end = DateFilter(field_name="date_start", lookup_expr='lte')
    description = CharFilter(field_name='description', lookup_expr='icontains')
    condition_description = CharFilter(field_name='condition_description', lookup_expr='icontains')
    name = CharFilter(field_name='name', lookup_expr='icontains')
    #simpleSearch = CharFilter

    class Meta:
        model = Record
        fields = ["name", "description", "condition_description", "my_catalog", "manufacturer", "condition_rating"]
