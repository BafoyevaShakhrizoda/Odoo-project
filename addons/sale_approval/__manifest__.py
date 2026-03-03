{
    'name': 'Sale Approval',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Katta summali buyurtmalarni tasdiqlash',
    'depends': ['sale'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/approval_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
}
