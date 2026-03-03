from odoo import models, fields, api
from odoo.exceptions import UserError

APPROVAL_LIMIT = 10000.0


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    approval_count = fields.Integer(
        compute='_compute_approval_count',
        string='Approvallar'
    )
    approval_state = fields.Char(
        compute='_compute_approval_count',
        string='Approval Holati'
    )

    def _compute_approval_count(self):
        for order in self:
            approvals = self.env['sale.approval.request'].search([
                ('sale_order_id', '=', order.id)
            ])
            order.approval_count = len(approvals)
            if approvals:
                order.approval_state = approvals[-1].state
            else:
                order.approval_state = ''

    def action_confirm(self):
        if self.env.context.get('skip_approval'):
            return super().action_confirm()

        for order in self:
            if order.amount_total > APPROVAL_LIMIT:
                # Tasdiqlangan approval bormi?
                approved = self.env['sale.approval.request'].search([
                    ('sale_order_id', '=', order.id),
                    ('state', '=', 'approved'),
                ], limit=1)

                if not approved:
                    # Kutilayotgan approval bormi?
                    existing = self.env['sale.approval.request'].search([
                        ('sale_order_id', '=', order.id),
                        ('state', 'in', ['draft', 'submitted']),
                    ], limit=1)

                    if not existing:
                        existing = self.env['sale.approval.request'].create({
                            'sale_order_id': order.id,
                            'requested_by': self.env.user.id,
                        })

                    # Approval yaratildi yoki mavjud, endi userni approval formiga olib boramiz
                    existing.message_post(
                        body=(
                            f"⚠️ Bu buyurtma {APPROVAL_LIMIT:,.0f}$ dan katta. "
                            f"Tasdiqlash so'rovi yaratildi yoki mavjud. "
                            f"Sales Manager tasdiqlaguncha buyurtma tasdiqlanmaydi."
                        )
                    )

                    action = self.env.ref('sale_approval.action_sale_approval_request').read()[0]
                    action['domain'] = [('id', '=', existing.id)]
                    action['views'] = [(False, 'form')]
                    action['context'] = {'default_sale_order_id': order.id}
                    return action

        return super().action_confirm()

    def action_view_approvals(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tasdiqlash So\'rovlari',
            'res_model': 'sale.approval.request',
            'view_mode': 'tree,form',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {'default_sale_order_id': self.id},
        }
