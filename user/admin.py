from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from transport.models import (
    Station,
    Crew,
    Train,
    Journey,
    Route,
    TrainType,
    Ticket,
    Order,
)

admin.site.register(User, UserAdmin)
admin.site.register(Station)
admin.site.register(Crew)
admin.site.register(Train)
admin.site.register(TrainType)
admin.site.register(Journey)
admin.site.register(Route)
admin.site.register(Ticket)
admin.site.register(Order)
