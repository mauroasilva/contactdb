from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from rest_framework import generics
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from contacts.permissions import IsUserOrReadOnly
from contacts.permissions import IsInOrgOrReadOnly
from contacts.serializers import UserSerializer
from contacts.serializers import GroupSerializer

from contacts.models import Person
from contacts.serializers import PersonSerializer
from contacts.filters import PersonFilter

from contacts.models import Organisation
from contacts.serializers import OrganisationSerializer
from contacts.filters import OrganisationFilter

from contacts.models import Countrycode
from contacts.serializers import CountrycodeSerializer

from contacts.models import Source
from contacts.serializers import SourceSerializer

from contacts.models import Tag
from contacts.serializers import TagSerializer

from contacts.models import ASN
from contacts.serializers import ASNSerializer

from contacts.models import Inetnum
from contacts.serializers import InetnumSerializer

import gnupg
import os


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def PGPKey(request, fingerprint):
    if request.method == 'GET':
        gpg = gnupg.GPG(homedir=os.environ['GNUPGHOME'])
        key = gpg.export_keys(fingerprint)
        return Response({fingerprint: key})


class CountrycodeViewSet(viewsets.ModelViewSet):
    queryset = Countrycode.objects.all()
    serializer_class = CountrycodeSerializer


class SourceViewSet(viewsets.ModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer


class OrganisationViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication,
                              TokenAuthentication)
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    filter_class = OrganisationFilter
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsInOrgOrReadOnly,)

    def pre_save(self, obj):
        g, created = Group.objects.get_or_create(name=obj.name)
        if not self.request.user.is_staff:
            g.user_set.add(self.request.user)


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    filter_class = PersonFilter
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsUserOrReadOnly,)

    def post_save(self, obj, **kwargs):
        if self.request.user.is_staff or obj.user == self.request.user:
            if obj.organisations is not None:
                for o in obj.organisations.all():
                    g, created = Group.objects.get_or_create(name=o.name)
                    if created or o.name in self.request.user.groups.all():
                        # only allow to add an organisation to an user if the user
                        # doing so is in the organisation
                        g.user_set.add(self.request.user)
        else:
            raise PermissionDenied(detail='User of Person has to be you.')


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This endpoint presents the users in the system.

    As you can see, the collection of snippet instances owned by a user are
    serialized using a hyperlinked representation.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows tags to be viewed or edited.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ASNViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tags to be viewed or edited.
    """
    queryset = ASN.objects.all()
    serializer_class = ASNSerializer

class InetnumViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tags to be viewed or edited.
    """
    queryset = Inetnum.objects.all()
    serializer_class = InetnumSerializer

class InetnumWhoisView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, ) # TODO: Change this to better object-protection level
    serializer_class = InetnumSerializer
    def get_queryset(self, ip):
        return Inetnum.objects.filter(init_ip__lte=ip).filter(end_ip__gte=ip).order_by('prefix_length').reverse()[:1]
        
    def get(self, request, ip):
        queryset = self.get_queryset(ip)
        serializer = InetnumSerializer(queryset, many=True)
        return Response(serializer.data)
        
class InetnumSubnetsView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, ) # TODO: Change this to better object-level protection
    serializer_class = InetnumSerializer
    def get_queryset(self, cidr):
        (init_ip, end_ip) = Inetnum.inet_borders(cidr)
        return Inetnum.objects.filter(init_ip__gte=init_ip).filter(end_ip__lte=end_ip)
        
    def get(self, request, cidr):
        queryset = self.get_queryset(cidr)
        serializer = InetnumSerializer(queryset, many=True)
        return Response(serializer.data)

