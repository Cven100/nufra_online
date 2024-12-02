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
from .models import DetallePedido, DetalleVenta, Pedido, Usuario,Administrador , Roles, Producto, CategoriaProducto, Picker, OrdenesCompra, Venta

#DECORADORES DE SESSION
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        # rol_id se basan en los de bd
        if request.session.get('user_id') and request.session.get('rol_id') == '2':
            usuario = Usuario.objects.get(id=request.session.get('user_id'))
            if usuario.estado == 'Activo':
                return view_func(request, *args, **kwargs)
            messages.error(request, 'Usuario sin privilegios')
            logout(request)
            return redirect('Login')  # Redirige al login si esta inactivo
        return redirect('Login')  # Redirige al login si no es admin
    return wrapper

def picker_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get('user_id') and request.session.get('rol_id') == '3':  # '3' para rol de picker
            usuario = Usuario.objects.get(id=request.session.get('user_id'))
            if usuario.estado == 'Activo':
                return view_func(request, *args, **kwargs)
            messages.error(request, 'Usuario sin privilegios')
            logout(request)
            return redirect('Login')  # Redirige al login si esta inactivo
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
                        request.session['rut'] = user.rut 
                        return redirect('AdminHome')
                    elif user.rol.id == 3:
                        request.session['rut'] = user.rut 
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
    roles = Roles.objects.all().exclude(id=1)
    if request.method == "POST":
        # USUARIO
        has_error = {}
        rut_entregado = request.POST.get('rut')
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
        if Usuario.objects.filter(email=username + '@nufra.com').exists():
            has_error['duplicado'] = 'Ya Existe un Trabajador con este Correo'
        
        # VALIDACION RUT
        if rut_entregado.strip() == "":
            has_error['rut_empty'] = 'El Campo RUT no Puede Estar Vacio'

        if not has_error:
            if rol == '2':
                user = Administrador(
                    rut=rut_entregado,
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
                    rut=rut_entregado,
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
    
    carrito = request.session.get('carrito', [])
    if producto_id in carrito:
        carrito[producto_id] += cantidad
    else:
        carrito[producto_id] = cantidad
    
    request.session['carrito'] = carrito

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
    carrito = request.session.get("carro", [])
    user_id = request.session.get('user_id', None)
    categorias_generales = CategoriaProducto.objects.filter(disponible=True)
    categorias_con_productos = CategoriaProducto.objects.filter(producto__isnull=False).distinct()
    productos = Producto.objects.filter(categoria__in=categorias_con_productos)

    if request.method == 'GET': 
        return render(request, 'usuario/catalog.html', {
            'categorias': categorias_con_productos, 
            'productos': productos, 
            'carro': carrito,
            'user_id': user_id,
            'categorias_generales': categorias_generales,
            })
    
    elif request.method == 'POST':
        nombre = request.POST.get('buscador_nombre')
        cate = request.POST.get('buscador_categorias')

        categorias = CategoriaProducto.objects.all()

        if nombre:
            productos = productos.filter(nombre__icontains=nombre)

        if cate and cate != '-1':
            productos = productos.filter(categoria__id=cate)
            categorias_con_productos = categorias_con_productos.filter(id=cate)

        return render(request, 'usuario/catalog.html', {
            'categorias': categorias_con_productos, 
            'productos': productos, 
            'carro': carrito,
            'user_id': user_id,
            'categorias_generales': categorias_generales,
            })

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

# Función para vaciar el carrito y ajustar el stock (VENDER)
def VaciarCarro(request):
    carro = request.session.get('carro', [])
    if carro:
        try:
            user = Usuario.objects.get(rut=request.session.get('rut', None))
        except Usuario.DoesNotExist:
            messages.error(request, 'usuario no encontrado')
            return redirect('cart')

        venta = Venta.objects.create(
            rut_cliente=user,
            fecha=datetime.date.today(),
            total=0,
        )

        total_compra = 0

        for item in carro:
            producto = get_object_or_404(Producto, id=item['id'])
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

            orden = OrdenesCompra.objects.create(
                usuario_id= user,
                producto=producto,
                cantidad=item['cantidad'],
                estado='Aprobado'
            )

            producto.stock_actual -= item['cantidad']
            producto.save()

        venta.total = total_compra
        venta.save()

        # Vaciar el carrito después de la compra
        request.session['carro'] = []
        messages.success(request, 'Compra confirmada con exito.')
    
    else:
        messages.error(request, 'No hay productos en el carrito.')

    return redirect('cart')

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
    usuario_en_session = request.session.get('user_id')
    roles = Roles.objects.all().exclude(id=1)
    users = Usuario.objects.all()
    adm = Administrador.objects.all()
    pick = Picker.objects.all()

    if request.method == 'POST':
        nombre = request.POST.get('buscador_nombre')
        rol = request.POST.get('buscador_rol')
        disponible = request.POST.get('buscador_disponible')

        if nombre:
            users = users.filter(nombre__icontains=nombre)
        
        if rol:
            if rol != '-1':
                users = users.filter(rol__id=rol)

        if disponible:
            if disponible != '3':
                if disponible == '1':
                    disponible = 'Activo'
                elif disponible == '2':
                    disponible = 'Inactivo'
                users = users.filter(estado=disponible)
        return render(request, 'admin/views/trabajadores.html',{'users': users, 'adm': adm, 'pick': pick, 'roles': roles, 'en_session': usuario_en_session})

    return render(request, 'admin/views/trabajadores.html',{'users': users, 'adm': adm, 'pick': pick, 'roles': roles, 'en_session': usuario_en_session})

@admin_required
def EditTrabajadores(request, id):
    roles = Roles.objects.all()
    trabajador = None

    if id:
        try:
            user = Usuario.objects.get(id=id)
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')
            return redirect('AdminHome')  # Redirigir si no se encuentra el usuario
        
        if user.rol.id == 2:
            trabajador = Administrador.objects.get(usuario_ptr_id=id)
        elif user.rol.id == 3:
            trabajador = Picker.objects.get(usuario_ptr_id=id)
            
    email_part = trabajador.email.split('@')[0] if trabajador.email else ''

    if request.method == 'POST':
        has_error = {}
        rut_entregado = request.POST.get('rut')
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        username = request.POST.get('username')
        rol = request.POST.get('rol')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        telefono = request.POST.get('telefono')

        chars_restringidos_correo = [
            ' ', '..', '(', ')', '<', '>', '[', ']', ',', ';', ':', '"', '@'
        ]
        
        # Validación de nombre
        if nombre.strip() == "":
            has_error['name_empty'] = 'El Campo NOMBRE no Puede Estar Vacio'
        elif len(nombre) > 150:
            has_error['name_max_char'] = 'Se ha Superado el MAXIMO de Caracteres, MAXIMO Permitido: 150'
        else:
            nombre = nombre.title()

        # Validación de teléfono
        if telefono.strip() == "":
            has_error['telefono_empty'] = 'El Campo TELEFONO no Puede Estar Vacio'

        # Validación de apellido
        if apellido.strip() == "":
            has_error['ape_empty'] = 'El Campo Apellido no Puede Estar Vacio'
        elif len(apellido) > 150:
            has_error['ape_max_char'] = 'Se ha Superado el MAXIMO de Caracteres, MAXIMO Permitido: 150'
        else:
            apellido = apellido.title()

        # Validación de correo
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
        
        # Validación de rol
        if rol == '-1':
            has_error['rol_default'] = 'El Campo ROL Debe ser DISTINTO al PREDETERMINADO'

        # Validación de contraseñas
        if password != confirm_password:
            has_error['password_final'] = 'Las contraseñas no coinciden'

        # Validación existencia del correo (excluyendo el usuario actual)
        if Usuario.objects.filter(email=username + '@nufra.com').exclude(id=id).exists():
            has_error['duplicado'] = 'Ya Existe un Trabajador con este Correo'
        
        # Validación RUT
        if rut_entregado.strip() == "":
            has_error['rut_empty'] = 'El Campo RUT no Puede Estar Vacio'
        

        # Validar existencia de correo
        if Usuario.objects.filter(email=username + '@nufra.com').exclude(id=id).exists():
            has_error['duplicado'] = 'Ya Existe un Trabajador con este Correo'

        # Si no hay errores
        if not has_error:
            if trabajador:
                # Actualizar trabajador existente
                trabajador.rut = rut_entregado
                trabajador.nombre = nombre
                trabajador.apellido = apellido
                trabajador.telefono = telefono
                trabajador.rol = Roles.objects.get(id=rol)
                trabajador.email = username + '@nufra.com'
                
                if password:
                    trabajador.set_password(password)
                trabajador.save()
            else:
                # Crear nuevo trabajador
                user = Administrador(
                    rut=rut_entregado,
                    nombre=nombre,
                    apellido=apellido,
                    rol=Roles.objects.get(id=rol),
                    email=username + '@nufra.com',
                    estado='Activo',
                    telefono=telefono
                )
                user.set_password(password)
                user.save()

            return redirect('Trabajadores')  # Redirigir después de guardar

        else:
            return render(request, 'admin/views/register.html', {'roles': roles, 
                                                                 'errores': has_error, 
                                                                 'trabajador': trabajador, 
                                                                 'editar': True,
                                                                 'email_part': email_part,
                                                                 })

    # Si es GET, renderizar formulario
    return render(request, 'admin/views/register.html', {'roles': roles, 'trabajador': trabajador, 'email_part': email_part, 'editar': True if trabajador else False})




@admin_required 
def BlockTrabajador(request, id):
    if request.method == 'GET':
        user = Usuario.objects.get(id=id)
        if user.estado == 'Activo':
            try:
                user.estado = 'Inactivo'
                user.save()
                return redirect('Trabajadores')
            except:
                return HttpResponse(f"Error al Deshabilitar al Trabajador: {user.nombre}", status=404)
        elif user.estado == 'Inactivo':
            try:
                user.estado = 'Activo'
                user.save()
                return redirect('Trabajadores')
            except:
                return HttpResponse("Error al Habilitar al Trabajador: {}".format(user.nombre), status=404)        

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
        
        if CategoriaProducto.objects.filter(nombre=nombre).exists():
                has_error['duplicado'] = 'La categoría ya existe.'
            
        if not has_error:
            categoria = CategoriaProducto(nombre=nombre)
            categoria.save()
            return redirect('categorias')
        else:
            return render(request, 'admin/productos/categorias/categorias.html', {'categorias': categorias, 'errores':has_error})
        
    elif request.method == 'GET':
        return render(request, 'admin/productos/categorias/categorias.html', {'categorias': categorias})

@admin_required
def BuscadorCategoria(request):
    if request.method == 'POST':
        nombre = request.POST.get('buscador_nombre')
        disponible = request.POST.get('buscador_disponible')

        categorias = CategoriaProducto.objects.all()

        if nombre:
            categorias = categorias.filter(nombre__icontains=nombre.title())

        if disponible:
            if disponible != '3':
                if disponible == '1':
                    disponible = True
                elif disponible == '2':
                    disponible = False
                categorias = categorias.filter(disponible=disponible)
        
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
    categorias = CategoriaProducto.objects.filter(disponible=True)
    if request.method == 'GET':
        return render(request, 'admin/productos/productos.html', {'productos': productos, 'categorias': categorias})

    elif request.method == 'POST':
        nombre = request.POST.get('buscador_nombre')
        fecha = request.POST.get('buscador_fecha')
        categoria = request.POST.get('buscador_categoria')
        disponible = request.POST.get('buscador_disponible')

        if nombre:
            productos = productos.filter(nombre__icontains=nombre)

        if fecha:
            productos = productos.filter(fecha_ingreso=fecha)

        if categoria:
            if categoria != '-1':
                productos = productos.filter(categoria__id=categoria)

        if disponible:
            if disponible != '3':
                if disponible == '1':
                    disponible = True
                elif disponible == '2':
                    disponible = False
                productos = productos.filter(disponible=disponible)

        return render(request, 'admin/productos/productos.html', {'productos': productos, 'categorias': categorias})


@admin_required 
def AddProducto(request):
    categorias = CategoriaProducto.objects.all()
    if request.method == 'POST':
        has_error = {}

        nombre = request.POST.get('nombre')
        categoria = request.POST.get('categoria')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        pedido = request.POST.get('pedido')
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

        # Validacion Precio
        if pedido.strip() == "":
            has_error['pedido_empty'] = 'El Campo PRECIO PEDIDO NO Puede Estar Vacio'
        else:
            try:
                pedido = float(pedido)
            except ValueError:
                has_error['pedido_char_error'] = 'El PRECIO PEDIDO Debe ser un Número Válido.'
        
        # Validacion Fecha
        # if not fecha:
        #     has_error['date_empty'] = 'La FECHA NO Puede Esta VACIA'
        # else:
        #     try:
        #         fecha_valida = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()
        #         if fecha_valida > datetime.date.today():
        #             has_error['future_date'] = 'La Fecha de Ingreso NO Puede Estar en el FUTURO'
        #     except ValueError:
        #         has_error['invalid_date'] = 'Fecha Ingresada Invalida'

        # Validar Existencia
        if Producto.objects.filter(nombre=nombre).exists():
                has_error['duplicado'] = 'Producto ya existente'

        if not has_error:
            producto = Producto(
                nombre=nombre,
                categoria=get_object_or_404(CategoriaProducto, id=categoria),
                descripcion=descripcion,
                precio_unitario=precio,
                precio_pedido=pedido,
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
        pedido = request.POST.get('pedido')
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
        # if not fecha:
        #     has_error['date_empty'] = 'La FECHA NO Puede Esta VACIA'
        # else:
        #     try:
        #         fecha_valida = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()
        #         if fecha_valida > datetime.date.today():
        #             has_error['future_date'] = 'La Fecha de Ingreso NO Puede Estar en el FUTURO'
        #     except ValueError:
        #         has_error['invalid_date'] = 'Fecha Ingresada Invalida'

        # Validar Existencia (solo si el nombre ha cambiado)
        if Producto.objects.filter(nombre=nombre).exclude(id=producto.id).exists():
            has_error['duplicado'] = 'Producto ya existente'

        if not has_error:
            # Actualizar el producto
            producto.nombre = nombre
            producto.categoria = get_object_or_404(CategoriaProducto, id=categoria)
            producto.descripcion = descripcion
            producto.precio_unitario = precio
            producto.precio_pedido = pedido
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
def RenderSupInventario(request):
    if request.method == 'GET':
        carro = request.session.get('carroPedido', [])
        productos = Producto.objects.all()
        return render(request, 'admin/inventario/inventario.html', {'inventario': productos, 'carroPedido': carro})
    
    elif request.method == 'POST':
        codigo = request.POST.get('buscador')
        nombre = request.POST.get('buscador_nombre')
        stock = request.POST.get('buscador_stock')
        stock_opcion = request.POST.get('buscador_stock_opcion')
        
        carro = request.session.get('carroPedido', [])
        productos = Producto.objects.all()

        if codigo:
            productos = productos.filter(id=codigo)

        if nombre:
            productos = productos.filter(nombre__icontains=nombre)

        if stock:
            try:
                stock = int(stock)
                if stock_opcion == 'lt':
                    productos = productos.filter(stock_actual__lt=stock)
                elif stock_opcion == 'gt':
                    productos = productos.filter(stock_actual__gt=stock)
                elif stock_opcion == 'equal':
                    productos = productos.filter(stock_actual=stock)
            except ValueError:
                messages.error(request, 'Stock no Valido')

        return render(request, 'admin/inventario/inventario.html', 
                      {
                        'inventario': productos, 
                        'carroPedido': carro
                          }) 
    
@admin_required
def AddCartPedido(request, id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=id)
        cantidad = int(request.POST.get('cantidad', 1))  # Obtiene la cantidad del formulario
        carro = request.session.get('carroPedido', [])

        # Verificar si el producto ya está en el carrito y aumentar la cantidad
        for item in carro:
            if item['id'] == producto.id:
                item['cantidad'] += cantidad
                item['subtotal'] = item['cantidad'] * item['precio']
                break
        else:
            # Si el producto no está en el carrito, añadirlo con la cantidad seleccionada
            carro.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'cantidad': cantidad,
                'precio': producto.precio_pedido,
                'subtotal': producto.precio_pedido * cantidad
            })

        # Guardar el carrito en la sesión
        request.session['carroPedido'] = carro
        messages.success(request, 'Producto agregado al carrito.')
        
        # Redirigir a la página de inventario o la página que desees
        return redirect('inventario')

