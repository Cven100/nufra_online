import datetime

#SESSION
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import UserCreationForm
#HTTP
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

#MODEL
from .models import Usuario,Administrador , Roles, Producto, CategoriaProducto, Inventario, Picker

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
            ']', ',', ';', ':', '"', '@'
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
                user = Usuario.objects.get(username=username)
                if user.check_password(password):
                    # SESSION DATA
                    request.session['user_id'] = user.id
                    request.session['username'] = user.username
                    request.session['rol_id'] = str(user.rol.id)  

                    if user.rol.id == 1:
                        return redirect('home')
                    elif user.rol.id == 2:
                        return redirect('AdminHome')
                    elif user.rol.id == 3:
                        return redirect('home')
                else:
                    has_error['cred_error'] = 'Las Credenciales no Coinciden'
            except Usuario.DoesNotExist:
                has_error['user_error'] = 'Usuario no Encontrado'
        return render(request, 'shared/login.html', {'errores': has_error})

    elif request.method == "GET":
        return render(request, 'shared/login.html')

# @admin_required
def RenderRegister(request):
    roles = Roles.objects.all()
    pickers = Picker.objects.all()
    if request.method == "POST":
        # USUARIO
        has_error = {}
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        username = request.POST.get('username')
        rol = request.POST.get('rol')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # DE ROLES
        telefono = request.POST.get('telefono')

        picker_select = request.POST.get('picker')

        
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
                    username=username,
                    rol=Roles.objects.get(id=rol),
                    correo= username + '@nufra.com',
                    telefono=telefono
                )
                user.set_password(password)
                user.save()




            return render(request, 'admin/views/register.html', {'roles': roles, 'pickers': pickers})
        else:
            return render(request, 'admin/views/register.html', {'roles': roles, 'pickers': pickers, 'errores': has_error})
    
    elif request.method == "GET":
        return render(request, 'admin/views/register.html', {'roles': roles, 'pickers': pickers})

# Usuario General

def agregar_a_carrito(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    cantidad = int(request.POST.get('cantidad', 1))
    
    # Aquí agregas la lógica para añadir el producto al carrito
    # Suponiendo que el carrito se guarda en la sesión o en otro modelo.

    # Por ejemplo, si el carrito es un diccionario en la sesión:
    carrito = request.session.get('carrito', {})
    if producto_id in carrito:
        carrito[producto_id] += cantidad
    else:
        carrito[producto_id] = cantidad
    
    request.session['carrito'] = carrito

    # Redirige de vuelta al catálogo o a donde sea necesario
    return redirect('Catalog')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'shared/register.html', {'form': form})

def RenderUserHome(request):
    return render(request, 'usuario/indexUser.html')

def RenderUserCatalog(request):
    if request.method == 'GET':
        # Filtros para visualizar solo las categorias con productos 
        categorias_con_productos = CategoriaProducto.objects.filter(producto__isnull=False).distinct()
        productos = Producto.objects.filter(categoria__in=categorias_con_productos)

        return render(request, 'usuario/catalog.html', {'categorias': categorias_con_productos, 'productos': productos})

def RenderAbout(request):
    return render(request, 'usuario/about.html')

def RenderFAQ(request):
    return render(request, 'usuario/faq.html')

# Admin
# @admin_required
def RenderAdminHome(request):
    return render(request, 'admin/views/indexAdmin.html')

# @admin_required
def RenderTrabajadores(request):
    return render(request, 'admin/views/trabajadores.html')

# @admin_required
def RenderReport(request):
    # FALTA CONCRETAR LOS REPORTES (QUE SE MANDA Y COMO DEPENDIENDO DE CADA TIPO)
    return render(request, 'admin/views/reportes.html')

# @admin_required
def RenderConfig(request):
    if request.method == 'GET':
        return render(request, 'admin/views/configTienda.html')


# Categorias
# @admin_required
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

# @admin_required
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

# @admin_required 
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

# @admin_required
def RenderProducto(request):
    productos = Producto.objects.all()
    if request.method == 'GET':
        return render(request, 'admin/productos/productos.html', {'productos': productos})

# @admin_required 
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
                proveedor=get_object_or_404(Proveedor, id=proveedor),
                descripcion=descripcion,
                precio_unitario=precio,
                fecha_ingreso=fecha,
                imagen=imagen
            )

            producto.save()
            return redirect('addProducto')
        else:
            return render(request, 'admin/productos/addProducto.html', {'categorias': categorias, 'proveedores': proveedores, 'errores':has_error})
  
    elif request.method == 'GET':
        return render(request, 'admin/productos/addProducto.html', {'categorias': categorias, 'proveedores': proveedores})

# @admin_required
def EditProducto(request, id):
    producto = get_object_or_404(Producto, id=id)
    categorias = CategoriaProducto.objects.all()
    proveedores = Proveedor.objects.all()

    if request.method == 'POST':
        has_error = {}

        nombre = request.POST.get('nombre')
        categoria = request.POST.get('categoria')
        proveedor = request.POST.get('proveedor')
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
        
        # Validacion Proveedor
        if proveedor == '-1':
            has_error['pro_default'] = 'El Campo Proveedor Debe ser DISTINTO al PREDETERMINADO'

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
            producto.proveedor = get_object_or_404(Proveedor, id=proveedor)
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
                'proveedores': proveedores,
                'producto': producto,
                'errores': has_error
            })
  
    elif request.method == 'GET':
        return render(request, 'admin/productos/addProducto.html', {
            'categorias': categorias,
            'proveedores': proveedores,
            'producto': producto
        })

# Manejo de Producto / Para no eliminar registros
# @admin_required
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

# @admin_required
def RenderSupHome(request):
    return render(request, 'supervisor/indexSuper.html')

# @admin_required
def RenderSupInventario(request):
    inventario = Inventario.objects.all()
    return render(request, 'supervisor/inventario.html', {'inventario': inventario})

# @admin_required
def AddInventario(request):
    productos = Producto.objects.all()
    inventario = Inventario.objects.all()
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
            return redirect('SupInvent') 
    
    elif request.method == 'GET':
        return render(request, 'supervisor/inventario/addInventario.html', {'productos': productos, 'inventario': inventario})
    
# @admin_required
def EditInventario(request):
    if request.method == 'POST':
        pass
    
    elif request.method == 'GET':
        return render(request, 'supervisor/inventario/editInventario.html')


# Vendedor
# @admin_required
def RenderVenHome(request):
    return render(request, 'vendedor/indexVendedor.html')

# @admin_required
def RenderVentas(request):
    return render(request, 'vendedor/ventas.html')
