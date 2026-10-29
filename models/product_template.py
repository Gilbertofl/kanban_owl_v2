# -*- coding: utf-8 -*-
# Módulo que extiende la funcionalidad de productos para el tablero Kanban OWL

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Stock mínimo de seguridad configurado por el usuario
    x_min_security_stock = fields.Float(
        string='Stock Mínimo de Seguridad',
        default=10.0,
        help='Cantidad mínima recomendada antes de emitir una alerta'
    )

    # Estado visual calculado automáticamente según las existencias
    x_stock_health_status = fields.Selection(
        selection=[
            ('critical', 'Sin Stock'),
            ('warning', 'Bajo Mínimo'),
            ('optimal', 'Óptimo'),
        ],
        string='Estado de Salud de Stock',
        compute='_compute_stock_health_status',
        help='Clasificación automática para organizar las columnas del tablero Kanban'
    )

    # Marca para identificar si ya se envió una solicitud de reabastecimiento
    x_replenish_requested = fields.Boolean(
        string='Reabastecimiento Solicitado',
        default=False,
        help='Indica si el producto tiene una solicitud en curso'
    )

    @api.depends('qty_available', 'x_min_security_stock')
    def _compute_stock_health_status(self):
        """Calcula el estado del producto comparando la cantidad disponible con el stock mínimo."""
        for product in self:
            available = product.qty_available
            min_stock = product.x_min_security_stock or 0.0

            if available <= 0:
                product.x_stock_health_status = 'critical'
            elif available < min_stock:
                product.x_stock_health_status = 'warning'
            else:
                product.x_stock_health_status = 'optimal'

    def write(self, vals):
        """Envía notificación por el Bus si se modifican campos relevantes para el tablero."""
        res = super(ProductTemplate, self).write(vals)
        fields_to_check = {'x_min_security_stock', 'x_replenish_requested', 'name', 'default_code'}
        if any(f in vals for f in fields_to_check):
            self._notify_stock_health_update()
        return res

    def _notify_stock_health_update(self):
        """Publica un mensaje en el Bus de Odoo para actualizar las vistas OWL en vivo."""
        channel = 'stock_health_channel'
        self.env['bus.bus']._sendone(channel, 'stock_updated', {'timestamp': fields.Datetime.now().isoformat()})

    def action_replenish_quick(self):
        """
        Crea una orden real de movimiento de inventario (recepción interna o ajuste)
        para reabastecer el producto desde la interfaz de OWL.
        """
        self.ensure_one()

        # Obtenemos la variante de producto principal
        variant = self.product_variant_id
        if not variant:
            raise UserError(_('El producto no tiene una variante válida configurada.'))

        # Obtenemos el almacén y las ubicaciones principales
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
        if not warehouse:
            raise UserError(_('No se encontró un almacén configurado para la empresa actual.'))

        # Ubicación de destino (ubicación de existencias del almacén)
        dest_location = warehouse.lot_stock_id

        # Ubicación origen (ubicación de proveedores de la empresa)
        supplier_location = self.env.ref('stock.stock_location_suppliers', raise_if_not_found=False)
        if not supplier_location:
            supplier_location = self.env['stock.location'].search([('usage', '=', 'supplier')], limit=1)

        # Tipo de operación de recepción para el almacén
        picking_type = warehouse.in_type_id

        # Cantidad sugerida a reabastecer: alcanzar el stock de seguridad + margen
        target_qty = (self.x_min_security_stock or 10.0) * 2.0
        qty_to_order = max(target_qty - self.qty_available, self.x_min_security_stock or 10.0)

        # 1. Crear el albarán/orden de recepción en el sistema de inventario
        picking_vals = {
            'picking_type_id': picking_type.id if picking_type else False,
            'location_id': supplier_location.id if supplier_location else self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': dest_location.id,
            'origin': _('Reabastecimiento rápido desde Tablero OWL'),
            'move_ids_without_package': [(0, 0, {
                'name': _('Reabastecimiento de %s') % self.name,
                'product_id': variant.id,
                'product_uom_qty': qty_to_order,
                'product_uom': self.uom_id.id,
                'location_id': supplier_location.id if supplier_location else self.env.ref('stock.stock_location_stock').id,
                'location_dest_id': dest_location.id,
            })],
        }

        picking = self.env['stock.picking'].create(picking_vals)

        # 2. Confirmar la orden para dejarla lista en el flujo de inventario
        picking.action_confirm()

        # Marcamos el producto con solicitud activa
        self.write({'x_replenish_requested': True})

        # Notificamos al Bus para que todos los clientes OWL vean el cambio
        self._notify_stock_health_update()

        # Publicamos un mensaje informativo en el historial del producto
        if hasattr(self, 'message_post'):
            self.message_post(
                body=_(
                    'Se generó una orden de recepción de inventario (<b><a href="#" data-oe-model="stock.picking" data-oe-id="%s">%s</a></b>) '
                    'por <b>%s %s</b> solicitada desde el Tablero Kanban OWL.'
                ) % (picking.id, picking.name, qty_to_order, self.uom_id.name),
                subtype_xmlid='mail.mt_note'
            )

        return {
            'status': 'success',
            'picking_id': picking.id,
            'picking_name': picking.name,
            'qty_ordered': qty_to_order,
            'product_name': self.name,
            'message': _('Se creó la orden de recepción %s por %s unidades.') % (picking.name, qty_to_order)
        }


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model_create_multi
    def create(self, vals_list):
        records = super(StockQuant, self).create(vals_list)
        self.env['bus.bus']._sendone('stock_health_channel', 'stock_updated', {'action': 'quant_created'})
        return records

    def write(self, vals):
        res = super(StockQuant, self).write(vals)
        if 'quantity' in vals or 'inventory_quantity' in vals:
            self.env['bus.bus']._sendone('stock_health_channel', 'stock_updated', {'action': 'quant_updated'})
        return res
