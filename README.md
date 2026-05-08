# Paid Order Recovery Control - POS Frontend Integration

**Version:** 19.0.6.0.0  
**Author:** Cositt Technology  
**License:** LGPL-3  
**Category:** Point of Sale

## Overview

This module enables restaurant and retail staff to quickly recover and re-edit **paid POS orders** directly from the Point of Sale terminal. With a single click on the **"🔙 Recuperar Pago"** button in the ticket screen, the system automatically:

1. Creates a **full automatic refund** of the original paid order
2. **Validates the refund** for accounting compliance
3. Creates a **new draft order** with the same items (without table assignment)
4. **Automatically loads** the new order into the POS for immediate modification and re-payment

Perfect for restaurants where payment errors, missing items, or adjustment needs require fast resolution without manual order re-entry.

## Key Features

### One-Click Recovery Flow
- ✅ **Automatic Refund:** Full refund of original paid order created and validated instantly
- ✅ **New Draft Order:** Fresh order created with same items, ready for editing
- ✅ **No Table Assignment:** Recovered orders appear as floating/takeout orders
- ✅ **Auto-Load to POS:** New order automatically appears on screen for immediate modification
- ✅ **Same Session Required:** Only works within the current active POS session

### Order Modification Capabilities
Once recovered, users can:
- ✅ Edit item quantities
- ✅ Add/remove products
- ✅ Adjust prices
- ✅ Change payment method (cash, card, bank transfer, etc.)
- ✅ Create payment splits (e.g., 50% card + 50% cash)
- ✅ Apply discounts

### Access & User Experience

- **Access Point:** POS Frontend > Orders Screen > Select Paid Order > "🔙 Recuperar Pago" button
- **Button Visibility:** Only appears on finalized, paid orders from current session
- **Auto-Navigation:** New order automatically loads in POS ProductScreen
- **Visual Identification:** Recovered orders labeled "RECUP. [original_order_name]"

### Safety & Compliance

- ✅ Session-based isolation (only current POS session)
- ✅ Full automatic refund with validation
- ✅ Prevents editing of closed sessions
- ✅ Validates all required fields (amount_tax, etc.)
- ✅ Clear error messages
- ✅ Accounting-compliant refund workflow

## Installation

1. Place the module in your Odoo addons directory:
   ```bash
   cp -r cs_pos_paid_order_recovery_control /path/to/odoo/addons/
   ```

2. Update the module list:
   - Odoo Apps > **Update Apps List**

3. Install the module:
   - Search for "Control Recuperación Tickets Pagados TPV"
   - Click **Install**

## Usage Guide

### Step 1: Open POS and Find a Paid Order
1. Launch the Point of Sale application
2. Navigate to **Orders Screen** (ticket list)
3. Find an order with status "Paid" (state = 'paid')

### Step 2: Click "Recuperar Pago"
1. Select the paid order
2. Click the **"🔙 Recuperar Pago"** button (appears at the bottom)
3. The system processes:
   - Creates full automatic refund ✓
   - Validates refund ✓
   - Creates new draft order ✓
   - Automatically loads new order ✓

### Step 3: Modify the New Order
The new order is now loaded in the POS with:
- All original items pre-populated
- Draft status (editable)
- No table assignment
- Ready for modification

Actions you can take:
- Change quantities
- Add/remove items
- Edit prices
- Apply discounts

### Step 4: Re-Payment
1. Click **Pay** button
2. Select payment method(s)
3. Complete payment as normal
4. Order finalized

## Technical Architecture

### Backend (`models/pos_order.py`)

**Method:** `action_edit_payment()`

**Process:**
```
1. Validate current POS session is active
2. Validate order state is 'paid'
3. Create refund order using _refund()
4. Create pos.payment for refund order
5. Call action_pos_order_paid() to validate refund
6. Create NEW pos.order (from scratch, not copy) with:
   - state: 'draft'
   - preset_id: False (no table)
   - floating_order_name: 'RECUP. [original_name]'
   - Copy all pos.order.line items
7. Call _compute_prices() for totals
8. Return {new_order_id: X} to frontend
9. Sync configuration for POS frontend
```

**Key Fields Required:**
- `amount_tax` (computed, initialized to 0)
- `amount_total` (computed)
- `amount_paid` (computed)
- `amount_return` (computed)

### Frontend (`static/src/js/recover_payment.js`)

**Patch:** `TicketScreen.prototype`

**Functionality:**
```javascript
canRecoverPayment getter:
  - Returns true if order is finalized AND state === 'paid'

async recoverPayment() method:
  - Calls backend action_edit_payment()
  - Receives new_order_id from backend
  - Waits 1.5s for POS to sync new order via websocket
  - Finds new order in POS models
  - Calls this.pos.setOrder(newOrder)
  - Calls this.pos.navigateToOrderScreen(newOrder)
  - Shows success notification
```

### UI Template (`static/src/xml/recover_payment.xml`)

**OWL Template:** Extends `TicketScreen`

**Button:**
```xml
<button
    t-if="isOrderSynced and canRecoverPayment"
    class="button btn btn-warning btn-lg py-3 w-100 mb-2"
    t-on-click="recoverPayment">
    🔙 Recuperar Pago
</button>
```

**Placement:** Before ActionpadWidget (above Refund button)

### Module Configuration (`__manifest__.py`)

