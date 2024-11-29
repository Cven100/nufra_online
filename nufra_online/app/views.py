import datetime
from django.contrib import messages
#SESSION
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import UserCreationForm
#HTTP
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from app.forms import AddUserForm

#MODEL
from .models import DetalleVenta, Usuario,Administrador , Roles, Producto, CategoriaProducto, Inventario, Picker, OrdenesCompra, Venta

#DECORADORES DE SESSION
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        # rol_id se basan en los de bd
        if request.session.get('user_id') and request.session.get('rol_id') == '2':
            return view_func(request, *args, **kwargs)
        return redirect('Login')  # Redirige al login si no es admin
    return wrapper

def picker_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get('user_id') and request.session.get('rol_id') == '3':  # '3' para rol de picker
            return view_func(request, *args, **kwargs)
        return redirect('Login')
    return wrapper


# Control de Acceso
def RenderLogout(request):
    logout(request)  # Limpia la sesión del usuario
    return redirect('Login')

def RenderLogin(request):
    if request.method == "POST":
        has_error = {}
        chars_restringidos_user = [
            ' ', '..', '(', ')', '<', '>', '[',
            ']', ',', ';', ':', '"'
            ]
        
        username = request.POST.get('username')

        if username.strip() == "":
            has_error['username_empty'] = 'El Campo Usuario no Puede Estar Vacio'
        elif len(username) > 255:
            has_error['username_max_char'] = 'Se ha Superado el MAXIMO de Caracteres, MAXIMO Permitido: 255'
        else:
            invalid_char = []
            for char in username:
                if char in chars_restringidos_user:
                    invalid_char.append(char)
            if len(invalid_char) > 0:
                invalid_char_str = ', '.join(set(invalid_char))
                has_error['username_char_error'] = 'Caracter no Valido: {}.'.format(invalid_char_str)
        
        password = request.POST.get('password')
        if password.strip() == "":
            has_error['password_empty'] = 'El Campo Contraseña no Puede Estar Vacio'
        elif len(password) > 128:
            has_error['password_max_char'] = 'Se ha Superado el MAXIMO de Caracteres, MAXIMO Permitido: 128'
            
        if not has_error:
            try:
                username = username
                user = Usuario.objects.get(email=username)
                if user.check_password(password):
                    # SESSION DATA
                    request.session['user_id'] = user.id
                    request.session['email'] = user.email
                    request.session['rol_id'] = str(user.rol.id) 

                    if user.rol.id == 1:
                        # ESTO QUITARLO SI DA DRAMA ES PARA EL CARRO
                        request.session['rut'] = user.rut  
                        return redirect('home')
                    elif user.rol.id == 2:
                        return redirect('AdminHome')
                    elif user.rol.id == 3:
                        return redirect('pickerHome')
                else:
                    has_error['cred_error'] = 'Las Credenciales no Coinciden'
            except Usuario.DoesNotExist:
                has_error['user_error'] = 'Usuario no Encontrado'
        return render(request, 'shared/login.html', {'errores': has_error})

    elif request.method == "GET":
        return render(request, 'shared/login.html')

