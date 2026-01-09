/**
 * Script para migrar datos de localStorage del usuario demo a Panchita's Catering
 * Ejecutar en la consola del navegador (F12) en el dashboard
 * 
 * Pasos:
 * 1. Inicia sesión como demo (para ver los datos)
 * 2. Abre la consola (F12)
 * 3. Copia y pega este código en la consola
 * 4. Presiona Enter
 * 5. Verifica que el script diga "✅ Migración completada"
 * 6. Cierra sesión
 * 7. Inicia sesión como Panchita's Catering
 * 8. Deberías ver todos los datos
 */

(function migrateUserData() {
    // Datos actuales sin prefijo (del demo)
    const demoCclientes = localStorage.getItem('clientes');
    const demoObras = localStorage.getItem('obras');
    const demoRegistros = localStorage.getItem('registros');
    const demoProductos = localStorage.getItem('productos');
    
    // Nuevo usuario
    const newUsername = "Panchita's Catering";
    const storagePrefix = `${newUsername}_`;
    
    console.log('📋 Iniciando migración de datos...');
    console.log(`   Desde: demo`);
    console.log(`   Hacia: ${newUsername}`);
    
    let count = 0;
    
    if (demoCclientes) {
        localStorage.setItem(storagePrefix + 'clientes', demoCclientes);
        console.log('✅ Clientes migrados');
        count++;
    }
    
    if (demoObras) {
        localStorage.setItem(storagePrefix + 'obras', demoObras);
        console.log('✅ Obras migradas');
        count++;
    }
    
    if (demoRegistros) {
        localStorage.setItem(storagePrefix + 'registros', demoRegistros);
        console.log('✅ Registros migrados');
        count++;
    }
    
    if (demoProductos) {
        localStorage.setItem(storagePrefix + 'productos', demoProductos);
        console.log('✅ Productos migrados');
        count++;
    }
    
    if (count > 0) {
        console.log(`\n✅ Migración completada! ${count} tipos de datos transferidos.`);
        console.log('\n📌 Próximos pasos:');
        console.log('   1. Cierra sesión');
        console.log('   2. Inicia sesión con: Panchita\'s Catering');
        console.log('   3. Deberías ver todos tus datos (10 obras, registros del 1-19 dic)');
    } else {
        console.log('⚠️ No se encontraron datos para migrar');
    }
})();
