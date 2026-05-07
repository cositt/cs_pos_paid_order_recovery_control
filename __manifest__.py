{
    'name': 'Control Recuperación Tickets Pagados TPV',
    'version': '19.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Bloquea la carga/modificación de tickets pagados que no pertenezcan a la sesión TPV actual',
    'author': 'Cositt Technology',
    'depends': ['point_of_sale'],
    'assets': {
        'point_of_sale._assets_pos': [
            'cs_pos_paid_order_recovery_control/static/src/js/paid_order_recovery_control.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
