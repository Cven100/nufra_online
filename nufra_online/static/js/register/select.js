document.addEventListener('DOMContentLoaded', function() {
    const rolSelect = document.getElementById('rol');
    const adminFields = document.getElementById('adminFields');
    const vendedorFields = document.getElementById('vendedorFields');
    const supervisorFields = document.getElementById('supervisorFields');
    const equipoFields = document.getElementById('equipoFields');

    rolSelect.addEventListener('change', function() {
        const selectedRol = rolSelect.value;

        // Ocultar todos los campos
        adminFields.style.display = 'none';
        vendedorFields.style.display = 'none';
        supervisorFields.style.display = 'none';
        equipoFields.style.display = 'none'; // Ocultar equipo por defecto

        // Mostrar campos correspondientes al rol seleccionado
        if (selectedRol === '1') { // Admin
            adminFields.style.display = 'block';
        } else if (selectedRol === '2') { // Vendedor
            vendedorFields.style.display = 'block';
        } else if (selectedRol === '3') { // Supervisor
            supervisorFields.style.display = 'block';
            equipoFields.style.display = 'block'; // Mostrar campo de equipo
        }
    });
});