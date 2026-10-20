from odoo import api, fields, models

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    custom_currency_rate = fields.Float(
        string='Custom Exchange Rate',
        digits=(12, 6),
        help='Manually update the exchange rate for this payment.',
    )

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        """
        Update the custom exchange rate to the latest inverse_company_rate when the currency changes.
        """
        if self.currency_id and self.company_id:
            latest_rate = self.env['res.currency.rate'].search([
                ('currency_id', '=', self.currency_id.id),
                ('company_id', '=', self.company_id.id)
            ], order='name desc', limit=1)
            self.custom_currency_rate = latest_rate.inverse_company_rate if latest_rate else 0.0

    @api.onchange('custom_currency_rate')
    def _onchange_custom_currency_rate(self):
        """
        Update the currency's exchange rate when a custom rate is set.
        """
        if self.currency_id and self.custom_currency_rate:
            stored_rate = self.custom_currency_rate

            existing_rate = self.env['res.currency.rate'].search([
                ('currency_id', '=', self.currency_id.id),
                ('name', '=', fields.Date.today()),
                ('company_id', '=', self.company_id.id)
            ], limit=1)

            if existing_rate:
                existing_rate.inverse_company_rate = stored_rate
            else:
                self.env['res.currency.rate'].create({
                    'currency_id': self.currency_id.id,
                    'inverse_company_rate': stored_rate,
                    'name': fields.Date.today(),
                    'company_id': self.company_id.id,
                })

    def post(self):
        """
        Ensure the custom currency rate is applied before posting.
        """
        for payment in self:
            if payment.currency_id and payment.custom_currency_rate:
                existing_rate = self.env['res.currency.rate'].search([
                    ('currency_id', '=', payment.currency_id.id),
                    ('name', '=', fields.Date.today()),
                    ('company_id', '=', self.company_id.id)
                ], limit=1)
        return super(AccountPayment, self).post()
