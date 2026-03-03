from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    credit_remaining = fields.Monetary(
        compute='_compute_credit_remaining',
        string='Qolgan Kredit',
        currency_field='currency_id'
    )
    credit_warning = fields.Boolean(
        compute='_compute_credit_remaining',
        string='Kredit Ogohlantirish'
    )

    @api.depends('partner_id', 'amount_total')
    def _compute_credit_remaining(self):
        for order in self:
            limit = self.env['customer.credit.limit'].search([
                ('partner_id', '=', order.partner_id.id),
                ('active', '=', True),
            ], limit=1)
            if limit:
                order.credit_remaining = limit.remaining_credit - order.amount_total
                order.credit_warning = order.credit_remaining < 0
            else:
                order.credit_remaining = 0.0
                order.credit_warning = False

    def action_view_credit_limit(self):
        """Open the credit limit record(s) for this order's partner."""
        self.ensure_one()
        action = self.env.ref('customer_credit_control.action_customer_credit_limit').read()[0]
        action['domain'] = [('partner_id', '=', self.partner_id.id)]
        return action

    def action_confirm(self):
        for order in self:
            limit = self.env['customer.credit.limit'].search([
                ('partner_id', '=', order.partner_id.id),
                ('active', '=', True),
            ], limit=1)

            if limit:
                if (limit.total_due + order.amount_total) > limit.credit_limit:
                    raise ValidationError(
                        f"❌ Kredit limit yetarli emas!\n\n"
                        f"Kredit limit:    {limit.credit_limit:,.2f} {limit.currency_id.name}\n"
                        f"Mavjud qarz:     {limit.total_due:,.2f} {limit.currency_id.name}\n"
                        f"Bu buyurtma:     {order.amount_total:,.2f} {limit.currency_id.name}\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"Jami bo'ladi:    {limit.total_due + order.amount_total:,.2f} {limit.currency_id.name}\n"
                        f"Qolgan limit:    {limit.remaining_credit:,.2f} {limit.currency_id.name}"
                    )
        return super().action_confirm()
