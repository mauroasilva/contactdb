import django_filters

from contacts.models import Organisation
from contacts.models import Person


class OrganisationFilter(django_filters.FilterSet):

    class Meta:
        model = Organisation
        fields = ['name']


class PersonFilter(django_filters.FilterSet):

    class Meta:
        model = Person
        fields = ['name']
