from django.urls import path
from .views import BlueprintGenerateView, RecipeListView

urlpatterns = [
    path('generate/', BlueprintGenerateView.as_view(), name='blueprint-generate'),
    path('items/', RecipeListView.as_view(), name='item-list'),
]
