{
    'name': 'Control Recuperación Tickets Pagados TPV',
    'version': '19.0.2.0.0',
    'category': 'Point of Sale',
    'summary': 'Recupera tickets pagados: anula pago, crea nuevo editable con mismos productos',
    'author': 'Cositt Technology',
    'depends': ['point_of_sale'],
    'data': [],
    'assets': {
        'point_of_sale._assets_pos': [
            'cs_pos_paid_order_recovery_control/static/src/js/pos_order_recovery.js',
            'cs_pos_paid_order_recovery_control/static/src/xml/ticket_screen_recovery.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