@admin_required
def RenderRegister(request):
    roles = Roles.objects.all()
    if request.method == "POST":
        # USUARIO
        has_error = {}
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        username = request.POST.get('username')
        rol = request.POST.get('rol')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        telefono = request.POST.get('telefono')

        
        # VALIDACIONES GENERALES
        chars_restringidos_correo = [
            ' ', '..', '(', ')', '<', '>', '[',
            ']', ',', ';', ':', '"', '@'
            ]
        
        if nombre.strip() == "":
            has_error['name_empty'] = 'El Campo NOMBRE no Puede Estar Vacio'
        elif len(nombre) > 150:
            has_error['name_max_char'] = 'Se ha Superado el MAXIMO de Caracteres, MAXIMO Permitido: 150'
        else:
            nombre = nombre.title()

        if telefono.strip() == "":
            has_error['telefono_empty'] = 'El Campo TELEFONO no Puede Estar Vacio'

        if apellido.strip() == "":
            has_error['ape_empty'] = 'El Campo Apellido no Puede Estar Vacio'
        elif len(apellido) > 150:
            has_error['ape_max_char'] = 'Se ha Superado el MAXIMO de Caracteres, MAXIMO Permitido: 150'
        else:
            apellido = apellido.title()

        if username.strip() == "":
            has_error['username_empty'] = 'El Campo CORREO no Puede Estar Vacio'
        else:
            invalid_char = []
            for char in username:
                if char in chars_restringidos_correo:
                    invalid_char.append(char)
            if len(invalid_char) > 0:
                invalid_char_str = ', '.join(set(invalid_char))
                has_error['username_char_error'] = 'Caracter no Valido: {}.'.format(invalid_char_str)
        
        if rol == '-1':
            has_error['rol_default'] = 'El Campo ROL Debe ser DISTINTO al PREDETERMINADO'

        if password.strip() == "":
            has_error['password_empty'] = 'El Campo Contraseña no Puede Estar Vacio'
        elif len(password) > 128:
            has_error['password_max_char'] = 'Se ha Superado el MAXIMO de Caracteres, MAXIMO Permitido: 128'
        
        if confirm_password.strip() == "":
            has_error['con_pass_empty'] = 'El Campo de Confirmacion de Contraseña no Puede Estar Vacio'
        elif len(confirm_password) > 128:
            has_error['con_pass_max_char'] = 'Se ha Superado el MAXIMO de Caracteres, MAXIMO Permitido: 128'

        if password != confirm_password:
            has_error['password_final'] = 'Las contraseñas no coinciden'     

        # VALIDAR EXISTENCIA DEL OBJETO

        if not has_error:
            if rol == '2':
                user = Administrador(
                    nombre=nombre,
                    apellido=apellido,
                    rol=Roles.objects.get(id=rol),
                    email= username + '@nufra.com',
                    estado= 'Activo',
                    telefono=telefono
                )
                user.set_password(password)
                user.save()

            if rol == '3':
                user = Picker(
                    nombre=nombre,
                    apellido=apellido,
                    rol=Roles.objects.get(id=rol),
                    email= username + '@nufra.com',
                    estado= 'Activo',
                    telefono=telefono
                )
                user.set_password(password)
                user.save()

            return render(request, 'admin/views/register.html', {'roles': roles})
        else:
            return render(request, 'admin/views/register.html', {'roles': roles, 'errores': has_error})
    
    elif request.method == "GET":
        return render(request, 'admin/views/register.html', {'roles': roles})

# Usuario General

def agregar_a_carrito(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    cantidad = int(request.POST.get('cantidad', 1))
    
    # Aquí agregas la lógica para añadir el producto al carrito
    # Suponiendo que el carrito se guarda en la sesión o en otro modelo.

    # Por ejemplo, si el carrito es un diccionario en la sesión:
    carrito = request.session.get('carrito', [])
    if producto_id in carrito:
        carrito[producto_id] += cantidad
    else:
        carrito[producto_id] = cantidad
    
    request.session['carrito'] = carrito

    # Redirige de vuelta al catálogo o a donde sea necesario
    return redirect('Catalog')

def register_view(request):
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.estado = 'n/a'
            user.rol = Roles.objects.get(id=1)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('home')
    else:
        form = AddUserForm()
    return render(request, 'usuario/register.html', {'form': form})

def RenderUserHome(request):
    return render(request, 'usuario/indexUser.html')

def RenderUserCatalog(request):
    if request.method == 'GET':
        carrito = request.session.get("carro", [])
        user_id = request.session.get('user_id', None)
        # Filtros para visualizar solo las categorias con productos 
        categorias_con_productos = CategoriaProducto.objects.filter(producto__isnull=False).distinct()
        productos = Producto.objects.filter(categoria__in=categorias_con_productos)

        return render(request, 'usuario/catalog.html', {
            'categorias': categorias_con_productos, 
            'productos': productos, 
            'carro': carrito,
            'user_id': user_id,
            })
    
### Probando ###

# Función para agregar productos al carrito
def AddCarro(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    cantidad = int(request.POST.get('cantidad', 1))
    carro = request.session.get('carro', [])

    # Verificar si el producto ya está en el carrito y aumentar la cantidad
    for item in carro:
        if item['id'] == producto.id:
            item['cantidad'] += cantidad
            break
    else:
        # Si el producto no está en el carrito, añadirlo con la cantidad seleccionada
        carro.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'cantidad': cantidad,
            'precio': producto.precio_unitario,
            'subtotal': producto.precio_unitario * cantidad
        })
        # Guardar el carrito en la sesión
        request.session['carro'] = carro
        messages.success(request, 'Producto agregado al carrito.')
    return redirect('Catalog')

