from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    path('about/', views.about, name='catalog-about'),
    path('home/', views.home, name='catalog-home'),
    path('catalog/', views.catalogList, name='catalog-list'),
    path('manufacturer/', views.manufacturerList, name='manufacturer-list'),
    path('', RedirectView.as_view(url='about/', permanent=True)),
    path('login/', views.loginPage, name='catalog-login'),
    path('logout/', views.logoutUser, name='catalog-logout'),
    path('register/', views.register, name='catalog-register'),
    path('record/<str:cr>/', views.recordList, name='record-list'),
    path('search/', views.advancedSearch, name='search'),
    # path('simpleSearch/', views.simpleSearch, name='simple-search'),
    path('create_record/', views.createRecord, name='record-create'),
    path('update_record/<str:ur>/', views.updateRecord, name='record-update'),
    path('record_detail/<str:pk>/', views.recordDetail, name='record-detail'),
    path('delete_record/<str:ur>/', views.deleteRecord, name='record-delete'),
    path('create_catalog/', views.createCatalog, name='catalog-create'),
    path('update_catalog/<str:ur>/', views.updateCatalog, name='catalog-update'),
    path('delete_catalog/<str:ur>/', views.deleteCatalog, name='catalog-delete'),
    path('create_provenance/', views.createProvenance, name='provenance-create'),
    path('update_provenance/<str:ur>/', views.updateProvenance, name='provenance-update'),
    path('delete_provenance/<str:ur>/', views.deleteProvenance, name='provenance-delete'),
    path('create_manufacturer/', views.createManufacturer, name='manufacturer-create'),
    path('update_manufacturer/<str:ur>/', views.updateManufacturer, name='manufacturer-update'),
    path('delete_manufacturer/<str:ur>/', views.deleteManufacturer, name='manufacturer-delete'),
]