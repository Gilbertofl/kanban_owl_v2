# Monitor de Salud de Stock - Tablero Kanban en OWL v2 (Odoo 17)

Un módulo interactivo y reactivo desarrollado para **Odoo 17** utilizando **OWL v2 (Odoo Web Library)** y **Python**, diseñado para la supervisión visual del inventario y la automatización de órdenes de reabastecimiento en tiempo real.

---

## 🎯 Características Principales

* **Tablero Reactivo tipo Kanban:** Clasificación automática de productos en tres columnas visuales:
  * 🔴 **Sin Stock (Agotado):** Productos con existencia igual o menor a cero.
  * 🟡 **Bajo Mínimo:** Productos por debajo del stock de seguridad configurado.
  * 🟢 **Óptimo:** Productos con existencias estables.
* **Búsqueda Instantánea en Memoria:** Filtro reactivo en el cliente (`t-model`) por nombre o código de referencia sin llamadas innecesarias al servidor.
* **Reabastecimiento Real con un Clic:** Creación directa de órdenes de recepción de almacén (`stock.picking`) mediante llamadas RPC al backend, registrando notas de trazabilidad en el chatter.
* **Diseño Limpio y Adaptativo:** Contenedores flexbox con barras de desplazamiento independientes por columna y tarjetas interactivas de producto.
* **Integración Nativa:** Se integra con el catálogo de productos y el flujo estándar de inventario de Odoo 17 (`stock`).

---

## 🛠️ Arquitectura Técnica y Tecnologías

### Frontend (OWL v2 en JavaScript)
* **Componentes Funcionales:** Clase `StockKanbanBoard` que hereda de `Component` de `@odoo/owl`.
* **Hooks Reactivos:**
  * `useState`: Manejo centralizado del estado reactivo (listado de productos, filtros activos y control de peticiones en proceso).
  * `onWillStart`: Carga asíncrona inicial de datos antes del renderizado de la interfaz.
* **Servicios Estándar de Odoo 17 (`useService`):**
  * `orm`: Consultas asíncronas (`searchRead` y `call`) directas hacia los modelos de base de datos sin controladores HTTP intermedios.
  * `notification`: Alertas flotantes (toast) informando el resultado de las operaciones al usuario.
  * `action`: Navegación directa hacia las fichas detalladas de los productos.
* **Plantillas XML (`qweb`):** Uso de directivas reactivas `t-if`, `t-else`, `t-foreach`, `t-model` y `t-on-click`.
* **Registro de Acciones:** Registrado en `registry.category("actions")` para ser lanzado a pantalla completa como `ir.actions.client`.

### Backend (Python - Odoo 17)
* **Extensión de Modelo (`product.template`):**
  * `x_min_security_stock`: Campo configurable para definir el umbral mínimo de seguridad.
  * `x_stock_health_status`: Campo calculado (`compute='_compute_stock_health_status'`) que categoriza dinámicamente el estado del producto.
  * `x_replenish_requested`: Bandera para control visual de solicitudes previas.
* **Lógica de Negocio (`action_replenish_quick`):**
  * Método transaccional que crea y confirma una orden de entrada real (`stock.picking` con líneas `stock.move`) en el almacén del usuario, asignando origen y dejando constancia en el historial.

---

## 📂 Estructura del Módulo

```text
kanban_owl_v2/
├── __init__.py                                 # Inicializador del módulo
├── __manifest__.py                             # Manifiesto con dependencias y assets de Odoo 17
├── security/
│   └── ir.model.access.csv                     # Reglas de permisos de acceso (ACLs)
├── models/
│   ├── __init__.py
│   └── product_template.py                     # Extensión del modelo y método de reabastecimiento
├── views/
│   └── stock_health_views.xml                  # Vista formulario, Client Action y menús
├── static/
│   └── src/
│       ├── components/
│       │   ├── stock_kanban_board.js           # Lógica del componente OWL v2 (Hooks, Estado y RPC)
│       │   └── stock_kanban_board.xml          # Plantilla XML interactiva
│       └── scss/
│           └── stock_kanban_board.scss         # Estilos visuales del tablero
└── README.md                                   # Documentación técnica del proyecto
```
---
## 📋 Autor y Licencia
* **Licencia:** LGPL-3
* **Compatibilidad:** Odoo 17.0 Community / Enterprise
