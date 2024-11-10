from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from app import views as vistas
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    # Principal
    path('', vistas.RenderUserHome, name='home'),

    # Control de acceso
    path('login/', vistas.RenderLogin, name='Login'),
    path('register/', vistas.RenderRegister, name='register'),
    path('registerr/', vistas.register_view, name='Register'),
    path('logout/', vistas.RenderLogout, name='LogOut'),
    
    # Usuario
    path('catalogo/', vistas.RenderUserCatalog, name='Catalog'),
    path('acerca-de/', vistas.RenderAbout, name='About'),
    path('preguntas-frecuentes/', vistas.RenderFAQ, name='FAQ'),
    path('agregar-a-carrito/<int:producto_id>/', vistas.agregar_a_carrito, name='agregar_a_carrito'),

        #CARRO DE COMPRAS


    # Admin
    path('home/admin/', vistas.RenderAdminHome, name='AdminHome'),
    path('home/admin/trabajadores/', vistas.RenderTrabajadores, name='Trabajadores'),
    path('home/admin/reportes/', vistas.RenderReport, name='Reportes'),
    path('home/admin/configuraciones/', vistas.RenderConfig, name='Config'),
    
        # Producto
    path('home/admin/config/productos/', vistas.RenderProducto, name='productos'),
    path('home/admin/config/add-producto/', vistas.AddProducto, name='addProducto'),
    path('home/admin/config/edit-producto/<int:id>/', vistas.EditProducto, name='editProducto'),
        # Block/Unblock Producto
    path('home/admin/config/productos/block-producto/<int:id>/', vistas.BlockProducto, name='blockProducto'),

    # Categorias
    path('home/admin/config/productos/categorias/', vistas.RenderCategorias, name='categorias'),
    path('home/admin/config/productos/categorias/edit-categoria/<int:id>/', vistas.EditCategoria, name='editCategoria'),
    
        # Block/Unblock categoria
    path('home/admin/config/productos/categorias/block-categoria/<int:id>/', vistas.BlockCategoria, name='blockCategoria'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
