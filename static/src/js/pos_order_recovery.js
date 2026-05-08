/** @odoo-module **/

import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(TicketScreen.prototype, {
    /**
     * Sobrescribe selectOrder para interceptar click en ticket y mostrar modal si está pagado
     */
    selectOrder(order) {
        if (order && order.finalized && order.session_id?.id === this.pos.session.id) {
            // El ticket está pagado y es de la sesión actual
            // Mostrar modal preguntando si quiere editarlo
            this.showEditTicketModal(order);
            return;  // No ejecutar el selectOrder original
        }
        
        // Si no está pagado, comportamiento normal
        return super.selectOrder(order);
    },

    /**
     * Muestra modal preguntando si quiere editar el ticket pagado
     */
    showEditTicketModal(order) {
        this.dialog.add(ConfirmationDialog, {
            title: _t("Editar ticket"),
            body: _t(
                `El ticket ${order.name} está pagado.\n\n` +
                `¿Deseas editarlo? Se realizará una devolución automática ` +
                `y podrás modificar el pedido y el pago.`
            ),
            confirm: () => this.editTicketPayment(order),
            cancel: () => {
                // Deseleccionar el ticket
                this.pos.selectedOrder = null;
            },
        });
    },

    /**
     * Edita el pago del ticket (devolución + cambio a draft)
     */
    async editTicketPayment(order) {
        try {
            // Llamar al backend para editar pago
            const orderId = await this.env.services.rpc({
                model: "pos.order",
                method: "action_edit_payment",
                args: [[order.id]],
            });

            // Esperar sincronización
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Recargar órdenes
            await this.pos.db.load_orders();
            
            // Obtener el pedido actualizado
            const updatedOrder = this.pos.db.get_order(orderId);

            if (updatedOrder) {
                // Establecer como orden actual
                this.env.posStore.setCurrentOrder(updatedOrder);

                // Mostrar mensaje de éxito
                this.dialog.add(AlertDialog, {
                    title: _t("Ticket editando"),
                    body: _t(
                        `El pago del ticket ${updatedOrder.name} ha sido devuelto.\n\n` +
                        `Ahora puedes modificar el pedido (items, cantidad, etc).`
                    ),
                });
            }
        } catch (error) {
            // Mostrar error
            this.dialog.add(AlertDialog, {
                title: _t("Error al editar ticket"),
                body: _t(error.data?.message || error.message || "Error desconocido"),
            });
        }
    },
});