# Función para eliminar un producto específico del carrito
def DeleteItemCarro(request, producto_id):
    carro = request.session.get('carro', [])
    carro = [item for item in carro if item['id'] != producto_id]
    request.session['carro'] = carro
    messages.success(request, 'Producto eliminado del carrito.')
    return redirect('cart')  # Redirige a la vista de detalle del carrito

# Función para vaciar el carrito y ajustar el stock
def VaciarCarro(request):
    carro = request.session.get('carro', [])
    if carro:
        user = Usuario.objects.get(rut=request.session.get('rut', None))
        venta = Venta.objects.create(
            rut_cliente=user,  # Asumimos que el usuario está en la sesión
            fecha=datetime.date.today(),
            total=0,  # Esto se actualizará más tarde
        )

        total_compra = 0

        for item in carro:
            producto = get_object_or_404(Producto, id=item['id'])
            inventario = Inventario.objects.get(producto=producto)
            subtotal = item['subtotal']
            total_compra += subtotal
            
            # Registrar el detalle de la venta
            detalle = DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=item['cantidad'],
                precio_unitario=item['precio'],
                subtotal=subtotal
            )
            inventario.stock_actual -= item['cantidad']
            inventario.save()

        venta.total = total_compra
        venta.save()

        # Vaciar el carrito después de la compra
        request.session['carro'] = []
        messages.success(request, 'Compra confirmada. El stock ha sido actualizado.')
    
    else:
        messages.error(request, 'No hay productos en el carrito.')

    return redirect('cart')  # Redirige a la vista de detalle del carrito

# Vista para mostrar los detalles del carrito
def DetalleCarrito(request):
    carro = request.session.get('carro', [])
    total = sum(item['precio'] * item['cantidad'] for item in carro)
    return render(request, 'usuario/carrito/detalle_carrito.html', {'carro': carro, 'total': total})


def RenderAbout(request):
    return render(request, 'usuario/about.html')

def RenderFAQ(request):
    return render(request, 'usuario/faq.html')

# Admin
@admin_required
def RenderAdminHome(request):
    return render(request, 'admin/views/indexAdmin.html')

@admin_required
def RenderTrabajadores(request):
    users = Usuario.objects.all()
    adm = Administrador.objects.all()
    pick = Picker.objects.all()
    return render(request, 'admin/views/trabajadores.html',{'users': users, 'adm': adm, 'pick': pick})



# Categorias
@admin_required
def RenderCategorias(request):
    categorias = CategoriaProducto.objects.all()
    if request.method == 'POST':
        has_error = {}
        nombre = request.POST.get('nombre')

        if nombre == "":
            has_error['name_empty'] = 'El NOMBRE NO puede estar VACIO'
        elif len(nombre) > 50:
            has_error['name_max_char'] = 'Se ha Superado el MAXIMO de Caracteres, MAXIMO Permitido: 50'
        else:
            nombre = nombre.title()

        if not has_error:
            categoria = CategoriaProducto(nombre=nombre)
            categoria.save()
            return redirect('categorias')
        else:
            return render(request, 'admin/productos/categorias/categorias.html', {'categorias': categorias, 'errores':has_error})
        
    elif request.method == 'GET':
        return render(request, 'admin/productos/categorias/categorias.html', {'categorias': categorias})

