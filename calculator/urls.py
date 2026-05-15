from django.urls import path
from . import views

urlpatterns = [
    path('access-code/', views.access_code_view, name='access_code'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    path('nouvelle-journee/', views.nouvelle_journee, name='nouvelle_journee'),
    path('journee/<str:date_str>/', views.journee_detail, name='journee_detail'),
    path('journee/<str:date_str>/modifier/', views.modifier_journee, name='modifier_journee'),
    path('journee/<str:date_str>/supprimer/', views.supprimer_journee, name='supprimer_journee'),
    path('journee/<str:date_str>/pdf/', views.export_pdf, name='export_pdf'),
    path('historique/', views.historique_journees, name='historique'),
]