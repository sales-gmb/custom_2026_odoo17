{
    'name': 'Exchange Rate Management. Manage Exchange Rates in Sales, Purchase, Customer Invoice, Vendor Bills, Journal Entries, and Payments',
    'version': '17.0.1.0.0',
    'summary': 'Manage exchange rates from Sales, Purchase, Invoices, Bills, Journal Entries and Payments. The resulting journal entries use this custom exchange rate.',
    'description': 'Manage exchange rates from Sales, Purchase, Invoices, Bills, Journal Entries and Payments. The resulting journal entries use this custom exchange rate for debits and credits.',
    'author': 'SIMI Technologies',
    'depends': ['account', 'sale', 'purchase'],
    'data': [
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'images': ['static/description/images/invil.png'],
}
