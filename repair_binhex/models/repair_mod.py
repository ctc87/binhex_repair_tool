# Copyright 2018 Apruzzese Francesco <f.apruzzese@apuliasoftware.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
"""

	BBBBBBBBBBBBBBBBB     iiii                   hhhhhhh
	B::::::::::::::::B   i::::i                  h:::::h
	B::::::BBBBBB:::::B   iiii                   h:::::h
	BB:::::B     B:::::B                         h:::::h
	  B::::B     B:::::Biiiiiiinnnn  nnnnnnnn    h::::h hhhhh           eeeeeeeeeeee  xxxxxxx      xxxxxxx
	  B::::B     B:::::Bi:::::in:::nn::::::::nn  h::::hh:::::hhh      ee::::::::::::ee x:::::x    x:::::x
	  B::::BBBBBB:::::B  i::::in::::::::::::::nn h::::::::::::::hh   e::::::eeeee:::::eex:::::x  x:::::x
	  B:::::::::::::BB   i::::inn:::::::::::::::nh:::::::hhh::::::h e::::::e     e:::::e x:::::xx:::::x
	  B::::BBBBBB:::::B  i::::i  n:::::nnnn:::::nh::::::h   h::::::he:::::::eeeee::::::e  x::::::::::x
	  B::::B     B:::::B i::::i  n::::n    n::::nh:::::h     h:::::he:::::::::::::::::e    x::::::::x
	  B::::B     B:::::B i::::i  n::::n    n::::nh:::::h     h:::::he::::::eeeeeeeeeee     x::::::::x
	  B::::B     B:::::B i::::i  n::::n    n::::nh:::::h     h:::::he:::::::e             x::::::::::x
	BB:::::BBBBBB::::::Bi::::::i n::::n    n::::nh:::::h     h:::::he::::::::e           x:::::xx:::::x
	B:::::::::::::::::B i::::::i n::::n    n::::nh:::::h     h:::::h e::::::::eeeeeeee  x:::::x  x:::::x
	B::::::::::::::::B  i::::::i n::::n    n::::nh:::::h     h:::::h  ee:::::::::::::e x:::::x    x:::::x
	BBBBBBBBBBBBBBBBB   iiiiiiii nnnnnn    nnnnnnhhhhhhh     hhhhhhh    eeeeeeeeeeeeeexxxxxxx      xxxxxxx

		@Author: Binhex Systems.
		@descrption:This file contains the models.
"""

from odoo import fields, models, api, exceptions, _
import logging
from odoo.tools import float_compare
from odoo.addons import decimal_precision as dp