```python
{
    'name': 'Control Recuperación Tickets Pagados TPV',
    'version': '19.0.6.0.0',
    'category': 'Point of Sale',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_order_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'cs_pos_paid_order_recovery_control/static/src/js/recover_payment.js',
            'cs_pos_paid_order_recovery_control/static/src/xml/recover_payment.xml',
        ],
    },
    'installable': True,
}
```

## Use Cases

### Use Case 1: Missing Item
**Scenario:** Customer paid €75 but forgot they wanted an extra drink

**Flow:**
1. Open POS Orders
2. Select the paid order
3. Click "🔙 Recuperar Pago"
4. New order auto-loads with all original items
5. Add the drink
6. Re-pay for the additional item

### Use Case 2: Wrong Payment Method
**Scenario:** Order shows card payment but customer actually paid cash

**Flow:**
1. Open POS Orders
2. Select the paid order
3. Click "🔙 Recuperar Pago"
4. Automatic refund created
5. New order auto-loads
6. Pay with cash instead

### Use Case 3: Split Payment
**Scenario:** Customer wants to split €100 between 2 cards

**Flow:**
1. Open POS Orders
2. Select the paid order
3. Click "🔙 Recuperar Pago"
4. New order auto-loads
5. Pay €50 on card 1
6. Pay €50 on card 2

### Use Case 4: Price Correction
**Scenario:** Item was incorrectly priced at €10, should be €15

**Flow:**
1. Open POS Orders
2. Select the paid order
3. Click "🔙 Recuperar Pago"
4. New order auto-loads
5. Edit item price from €10 to €15
6. Re-pay the difference

## Important Notes & Limitations

### ✅ What Works
- ✅ Recovery within same POS session
- ✅ Full automatic refund with validation
- ✅ Item editing (quantities, additions, deletions)
- ✅ Price modifications
- ✅ Payment method changes
- ✅ Split payments
- ✅ Multi-session safe (isolated by session)
- ✅ All Odoo payment methods supported

### ❌ What Doesn't Work
- ❌ Recovery from closed POS sessions
- ❌ Recovery of invoiced orders
- ❌ Recovery from different sessions
- ❌ Unfinalized orders (only 'paid' state)

## Error Messages & Solutions

### "No hay ninguna sesión de caja abierta"
**Translation:** "No open cash register session"  
**Solution:** Open a POS session before attempting recovery

### "El pedido no está en estado pagado"
**Translation:** "Order is not in paid state"  
**Solution:** Only fully paid orders can be recovered (state='paid')

### "El pedido no tiene artículos"
**Translation:** "Order has no items"  
**Solution:** Cannot recover an empty order

### "No hay métodos de pago disponibles en la sesión actual"
**Translation:** "No payment methods available in session"  
**Solution:** Configure payment methods in POS settings

## Dependencies

- **Odoo 19.0+** (tested on 19.0 Enterprise)
- **Module:** point_of_sale
- **PostgreSQL:** 16+ (any recent version)

## Compatibility

- ✅ Odoo 19.0 Enterprise
- ✅ Odoo 19.0 Community
- ✅ Multi-session capable
- ✅ All POS payment methods
- ✅ All browser types (responsive design)

## Troubleshooting

### Button Not Visible

1. **Verify order is in paid state:**
   - Open POS Orders
   - Select order, check state field shows "paid"

2. **Verify module is installed:**
   - Odoo Apps > Search "Recuperación"
   - Should show "Installed"

3. **Clear browser cache:**
   - Ctrl+Shift+R (hard refresh)
   - Or clear cookies in browser settings

4. **Restart Odoo:**
   ```bash
   docker-compose restart odoo
   ```

### Recovery Process Hangs

1. **Check POS connectivity:**
   - Verify internet connection
   - Verify POS can reach Odoo server

2. **Check server logs:**
   ```bash
   docker-compose logs odoo 2>&1 | grep -E "action_edit_payment|ERROR" | tail -20
   ```

3. **Restart POS:**
   - Close POS application
   - Reopen and try again

4. **Restart Odoo:**
   ```bash
   docker-compose restart odoo
   ```

## Change Log

### v19.0.6.0.0 (Current)
- ✅ **MAJOR:** Auto-load recovered order into POS without "Cargar Pedido" click
- ✅ Backend returns `new_order_id` for frontend navigation
- ✅ Fixed required field `amount_tax` in order creation
- ✅ Frontend JS uses `navigateToOrderScreen()` for automatic navigation
- ✅ Added 1.5s sync delay for websocket order synchronization
- ✅ New orders created with `preset_id: False` (no table assignment)
- ✅ Orders labeled "RECUP. [name]" for clear identification

### v19.0.5.0.0
- ✅ Shifted from backend Odoo form button to POS frontend button
- ✅ Button appears in ticket screen (TicketScreen)
- ✅ Automatic refund and new draft order creation
- ✅ No table assignment for recovered orders

### v19.0.3.0.0 - v19.0.4.0.0
- Initial implementations with various UI iterations

## License

LGPL-3 - See LICENSE file for details

## Author

**Cositt Technology**  
Specialized in Point of Sale and restaurant management solutions for Odoo

---

**Last Updated:** May 8, 2026  
**Tested on:** Odoo 19.0 Enterprise, PostgreSQL 16, Python 3.12  
**Status:** Production Ready ✅
