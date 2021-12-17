import re
import datetime
from rest_framework.response import Response
from rest_framework import status
from .models import Client, Contract, Event


def filter_date(date, objects, attr_date):
    if date:
        date = re.split('\-|\/|\.', date)
        try:
            year, month, day = list(map(int, date))
            date = datetime.datetime(year, month, day)
            kwargs = {
                f'{attr_date}__year': year,
                f'{attr_date}__month': month,
                f'{attr_date}__day': day,
            }
            objects = objects.filter(**kwargs)
            return objects
        except ValueError as e:
            raise ValueError(e.args)
    return objects

def is_responsibleOfObject(responsible, user, objects):
    if responsible is None:
        return objects
    try:
        responsible = int(responsible)
        if responsible not in [0,1]:
            raise ValueError('Must be 0 or 1.')
    except ValueError as e:
        raise ValueError(e.args)
    
    if user.role == 'support':
        if objects.model.__name__ == 'Client':
            clients_id = Event.objects.filter(support_contact=user).values_list('client_id', flat=True)
            objects = Client.objects.filter(id__in=clients_id)

        if objects.model.__name__ == 'Event':
            objects = Event.objects.filter(support_contact=user.id)

    if user.role == 'seller':
        if objects.model.__name__ == 'Client':
            objects = Client.objects.filter(sale_contact=user)
        
        if objects.model.__name__ == 'Contract':
            objects = Contract.objects.filter(sales_contact=user.id)
    return objects