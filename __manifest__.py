{
    'name': 'Monitor de Salud de Stock - Tablero Kanban OWL v2',
    'version': '17.0.1.0.0',
    'summary': 'Tablero interactivo en tiempo real con OWL v2 para el monitoreo de existencias y reabastecimiento rápido',
    'description': """
Monitor de Salud de Stock con OWL v2
====================================
Este módulo proporciona un tablero reactivo tipo Kanban para el control visual de inventario:
- Clasificación de productos en 3 niveles de alerta (Agotado, Bajo Mínimo y Óptimo).
- Búsqueda y filtrado en tiempo real sin recargar la página.
- Generación de órdenes reales de recepción de inventario (stock.picking) con un solo clic.
- Actualización en tiempo real mediante el Bus de WebSockets de Odoo sin necesidad de polling.
- Arquitectura moderna de frontend con el framework OWL v2 de Odoo 17.
    """,
    'category': 'Inventory/Inventory',
    'author': 'Tu Nombre',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'stock',
        'bus',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_health_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'kanban_owl_v2/static/src/scss/*.scss',
            'kanban_owl_v2/static/src/components/*.js',
            'kanban_owl_v2/static/src/components/*.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
