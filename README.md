# Paid Order Recovery Control (Control Recuperación Tickets Pagados TPV)

**Version:** 19.0.1.0.0  
**Author:** Cositt Technology  
**License:** LGPL-3  
**Category:** Point of Sale

## Overview

This module implements critical security controls for Odoo Point of Sale environments by preventing unauthorized modification of finalized (paid) orders from other cash register sessions. It ensures data integrity and prevents accidental or intentional tampering with completed transactions.

The module is essential for multi-terminal POS setups and environments where multiple staff members or cashiers operate different POS terminals simultaneously.

## Features

### Security Control

- **Session-Based Validation:** Blocks modification of paid orders from other POS sessions
- **Finalized Order Protection:** Prevents changes to completed transactions
- **Smart Blocking:** Only affects order editing, not viewing or reprinting
- **User-Friendly Alerts:** Clear messages when access is denied

### Operational Flexibility

- **Allowed Operations:**
  - View paid orders (query/read)
  - Reprint receipts
  - Process returns/refunds
  - Historical order review

- **Blocked Operations:**
  - Edit paid orders from other sessions
  - Modify finalized transaction details
  - Change customer information
  - Alter payment records

### Multi-Terminal Support

- **Session Isolation:** Each POS terminal maintains its own session
- **Cross-Terminal Protection:** Prevents interference between cashiers
- **Audit Trail:** Maintains clear separation of transactions

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
- Multi-terminal setup (single or multiple POS terminals)
- Standard Odoo POS user permissions

### No Configuration Required

This module works out-of-the-box with no additional configuration needed. It automatically:
- Detects current POS session
- Checks order finalization status
- Validates session ownership
- Applies restrictions accordingly

## Usage

### Normal Operations

#### Same-Session Operations (Allowed)

1. **Opening Paid Orders from Current Session:**
   - Cashier can open and review their own paid orders
   - Can reprint receipts
   - Can process returns if permitted

2. **Creating New Orders:**
   - New orders created normally
   - No restrictions on current session transactions

3. **Historical Review:**
   - View previous orders for information
   - Access transaction history
   - Check customer history

#### Cross-Session Operations (Blocked)

1. **Attempting to Edit Another Cashier's Paid Order:**
   - System displays alert: "Acceso restringido"
   - Message: "Este ticket no pertenece a la caja actual y no puede modificarse"
   - Operation is canceled
   - Cashier cannot proceed

### Error Messages

**Alert Dialog:**
```
Title: "Acceso restringido" (Access Restricted)
Message: "Este ticket no pertenece a la caja actual y no puede modificarse."
         (This ticket does not belong to the current cash register and cannot be modified.)
```

### Intended Use Cases

#### Multi-Cashier Environment

- **Scenario:** Restaurant with 3 cashiers, each with separate POS terminal
- **Benefit:** Cashier A cannot modify orders from Cashier B's session
- **Result:** Data integrity maintained, audit trail clear

#### Shift Handover

- **Scenario:** Morning shift closing, afternoon shift starting
- **Benefit:** Previous shift's orders are protected from modification
- **Result:** Each session remains independent and auditable

#### Training/New Staff

- **Scenario:** New cashier accidentally selects wrong order
- **Benefit:** System prevents modification if order from another session
- **Result:** Safe, error-tolerant operation

## Technical Details

### Dependencies

- `point_of_sale` (Odoo core module)

### Module Components

#### JavaScript Patch (`paid_order_recovery_control.js`)

**Target:** `TicketScreen.prototype.setOrder()`

**Logic:**
```javascript
if (order?.finalized && order.session_id?.id !== this.pos.session.id) {
  // Display alert and block operation
  return;  // Don't proceed with setOrder
}
return super.setOrder(order);  // Allow operation
```

**Conditions:**
- `order.finalized` = Order is marked as paid/completed
- `order.session_id.id` = Session of the order
- `this.pos.session.id` = Current POS session ID
- Comparison: Orders must belong to current session to be editable

### Key Implementation Details

