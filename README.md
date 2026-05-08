# Paid Order Recovery Control - Edit Payment (Control Recuperación Tickets Pagados TPV)

**Version:** 19.0.3.0.0  
**Author:** Cositt Technology  
**License:** LGPL-3  
**Category:** Point of Sale

## Overview

This module enables administrators and staff to quickly recover and edit payment information for finalized (paid) orders within the same cash register session. With a single click on a "🔙 Recuperar Pago" button in the Order form, users can remove incorrect payments and reconfigure them with different payment methods, splits, or amounts.

Perfect for restaurants where payment errors or adjustments are common and need fast resolution.

## Features

### Payment Recovery & Editing

- **One-Click Payment Recovery:** "🔙 Recuperar Pago" button visible on closed orders
- **Automatic Payment Removal:** Deletes all payment lines from the order
- **Draft Status:** Converts order back to draft status for re-payment
- **Same Session Requirement:** Orders can only be edited within the same cash register session
- **Closed Session Protection:** Prevents editing once cash register session is closed

### Access & Usage

- **Access Point:** Odoo web interface > Point of Sale > Orders (pos.order form view)
- **Button Visibility:** Only appears on finalized orders (state = 'done', finalized = True)
- **User-Friendly:** Clear messaging with error validation

### Flexibility After Recovery

Once an order is recovered (payment removed, back to draft):
- ✅ Edit order items if needed
- ✅ Add/remove products
- ✅ Create payment splits (e.g., 25€ cash + 25€ card)
- ✅ Change payment method (cash, card, bank transfer, etc.)
- ✅ Adjust amounts

### Safety & Compliance

- ✅ Session-based isolation (only current session)
- ✅ Automatic validation of order status
- ✅ Prevention of editing closed sessions
- ✅ Clear error messages for users
- ✅ Order state properly managed

## Installation

1. Place the module in your Odoo addons directory:
   ```bash
   cp -r cs_pos_paid_order_recovery_control /path/to/odoo/addons/
   ```

2. Update the module list:
   - Navigate to **Apps** > **Update Apps List**

3. Install the module:
   - Search and click **Install** on "Control Recuperación Tickets Pagados TPV"

## Usage Guide

### Step 1: Access Orders
1. Go to **Point of Sale** > **Orders** (in Odoo web interface)
2. Find a finalized order (status = "Pagado" / "Paid")

### Step 2: Click "Recuperar Pago" Button
1. Open the order form
2. Click the **"🔙 Recuperar Pago"** button (appears in the header, only for paid orders)
3. The system will:
   - Validate the session is current and open
   - Remove all payment records
   - Change order state to draft
   - Display a success message

### Step 3: Re-Configure Payment
1. Order is now editable and in draft status
2. Edit items if needed (add/remove products)
3. Click **"Guardar"** to save changes
4. The order is ready for re-payment in POS

### Step 4: Re-Payment in POS
1. Open POS application
2. The recovered order appears as a draft order
3. Complete the payment with correct method/amount/split
4. Order is finalized again

## Technical Details

### Backend Model (`models/pos_order.py`)

**Method:** `action_edit_payment()`

**Validations:**
- Order belongs to current cash register session
- Session is open (state = 'in_progress')
- Order is finalized (finalized = True)
- Order has payment records

**Operations:**
- Deletes all `pos.payment` records linked to the order
- Writes order state to 'draft'
- Returns order ID

**Error Handling:**
- Raises `ValidationError` with clear message if:
  - Order not in current session
  - Session is closed
  - Order not finalized
  - No payments exist

### UI Component (`views/pos_order_views.xml`)

**Button Definition:**
```xml
<button
    name="action_edit_payment"
    type="object"
    string="🔙 Recuperar Pago"
    class="oe_highlight"
    attrs="{'invisible': ['|', ('finalized', '=', False), ('state', '!=', 'done')]}"/>
```

**Visibility Rules:**
- Shows only when `finalized = True` AND `state = 'done'`
- Hidden for draft, pending, or invoiced orders

### Module Manifest (`__manifest__.py`)

