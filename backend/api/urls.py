from django.urls import path
from .views import BlueprintGenerateView

urlpatterns = [
    path('generate/', BlueprintGenerateView.as_view(), name='blueprint-generate'),
]
