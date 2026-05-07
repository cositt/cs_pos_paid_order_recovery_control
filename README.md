# Paid Order Recovery Control - Edit Payment (Control Recuperación Tickets Pagados TPV)

**Version:** 19.0.2.0.0  
**Author:** Cositt Technology  
**License:** LGPL-3  
**Category:** Point of Sale

## Overview

This module enables waitstaff to quickly edit payment information for finalized (paid) orders within the same cash register session. With a single click, users can remove incorrect payments and reconfigure them with different payment methods, splits, or amounts - all without modifying the order items.

Perfect for restaurants where payment errors or adjustments are common and need fast resolution.

## Features

### Payment Editing

- **One-Click Payment Edit:** Simple "Editar Pago" button on closed orders
- **Clean Payment Removal:** Automatically removes all payment lines
- **Direct to Payment Screen:** Opens PaymentScreen for immediate reconfiguration
- **Same Session Requirement:** Orders can only be edited within the same cash register session
- **Closed Session Protection:** Prevents editing once cash register session is closed

### Flexibility

- **Payment Method Change:** Switch between cash, card, bank transfer, etc.
- **Payment Splits:** Create multi-method payments (e.g., 25€ cash + 25€ card)
- **Amount Adjustment:** Pay different amounts if needed
- **Quick Process:** Items remain untouched, only payment is reconfigured

### Safety & Compliance

- ✅ Session-based isolation
- ✅ Automatic validation
- ✅ User confirmation dialog
- ✅ Error handling with clear messages
- ✅ Order state management

## Installation

1. Place the module in your Odoo addons directory:
   ```bash
   cp -r cs_pos_paid_order_recovery_control /path/to/odoo/addons/
   ```

2. Update the module list:
   - Navigate to **Apps** > **Update Apps List**

3. Install the module:
   - Search and click **Install** on "Control Recuperación Tickets Pagados TPV"

## Configuration

### Prerequisites

- Point of Sale module installed
- Standard Odoo POS setup
- Cash register session in progress

### No Additional Configuration Required

The "Editar Pago" button appears automatically on all finalized orders in the current session.

## Usage

### When to Use

Use payment editing when:
- Wrong payment method was charged (charged card instead of cash)
- Need to split payment between methods
- Customer wants to pay with different method
- Payment amount needs adjustment

### Workflow

#### Step 1: Find Closed Order

1. In POS, go to **Tickets Screen**
2. Find the order that needs payment adjustment

#### Step 2: Click Edit Payment Button

1. Click **"Editar Pago"** button on the order
2. Confirmation dialog appears:
   ```
   Title: "Editar pago"
   Message: "¿Editar pago del pedido [ORDER_NAME]?
   
             Se eliminarán todos los pagos actuales y podrá 
             configurar el pago nuevamente en la pantalla de pago."
   
   Buttons: [Confirmar] [Cancelar]
   ```

#### Step 3: Confirm

1. Click **"Confirmar"**
2. System removes all payments from order
3. Order state changes to draft (payable)
4. PaymentScreen opens automatically

#### Step 4: Configure New Payment

Now in PaymentScreen with empty payment:
- Select payment method (cash, card, etc.)
- Enter amount
- If payment split needed:
  - Add first payment line (e.g., 25€ cash)
  - Add second payment line (e.g., 25€ card)
  - Each line: method + amount
- Confirm payment

#### Step 5: Payment Complete

- Order closes with new payment configured
- Original payment completely replaced
- Customer satisfied

### Practical Examples

**Example 1: Wrong Payment Method**

```
Current State:  50€ CARD (incorrect)
Action:         Click "Editar Pago"
PaymentScreen:  Configure 50€ CASH
Result:         Payment changed to cash ✓
```

**Example 2: Payment Split**

```
Current State:  50€ CARD (full amount)
Customer Says:  "50€ cash, 25€ card please"
Action:         Click "Editar Pago"
PaymentScreen:  
  Line 1: 25€ CASH
  Line 2: 25€ CARD
Result:         Payment split correctly ✓
```

**Example 3: Amount Correction**

