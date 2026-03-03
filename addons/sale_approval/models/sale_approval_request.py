from odoo import models, fields, api


class SaleApprovalRequest(models.Model):
    _name = 'sale.approval.request'
    _description = 'Savdo Tasdiqlash So\'rovi'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Raqam',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'sale.approval.request'
        ) or 'Yangi'
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Buyurtma',
        required=True,
        ondelete='cascade'
    )
    requested_by = fields.Many2one(
        'res.users',
        string="So'ragan",
        default=lambda self: self.env.user,
        readonly=True
    )
    approved_by = fields.Many2one(
        'res.users',
        string='Tasdiqlagan',
        readonly=True
    )
    state = fields.Selection([
        ('draft', 'Qoralama'),
        ('submitted', 'Yuborildi'),
        ('approved', 'Tasdiqlandi'),
        ('rejected', 'Rad etildi'),
    ], default='draft', string='Holat', tracking=True)

    reject_reason = fields.Text(string='Rad etish sababi')

    currency_id = fields.Many2one(
        related='sale_order_id.currency_id',
        store=True,
        string='Valyuta'
    )
    total_amount = fields.Monetary(
        compute='_compute_total_amount',
        store=True,
        string='Jami Summa',
        currency_field='currency_id'
    )

    @api.depends('sale_order_id.amount_total')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = rec.sale_order_id.amount_total

    def action_submit(self):
        self.state = 'submitted'
        self.message_post(body="📤 Tasdiqlash so'rovi yuborildi.")

    def action_approve(self):
        self.approved_by = self.env.user
        self.state = 'approved'
        self.message_post(body=f"✅ {self.env.user.name} tomonidan tasdiqlandi.")
        self.sale_order_id.with_context(skip_approval=True).action_confirm()

    def action_reject(self):
        self.state = 'rejected'
        reason = self.reject_reason or "Ko'rsatilmagan"
        self.message_post(
            body=f"❌ Rad etildi. Sabab: {reason}"
        )