@admin_required
def EditCategoria(request, id):
    categorias = CategoriaProducto.objects.all()
    categoria = get_object_or_404(CategoriaProducto, id=id)

    if request.method == 'POST':
        has_error = {}
        nombre = request.POST.get('nombre')

        # Validaciones de datos
        if not nombre:
            has_error['name_empty'] = 'El NOMBRE NO puede estar VACIO'
        elif len(nombre) > 50:
            has_error['name_max_char'] = 'Se ha Superado el MAXIMO de Caracteres, MAXIMO Permitido: 50'
        else:
            nombre = nombre.title()

        if not has_error:
            categoria.nombre = nombre
            categoria.save()
            return redirect('categorias')
        else:
            return render(request, 'admin/productos/categorias/categorias.html', {
                'categorias': categorias,
                'editable': categoria,
                'errores': has_error
            })

    elif request.method == 'GET':
        return render(request, 'admin/productos/categorias/categorias.html', {
            'categorias': categorias,
            'editable': categoria
        })

@admin_required 
def BlockCategoria(request, id):
    if request.method == 'GET':
        categoria = CategoriaProducto.objects.get(id=id)
        if categoria.disponible:
            try:
                categoria.disponible = False
                categoria.save()
                return redirect('categorias')
            except:
                return HttpResponse(f"Error al Deshabilitar la Categoria: {categoria.nombre}", status=404)
        else:
            try:
                categoria.disponible = True
                categoria.save()
                return redirect('categorias')
            except:
                return HttpResponse("Error al Habilitar la Categoria: {}".format(categoria.nombre), status=404)        

@admin_required
def RenderProducto(request):
    productos = Producto.objects.all()
    if request.method == 'GET':
        return render(request, 'admin/productos/productos.html', {'productos': productos})

@admin_required 
def AddProducto(request):
    categorias = CategoriaProducto.objects.all()
    if request.method == 'POST':
        has_error = {}

        nombre = request.POST.get('nombre')
        categoria = request.POST.get('categoria')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        fecha = request.POST.get('fecha')
        imagen = request.FILES.get('imagen')

        # Validacion Nombre
        if nombre.strip() == "":
            has_error['name_empty'] = 'El Campo NOMBRE NO Puede Estar Vacio'
        elif len(nombre) > 150:
            has_error['name_max_char'] = 'Se ha Superado el Limite de Caracteres, MAXIMO Permitido: 150'
        elif nombre.isdigit():
            has_error['char_numerico'] = 'El Campo NOMBRE NO Puede ser Solamente NUMERICO'
        else:
            nombre = nombre.title()

        # Validacion Categoria
        if categoria == '-1':
            has_error['cate_default'] = 'El Campo CATEGORIA Debe ser DISTINTO al PREDETERMINADO'


        # Validacion Descripcion
        if descripcion.strip() == "":
            has_error['des_empty'] = 'El Campo Descripcion NO Puede Estar Vacio'
        else:
            descripcion = descripcion.capitalize()

        # Validacion Precio
        if precio.strip() == "":
            has_error['price_empty'] = 'El Campo Precio NO Puede Estar Vacio'
        else:
            try:
                precio = float(precio)
            except ValueError:
                has_error['price_char_error'] = 'El PRECIO Debe ser un Número Válido.'
        
        # Validacion Fecha
        if not fecha:
            has_error['date_empty'] = 'La FECHA NO Puede Esta VACIA'
        else:
            try:
                fecha_valida = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()
                if fecha_valida > datetime.date.today():
                    has_error['future_date'] = 'La Fecha de Ingreso NO Puede Estar en el FUTURO'
            except ValueError:
                has_error['invalid_date'] = 'Fecha Ingresada Invalida'

        # Validar Existencia
        if Producto.objects.filter(nombre=nombre).exists():
                has_error['duplicado'] = 'Producto ya existente'

        if not has_error:
            producto = Producto(
                nombre=nombre,
                categoria=get_object_or_404(CategoriaProducto, id=categoria),
                descripcion=descripcion,
                precio_unitario=precio,
                fecha_ingreso=fecha,
                imagen=imagen
            )

            producto.save()
            return redirect('addProducto')
        else:
            return render(request, 'admin/productos/addProducto.html', {'categorias': categorias, 'errores':has_error})
  
    elif request.method == 'GET':
        return render(request, 'admin/productos/addProducto.html', {'categorias': categorias})

