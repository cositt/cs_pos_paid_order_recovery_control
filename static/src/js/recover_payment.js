import { patch } from "@web/core/utils/patch";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";

patch(TicketScreen.prototype, {
    get canRecoverPayment() {
        const order = this.getSelectedOrder();
        return order?.finalized && order?.state === "paid";
    },

    async recoverPayment() {
        const order = this.getSelectedOrder();
        if (!order) return;

        try {
            // Llamar al backend: crea devolución + nuevo pedido draft sin mesa
            const result = await this.env.services.orm.call(
                "pos.order",
                "action_edit_payment",
                [[order.id]]
            );

            if (result && result.new_order_id) {
                // Esperar a que el POS sincronice el nuevo pedido desde el backend
                await new Promise((resolve) => setTimeout(resolve, 1500));

                // Buscar el nuevo pedido en los modelos del POS
                const newOrder = this.pos.models["pos.order"].find(
                    (o) => o.id === result.new_order_id
                );

                if (newOrder) {
                    // Cargar el pedido y navegar a él automáticamente
                    this.pos.setOrder(newOrder);
                    this.pos.navigateToOrderScreen(newOrder);
                    return;
                }
            }

            // Fallback si no encontró el pedido tras sincronizar
            this.env.services.notification.add(
                "Pedido recuperado. Búscalo en la lista de Pedidos.",
                { type: "success" }
            );
            this.pos.showScreen("ProductScreen");

        } catch (error) {
            this.env.services.notification.add(
                error.data?.message || "Error al recuperar el pago",
                { type: "danger" }
            );
        }
    },
});
