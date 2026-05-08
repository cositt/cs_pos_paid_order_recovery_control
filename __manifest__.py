{
    'name': 'Control Recuperación Tickets Pagados TPV',
    'version': '19.0.6.0.0',
    'category': 'Point of Sale',
    'summary': 'Recupera tickets pagados: anula pago, vuelven a draft para poder editarlos',
    'author': 'Cositt Technology',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_order_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'cs_pos_paid_order_recovery_control/static/src/js/recover_payment.js',
            'cs_pos_paid_order_recovery_control/static/src/xml/recover_payment.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