@admin_required
def EditProducto(request, id):
    producto = get_object_or_404(Producto, id=id)
    categorias = CategoriaProducto.objects.all()

    if request.method == 'POST':
        has_error = {}

        nombre = request.POST.get('nombre')
        categoria = request.POST.get('categoria')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        fecha = request.POST.get('fecha')
        imagen = request.FILES.get('imagen')

        # Validacion Nombre
        if nombre.strip() == "":
            has_error['name_empty'] = 'El Campo NOMBRE NO Puede Estar Vacio'
        elif len(nombre) > 150:
            has_error['name_max_char'] = 'Se ha Superado el Limite de Caracteres, MAXIMO Permitido: 150'
        elif nombre.isdigit():
            has_error['char_numerico'] = 'El Campo NOMBRE NO Puede ser Solamente NUMERICO'
        else:
            nombre = nombre.title()

        # Validacion Categoria
        if categoria == '-1':
            has_error['cate_default'] = 'El Campo CATEGORIA Debe ser DISTINTO al PREDETERMINADO'
        

        # Validacion Descripcion
        if descripcion.strip() == "":
            has_error['des_empty'] = 'El Campo Descripcion NO Puede Estar Vacio'
        else:
            descripcion = descripcion.capitalize()

        # Validacion Precio
        if precio.strip() == "":
            has_error['price_empty'] = 'El Campo Precio NO Puede Estar Vacio'
        else:
            try:
                precio = float(precio)
            except ValueError:
                has_error['price_char_error'] = 'El PRECIO Debe ser un Número Válido.'
        
        # Validacion Fecha
        if not fecha:
            has_error['date_empty'] = 'La FECHA NO Puede Esta VACIA'
        else:
            try:
                fecha_valida = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()
                if fecha_valida > datetime.date.today():
                    has_error['future_date'] = 'La Fecha de Ingreso NO Puede Estar en el FUTURO'
            except ValueError:
                has_error['invalid_date'] = 'Fecha Ingresada Invalida'

        # Validar Existencia (solo si el nombre ha cambiado)
        if Producto.objects.filter(nombre=nombre).exclude(id=producto.id).exists():
            has_error['duplicado'] = 'Producto ya existente'

        if not has_error:
            # Actualizar el producto
            producto.nombre = nombre
            producto.categoria = get_object_or_404(CategoriaProducto, id=categoria)
            producto.descripcion = descripcion
            producto.precio_unitario = precio
            producto.fecha_ingreso = fecha
            if imagen:
                producto.imagen = imagen
        
            producto.save()

            return redirect('productos') 
        else:
            return render(request, 'admin/productos/editProducto.html', {
                'categorias': categorias,
                'producto': producto,
                'errores': has_error
            })
  
    elif request.method == 'GET':
        return render(request, 'admin/productos/addProducto.html', {
            'categorias': categorias,
            'producto': producto
        })

# Manejo de Producto / Para no eliminar registros
@admin_required
def BlockProducto(request, id):
    if request.method == 'GET':
        producto = Producto.objects.get(id=id)
        if producto.disponible:
            try:
                producto.disponible = False
                producto.save()
                return redirect('productos')
            except:
                return HttpResponse(f"Error al deshabilitar el producto: {producto.nombre}", status=404)
        else:
            try:
                producto.disponible = True
                producto.save()
                return redirect('productos')
            except:
                return HttpResponse("Error al habilitar el producto: {}".format(producto.nombre), status=404)        

@admin_required
def RenderSupHome(request):
    return render(request, 'supervisor/indexSuper.html')

@admin_required
def RenderSupInventario(request):
    if request.method == 'GET':
        inventario = Inventario.objects.all()
        return render(request, 'admin/inventario/inventario.html', {'inventario': inventario})

