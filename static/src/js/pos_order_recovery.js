/** @odoo-module **/

import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

patch(TicketScreen.prototype, {
    setup() {
        super.setup();
        this.floatingButtonContainer = null;
    },

    /**
     * Sobrescribe selectOrder para mostrar/ocultar botón flotante
     */
    selectOrder(order) {
        super.selectOrder(order);
        
        // Si hay un ticket seleccionado, mostrar botón flotante
        if (order) {
            this.showFloatingEditButton(order);
        } else {
            this.hideFloatingEditButton();
        }
    },

    /**
     * Muestra botón flotante "Editar Pago"
     */
    showFloatingEditButton(order) {
        // Solo mostrar si el ticket está finalizado y es de la sesión actual
        if (!order.finalized || order.session_id?.id !== this.pos.session.id) {
            this.hideFloatingEditButton();
            return;
        }

        // Si ya existe, ocultarlo primero
        this.hideFloatingEditButton();

        // Crear contenedor del botón flotante
        this.floatingButtonContainer = document.createElement('div');
        this.floatingButtonContainer.className = 'cs-floating-edit-payment-btn';
        this.floatingButtonContainer.innerHTML = `
            <button class="btn btn-primary" title="Editar pago del ticket">
                <i class="fa fa-edit"></i> Editar Pago
            </button>
        `;

        // Agregar estilos CSS
        this.floatingButtonContainer.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            border-radius: 5px;
        `;

        // Agregar evento click
        const button = this.floatingButtonContainer.querySelector('button');
        button.addEventListener('click', () => this.editPayment(order));

        // Agregar al DOM
        document.body.appendChild(this.floatingButtonContainer);
    },

    /**
     * Oculta botón flotante
     */
    hideFloatingEditButton() {
        if (this.floatingButtonContainer) {
            this.floatingButtonContainer.remove();
            this.floatingButtonContainer = null;
        }
    },

    /**
     * Método: editPayment()
     * Permite editar el pago de un pedido cerrado
     * Elimina los pagos y abre PaymentScreen
     */
    async editPayment(order) {
        // Mostrar diálogo de confirmación
        const confirmed = await new Promise((resolve) => {
            this.dialog.add(ConfirmationDialog, {
                title: _t("Editar pago"),
                body: _t(
                    `¿Editar pago del pedido ${order.name}?\n\n` +
                    `Se eliminarán todos los pagos actuales y podrá ` +
                    `configurar el pago nuevamente en la pantalla de pago.`
                ),
                confirm: () => resolve(true),
                cancel: () => resolve(false),
            });
        });

        if (!confirmed) {
            return;
        }

        try {
            // Llamar al backend para editar pago
            const orderId = await this.env.services.rpc({
                model: "pos.order",
                method: "action_edit_payment",
                args: [[order.id]],
            });

            // Si éxito, esperar a que se sincronice
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Recargar órdenes
            await this.pos.db.load_orders();
            
            // Obtener el pedido actualizado
            const updatedOrder = this.pos.db.get_order(orderId);

            if (updatedOrder) {
                // Establecer como orden actual
                this.env.posStore.setCurrentOrder(updatedOrder);

                // Navegar a PaymentScreen para editar pago
                this.pos.showScreen("PaymentScreen");

                // Ocultar botón flotante
                this.hideFloatingEditButton();

                // Mostrar mensaje
                this.dialog.add(AlertDialog, {
                    title: _t("Editar pago"),
                    body: _t(
                        `El pago del pedido ${updatedOrder.name} ha sido eliminado.\n\n` +
                        `Configure el nuevo pago en la pantalla de pago.`
                    ),
                });
            }
        } catch (error) {
            // Mostrar error
            this.dialog.add(AlertDialog, {
                title: _t("Error al editar pago"),
                body: _t(error.data?.message || error.message || "Error desconocido"),
            });
        }
    },
});

