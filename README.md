# Paid Order Recovery Control (Control Recuperación Tickets Pagados TPV)

**Version:** 19.0.2.0.0  
**Author:** Cositt Technology  
**License:** LGPL-3  
**Category:** Point of Sale

## Overview

This module enables waitstaff to recover and modify finalized (paid) orders within the same cash register session. When a payment error occurs or items need adjustment, staff can instantly recover the closed order, reverse the payment, and create a new editable draft order with identical items, allowing full modification including items, quantities, and payment methods.

Essential for restaurant environments where payment errors or order corrections must be handled quickly and efficiently.

## Features

### Order Recovery System

- **One-Click Recovery:** Simple "Recover Order" button on closed orders
- **Payment Reversal:** Automatically reverses all payments from the original order
- **Draft Recreation:** Creates new editable draft order with original items
- **Same Session Requirement:** Orders can only be recovered within the same cash register session
- **Closed Session Protection:** Prevents recovery once cash register session is closed
- **Audit Trail:** Original order marked as cancelled with recovery reference

### Flexibility

- **Full Item Modification:** Add, remove, or change quantities in recovered order
- **Payment Method Change:** Pay with different method (cash ↔ card)
- **Payment Splits:** Create multi-method payments (e.g., 25€ cash + 25€ card)
- **Customer Modification:** Change customer assignment if needed
- **Complete Redo:** Essentially a new order with original data as starting point

### Safety & Compliance

- ✅ Session-based isolation (prevents cross-session tampering)
- ✅ Automatic audit trail (original order preserved)
- ✅ Validation checks (session status, order finalization, payment existence)
- ✅ User-friendly dialogs with confirmation
- ✅ Error handling and clear messages

## Installation

1. Place the module in your Odoo addons directory:
   ```bash
   cp -r cs_pos_paid_order_recovery_control /path/to/odoo/addons/
   ```

2. Update the module list:
   - Navigate to **Apps** > **Update Apps List**
   - Search for "Control Recuperación Tickets Pagados TPV" or "Paid Order Recovery Control"

3. Install the module:
   - Click **Install** on the module card

## Configuration

### Prerequisites

- Point of Sale module must be installed
- Standard Odoo POS setup with payment methods
- Cash register session in progress (not closed)

### No Additional Configuration Required

This module works out-of-the-box with no configuration needed. The "Recover Order" button appears automatically on eligible orders.

## Usage

### When to Use

Use order recovery when:
- Wrong payment method selected (charged card instead of cash)
- Customer asks to modify order after payment
- Items need to be added or removed post-payment
- Need to process refund + new payment for changed order
- Payment error occurred during transaction

### Recovery Workflow

#### Step 1: Identify Closed Order

1. In POS, go to **Tickets Screen** (closed orders view)
2. Browse through closed/finalized orders
3. Find the order that needs correction

#### Step 2: Open Recovery Dialog

1. Click the **"Recuperar Pedido"** (Recover Order) button on the order
2. System displays confirmation dialog:
   ```
   Title: "Confirmar recuperación"
   Message: "¿Recuperar pedido [ORDER_NAME]?
   
            Se revertirá el pago y se creará un nuevo pedido 
            editable con los mismos productos para que pueda 
            modificarlo."
   
   Buttons: [Confirmar] [Cancelar]
   ```

#### Step 3: Confirm Recovery

1. Click **"Confirmar"** to proceed
2. System automatically:
   - Reverses all payments from original order
   - Marks original order as cancelled
   - Creates new draft order with identical items
3. New order opens in **Product Screen** (ready to edit)

#### Step 4: Modify the Order

Now you have a fully editable draft order where you can:

**Modify Items:**
- Change quantities (more or less)
- Remove unwanted items
- Add new items
- Change item details (notes, attributes)

**Modify Payment:**
- Select different payment method (cash, card, etc.)
- Create payment splits:
  - Example: 25€ cash + 25€ card
  - Add multiple payment lines with different methods
  - Each line specifies method and amount

**Modify Customer:**
- Change or add customer details if needed

#### Step 5: Complete Payment

1. Proceed with payment as normal POS order
2. Choose payment method(s):
   - Single method: Simple payment screen
   - Multiple methods: Add multiple payment lines
3. Confirm payment
4. Order closes with new payment

**Result:**
- Original order: Marked as "cancelled" (history/audit)
- New order: Paid with corrections/modifications
- Payments reversed and new payment recorded
- Customer satisfied with corrected order

### Practical Examples

**Example 1: Wrong Payment Method**

```
Original Order: 50€ (charged to CARD by mistake)
Action:         Recover order
Modification:   (no changes needed)
New Payment:    50€ CASH
Result:         Payment reversed from card, 50€ charged to cash ✓
```

**Example 2: Item Correction**

```
Original Order:  Coffee (5€) + Juice (4€) = 9€
Mistake:         Charged 15€ by mistake
Action:          Recover order
Modification:    Remove juice (only coffee needed)
New Subtotal:    5€
New Payment:     5€ CASH
Result:          Refund 15€ card, charge 5€ cash ✓
```

**Example 3: Payment Split**

```
Original Order:  Meal 50€ (all CARD)
Customer Says:   "I want to pay part with cash"
Action:          Recover order
New Payment:     25€ CASH + 25€ CARD (split)
Result:          50€ distributed between two payment methods ✓
```

**Example 4: Item Addition**

```
Original Order:  Appetizer 8€ (CARD)
Customer Wants:  Add dessert 6€
Action:          Recover order
Modification:    Add dessert item
New Subtotal:    14€
New Payment:     14€ CARD
Result:          14€ charged (8€ refunded, 14€ new charge) ✓
```

