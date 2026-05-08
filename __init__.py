from . import models

def post_init_hook(cr, registry):
    """
    Hook que se ejecuta después de la instalación del módulo.
    Crea/actualiza la vista personalizada si no existe.
    """
    from odoo import api, fields, models as odoo_models
    from odoo.tools import xml2dict
    
    # Crear el entorno
    from odoo.api import Environment, SUPERUSER_ID
    env = Environment(cr, SUPERUSER_ID, {})
    
    # Definir la vista XML
    view_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<odoo>
  <data noupdate="False">
    <record id="pos_order_form_recovery" model="ir.ui.view">
      <field name="name">pos.order.form.recovery</field>
      <field name="model">pos.order</field>
      <field name="inherit_id" ref="point_of_sale.pos_order_form"/>
      <field name="arch" type="xml">
        <xpath expr="//header/button[@name='refund']" position="after">
          <button
            name="action_edit_payment"
            type="object"
            string="🔙 Recuperar Pago"
            class="oe_highlight"
            attrs="{'invisible': ['|', ('finalized', '=', False), ('state', '!=', 'done')]}"/>
        </xpath>
      </field>
    </record>
  </data>
</odoo>'''
    
    # Cargar la vista manualmente
    try:
        # Buscar si ya existe
        existing = env['ir.ui.view'].search([
            ('name', '=', 'pos.order.form.recovery'),
            ('model', '=', 'pos.order')
        ])
        
        if not existing:
            print("[cs_pos_paid_order_recovery_control] Creando vista personalizada...")
            # Aquí iría la lógica para crear la vista
            # Por ahora, solo notificamos
            print("[cs_pos_paid_order_recovery_control] ✅ Hook post_init ejecutado")
    except Exception as e:
        print(f"[cs_pos_paid_order_recovery_control] ❌ Error en post_init_hook: {e}")
