from rest_framework import generics
from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Client, User, Contract, Event
from .serializers import ClientSerializer, ContractSerializer, EventSerializer
from .permissions import IsSeller, IsSellerResponsibleOfClient, IsSellerResponsibleOfContract, IsSupport
from .utils import filter_date, is_responsibleOfObject


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
        clients = self.get_queryset()
        lastname, email = request.query_params.get('lastname'), request.query_params.get('email')
        responsible = request.query_params.get('responsible')
        
        try:
            clients = is_responsibleOfObject(responsible, request.user, clients)
        except ValueError as e:
            return Response({'detail': e.args}, status=status.HTTP_404_NOT_FOUND)

        if lastname: clients = clients.filter(lastname=lastname)
        if email: clients = clients.filter(email=email)

        serializer = self.serializer_class(clients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        self.check_object_permissions(request, None)
        serializer.is_valid(raise_exception=True)
        serializer.save(sale_contact=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        

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
        try:
            client = Client.objects.get(id=self.kwargs['pk'])
            
        except Client.DoesNotExist:
            return Response({"detail": "This ID client doesn't exist."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, client)
        serializer = self.serializer_class(client, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ContractList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Contract.objects.all()
    serializer_class  = ContractSerializer
    permission_classes = [IsAuthenticated, IsSeller]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        contracts = self.get_queryset()
        lastname, email = request.query_params.get('lastname'), request.query_params.get('email')
        date_created, amount = request.query_params.get('date_created'), request.query_params.get('amount')
        responsible = request.query_params.get('responsible')
        
        
        try:
            contracts = is_responsibleOfObject(responsible, request.user, contracts)
            contracts = filter_date(date_created, contracts, 'date_created')
            if lastname: contracts = contracts.filter(client__lastname=lastname)
            if email: contracts = contracts.filter(client__email=email)
        except ValueError as e:
            return Response({'detail': e.args}, status=status.HTTP_404_NOT_FOUND)
        if amount: contracts = contracts.filter(amount=amount)


        serializer = self.serializer_class(contracts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        self.check_object_permissions(request, None)
        serializer = self.serializer_class(data=request.data)
        try:
            client = Client.objects.get(email=request.data['client_email'])
        except Client.DoesNotExist:
            return Response({'detail': "This client doesn't exist."}, status=status.HTTP_404_NOT_FOUND)
        if client.role == 'prospect':
            return Response({'detail': "Can't create a contract for a prospect."}, status=status.HTTP_404_NOT_FOUND)
        if client.sale_contact != request.user:
            return Response({'detail': "You're not responsible of this client."}, status=status.HTTP_404_NOT_FOUND)
        serializer.is_valid(raise_exception=True)
        serializer.save(sales_contact=request.user, client=client, status='unsigned')
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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


class EventList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Event.objects.all()
    serializer_class  = EventSerializer
    permission_classes = [IsAuthenticated, IsSeller]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        events = self.get_queryset()
        lastname, email = request.query_params.get('lastname'), request.query_params.get('email')
        event_date, responsible = request.query_params.get('event_date'), request.query_params.get('responsible')

        try:
            events = is_responsibleOfObject(responsible, request.user, events)
            if lastname: events = events.filter(client__lastname=lastname)
            if email: events = events.filter(client__email=email)
            events = filter_date(event_date, events, 'event_date')
        except ValueError as e:
            return Response({'detail': e.args}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Seul un 'seller' peut créer un évenement grâce à la permission 'IsSeller'.
        On vérifie que le contrat n'a pas d'évémenent pour avoir un événement par contrat.
        """
        self.check_object_permissions(request, None)
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

        if client.sale_contact != request.user:
            return Response({'detail': "You're not responsible on this client."}, status=status.HTTP_404_NOT_FOUND)
        if contract.events.exists():
            return Response({'detail': f"Contract '{contract.id}' already have an event."}, status=status.HTTP_404_NOT_FOUND)
        if contract.id not in contracts_id:
            return Response({'detail': f"Client '{client.email}' don't have the contract ID {contract.id}."}, status=status.HTTP_404_NOT_FOUND)

        serializer.is_valid(raise_exception=True)
        serializer.save(client=client, contract=contract)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
        try:
            event = Event.objects.get(id=self.kwargs['pk'])
        except Event.DoesNotExist:
            return Response({"detail": "This ID event doesn't exist."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, event)
        if event.support_contact != request.user:
            return Response({"detail": "You're not responsible on this event."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(event, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)



