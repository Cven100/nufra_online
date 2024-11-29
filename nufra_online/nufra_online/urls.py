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
    path('register/admin/', vistas.RenderRegister, name='RegisterADM'),
    path('register/', vistas.register_view, name='RegisterUSER'),
    path('logout/', vistas.RenderLogout, name='LogOut'),
    
    # Usuario
    path('catalogo/', vistas.RenderUserCatalog, name='Catalog'),
    path('acerca-de/', vistas.RenderAbout, name='About'),
    path('preguntas-frecuentes/', vistas.RenderFAQ, name='FAQ'),
    
        #CARRO DE COMPRAS
    path('carrito/agregar/<int:producto_id>/', vistas.AddCarro, name='AddCarro'),
    path('carrito/eliminar/<int:producto_id>/', vistas.DeleteItemCarro, name='DeleteItemCarro'),
    path('carrito/vaciar/', vistas.VaciarCarro, name='VaciarCarro'),
    path('carrito/', vistas.DetalleCarrito, name='cart'),  # Nueva ruta para el detalle del carrito

    # Admin
    path('home/admin/', vistas.RenderAdminHome, name='AdminHome'),
    path('home/admin/trabajadores/', vistas.RenderTrabajadores, name='Trabajadores'),
    
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
        
        # Inventario
    path('home/admin/config/inventario/', vistas.RenderSupInventario, name='inventario'),
    path('home/admin/config/inventario/add', vistas.AddInventario, name='addInventario'),
    path('home/admin/config/inventario/edit/<int:id>/', vistas.EditInventario, name='editInventario'),
    path('home/admin/config/inventario/block/<int:id>/', vistas.BlockInventario, name='blockInventario'),

        # Picker
    # Ruta para gestionar pedidos
    path('home/picker/gestionar-pedidos/', vistas.RenderPedido, name='pickerHome'),
    
    # Ruta para ver un pedido específico
    path('home/picker/gestionar-pedidos/visualizar-pedidos/', vistas.VisualizarPedido, name='visualizarPedidos'),
    
    # Ruta para actualizar el estado de un pedido
    path('home/picker/gestionar-pedidos/actualizar-estado/', vistas.ActualizarEstado, name='actualizarEstado'),
    
    # # Ruta para visualizar stock
    # path('home/picker/visualizar-stock/', vistas.VisualizarStock, name='visualizarStock'),





] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
