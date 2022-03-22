from odoo import api, fields, models


class ManufacturingOrder(models.Model):
    _inherit = "mrp.production"

    def action_draft(self):
        self.move_raw_ids.write({'is_done':False})
        # self.move_raw_ids = False
        self.move_finished_ids = False
        self.write({'state': 'draft'})
        return True

    def action_confirm(self):

        self._check_company()
        for production in self:
            production._onchange_move_raw()
            production._onchange_move_finished()
            if production.bom_id:
                production.consumption = production.bom_id.consumption
            if not production.move_raw_ids:
                raise UserError(_("Add some materials to consume before marking this MO as to do."))
            # In case of Serial number tracking, force the UoM to the UoM of product
            if production.product_tracking == 'serial' and production.product_uom_id != production.product_id.uom_id:
                production.write({
                    'product_qty': production.product_uom_id._compute_quantity(production.product_qty, production.product_id.uom_id),
                    'product_uom_id': production.product_id.uom_id
                })
                for move_finish in production.move_finished_ids.filtered(lambda m: m.product_id == production.product_id):
                    move_finish.write({
                        'product_uom_qty': move_finish.product_uom._compute_quantity(move_finish.product_uom_qty, move_finish.product_id.uom_id),
                        'product_uom': move_finish.product_id.uom_id
                    })
            production.move_raw_ids._adjust_procure_method()
            (production.move_raw_ids | production.move_finished_ids)._action_confirm()
            production.workorder_ids._action_confirm()
            # run scheduler for moves forecasted to not have enough in stock
            production.move_raw_ids._trigger_scheduler()
        return True