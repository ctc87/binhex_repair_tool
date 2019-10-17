{
    'name': 'Repair modification for stock operations',
    'category': 'Add stock operations in repair tool in Odoo to repair external products.',
    'summary': 'Add stock operations in repair tool in Odoo to repair external products.',
    'price': 30,
    'currency': 'EUR',
    'version': '1.0.0',
    'license': 'AGPL-3',
    'author':  'Binhex Sysems',
    'website': 'https://binhex.es',
    'depends': [
        'repair', 'stock', 'web_digital_sign'
        ],
    'data': [
        'data/data.xml',
        'views/repair.xml',
        'reports/repair_reports.xml',
        'reports/repair_templates_repair_order.xml',
        ],
    'installable': True,
}
