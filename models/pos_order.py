# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PosOrder(models.Model):
    _inherit = "pos.order"

    # Campo que controla la visibilidad del botón
    can_recover_payment = fields.Boolean(
        string="Puede Recuperar Pago",
        compute="_compute_can_recover_payment",
        store=False
    )

    def _compute_can_recover_payment(self):
        """
        Determina si el pedido puede recuperar pago.
        Solo si está en estado 'done' y la sesión está abierta.
        """
        for order in self:
            can_recover = False
            try:
                if order.state == 'done':
                    current_session = self.env['pos.session'].search(
                        [('state', '=', 'in_progress')], limit=1
                    )
                    if current_session and order.session_id.id == current_session.id:
                        if order.session_id.state == 'in_progress':
                            can_recover = True
            except:
                pass
            order.can_recover_payment = can_recover

    def action_edit_payment(self):
        """
        Permite editar el pago de un pedido cerrado:
        1. Valida que es la misma sesión y sesión está abierta
        2. Elimina todos los pagos del pedido
        3. Marca el pedido como "draft" para poder pagar nuevamente
        """
        self.ensure_one()

        # Validación 1: ¿Es la sesión actual?
        current_session = self.env["pos.session"].search(
            [("state", "=", "in_progress")], limit=1
        )
        if not current_session or self.session_id.id != current_session.id:
            raise ValidationError(
                _("Este pedido no pertenece a la sesión de caja actual.")
            )

        # Validación 2: ¿Sesión abierta?
        if self.session_id.state != "in_progress":
            raise ValidationError(
                _("La sesión de caja está cerrada. No se puede editar pagos.")
            )

        # Validación 3: ¿Orden finalizada?
        if self.state != 'done':
            raise ValidationError(_("El pedido no está finalizado."))

        # Validación 4: ¿Hay pagos?
        if not self.payment_ids:
            raise ValidationError(_("El pedido no tiene pagos registrados."))

        # PASO 1: Eliminar todos los pagos
        self.payment_ids.unlink()

        # PASO 2: Marcar como draft para permitir nuevo pago
        self.write(
            {
                "state": "draft",
            }
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Éxito'),
                'message': _('El pago ha sido recuperado. El ticket está listo para re-pagarse.'),
                'type': 'success',
                'sticky': False,
            }
        }