@admin_required
def AddInventario(request):
    productos = Producto.objects.all()
    existencia = Inventario.objects.all()
    has_error = {}
    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        stock = request.POST.get('stock_actual')
        descripcion = request.POST.get('descripcion')
        fecha = request.POST.get('fecha_actualizacion')

    # Validaciones
        if producto_id == '-1':
            has_error['producto_empty'] = "Debe seleccionar un producto."
        
        if not stock:
            has_error['stock_empty'] = "El stock no puede estar vacío."
        elif not stock.isdigit() or int(stock) < 0:
            has_error['stock_invalid'] = "El stock debe ser un número positivo."

        if not descripcion:
            has_error['descripcion_empty'] = "La descripción no puede estar vacía."

        if not fecha:
            has_error['fecha_empty'] = "La fecha de actualización es obligatoria."
        else:
            try:
                fecha_valida = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()
                if fecha_valida > datetime.date.today():
                    has_error['future_date'] = 'La Fecha de Ingreso NO Puede Estar en el FUTURO'
            except ValueError:
                has_error['invalid_date'] = 'Fecha Ingresada Invalida'
        
        if Inventario.objects.filter(producto_id=producto_id).exists():
                has_error['duplicado'] = "Ya existe un registro en el inventario para este producto."
            
        if not has_error:
            producto = Producto.objects.get(id=producto_id)
            nuevo_inventario = Inventario(
                producto=producto,
                nombre=producto.nombre,
                stock_actual=int(stock),
                descripcion=descripcion,
                fecha_actualizacion=fecha
            )
            nuevo_inventario.save()
            return redirect('inventario') 
        else:
            return render(request, 'admin/inventario/addInventario.html', {'productos': productos, 'errores': has_error, 'existencia': existencia})

    elif request.method == 'GET':
        print(productos)
        print(existencia)
        return render(request, 'admin/inventario/addInventario.html', {'productos': productos, 'existencia': existencia})

@admin_required
def EditInventario(request, id):
    inventario = Inventario.objects.get(id=id)  # Obtener el inventario a editar
    productos = Producto.objects.all()  # Obtener todos los productos disponibles
    has_error = {}

    if request.method == 'POST':
        # Obtener los datos del formulario
        producto_id = request.POST.get('producto')
        stock = request.POST.get('stock_actual')
        descripcion = request.POST.get('descripcion')
        fecha = request.POST.get('fecha_actualizacion')

        # Validaciones
        if producto_id == '-1':
            has_error['producto_empty'] = "Debe seleccionar un producto."
        
        if not stock:
            has_error['stock_empty'] = "El stock no puede estar vacío."
        elif not stock.isdigit() or int(stock) < 0:
            has_error['stock_invalid'] = "El stock debe ser un número positivo."

        if not descripcion:
            has_error['descripcion_empty'] = "La descripción no puede estar vacía."

        if not fecha:
            has_error['fecha_empty'] = "La fecha de actualización es obligatoria."
        else:
            try:
                fecha_valida = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()
                if fecha_valida > datetime.date.today():
                    has_error['future_date'] = 'La Fecha de Ingreso NO Puede Estar en el FUTURO'
            except ValueError:
                has_error['invalid_date'] = 'Fecha Ingresada Invalida'

        # Si no hay errores, actualizar el inventario
        if not has_error:
            producto = get_object_or_404(Producto, id=producto_id)
            inventario.producto = producto
            inventario.nombre = producto.nombre
            inventario.stock_actual = int(stock)
            inventario.descripcion = descripcion
            inventario.fecha_actualizacion = fecha
            inventario.save()

            return redirect('inventario')  # Redirige a la vista de inventarios

        # Si hay errores, renderizar el formulario con los errores
        return render(request, 'admin/inventario/addInventario.html', {
            'productos': productos,
            'inventario': inventario,
            'errores': has_error
        })

    elif request.method == 'GET':
        # Si es una solicitud GET, renderizar el formulario con los datos del inventario
        return render(request, 'admin/inventario/addInventario.html', {
            'productos': productos,
            'inventario': inventario
        })
    
