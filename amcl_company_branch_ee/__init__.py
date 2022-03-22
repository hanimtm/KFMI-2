# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import SUPERUSER_ID, api

from . import models
from . import report
from . import wizard


def post_init_check(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    user_ids = env['res.users'].search([])
    group_id = env.ref('amcl_company_branch_ee.group_multi_branches')
    group_id.write({'users': [(6, 0, user_ids.ids)]})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
