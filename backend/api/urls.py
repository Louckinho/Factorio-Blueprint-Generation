from django.urls import path
from .views import BlueprintGenerateView, RecipeListView
from .ai_views import ADAMGenerateView

urlpatterns = [
    path('generate/', BlueprintGenerateView.as_view(), name='blueprint-generate'),
    path('generate-ai/', ADAMGenerateView.as_view(), name='blueprint-generate-ai'),
    path('items/', RecipeListView.as_view(), name='item-list'),
]
