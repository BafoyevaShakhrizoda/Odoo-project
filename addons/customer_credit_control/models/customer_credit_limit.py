from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CustomerCreditLimit(models.Model):
    _name = 'customer.credit.limit'
    _description = 'Mijoz Kredit Limiti'

    partner_id = fields.Many2one(
        'res.partner',
        required=True,
        string='Mijoz',
        ondelete='restrict'
    )
    credit_limit = fields.Monetary(
        required=True,
        string='Kredit Limit',
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Valyuta',
        default=lambda self: self.env.company.currency_id
    )
    active = fields.Boolean(default=True, string='Aktiv')
    note = fields.Text(string='Izoh')

    total_due = fields.Monetary(
        compute='_compute_total_due',
        store=True,
        string='Jami Qarzdorlik',
        currency_field='currency_id'
    )
    remaining_credit = fields.Monetary(
        compute='_compute_remaining_credit',
        store=True,
        string='Qolgan Limit',
        currency_field='currency_id'
    )

    @api.depends('partner_id')
    def _compute_total_due(self):
        for rec in self:
            if not rec.partner_id:
                rec.total_due = 0.0
                continue
            invoices = self.env['account.move'].search([
                ('partner_id', '=', rec.partner_id.id),
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial']),
            ])
            rec.total_due = sum(invoices.mapped('amount_residual'))

    @api.depends('credit_limit', 'total_due')
    def _compute_remaining_credit(self):
        for rec in self:
            rec.remaining_credit = rec.credit_limit - rec.total_due

    @api.constrains('partner_id', 'active')
    def _check_unique_active_limit(self):
        for rec in self:
            if rec.active:
                duplicate = self.search([
                    ('partner_id', '=', rec.partner_id.id),
                    ('active', '=', True),
                    ('id', '!=', rec.id),
                ])
                if duplicate:
                    raise ValidationError(
                        "⚠️ Bu mijoz uchun allaqachon aktiv kredit limit mavjud!\n"
                        "Avval mavjud limitni arxivlang."
                    )
