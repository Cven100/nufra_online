from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Tabla General de Usuarios
class Roles(models.Model):
    nombre = models.CharField(max_length=50)

class Usuario(models.Model):
    rut = models.CharField(max_length=14, unique=True)
    nombre = models.CharField(max_length=150, default="")
    email = models.CharField(max_length=255, unique=True)
    telefono = models.IntegerField(default=0)
    direccion = models.CharField(max_length=255, default="")
    password = models.CharField(max_length=128)
    estado = models.CharField(max_length=30, blank=True, null=True)
    rol = models.ForeignKey(Roles, on_delete=models.CASCADE, default=1)

    def set_password(self, raw_password):
        """Establecer la contraseña de forma segura."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verificar la contraseña."""
        return check_password(raw_password, self.password)

# Tablas Admin
class Administrador(Usuario):
    apellido = models.CharField(max_length=150, default="")

class Picker(Usuario):
    apellido = models.CharField(max_length=150, default="")

class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=50, default="")
    disponible = models.BooleanField(default=True)

class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.DO_NOTHING)
    descripcion = models.TextField()
    fecha_ingreso = models.DateField(auto_now_add=True)
    precio_unitario = models.FloatField(default=0)
    precio_pedido = models.FloatField(default=0)
    disponible = models.BooleanField(default=True)
    stock_actual = models.IntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)  # <-- Añadir este campo

class Pedido(models.Model):
    nro_pedido = models.AutoField(unique=True, primary_key=True)
    fecha = models.DateField(auto_now_add=True)
    total_pedido = models.FloatField()

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.DO_NOTHING)
    cantidad = models.IntegerField()
    precio_unitario = models.FloatField()
    subtotal = models.FloatField()

# class Inventario(models.Model):
#     producto = models.ForeignKey(Producto, on_delete=models.DO_NOTHING)
#     nombre = models.CharField(max_length=150)
#     stock_actual = models.IntegerField()
#     descripcion = models.TextField()
#     fecha_actualizacion = models.DateField()
#     disponible = models.BooleanField(default=True)

class OrdenesCompra(models.Model):
    usuario_id = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    producto = models.ForeignKey(Producto, on_delete=models.DO_NOTHING)
    cantidad = models.IntegerField(default=1)
    estado = models.CharField(max_length=50, default="")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField(blank=True, null=True)

class Venta(models.Model):
    nro_boleta = models.IntegerField(default=0)
    rut_cliente = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    fecha = models.DateField()
    total = models.FloatField()

    def save(self, *args, **kwargs):
        #Sobreescribir el Metodo Save para que el nro_boleta sea auto-incrementable
        if not self.nro_boleta:
            # Obtener el último nro_boleta generado
            max_nro_boleta = Venta.objects.aggregate(max_nro=models.Max('nro_boleta'))['max_nro']
            self.nro_boleta = (max_nro_boleta or 0) + 1  # Incrementar a partir del último nro_boleta
        super().save(*args, **kwargs)
    
class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.DO_NOTHING)
    producto = models.ForeignKey(Producto, on_delete=models.DO_NOTHING)
    cantidad = models.IntegerField()
    precio_unitario = models.FloatField()
    subtotal = models.FloatField()

# EN PROCESO
# class OrdenesCompra(models.Model):
#     # Relación con Usuario y Producto
#     usuario_id = models.ForeignKey('Usuario', on_delete=models.DO_NOTHING)
#     producto = models.ForeignKey('Producto', on_delete=models.DO_NOTHING)

#     # Campo de Estado con opciones limitadas
#     ESTADOS = [
#         ('Pendiente', 'Pendiente'),
#         ('Enviado', 'Enviado'),
#         ('Entregado', 'Entregado'),
#         ('Cancelado', 'Cancelado'),
#     ]
#     estado = models.CharField(max_length=50, choices=ESTADOS, default='Pendiente')

#     # Fechas de creación y entrega (DateTimeField para almacenar fecha y hora)
#     fecha_creacion = models.DateTimeField(auto_now_add=True)
#     fecha_entrega = models.DateTimeField(null=True, blank=True)  # Puede ser null si no se ha entregado aún

#     def __str__(self):
#         return f"Orden #{self.id} - {self.estado}"


# EN PROCESO
# class CarroCompra(models.Model):
#     usuario_id = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
#     producto = models.ForeignKey(Producto, on_delete=models.DO_NOTHING)
#     cantidad = models.IntegerField(default=1)  # <-- Añadir este campo
#     total = models.FloatField()