def RemoverCartPedido(request, id):
    carro = request.session.get('carroPedido', [])
    carro = [item for item in carro if item['id'] != id]
    request.session['carroPedido'] = carro
    messages.success(request, 'Producto eliminado del carrito.')
    return redirect('inventario')  

def CrearPedido(request):
    if request.method == 'POST':
        carro = request.session.get('carroPedido', [])
        if carro:
            # VALIDACION DE ITEM EN CARRO DESHABILITADO
            productos_invalidos = []
            for i in carro:
                try:
                    producto = Producto.objects.get(id=i['id'])
                    if not producto.disponible:
                        productos_invalidos.append(i)
                except Producto.DoesNotExist:
                    messages.error(request, f'Producto no Encontrado: {i['nombre']}')
                    return redirect('inventario')
            
            if len(productos_invalidos) > 0:
                mensaje = ''
                for invalido in productos_invalidos:
                    mensaje += invalido['nombre'] + '  '
                    RemoverCartPedido(request, invalido['id'])
                messages.error(request, f'Hay Productos no Disponibles en el Carro: {mensaje}, Se eliminaran a continuacion')
                return redirect('inventario')
            
            pedido = Pedido.objects.create(
                total_pedido = 0
            )

            valor_pedido = 0

            for item in carro:
                producto = get_object_or_404(Producto, id=item['id'])
                subtotal = item['subtotal']
                valor_pedido += subtotal
                
                # Registrar el detalle de la venta
                detalle = DetallePedido.objects.create(
                    pedido = pedido,
                    producto = producto,
                    cantidad = item['cantidad'],
                    precio_unitario = item['precio'],
                    subtotal = item['subtotal'] 
                )
                producto.stock_actual += item['cantidad']
                producto.save()

            pedido.total_pedido = valor_pedido
            pedido.save()

            # Vaciar el carrito después de la compra
            request.session['carroPedido'] = []
            messages.success(request, 'El stock ha sido actualizado.')
        else:
            messages.error(request, 'No hay productos en el carrito.')

        return redirect('inventario')