@admin_required
def BlockInventario(request, id):
    if request.method == 'GET':
        inventario = Inventario.objects.get(id=id)
        if inventario.disponible:
            try:
                inventario.disponible = False
                inventario.save()
                return redirect('inventario')
            except:
                return HttpResponse(f"Error al deshabilitar el producto: {inventario.nombre}", status=404)
        else:
            try:
                inventario.disponible = True
                inventario.save()
                return redirect('inventario')
            except:
                return HttpResponse("Error al habilitar el producto: {}".format(inventario.nombre), status=404)        
    
# Vendedor
# @admin_required
# def RenderVenHome(request):
#     return render(request, 'vendedor/indexVendedor.html')

# # @admin_required
# def RenderVentas(request):
#     return render(request, 'vendedor/ventas.html')

# def inicio(request):
#     # Obtenemos los productos del carrito (IDs almacenados en la sesión)
#     carrito = request.session.get("carrito", [])
#     # Obtenemos todos los productos disponibles
#     productos = Producto.objects.all()
#     # Pasamos el número de productos en el carrito al template
#     return render(request, "inicio.html", {"productos": productos, "carrito": len(carrito)})

# def agregarAlCarro(request, id):
#     # Si el carrito no existe en la sesión, se inicializa como lista vacía
#     carrito = request.session.get("carrito", [])
#     # Agregamos el ID del producto al carrito
#     carrito.append(id)
#     # Guardamos el carrito actualizado en la sesión
#     request.session["carrito"] = carrito
#     return inicio(request)  # Volvemos a la página de inicio

def detalleCarrito(request):
    # Obtenemos los IDs de los productos en el carrito
    idsProductos = request.session.get("carrito", [])
    # Consultamos los productos correspondientes a esos IDs
    productos = Producto.objects.filter(id__in=idsProductos)
    
    return render(request, "usuario/carrito/detalle_carrito.html", {"productos": productos})


# gestionar los pedidos VERIFICARRRRRRRRRRRRRRR 

# def RenderPedido(request, id=None):
#     if id is None:
#         pedidos = OrdenesCompra.objects.all()
#         return render (request, "picker/gestionarPedidos.html",{"pedidos:pedidos"})

#     pedido = get_object_or_404(OrdenesCompra, id=id)

#     if request.method=="POST" and "actualizarEstado" in request.POST:
#         newestado= request.POST.get("estado")
#         pedido.estado = newestado
#         pedido.save()
#         return redirect("visualizarPedidos",id=pedido.id)

#     return render(request, "visualizarPedidos.html",{"pedido":pedido})

# Vista para gestionar pedidos
@picker_required
def RenderPedido(request):
    # Obtener todos los pedidos (o filtrar según tus necesidades)
    pedidos = OrdenesCompra.objects.all()
    return render(request, 'picker/gestionarPedidos.html', {'pedidos': pedidos})

# Vista para visualizar un pedido específico
@picker_required
def VisualizarPedido(request):
    # Obtener todos los pedidos
    pedidos = OrdenesCompra.objects.all()
    return render(request, 'picker/visualizarPedidos.html', {'pedidos': pedidos})

# Vista para actualizar el estado de un pedido
@picker_required
def ActualizarEstado(request):
    if request.method == 'POST':
        # Aquí agregarías la lógica para actualizar el estado de un pedido
        # Ejemplo:
        # pedido_id = request.POST.get('pedido_id')
        # estado = request.POST.get('estado')
        # Pedido.objects.filter(id=pedido_id).update(estado=estado)
        return HttpResponse("Estado actualizado con éxito")

    # Mostrar la página de actualizar estado
    return render(request, 'picker/actualizarEstado.html')

# Vista para visualizar el stock de productos
def VisualizarStock(request):
    productos = Producto.objects.all()  # Obtiene todos los productos
    return render(request, "picker/visualizarStock.html", {"productos": productos})

