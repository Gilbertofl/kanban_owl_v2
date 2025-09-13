{
    'name': 'Mi Kanban Básico',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'summary': 'Kanban básico con OWL v2',
    'description': 'Un módulo simple con modelo backend y componente OWL v2 para Kanban',
    'depends': ['web', 'first_application'],
    'data': [
        'security/ir.model.access.csv',
        'views/vistas.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'mi_kanban_basico/static/src/js/*.js',
            'mi_kanban_basico/static/src/xml/*.xml',
            'first_application/static/src/js/animated_svg.js',
            'first_application/static/src/xml/animated_svg.xml',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}