def detalleCarrito(request):
    # Obtenemos los IDs de los productos en el carrito
    idsProductos = request.session.get("carrito", [])
    # Consultamos los productos correspondientes a esos IDs
    productos = Producto.objects.filter(id__in=idsProductos)
    
    return render(request, "usuario/carrito/detalle_carrito.html", {"productos": productos})

# Vista para gestionar pedidos
@picker_required
def RenderOrdenes(request):
    # Obtener todos los pedidos (o filtrar según tus necesidades)
    ordenes = OrdenesCompra.objects.all()
    return render(request, 'picker/gestionarPedidos.html', {'ordenes': ordenes})

def CheckEstado(request, id):
    if request.method == 'POST':
        try:
            orden = OrdenesCompra.objects.get(id=id)
        except OrdenesCompra.DoesNotExist:
            messages.error(request, 'Orden no Encontrada')
            redirect('pickerHome')
        
        estado = request.POST.get('estados')

        if estado == '1':
            orden.estado = 'Aprobado'
        elif estado == '2':
            orden.estado = 'Pendiente'
        elif estado == '3':
            orden.estado = 'En Preparacion'
        elif estado == '4':
            orden.estado = 'Listo Para Envio'
        elif estado == '5':
            orden.estado = 'Enviado'
        elif estado == '6':
            orden.estado = 'Entregado'
            orden.fecha_entrega = datetime.date.today()
        elif estado == '7':
            orden.estado = 'Cancelado'
            orden.fecha_entrega = datetime.date.today()

        orden.save()
        
        return redirect('pickerHome')