_logger = logging.getLogger(__name__)
"""

    ########  ######## ########     ###    #### ########  ########  #### ##    ## ##     ## ######## ##     ## ##     ##  #######  ########  
    ##     ## ##       ##     ##   ## ##    ##  ##     ## ##     ##  ##  ###   ## ##     ## ##        ##   ##  ###   ### ##     ## ##     ## 
    ##     ## ##       ##     ##  ##   ##   ##  ##     ## ##     ##  ##  ####  ## ##     ## ##         ## ##   #### #### ##     ## ##     ## 
    ########  ######   ########  ##     ##  ##  ########  ########   ##  ## ## ## ######### ######      ###    ## ### ## ##     ## ##     ## 
    ##   ##   ##       ##        #########  ##  ##   ##   ##     ##  ##  ##  #### ##     ## ##         ## ##   ##     ## ##     ## ##     ## 
    ##    ##  ##       ##        ##     ##  ##  ##    ##  ##     ##  ##  ##   ### ##     ## ##        ##   ##  ##     ## ##     ## ##     ## 
    ##     ## ######## ##        ##     ## #### ##     ## ########  #### ##    ## ##     ## ######## ##     ## ##     ##  #######  ########  
        
        
    @Author: Binhex Systems.
    @descrption:This class change the repair module to repair external products.

"""
class RepairBinhexMod(models.Model):
    _inherit = 'repair.order'


    @api.model
    def _default_stock_location(self):
        """
            Get default location defined in /data/data.xml.
            @returns: default location
		"""
        warehouse =  self.env.ref('binhex_repair_tool.repair_location').id
        _logger.info("DEBUG almacen " + str(warehouse))
        if warehouse:
            return warehouse
        return False
    
    partner_id = fields.Many2one(
        'res.partner', 'Customer',
        reuqired=True,
        index=True, states={'confirmed': [('readonly', True)]},
        help='Choose partner for whom the order will be invoiced and delivered. You can find a partner by its Name, TIN, Email or Internal Reference.'
    )
    signature = fields.Binary(string="Signature") 
    
    picking_ids = fields.Many2many(
        'stock.picking', string='Pickings', states={'confirmed': [('readonly', True)]},
        help='This is the stock pickng for the repair movement. There are in and out.'
    )
    
    picking_notes = fields.Text('Stock picking Notes')

    picking_order_count = fields.Integer("Number of picking", default=0)

    operations = fields.One2many(
        'repair.line', 'repair_id', 'Parts',
        copy=True, readonly=True, 
        states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]})
        
    fees_lines = fields.One2many(
        'repair.fee', 'repair_id', 'Operations',
        copy=True, readonly=True, 
        states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]})

    location_id = fields.Many2one(
        'stock.location', 'Location',
        default=_default_stock_location,
        index=True, readonly=True, required=True,
        help="This is the location where the product to repair is located.",
        states={'draft': [('readonly', False)], 'confirmed': [('readonly', True)]})

    date_in = fields.Datetime('Date In', required=False, readonly=False, select=True)

    @api.onchange('product_id')
    def onchange_product_id_storable(self):
        """
            check the type of the product needs storable product.
		"""
        if self.product_id:
            if not self.product_id.type == 'product':
                raise exceptions.except_orm(_('ERROR'), _('The product has to be storable'))

    @api.onchange('signature')
    def onchange_signature(self):
        """
            Change signature in stock picking.
		"""
        if self.signature:
            if self.picking_ids:
                for p in self.picking_ids:
                    p.write({'signature':self.signature})

    def action_validate(self):
        """
            Make up the repair and create the entrance stock picking.
            @returns: Action if the entrace its not created yet.
		"""
        self.ensure_one()
        self.create_stock_picking('Reparation in')
        self.date_in = fields.datetime.now()
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        available_qty_owner = self.env['stock.quant']._get_available_quantity(self.product_id, self.location_id, self.lot_id, owner_id=self.partner_id, strict=True)
        available_qty_noown = self.env['stock.quant']._get_available_quantity(self.product_id, self.location_id, self.lot_id, strict=True)
        a = self.location_id.read()
        for available_qty in [available_qty_owner, available_qty_noown]:
            if float_compare(available_qty, self.product_qty, precision_digits=precision) >= 0:
                return self.action_repair_confirm()
        else:
            return {
                'name': _('Insufficient Quantity'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.warn.insufficient.qty.repair',
                'view_id': self.env.ref('repair.stock_warn_insufficient_qty_repair_form_view').id,
                'type': 'ir.actions.act_window',
                'context': {
                    'default_product_id': self.product_id.id,
                    'default_location_id': self.location_id.id,
                    'default_repair_id': self.id
                    },
                'target': 'new'
            }

    @api.multi
    def action_repair_cancel(self):
        """
            Make up the repair and create the entrance stock picking.
            @returns: self instance values with the changes.
		"""
        val = super(RepairBinhexMod, self).action_repair_cancel()
        self.create_stock_picking('Reparation out')
        return val

    @api.multi
    def action_repair_end(self):
        """
            Writes repair order state to 'To be invoiced' if invoice method is
            After repair else state is set to 'Ready'.
            @return: True
        """
        if self.filtered(lambda repair: repair.state != 'under_repair'):
            raise UserError(_("Repair must be under repair in order to end reparation."))
        for repair in self:
            repair.write({'repaired': True})
            vals = {'state': 'done'}
            vals['move_id'] = repair.create_stock_picking('Reparation out').id
            if not repair.invoiced and repair.invoice_method == 'after_repair':
                vals['state'] = '2binvoiced'
            repair.write(vals)
        return True

    def create_stock_picking(self, operation):
        """
            Create the stock picking in or out.
            @param operation: In or out operation 
            returns: created stock move.
		"""
        operation_type = self.env['stock.picking.type'].search([('name', 'like', operation)])
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        owner_id = False
        available_qty_owner = self.env['stock.quant']._get_available_quantity(self.product_id, self.location_id, self.lot_id, owner_id=self.partner_id, strict=True)
        if float_compare(available_qty_owner, self.product_qty, precision_digits=precision) >= 0:
            owner_id = self.partner_id.id
        vals = {
            'signature' : self.signature,
            'partner_id' : self.partner_id.id,
            'picking_type_id' : operation_type.id,
            'location_id' : operation_type.default_location_src_id.id,
            'location_dest_id' : operation_type.default_location_dest_id.id,
            'origin' : self.name,
            'move_type' : 'one',
            'note' : self.picking_notes

        }
        pick = self.env['stock.picking'].create(vals)
        move = self.env['stock.move'].create ({
                'picking_id' : pick.id,
                'name': self.name,
                'product_id': self.product_id.id,
                'product_uom': self.product_uom.id or self.product_id.uom_id.id,
                'product_uom_qty': self.product_qty,
                'partner_id': self.address_id.id,
                'location_id': operation_type.default_location_src_id.id,
                'location_dest_id': operation_type.default_location_dest_id.id,
                'repair_id': self.id,
                'origin': self.name,
                
        })
        pick.action_confirm()
        pick.action_assign()
        self.env['stock.move.line'].search([('move_id', '=',  move.id)]).write({
                'product_id': self.product_id.id,
                'lot_id': self.lot_id.id, 
                'product_uom_qty': self.product_qty,  # bypass reservation here
                'product_uom_id': self.product_uom.id or self.product_id.uom_id.id,
                'qty_done': self.product_qty,
                'package_id': False,
                'result_package_id': False,
                'owner_id': owner_id,
                'location_id': operation_type.default_location_src_id.id, #TODO: owner stuff
                'location_dest_id': operation_type.default_location_dest_id.id,
        })
        pick.button_validate()
        self.picking_order_count = self.picking_order_count + 1
        self.write({'picking_ids': [(4, pick.id, 0)]})
        return move

    @api.multi
    def open_tree_view(self):
        """
            Open stock picking tree view.
            returns: Action of the tree stock piking.
		"""
        tree_id = self.env.ref('stock.vpicktree').id
        form_id = self.env.ref('stock.view_picking_form').id
        domain = [('id', 'in', self.picking_ids.ids)]
        return {
            "target": "current",
            'type': 'ir.actions.act_window',
            'name': _('Pickings from reparation'),
            'view_type': 'form',
            'view_mode': 'pivot',
            "views": [
                (tree_id, "tree"),
                (form_id, 'form'),
            ],
            'res_model': 'stock.picking',
            "domain" : domain
        }

    @api.multi
    def print_repair_label(self):
        return self.env.ref('binhex_repair_tool.action_report_repair_label').report_action(self)


class SyockPinkingBinhexMod(models.Model):
    _inherit = 'stock.picking'
    
    signature = fields.Binary(string="Signature") 
