/** @odoo-module **/

import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(TicketScreen.prototype, {
    /**
     * Intercepta la carga de un pedido como editable.
     * Bloquea si el pedido está pagado (finalized) y pertenece a una sesión distinta a la actual.
     * Consulta, reimpresión y devolución NO pasan por aquí y no se ven afectadas.
     */
    async setOrder(order) {
        if (order?.finalized && order.session_id?.id !== this.pos.session.id) {
            this.dialog.add(AlertDialog, {
                title: _t("Acceso restringido"),
                body: _t("Este ticket no pertenece a la caja actual y no puede modificarse."),
            });
            return;
        }
        return super.setOrder(order);
    },
});
