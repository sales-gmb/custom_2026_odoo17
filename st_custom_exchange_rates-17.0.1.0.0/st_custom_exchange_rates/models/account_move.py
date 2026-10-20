from odoo import api, fields, models
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Override the existing currency rate field or add custom behavior
    custom_currency_rate = fields.Float(
        string='Custom Exchange Rate',
        digits=(12, 6),
        help='Manually update the exchange rate for this document.',
    )

    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        """
        Update the custom exchange rate to pick the inverse_company_rate when the currency changes.
        """
        if self.currency_id and self.company_id:
            # Find the latest rate for the selected currency and company
            latest_rate = self.env['res.currency.rate'].search([
                ('currency_id', '=', self.currency_id.id),
                ('company_id', '=', self.company_id.id)
            ], order='name desc', limit=1)

            # Set the custom_currency_rate to the inverse_company_rate
            self.custom_currency_rate = latest_rate.inverse_company_rate if latest_rate else 0.0



    @api.onchange('custom_currency_rate')
    def _onchange_custom_currency_rate(self):
        """
        Update the currency's exchange rate when a custom rate is set.
        """
        if self.currency_id and self.custom_currency_rate:
            # currency = self.currency_id
            # currency.rate = self.custom_currency_rate

            stored_rate = self.custom_currency_rate

            existing_rate = self.env['res.currency.rate'].search([
                ('currency_id', '=', self.currency_id.id),
                ('name', '=', fields.Date.today()),
                ('company_id', '=', self.company_id.id)
            ], limit=1)

            if existing_rate:
                # Update the inverse_company_rate for today
                existing_rate.inverse_company_rate = stored_rate
                print('Updated Existing Inverse Rate:', self.custom_currency_rate, stored_rate)
            else:
                # Create a new rate record for today if none exists
                self.env['res.currency.rate'].create({
                    'currency_id': self.currency_id.id,
                    'inverse_company_rate': stored_rate,
                    'name': fields.Date.today(),
                    'company_id': self.company_id.id,
                })
                print('Created New Inverse Rate:', self.custom_currency_rate, stored_rate)

    def post(self):
        """
        Ensure that the currency rate is updated before posting.
        """
        for move in self:
            if move.currency_id and move.custom_currency_rate:
                move.currency_id.rate = move.custom_currency_rate

                existing_rate = self.env['res.currency.rate'].search([
                    ('currency_id', '=', self.currency_id.id),
                    ('name', '=', fields.Date.today()),
                    ('company_id', '=', self.company_id.id)
                ], limit=1)

                print('Existing Rate: ', existing_rate)
        return super(AccountMove, self).post()

    @api.model
    def create(self, vals):
        """
        Override the create method to add a new exchange rate record
        for the selected currency when a custom rate is provided.
        """
        move = super(AccountMove, self).create(vals)
        if vals.get('custom_currency_rate') and vals.get('currency_id'):
            self._create_currency_rate(
                currency_id=vals['currency_id'],
                rate=vals['custom_currency_rate']
            )

        return move

    def write(self, vals):
        """
        Override the write method to add a new exchange rate record
        for the selected currency when a custom rate is provided.
        """
        result = super(AccountMove, self).write(vals)
        if 'custom_currency_rate' in vals:
            for move in self:
                if move.custom_currency_rate and move.currency_id:
                    self._create_currency_rate(
                        currency_id=move.currency_id.id,
                        rate=move.custom_currency_rate
                    )

        return result


    def _create_currency_rate(self, currency_id, rate):
        """
        Helper method to create a new exchange rate record for the currency.
        """
        currency = self.env['res.currency'].browse(currency_id)
        currency_rate_model = self.env['res.currency.rate']

        # Compute the reciprocal of the custom rate
        stored_rate = 1 / rate

        # Check if a rate for today already exists for this currency
        existing_rate = currency_rate_model.search([
            ('currency_id', '=', currency_id),
            ('name', '=', fields.Date.today())
        ], limit=1)

        if existing_rate:
            # Update the existing rate for today
            existing_rate.inverse_company_rate = rate
            
        else:
            # Create a new rate for today
            currency_rate_model.create({
                'currency_id': currency_id,
                'inverse_company_rate': stored_rate,
                'name': fields.Date.today(),
                'company_id': self.env.company.id,
            })