## Technical Details

### Dependencies

- `point_of_sale` (Odoo core module)

### Module Components

#### Backend (Python)

**Model:** `pos.order` (extended)

**New Fields:**
- `original_order_id` (Many2one): Links to the original recovered order
- `is_recovery` (Boolean): Marks if this order is a recovery

**New Method:** `action_recover_order()`

```python
def action_recover_order(self):
    """
    Main recovery workflow:
    1. Validate same session and session is open
    2. Reverse all payments
    3. Create new draft order with copied items
    4. Mark original as cancelled
    5. Return new order ID
    """
```

**Process:**
1. **Validation Phase:**
   - Check current session (must be same)
   - Check session state (must be 'in_progress')
   - Check order finalization
   - Check payment existence

2. **Payment Reversal:**
   - For each payment line in original order
   - Create negative payment (reversal)
   - Recorded in order history for audit

3. **New Order Creation:**
   - Create new order in draft state
   - Copy all order lines (items) to new order
   - Link back to original via `original_order_id`
   - Mark with `is_recovery = True`

4. **Original Order Marking:**
   - Set state to 'cancelled'
   - Set is_recovery = True
   - Audit trail preserved

#### Frontend (JavaScript)

**Method:** `recoverOrder(order)`

**Flow:**
1. Show confirmation dialog to user
2. If confirmed: Call RPC to backend `action_recover_order()`
3. On success:
   - Load updated orders from POS database
   - Set new order as current order
   - Navigate to ProductScreen for editing
   - Show success message
4. On error:
   - Show error dialog with error message
   - Remain on ticket screen

**User Dialogs:**
- **Confirmation:** "¿Recuperar pedido [NAME]? Se revertirá el pago..."
- **Success:** "El pedido [NAME] ha sido recuperado..."
- **Error:** "Error al recuperar pedido: [MESSAGE]"

#### UI Elements (XML)

**Button Placement:** TicketScreen (after reprint button)

**Button Properties:**
- Text: "Recuperar Pedido"
- Icon: Undo symbol (↶)
- Color: Warning (orange/yellow)
- Visibility: Only when:
  - Order is finalized (`ticket.finalized`)
  - Same session (`ticket.session_id.id === pos.session.id`)
  - Not already a recovery (`!ticket.is_recovery`)

### Validation Rules

```
✅ Order must be finalized (state = 'paid')
✅ Must be in current session
✅ Session must be in_progress (not closed)
✅ Order must have at least one payment
❌ Prevent double-recovery (is_recovery = False)
```

### Audit Trail

Original order is preserved:
- State: `cancelled`
- is_recovery: `True`
- All original data intact
- Visible in order history
- No data lost, fully traceable

## Troubleshooting

### "Recover Order" Button Not Visible

**Problem:** Button doesn't appear on closed orders.

**Solution:**
1. Verify module is installed:
   - Go to **Apps > Installed Modules**
   - Search for module name
2. Verify order is finalized:
   - Order must have state = 'paid'
   - Must show as "closed" in tickets list
3. Verify correct session:
   - Order must belong to current session
   - Button only appears for current session orders
4. Clear POS cache:
   - Refresh browser (F5 or Ctrl+R)
   - Clear browser cache (Ctrl+Shift+Delete)

### "This order does not belong to current cash register session"

**Problem:** Error when trying to recover old order.

**Solution:**
1. This is expected behavior - prevents cross-session tampering
2. Orders can only be recovered within the same cash register session
3. Once session closes, no recovery is possible
4. To modify closed session orders, contact administrator
5. This is a security feature to maintain data integrity

### "The cash register session is closed"

**Problem:** Cannot recover order because session is closed.

**Solution:**
1. This is by design - prevents tampering with completed sessions
2. Recovery only works during active session (in_progress state)
3. To recover orders from closed session:
   - Request administrator to reopen session (if needed)
   - Or manual reversal process (consult IT)
4. Prevention: Always recover orders BEFORE closing session

### "The order is not closed/finalized"

**Problem:** Trying to recover draft or in-progress order.

**Solution:**
1. This is normal - recovery only for finalized orders
2. If order is still editable (draft):
   - Make changes directly (no recovery needed)
   - Pay normally when ready
3. If unsure of order state:
   - Check if order is in "Paid" section of tickets

### Recovery Failed - Payment Reversal Error

**Problem:** Technical error during payment reversal.

**Solution:**
1. This is rare - indicates payment system issue
2. Check payment method configuration:
   - Go to **Point of Sale > Payment Methods**
   - Verify all methods are active and configured
3. Check order payments:
   - Multiple payment methods may cause issues
   - Single payment method usually works fine
4. Contact administrator if problem persists
5. Manual intervention may be needed

## Limitations

- ⚠️ Can only recover within same session
- ⚠️ Cannot recover if session is closed
- ⚠️ Cannot recover draft/unpaid orders (use direct edit)
- ⚠️ Payment reversal depends on payment method support
- ⚠️ Some payment methods may not support reversal

## Support

For issues, feature requests, or technical assistance:
- **Website:** https://cositt.com
- **Email:** support@cositt.com

## Compatibility

- **Odoo Version:** 19.0 Enterprise
- **POS Requirements:** Standard Point of Sale setup
- **Payment Methods:** Compatible with all standard Odoo payment methods

## License

This module is licensed under LGPL-3. See LICENSE file for details.

## Changelog

### Version 19.0.2.0.0
- Complete rewrite: Order recovery system
- Automatic payment reversal
- New editable draft order creation
- Copied items from original
- Session-based security controls
- User-friendly dialogs
- Full audit trail

### Version 19.0.1.0.0
- Initial release
- Basic order access blocking by session
