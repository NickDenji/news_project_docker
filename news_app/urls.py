from django.urls import path
from .views import home
from .views import approve_article

urlpatterns = [
    path('', home, name='home'),
    path('approve/<int:article_id>/', approve_article, name='approve_article'),
]
