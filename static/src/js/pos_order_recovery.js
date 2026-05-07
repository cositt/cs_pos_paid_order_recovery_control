/** @odoo-module **/

import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(TicketScreen.prototype, {
    /**
     * Método patched: recoverOrder()
     * Permite recuperar un pedido pagado dentro de la misma sesión
     */
    async recoverOrder(order) {
        // Mostrar diálogo de confirmación
        const confirmed = await new Promise((resolve) => {
            this.dialog.add(ConfirmationDialog, {
                title: _t("Confirmar recuperación"),
                body: _t(
                    `¿Recuperar pedido ${order.name}?\n\n` +
                    `Se revertirá el pago y se creará un nuevo pedido editable ` +
                    `con los mismos productos para que pueda modificarlo.`
                ),
                confirm: () => resolve(true),
                cancel: () => resolve(false),
            });
        });

        if (!confirmed) {
            return;
        }

        try {
            // Llamar al backend para recuperar el pedido
            const newOrderId = await this.env.services.rpc({
                model: "pos.order",
                method: "action_recover_order",
                args: [[order.id]],
            });

            // Si éxito, esperar a que se sincronice la BD
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Recargar órdenes del servidor
            await this.pos.db.load_orders();
            
            // Obtener el nuevo pedido
            const newOrder = this.pos.db.get_order(newOrderId);

            if (newOrder) {
                // Establecer como orden actual
                this.env.posStore.setCurrentOrder(newOrder);

                // Navegar a ProductScreen para editar
                this.pos.showScreen("ProductScreen");

                // Mostrar mensaje de éxito
                this.dialog.add(AlertDialog, {
                    title: _t("Pedido recuperado"),
                    body: _t(
                        `El pedido ${newOrder.name} ha sido recuperado.\n\n` +
                        `Puede modificar los productos y el método de pago.`
                    ),
                });
            }
        } catch (error) {
            // Mostrar error
            this.dialog.add(AlertDialog, {
                title: _t("Error al recuperar pedido"),
                body: _t(error.data?.message || error.message || "Error desconocido"),
            });
        }
    },
});