# Vista para visualizar el stock de productos
def VisualizarStock(request):
    productos = Producto.objects.all()  # Obtiene todos los productos
    return render(request, "picker/visualizarStock.html", {"productos": productos})

@admin_required
def RenderVentas(request):
    if request.method == 'GET':
        ventas = Venta.objects.all()
        return render(request, 'admin/views/ventas.html', {'ventas': ventas})
    
    elif request.method == 'POST':
        nro = request.POST.get('buscador')
        rut = request.POST.get('buscador_rut')
        total = request.POST.get('buscador_total')
        fecha = request.POST.get('buscador_fecha')
        
        ventas = Venta.objects.all()

        if nro:
            ventas = ventas.filter(nro_boleta=nro)

        if rut:
            ventas = ventas.filter(rut_cliente__rut=rut)

        if total:
            ventas = ventas.filter(total=total)

        if fecha:
            ventas = ventas.filter(fecha=fecha)

        return render(request, 'admin/views/ventas.html', {'ventas': ventas}) 
    

@admin_required
def RenderDetalle(request, id):
    if request.method == 'GET':
        detalle = DetalleVenta.objects.filter(venta=id)
        if not detalle:
            messages.error(request, 'No se encontraron detalles para esta venta.')
            return redirect('ventas') 
        return render(request, 'admin/views/detalleVenta.html', {'detalle': detalle})
    
@admin_required
def RenderPedido(request):
    if request.method == 'GET':
        pedido = Pedido.objects.all()
        return render(request, 'admin/views/pedidos.html', {'pedido': pedido})
    
    elif request.method == 'POST':
        nro = request.POST.get('buscador')
        total = request.POST.get('buscador_total')
        fecha = request.POST.get('buscador_fecha')
        
        pedidos = Pedido.objects.all()

        if nro:
            pedidos = pedidos.filter(nro_pedido=nro)

        if total:
            pedidos = pedidos.filter(total_pedido=total)

        if fecha:
            pedidos = pedidos.filter(fecha=fecha) 

        return render(request, 'admin/views/pedidos.html', {'pedido': pedidos}) 
    
@admin_required
def RenderDetallePedido(request, id):
    if request.method == 'GET':
        detalle = DetallePedido.objects.filter(pedido=id)
        if not detalle:
            messages.error(request, 'No se encontraron detalles para este pedido.')
            return redirect('pedidos') 
        return render(request, 'admin/views/detallePedidos.html', {'detalle': detalle})
        