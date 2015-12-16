# -*- coding: utf-8 -*-
##############################################################################
# Author: waveyeung<waveyeung@gmail.com>
#         http://github.com/waveyeung
##############################################################################

{
    'name' : 'Triple Validation on Purchases',
    'version' : '1.1',
    'category': 'Purchase Management',
    'depends' : ['base','purchase'],
    'author' : 'waveyeung@gmail.com',
    'description': """
Triple-validation for purchases .
=========================================================

This module modifies the purchase workflow in order to validate purchases.
    """,
    'website': 'http://github.com/waveyeung',
    'data': [
        'purchase_triple_validation_workflow.xml',
        'purchase_triple_validation_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
