from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/', views.product_list, name='product_list'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),  # ← ЭТА СТРОКА ДОЛЖНА БЫТЬ!
    path('import/', views.import_products, name='import_products'),
    path('files/', views.view_files, name='view_files'),
    path('files/delete/<str:filename>/', views.delete_file, name='delete_file'),
    path('files/delete-all/', views.delete_all_files, name='delete_all_files'),
]