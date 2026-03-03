{
    'name': 'Customer Credit Control',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Mijozlarga kredit limit belgilash',
    'depends': ['sale', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/credit_limit_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
}
