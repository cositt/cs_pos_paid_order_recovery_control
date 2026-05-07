# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PosOrder(models.Model):
    _inherit = "pos.order"

    original_order_id = fields.Many2one(
        "pos.order",
        string="Pedido original",
        readonly=True,
        help="Pedido original del cual fue recuperado este pedido",
    )
    is_recovery = fields.Boolean(
        string="Es recuperación",
        default=False,
        help="Indica si este pedido fue creado como recuperación",
    )

    def action_recover_order(self):
        """
        Recupera un pedido pagado:
        1. Valida que es la misma sesión y sesión está abierta
        2. Revierte los pagos del pedido original
        3. Marca el pedido original como cancelado
        4. Crea un nuevo pedido en draft con los mismos ítems
        5. Retorna el nuevo pedido
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
                _("La sesión de caja está cerrada. No se puede recuperar pedidos.")
            )

        # Validación 3: ¿Orden finalizada?
        if not self.finalized:
            raise ValidationError(_("El pedido no está cerrado/finalizado."))

        # Validación 4: ¿Hay pagos?
        if not self.payment_ids:
            raise ValidationError(_("El pedido no tiene pagos registrados."))

        # PASO 1: Revertir pagos
        self._reverse_payments()

        # PASO 2: Crear nuevo pedido
        new_order = self._create_recovery_order()

        # PASO 3: Marcar original como cancelado/recuperado
        self.write(
            {
                "state": "done",
                "is_recovery": True,
            }
        )

        return new_order.id

    def _reverse_payments(self):
        """
        Revierte todos los pagos del pedido.
        Crea un registro de reversión para auditoría.
        """
        for payment in self.payment_ids:
            # En Odoo, los pagos se pueden anular marcándolos como "reversed"
            # o creando un pago negativo (reversal payment)
            # Opción: crear pago negativo (más limpio para auditoría)

            # Buscar si ya existe un reversal de este pago
            existing_reversal = self.env["pos.payment"].search(
                [
                    ("order_id", "=", self.id),
                    ("amount", "=", -payment.amount),
                    ("payment_method_id", "=", payment.payment_method_id.id),
                ],
                limit=1,
            )

            if not existing_reversal:
                # Crear pago negativo (reversal)
                self.env["pos.payment"].create(
                    {
                        "order_id": self.id,
                        "payment_method_id": payment.payment_method_id.id,
                        "amount": -payment.amount,
                        "payment_date": fields.Datetime.now(),
                    }
                )

    def _create_recovery_order(self):
        """
        Crea un nuevo pedido en estado draft con los mismos ítems del original.
        """
        # Preparar valores del nuevo pedido
        new_order_values = {
            "session_id": self.session_id.id,
            "partner_id": self.partner_id.id if self.partner_id else False,
            "user_id": self.user_id.id,
            "original_order_id": self.id,
            "is_recovery": True,
        }

        # Crear nuevo pedido
        new_order = self.create(new_order_values)

        # Copiar líneas de productos
        for line in self.lines:
            line.copy(
                {
                    "order_id": new_order.id,
                }
            )

        return new_order
