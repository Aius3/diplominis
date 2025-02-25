from django.urls import path
from . import views
from .views import ReceptasDetail

urlpatterns = [
 path('', views.index, name='index'),
 path('register/', views.register_user, name='register'),
 path('profile/', views.get_user_profile, name='user-profile'),
 path('submit-recipe/', views.submit_recipe, name='submit-recipe'),
 path('recipe/<int:pk>/', ReceptasDetail.as_view(), name='recipe'),
 path('recipe/<int:recipe_id>/', ReceptasDetail.as_view(), name='Receptas'),
 path('profile/<str:username>/', views.view_other_profile, name='view-other-profile'),
 path('mano-receptai/', views.mano_receptai, name='mano-receptai'),
]



    

