/**
 * API Service - Maneja todas las comunicaciones con el backend
 * Reemplaza localStorage con peticiones HTTP al servidor
 */

const API = {
    baseURL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
        ? "http://127.0.0.1:8000"
        : "https://fintrack-backend.onrender.com",
    
    // Obtener username actual
    getUsername() {
        return sessionStorage.getItem('username');
    },

    // Helper para hacer peticiones
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const config = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail?.message || data.message || 'Error en la petición');
            }
            
            return data;
        } catch (error) {
            console.error(`Error en ${endpoint}:`, error);
            throw error;
        }
    },

    // Helper para FormData
    async requestFormData(endpoint, formData) {
        const url = `${this.baseURL}${endpoint}`;
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail?.message || data.message || 'Error en la petición');
            }
            
            return data;
        } catch (error) {
            console.error(`Error en ${endpoint}:`, error);
            throw error;
        }
    },

    // ============== USUARIO / PERFIL ==============
    async getUser() {
        const username = this.getUsername();
        if (!username) throw new Error('Usuario no autenticado');
        
        const data = await this.request(`/api/user?username=${encodeURIComponent(username)}`);
        return data;
    },

    // ============== CLIENTES ==============
    async getClientes() {
        const username = this.getUsername();
        if (!username) throw new Error('Usuario no autenticado');
        
        const data = await this.request(`/api/clientes?username=${encodeURIComponent(username)}`);
        return data.clientes || [];
    },

    async createCliente(cliente) {
        const username = this.getUsername();
        if (!username) throw new Error('Usuario no autenticado');
        
        const formData = new FormData();
        formData.append('username', username);
        formData.append('nombre', cliente.nombre);
        formData.append('cedula', cliente.cedula || '');
        formData.append('obra', cliente.obra || '');
        formData.append('estado', cliente.estado || 'activo');
        formData.append('fecha', cliente.fecha || '');
        
        return await this.requestFormData('/api/clientes', formData);
    },

    async updateCliente(id, cliente) {
        const username = this.getUsername();
        if (!username) throw new Error('Usuario no autenticado');
        
        const formData = new FormData();
        formData.append('username', username);
        formData.append('nombre', cliente.nombre);
        formData.append('cedula', cliente.cedula || '');
        formData.append('obra', cliente.obra || '');
        formData.append('estado', cliente.estado || 'activo');
        formData.append('fecha', cliente.fecha || '');
        
        const response = await fetch(`${this.baseURL}/api/clientes/${id}`, {
            method: 'PUT',
            body: formData
        });
        
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail?.message || data.message || 'Error al actualizar');
        }
        return data;
    },

    async deleteCliente(id) {
        const username = this.getUsername();
        if (!username) throw new Error('Usuario no autenticado');
        
        return await this.request(`/api/clientes/${id}?username=${encodeURIComponent(username)}`, {
            method: 'DELETE'
        });
    },

    // ============== OBRAS ==============
    async getObras() {
        const username = this.getUsername();
        if (!username) throw new Error('Usuario no autenticado');
        
        const data = await this.request(`/api/obras?username=${encodeURIComponent(username)}`);
        return data.obras || [];
    },

    async createObra(obra) {
        const username = this.getUsername();
        if (!username) throw new Error('Usuario no autenticado');
        
        const formData = new FormData();
        formData.append('username', username);
        formData.append('nombre', obra.nombre);
        formData.append('ubicacion', obra.ubicacion || '');
        formData.append('estado', obra.estado || 'activa');
        
        return await this.requestFormData('/api/obras', formData);
    },

    async updateObra(id, obra) {
        const username = this.getUsername();
        if (!username) throw new Error('Usuario no autenticado');
        
        const formData = new FormData();
        formData.append('username', username);
        formData.append('nombre', obra.nombre);
        formData.append('ubicacion', obra.ubicacion || '');
        formData.append('estado', obra.estado || 'activa');
        
        const response = await fetch(`${this.baseURL}/api/obras/${id}`, {
            method: 'PUT',
            body: formData
        });
        
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail?.message || data.message || 'Error al actualizar');
        }
        return data;
    },

    async deleteObra(id) {
        const username = this.getUsername();
        if (!username) throw new Error('Usuario no autenticado');
        
        return await this.request(`/api/obras/${id}?username=${encodeURIComponent(username)}`, {
            method: 'DELETE'
        });
    },

    // ============== PRODUCTOS ==============
    async getProductos() {
        const username = this.getUsername();
        if (!username) throw new Error('Usuario no autenticado');
        
        const data = await this.request(`/api/productos?username=${encodeURIComponent(username)}`);
        return data.productos || [];
    },

    async createProducto(producto) {
        const username = this.getUsername();
        if (!username) throw new Error('Usuario no autenticado');
        
        const formData = new FormData();
        formData.append('username', username);
        formData.append('nombre', producto.nombre);
        formData.append('precio', producto.precio || 0);
        
        return await this.requestFormData('/api/productos', formData);
    },

    async updateProducto(id, producto) {
        const username = this.getUsername();
        if (!username) throw new Error('Usuario no autenticado');
        
        const formData = new FormData();
        formData.append('username', username);
        formData.append('nombre', producto.nombre);
        formData.append('precio', producto.precio || 0);
        
        const response = await fetch(`${this.baseURL}/api/productos/${id}`, {
            method: 'PUT',
            body: formData
        });
        
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail?.message || data.message || 'Error al actualizar');
        }
        return data;
    },

    async deleteProducto(id) {
        const username = this.getUsername();
        if (!username) throw new Error('Usuario no autenticado');
        
        return await this.request(`/api/productos/${id}?username=${encodeURIComponent(username)}`, {
            method: 'DELETE'
        });
    },

    // ============== REGISTROS ==============
    async getRegistros(filters = {}) {
        const username = this.getUsername();
        if (!username) throw new Error('Usuario no autenticado');
        
        let url = `/api/registros?username=${encodeURIComponent(username)}`;
        
        if (filters.obra) {
            url += `&obra=${encodeURIComponent(filters.obra)}`;
        }
        if (filters.fecha_inicio) {
            url += `&fecha_inicio=${filters.fecha_inicio}`;
        }
        if (filters.fecha_fin) {
            url += `&fecha_fin=${filters.fecha_fin}`;
        }
        
        const data = await this.request(url);
        return data.registros || [];
    },

    async createRegistro(registro) {
        const username = this.getUsername();
        if (!username) throw new Error('Usuario no autenticado');
        
        const payload = {
            username,
            fecha: registro.fecha || null,
            obra: registro.obra || null,
            totalCantidad: registro.totalCantidad || 0,
            totalCobrar: registro.totalCobrar || 0,
            totalPagado: registro.totalPagado || 0,
            status: registro.status || 'pendiente',
            clientesAdicionales: registro.clientesAdicionales || [],
            detalles: registro.detalles || []
        };
        
        return await this.request('/api/registros', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
    },

    async updateRegistro(id, registro) {
        const username = this.getUsername();
        if (!username) throw new Error('Usuario no autenticado');
        
        const payload = {
            username,
            fecha: registro.fecha || null,
            obra: registro.obra || null,
            totalCantidad: registro.totalCantidad || 0,
            totalCobrar: registro.totalCobrar || 0,
            totalPagado: registro.totalPagado || 0,
            status: registro.status || 'pendiente',
            clientesAdicionales: registro.clientesAdicionales || [],
            detalles: registro.detalles || []
        };
        
        return await this.request(`/api/registros/${id}`, {
            method: 'PUT',
            body: JSON.stringify(payload)
        });
    },

    async deleteRegistro(id) {
        const username = this.getUsername();
        if (!username) throw new Error('Usuario no autenticado');
        
        return await this.request(`/api/registros/${id}?username=${encodeURIComponent(username)}`, {
            method: 'DELETE'
        });
    },

    // ============== REPORTES ==============
    async getReportes(filters = {}) {
        const username = this.getUsername();
        if (!username) throw new Error('Usuario no autenticado');
        
        let url = `/api/reportes?username=${encodeURIComponent(username)}`;
        
        if (filters.obra) {
            url += `&obra=${encodeURIComponent(filters.obra)}`;
        }
        if (filters.fecha_inicio) {
            url += `&fecha_inicio=${filters.fecha_inicio}`;
        }
        if (filters.fecha_fin) {
            url += `&fecha_fin=${filters.fecha_fin}`;
        }
        
        return await this.request(url);
    }
};

// Exportar para uso global
window.API = API;