- **Non-Intrusive:** Only adds one method patch
- **Session-Aware:** Uses native Odoo session identification
- **Finalized Check:** Uses `finalized` field (true = paid order)
- **Dialog Alert:** Uses Odoo's standard AlertDialog component
- **Translation Support:** Uses `_t()` for localization

### What This Module Does NOT Block

The following operations bypass this control:

1. **Order Query:**
   - Reading/viewing paid orders is allowed
   - Historical lookups work normally

2. **Reprinting:**
   - Uses separate reprint function
   - Not affected by this module

3. **Returns/Refunds:**
   - Separate return management screens
   - Not subject to this restriction

4. **Payment Operations:**
   - Finalization logic separate
   - Module only blocks editing, not payment

## Troubleshooting

### Block Alert Appears Unexpectedly

**Problem:** Getting "Acceso restringido" alert when trying to modify own orders.

**Solution:**
1. Verify you're in the correct POS session:
   - Check session ID displayed in POS interface
   - Ensure you haven't switched terminals
2. Check order finalization status:
   - Paid orders cannot be edited (by design)
   - Unpaid orders should be editable
3. Check order session assignment:
   - Order should show current session in details
   - Contact administrator if incorrect

### Cannot Modify Current Session Orders

**Problem:** Even current session paid orders cannot be modified.

**Solution:**
1. This is expected behavior for finalized orders
2. Paid orders are locked by design (Odoo standard)
3. To modify paid orders, you may need:
   - Administrator privileges
   - Process return/exchange instead
   - Contact your system administrator

### Module Not Blocking Cross-Session Access

**Problem:** Users can modify paid orders from other sessions.

**Solution:**
1. Verify module is installed:
   - Check **Apps** > **Installed Modules**
   - Search for module name
2. Check POS configuration:
   - Ensure POS is using correct session
3. Verify order finalization:
   - Check if orders are actually marked as finalized
4. Clear cache and restart POS
5. Contact administrator if issue persists

### Missing Alert Dialog

**Problem:** No alert appears when attempting cross-session edit.

**Solution:**
1. Check browser console for errors:
   - Press F12 to open developer tools
   - Look for JavaScript errors
2. Verify alert dialog component is available
3. Check POS assets are loaded:
   - Refresh POS page (Ctrl+R)
   - Clear browser cache (Ctrl+Shift+Delete)
4. Verify module installation is correct

## Security Considerations

### What This Module Protects Against

- ✅ Accidental modification of other cashier's orders
- ✅ Unauthorized editing of finalized transactions
- ✅ Data integrity across multiple terminals
- ✅ Clear audit trail by session

### What This Module Does NOT Protect Against

- ❌ Direct database manipulation (requires OS-level access)
- ❌ Orders modified before finalization
- ❌ Administrative overrides (super-users may bypass)
- ❌ Refund/return processing (separate authorization)

### Recommendations

1. **User Permissions:**
   - Configure POS user groups appropriately
   - Limit admin access to authorized personnel
   - Use role-based access control

2. **Session Management:**
   - Always close sessions properly
   - Don't share login credentials
   - Enforce password policies

3. **Audit Logging:**
   - Enable Odoo audit trail for POS transactions
   - Monitor order modifications
   - Review session logs regularly

4. **Hardware Security:**
   - Secure physical POS terminals
   - Implement screen lock timeouts
   - Use dedicated terminals when possible

## Support

For issues, feature requests, or technical assistance:
- **Website:** https://cositt.com
- **Email:** support@cositt.com

## Compatibility

- **Odoo Version:** 19.0 Enterprise
- **POS Terminals:** Multiple terminals required for full benefit
- **User Roles:** Compatible with standard POS user groups

## License

This module is licensed under LGPL-3. See LICENSE file for details.

## Changelog

### Version 19.0.1.0.0
- Initial release
- Cross-session order protection
- Finalized order edit blocking
- Session-based access control
- Spanish localization included
- Compatible with Odoo 19 Enterprise
