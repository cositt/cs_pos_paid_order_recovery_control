# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PosOrder(models.Model):
    _inherit = "pos.order"

    def action_edit_payment(self):
        """
        Permite editar el pago de un pedido cerrado:
        1. Valida que es la misma sesión y sesión está abierta
        2. Elimina todos los pagos del pedido
        3. Marca el pedido como "draft" para poder pagar nuevamente
        4. Retorna el orden para abrirlo en PaymentScreen
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
        if not self.finalized:
            raise ValidationError(_("El pedido no está cerrado/finalizado."))

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

        return self.id
