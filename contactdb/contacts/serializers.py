from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from contacts.models import Entity
from contacts.models import Person
from contacts.models import Organisation
from contacts.models import Countrycode
from contacts.models import Source
from contacts.models import Tag
from contacts.models import ASN
from contacts.models import Inetnum


class CountrycodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Countrycode
        fields = ('cc', 'country_name', )


class SourceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Source
        fields = ('name', 'reliability')


class OrganisationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organisation
        fields = ('name', 'long_name', 'countrycodes', 'address', 'email', 'pgp_fingerprint', 'phone_number', 'url', 'business_hh_start', 'business_hh_end', 'comment', 'tags', 'date_established', 'confirmed', 'active', 'ti_url', 'first_url')


class PersonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Person
        fields = ('name', 'long_name', 'user', 'countrycodes', 'email', 'pgp_fingerprint', 'phone_number', 'jabber_handle', 'organisations', 'picture', 'comment', 'tags')


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('url', 'groups', 'username')


class GroupSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Group
        fields = ('url', 'name', 'permissions')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('name', )


class ASNSerializer(serializers.ModelSerializer):

    class Meta:
        model = ASN
        fields = ('asn', 'owners', 'source', 'active', )

class InetnumSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = Inetnum
        fields = ('inet', 'prefix_length', 'init_ip', 'end_ip', 'owners', 'source', 'active', )
        depth = 1
