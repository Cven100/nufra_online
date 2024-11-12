from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Tabla General de Usuarios
class Roles(models.Model):
    nombre = models.CharField(max_length=50)

class Usuario(models.Model):
    rut = models.CharField(max_length=14, default="")
    nombre = models.CharField(max_length=150, default="")
    email = models.CharField(max_length=255, default="")
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
    fecha_ingreso = models.DateField()
    precio_unitario = models.FloatField()
    disponible = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)  # <-- Añadir este campo

class Inventario(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.DO_NOTHING)
    nombre = models.CharField(max_length=150)
    stock_actual = models.IntegerField()
    descripcion = models.TextField()
    fecha_actualizacion = models.DateField()

class OrdenesCompra(models.Model):
    usuario_id = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    producto = models.ForeignKey(Producto, on_delete=models.DO_NOTHING)
    estado = models.CharField(max_length=50, default="")
    fecha_creacion = models.TimeField(auto_now_add=True)
    fecha_entrega = models.TimeField(auto_now_add=True)

# class CarroCompra(models.Model):
#     usuario_id = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
#     producto = models.ForeignKey(Producto, on_delete=models.DO_NOTHING)
#     cantidad = models.IntegerField(default=1)  # <-- Añadir este campo
#     total = models.FloatField()

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