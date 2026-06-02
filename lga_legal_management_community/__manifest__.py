{
    'name': 'Legal Case Management - International',
    'version': '18.0.1.0.0',
    'category': 'Legal/Legal',
    'summary': 'International Legal Case Management System',
    'description': """
        Complete law firm management solution
        =================================================

        Main features:
        ----------------------------
        * Legal case management with workflow
        * Hearing scheduling with calendar
        * Deadline and due date tracking with alerts
        * Time and fee management
        * Complete document management
        * Secure customer portal
        * GDPR compliance
        * Multi-country support (Europe, America, Asia, Africa)
        * Complete REST API
        * Multi-language (8 languages supported)

        Configuration:
        --------------
        1. Install the module
        2. Go to Legal → Configuration → Configure my country
        3. Select your country
        4. Legal parameters are automatically adapted

        Multi-country support:
        -------------------
        - France (Civil Law)
        - Germany (Civil Law)
        - United Kingdom (Common Law)
        - United States (Common Law)
        - Japan (Civil Law)
        - Brazil (Civil Law)
        - China (Civil Law)

        GDPR features:
        ---------------------
        * Customer consent
        * Right to be forgotten
        * Data portability
        * Audit log
        * Automated customer requests

        Customer portal:
        ---------------
        * Secure access via email/token
        * Case consultation
        * Hearing viewing
        * Deadline tracking
        * Document download
        * Consent management
    """,
    'author': 'EandA',
    'website': 'https://www.eanda.tech',
    'category': 'LGA/Legal',
    'depends': [
        'base',
        'contacts',
        'calendar',
        'project',
        'mail',
        
    ],
    'data': [
         # Sécurité
        'security/legal_security.xml',
        'security/ir.model.access.csv',
        
        # Données de base
        'data/sequences.xml',
        'data/upgrade_urls.xml',
        'data/upgrade_email_templates.xml',
        
        # Vues
        'views/legal_views.xml',
        'views/legal_menu.xml',

        
        'views/legal_upgrade_buttons.xml',
        'wizards/legal_upgrade_wizard.xml',
    ],
    'demo': [
        'demo/legal_demo.xml',
    ],
    'controllers': [
        
    ],
    'assets': {
        'web.assets_backend': [
            'lga_legal_management_community/static/src/js/upgrade.js',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'images': ['static/description/icon.png'],
    'icon': '/static/description/icon.png',
    'external_dependencies': {
        'python': ['requests', 'pytz', 'pycountry'],
    },
    'price': 0.00,
    'currency': 'USD',
    'live_test_url': 'https://demo.eanda.tech/odoo/lga',
    'support': 'support@eanda.tech',
}