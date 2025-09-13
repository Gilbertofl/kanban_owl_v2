from odoo import models, fields, api

class MiModelo(models.Model):
    _name = 'mi.modelo'
    _description = 'Mi Modelo Básico'

    name = fields.Char(string='Nombre')
    image = fields.Binary(string='Imagen')
    descripcion = fields.Text(string='Descripción')
    contador_caracteres = fields.Integer(
        string='Caracteres usados',
        compute='_compute_contador_caracteres',
        store=True
    )
    max_caracteres = fields.Integer(
        string='Limite de caracteres',
        default=255
    )

    @api.depends('descripcion')
    def _compute_contador_caracteres(self):
        for record in self:
            if record.descripcion:
                record.contador_caracteres = len(record.descripcion)
            else:
                record.contador_caracteres = 0