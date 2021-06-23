{
    'name': 'PagaDirect Payment Acquirer',
    'category': 'Accounting/Payment Acquirers',
    'summary': 'Payment Acquirer: PagaDirect Implementation',
    'depends': ['payment'],
    'data': [
        'views/assets.xml',
        'views/payment_pagadirect_templates.xml',
        'data/payment_acquirer_data.xml',
        'views/payment_views.xml',
    ],
    'post_init_hook': 'create_missing_journal_for_acquirers',
    'uninstall_hook': 'uninstall_hook',
}