```
Current State:  15€ CARD (wrong amount, should be 20€)
Action:         Click "Editar Pago"
PaymentScreen:  Configure 20€ CARD
Result:         Amount corrected ✓
```

## Technical Details

### Dependencies

- `point_of_sale` (Odoo core module)

### Module Components

#### Backend (Python)

**Model:** `pos.order` (extended)

**New Method:** `action_edit_payment()`

```python
def action_edit_payment(self):
    """
    Edits payment of a finalized order:
    1. Validate same session and session is open
    2. Delete all payment lines
    3. Mark order as draft (payable again)
    4. Return order ID
    """
```

**Process:**
1. **Validation Phase:**
   - Check current session (must be same)
   - Check session state (must be 'in_progress')
   - Check order finalization
   - Check payment existence

2. **Payment Removal:**
   - `self.payment_ids.unlink()` - Removes all payments
   - No record kept (clean removal)

3. **Order State Change:**
   - Set state to 'draft'
   - Order becomes editable for payment

#### Frontend (JavaScript)

**Method:** `editPayment(order)`

**Flow:**
1. Show confirmation dialog
2. If confirmed: Call RPC to backend `action_edit_payment()`
3. On success:
   - Load updated orders from POS database
   - Set order as current
   - Navigate to PaymentScreen
   - Show info message
4. On error:
   - Show error dialog
   - Remain on ticket screen

**User Dialogs:**
- **Confirmation:** "¿Editar pago del pedido [NAME]?..."
- **Info:** "El pago del pedido [NAME] ha sido eliminado..."
- **Error:** "Error al editar pago: [MESSAGE]"

#### UI Elements (XML)

**Button Placement:** TicketScreen (after other buttons)

**Button Properties:**
- Text: "Editar Pago"
- Icon: Edit symbol (✎)
- Color: Primary (blue)
- Visibility: Only when:
  - Order is finalized (`ticket.finalized`)
  - Same session (`ticket.session_id.id === pos.session.id`)

### Validation Rules

```
✅ Order must be finalized (state = 'paid')
✅ Must be in current session
✅ Session must be in_progress (not closed)
✅ Order must have at least one payment
```

## Troubleshooting

### "Editar Pago" Button Not Visible

**Problem:** Button doesn't appear on closed orders.

**Solution:**
1. Verify module is installed
2. Verify order is finalized
3. Verify correct session
4. Clear POS cache (F5, Ctrl+Shift+Delete)

### "This order does not belong to current session"

**Problem:** Cannot edit old order's payment.

**Solution:**
1. This is expected - prevents cross-session tampering
2. Orders can only be edited in the same session
3. Once session closes, no editing possible

### "The cash register session is closed"

**Problem:** Cannot edit because session is closed.

**Solution:**
1. By design - prevents tampering with completed sessions
2. Edit payments BEFORE closing session
3. Contact administrator if urgent need

### "The order is not closed/finalized"

**Problem:** Trying to edit draft or in-progress order.

**Solution:**
1. This is normal - only finalized orders can edit payment
2. If order is still being prepared, just edit normally
3. If unsure, check if order is in "Paid" tickets section

## Differences from Previous Version

**v19.0.1.0.0 (Old):**
- "Recuperar Pedido" button
- Copies entire order + items
- Creates new draft order
- More complex workflow

**v19.0.2.0.0 (New):**
- "Editar Pago" button
- Only removes payments
- Order items untouched
- Simpler, faster workflow
- Direct to PaymentScreen

## Support

For issues, feature requests, or technical assistance:
- **Website:** https://cositt.com
- **Email:** support@cositt.com

## Compatibility

- **Odoo Version:** 19.0 Enterprise
- **POS Requirements:** Standard Point of Sale setup
- **Payment Methods:** All standard Odoo payment methods

## License

This module is licensed under LGPL-3. See LICENSE file for details.

## Changelog

### Version 19.0.2.0.0
- Complete redesign: Payment editing system
- Remove payment lines from finalized orders
- Direct PaymentScreen navigation
- Simpler, faster workflow
- Session-based security
- User-friendly confirmation dialogs

### Version 19.0.1.0.0
- Initial release
- Basic order access blocking by session
