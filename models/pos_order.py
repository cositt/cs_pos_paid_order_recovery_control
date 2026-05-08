# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PosOrder(models.Model):
    _inherit = "pos.order"

    def action_edit_payment(self):
        """
        Flujo de recuperación de ticket:
        1. Crea una devolución total automática del pedido pagado y la valida
        2. Crea un nuevo pedido draft SIN MESA con los mismos artículos
        3. Retorna el ID del nuevo pedido para que el frontend navegue a él
        """
        self.ensure_one()

        # Validación 1: ¿Sesión activa?
        current_session = self.env["pos.session"].search(
            [("state", "in", ["in_progress", "opened"])], limit=1
        )
        if not current_session:
            raise ValidationError(_("No hay ninguna sesión de caja abierta."))

        # Validación 2: ¿Orden pagada?
        if self.state != "paid":
            raise ValidationError(_("El pedido no está en estado pagado."))

        # Validación 3: ¿Hay líneas?
        if not self.lines:
            raise ValidationError(_("El pedido no tiene artículos."))

        # ── PASO 1: Devolución total automática ───────────────────────────
        refund_order = self._refund()

        payment_method = current_session.config_id.payment_method_ids[:1]
        if not payment_method:
            raise ValidationError(
                _("No hay métodos de pago disponibles en la sesión actual.")
            )

        self.env["pos.payment"].create({
            "pos_order_id": refund_order.id,
            "payment_method_id": payment_method.id,
            "amount": refund_order.amount_total,
        })
        refund_order._compute_prices()
        refund_order.action_pos_order_paid()

        # ── PASO 2: Nuevo pedido draft SIN MESA ───────────────────────────
        new_order = self.env["pos.order"].create({
            "session_id": current_session.id,
            "config_id": self.config_id.id,
            "state": "draft",
            "user_id": self.user_id.id,
            "company_id": self.company_id.id,
            "partner_id": self.partner_id.id if self.partner_id else False,
            "pricelist_id": self.pricelist_id.id if self.pricelist_id else False,
            "fiscal_position_id": self.fiscal_position_id.id if self.fiscal_position_id else False,
            "preset_id": False,
            "floating_order_name": _("RECUP. %s", self.name),
            "source": self.source or False,
            "general_customer_note": self.general_customer_note or False,
            # Campos numéricos obligatorios, _compute_prices los recalculará
            "amount_tax": 0,
            "amount_total": 0,
            "amount_paid": 0,
            "amount_return": 0,
        })

        # Copiar solo las líneas de artículos
        for line in self.lines:
            self.env["pos.order.line"].create({
                "order_id": new_order.id,
                "product_id": line.product_id.id,
                "full_product_name": line.full_product_name,
                "qty": line.qty,
                "price_unit": line.price_unit,
                "discount": line.discount,
                "customer_note": line.customer_note if hasattr(line, "customer_note") else False,
                "tax_ids": [(6, 0, line.tax_ids.ids)],
                "price_subtotal": 0,
                "price_subtotal_incl": 0,
            })

        new_order._compute_prices()

        # Notificar al POS frontend para que sincronice el nuevo pedido
        new_order.config_id.notify_synchronisation(current_session.id, 0)

        # Retornar el ID para que el JS navegue automáticamente
        return {"new_order_id": new_order.id}