```python
{
    'name': 'Control Recuperación Tickets Pagados TPV',
    'version': '19.0.3.0.0',
    'category': 'Point of Sale',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_order_views.xml',
    ],
    'installable': True,
}
```

## Use Cases

### Use Case 1: Customer Paid Wrong Amount
**Scenario:** Customer paid €50 instead of €75
- Click "🔙 Recuperar Pago"
- Order returns to draft
- Correct the payment amount to €75
- Finalize

### Use Case 2: Wrong Payment Method
**Scenario:** Order marked as card payment, but customer paid cash
- Click "🔙 Recuperar Pago"
- Order returns to draft with no payment
- Add cash payment
- Finalize

### Use Case 3: Split Payment Required
**Scenario:** Customer wants to split €100 order between 2 cards
- Click "🔙 Recuperar Pago"
- Order returns to draft
- Add first card payment: €50
- Add second card payment: €50
- Finalize

### Use Case 4: Additional Items Forgotten
**Scenario:** Customer remembered they wanted an extra coffee, but order already paid
- Click "🔙 Recuperar Pago"
- Order returns to draft
- Add coffee to items
- Adjust total payment
- Finalize

## Limitations & Important Notes

### ❌ Cannot Edit

- **Closed Sessions:** Orders from closed cash register sessions cannot be recovered
- **Invoiced Orders:** Orders that have been invoiced cannot be edited
- **Different Sessions:** Can only edit orders from the current/active session

### ✅ Can Edit

- Items (add/remove products)
- Payment methods
- Payment amounts
- Payment splits

## Error Messages & Solutions

### Error: "Este pedido no pertenece a la sesión de caja actual"
**Translation:** "This order does not belong to the current cash register session"
**Solution:** The order was placed in a different session. Switch to that session or wait for the session to reopen.

### Error: "La sesión de caja está cerrada"
**Translation:** "The cash register session is closed"
**Solution:** The session has been closed. You can only edit orders in active sessions.

### Error: "El pedido no está cerrado/finalizado"
**Translation:** "The order is not closed/finalized"
**Solution:** Only finalized orders can be recovered. This order may already be in draft status.

### Error: "El pedido no tiene pagos registrados"
**Translation:** "The order has no payment records"
**Solution:** This order doesn't have any payments to remove. Check the order status.

## Dependencies

- **Odoo 19.0+**
- **Module:** point_of_sale

## Compatibility

- ✅ Odoo 19.0 Enterprise
- ✅ Odoo 19.0 Community
- ✅ Multi-session capable
- ✅ Works with all payment methods

## Support & Troubleshooting

### Button Not Visible

1. **Verify Order Status:**
   - Check that order state = 'done'
   - Check that finalized = True
   - In Odoo menu: Point of Sale > Orders > (open order) > check state field

2. **Verify Module Installation:**
   - Go to Apps > Search "Recuperación"
   - Module should show as "Installed"

3. **Clear Cache:**
   - Browser: Clear cache and hard refresh (Ctrl+Shift+R)
   - Odoo: Restart server `docker compose restart odoo`

### Action Not Working

1. **Check Session Status:**
   - Point of Sale > Cash Register Sessions
   - Find current session, verify state = "En progreso" (In Progress)

2. **Check Order Status:**
   - Order must be finalized (status = "Pagado")
   - Order must have payment records

3. **Check Logs:**
   ```bash
   docker compose logs odoo 2>&1 | grep "action_edit_payment" | tail -20
   ```

4. **If Still Failing:**
   - Restart Odoo: `docker compose restart odoo`
   - Wait 10 seconds for module reload
   - Try again

## Change Log

### v19.0.3.0.0 (Current)
- ✅ Switched from POS UI patching (fragile) to web form button (stable)
- ✅ Button appears in order form view
- ✅ Removed broken JavaScript patches
- ✅ Simplified and proven implementation

### v19.0.2.0.0
- Initial implementation with JavaScript patching (deprecated)

## License

LGPL-3 - See LICENSE file for details

## Author

**Cositt Technology**  
Specialized in POS and restaurant management solutions for Odoo

---

**Last Updated:** May 8, 2026  
**Tested on:** Odoo 19.0 Enterprise, PostgreSQL 17
