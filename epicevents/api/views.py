from functools import partial
from django.core import exceptions
from django.db.models.expressions import Value
from django.db.models.query import QuerySet
from django.shortcuts import render
from .models import Client, User, Contract, Event
from .serializers import ClientSerializer, UserSerializer, ContractSerializer, EventSerializer
from rest_framework import generics, serializers
from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsSalesContact, IsSeller, IsSellerResponsibleOfClient, IsSellerResponsibleOfContract, IsSupport


# DONE
class ClientList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Client.objects.all()
    serializer_class  = ClientSerializer
    permission_classes = [IsAuthenticated, IsSeller]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.check_object_permissions(request, None)
        return self.create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Liste les Clients, on apelle pas 'check_object_permissions' car tous les 'seller'
        et les 'support' on un accès à tous les clients en lecture.
        On utilise 'responsible' pour récupérer les clients attribués à un utilisateur 'support'.
        """
        clients = self.get_queryset()
        lastname, email = request.query_params.get('lastname'), request.query_params.get('email')
        responsible = request.query_params.get('responsible')
        if responsible:
            responsible = int(responsible)

        if request.user.role == 'support' and responsible:
            clients_id = Event.objects.filter(support_contact=request.user.id).values_list('client_id', flat=True)
            clients = clients.filter(id__in=clients_id)

        if lastname:
            clients = clients.filter(lastname=lastname)
        if email:
            clients = clients.filter(email=email)

        serializer = self.serializer_class(clients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
# DONE
class ClientDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Client.objects.all()
    serializer_class  = ClientSerializer
    permission_classes = [IsAuthenticated, IsSeller, IsSellerResponsibleOfClient]

    def get(self, request, *args, **kwargs):
        try:
            client = Client.objects.get(id=self.kwargs['pk'])
        except Client.DoesNotExist:
            return Response({"detail": "This ID client doesn't exist."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(client)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        """
        Seul un 'seller' peut changer un client qui lui a été attribué grâce aux permissions
        'IsSeller' et 'IsSellerResponsibleOfClient'.
        """
        try:
            client = Client.objects.get(id=self.kwargs['pk'])
        except Client.DoesNotExist:
            return Response({"detail": "This ID client doesn't exist."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, client)
        serializer = self.serializer_class(client, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


# DONE
class ContractList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Contract.objects.all()
    serializer_class  = ContractSerializer
    permission_classes = [IsAuthenticated, IsSeller]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Les 'seller' et les 'support' on un accès en lecture.
        La variable 'responsible' permet de filtrer les contrats attribués
        a un utilisateur 'seller'.
        """
        contracts = self.get_queryset()
        lastname, email = request.query_params.get('lastname'), request.query_params.get('email')
        date_created, amount = request.query_params.get('date_created'), request.query_params.get('amount')
        responsible = request.query_params.get('responsible')
        if responsible:
            responsible = int(responsible)

        if request.user.role == 'seller' and responsible:
            contracts = Contract.objects.filter(sales_contact=request.user.id)
        
        if lastname:
            contracts = contracts.filter(lastname=lastname)
        if email:
            contracts = contracts.filter(email=email)
        if date_created:
            contracts = contracts.filter(date_created=date_created)
        if amount:
            contracts = contracts.filter(amount=amount)


        serializer = self.serializer_class(contracts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Seul un 'seller' peut créer un contrat grâce à la permission 'IsSeller'.
        """
        serializer = self.serializer_class(data=request.data)
        try:
            client = Client.objects.get(email=request.data['client'])
        except Client.DoesNotExist:
            return Response({'detail': "This client doesn't exist."}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, None)
        serializer.is_valid(raise_exception=True)
        serializer.save(sales_contact=request.user, client=client)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# DONE
class ContractDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Contract.objects.all()
    serializer_class  = ContractSerializer
    permission_classes = [IsAuthenticated, IsSeller, IsSellerResponsibleOfContract]

    def get(self, request, *args, **kwargs):
        try:
            contract = Contract.objects.get(id=self.kwargs['pk'])
        except Contract.DoesNotExist:
            return Response({"detail": "This ID contract doesn't exist."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(contract)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        """
        Seul un 'seller' peut changer un contrat si il lui a été attribué grâce aux
        permissions 'IsSeller' et 'IsSellerResponsibleOfContract'.
        """
        try:
            contract = Contract.objects.get(id=self.kwargs['pk'])
        except Contract.DoesNotExist:
            return Response({"detail": "This ID contract doesn't exist."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, contract)
        client = contract.client
        if request.data['client']:
            try:
                client = Client.objects.get(email=request.data['client'])
            except Client.DoesNotExist:
                return Response({"detail": "This client doesn't exist."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(contract, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(client=client)
        return Response(serializer.data, status=status.HTTP_200_OK)


# DONE
class EventList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Event.objects.all()
    serializer_class  = EventSerializer
    permission_classes = [IsAuthenticated, IsSeller]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Tous les 'seller' et les 'support' ont accès en lecture seule aux événements.
        La variable responsible permet de filtrer tous les événements attribué à un utilisateur 'support'.
        """
        events = self.get_queryset()
        lastname, email = request.query_params.get('lastname'), request.query_params.get('email')
        event_date, responsible = request.query_params.get('date_created'), request.query_params.get('responsible')

        if responsible:
            responsible = int(responsible)

        if request.user.role == 'support' and responsible:
            events = Event.objects.filter(support_contact=request.user.id)
        
        if lastname:
            events = events.filter(lastname=lastname)
        if email:
            events = events.filter(email=email)
        if event_date:
            events = events.filter(event_date=event_date)

        serializer = self.serializer_class(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Seul un 'seller' peut créer un évenement grâce à la permission 'IsSeller'.
        On vérifie que le contrat n'a pas d'évémenent pour avoir un événement par contrat.
        """
        serializer = self.serializer_class(data=request.data)
        try:
            client = Client.objects.get(email=request.data['client_mail'])
            contracts_id = client.contracts.all().values_list('id', flat=True)

            contract = Contract.objects.get(id=int(request.data['contract_id']))
        except Client.DoesNotExist:
            return Response({'detail': "This client doesn't exist."}, status=status.HTTP_404_NOT_FOUND)
        except Contract.DoesNotExist:
            return Response({'detail': "This contract doesn't exist."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'detail': "Enter a correct contract ID."}, status=status.HTTP_404_NOT_FOUND)

        if contract.events.exists():
            return Response({'detail': f"Contract '{contract.id}' already have an event."}, status=status.HTTP_404_NOT_FOUND)
        if contract.id not in contracts_id:
            return Response({'detail': f"Client '{client.email}' don't have the contract ID {contract.id}."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, None)
        serializer.is_valid(raise_exception=True)
        serializer.save(client=client, contract=contract)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# DONE
class EventDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Event.objects.all()
    serializer_class  = EventSerializer
    permission_classes = [IsAuthenticated, IsSupport]

    def get(self, request, *args, **kwargs):
        try:
            event = Event.objects.get(id=self.kwargs['pk'])
        except Event.DoesNotExist:
            return Response({"detail": "This ID event doesn't exist."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        """
        Seul un 'seller' peut changer un contrat si il lui a été attribué grâce aux
        permissions 'IsSeller' et 'IsSellerResponsibleOfContract'.
        """
        try:
            event = Event.objects.get(id=self.kwargs['pk'])
        except Event.DoesNotExist:
            return Response({"detail": "This ID event doesn't exist."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, event)
        support_contact=event.support_contact

        if 'support_contact' in request.data and request.data['support_contact']:
            try:
                support_contact = User.objects.get(username=request.data['support_contact'])
            except User.DoesNotExist:
                return Response({"detail": "This user doesn't exist."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(event, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(support_contact=support_contact)
        return Response(serializer.data, status=status.HTTP_200_OK)