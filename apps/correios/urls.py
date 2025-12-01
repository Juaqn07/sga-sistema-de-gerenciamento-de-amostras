from django.urls import path
from . import views

app_name = 'correios'

urlpatterns = [
    # ...
    path('api/tracking/update/<int:pk>/',
         views.api_tracking_update_view, name='api_tracking_update'),

    path('api/consulta-cep/', views.api_consult_zipcode_view,
         name='api_consulta_cep'),

]
