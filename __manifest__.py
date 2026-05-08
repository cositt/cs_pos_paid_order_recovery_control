{
    'name': 'Control Recuperación Tickets Pagados TPV',
    'version': '19.0.3.0.0',
    'category': 'Point of Sale',
    'summary': 'Recupera tickets pagados: anula pago, vuelven a draft para poder editarlos',
    'author': 'Cositt Technology',
    'depends': ['point_of_sale'],
    'data': [
        'data/data.xml',
        'views/pos_order_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'assets': {},
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
