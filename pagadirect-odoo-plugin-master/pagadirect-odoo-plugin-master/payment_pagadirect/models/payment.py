import requests

from werkzeug import urls

from odoo import api, fields, models


class PaymentAcquirerPagaDirect(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[
        ('pagadirect', 'PagaDirect')
    ], ondelete={'pagadirect': 'set default'})
    pagadirect_merchant_key = fields.Char(string='PagaDirect Merchant Key', required_if_provider='pagadirect', groups='base.group_user')

    def _get_pagadirect_urls(self, environment):
        """ PagaDirect URLs"""
        if environment == 'prod':
            return {'pagadirect_form_url': 'https://api.pagadirect.com/api/'}
        else:
            return {'pagadirect_form_url': 'https://test-api.pagadirect.com/api/'}

    def pagadirect_form_generate_values(self, values):
        self.ensure_one()
        payment = self.env['payment.transaction'].search([('reference', '=', values['reference'])])
        base_url = self.get_base_url()
        environment = 'prod' if self.state == 'enabled' else 'test'
        url = self._get_pagadirect_urls(environment)['pagadirect_form_url']
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'PagaDirect-Api-Key': self.pagadirect_merchant_key,
        }
        params = {
            'amount': values['amount'],
            'reference': values['reference'],
            'return_url': urls.url_join(base_url, '/payment/pagadirect/return?ref={ref}'.format(ref=values['reference'])),
        }
        r = requests.post(urls.url_join(url, 'payments'), params=params, headers=headers)
        if r.status_code == 200:
            resp_dict = r.json()
            values['pagadirect_tx_url'] = resp_dict['redirect_url']
            payment.write({'acquirer_reference': resp_dict['transaction_id']})
        else:
            raise Exception(r.json()['error'])
        return values


class PaymentTransactionPagaDirect(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _pagadirect_form_get_tx_from_data(self, data):
        transaction = self.search([('reference', '=', data['ref'])])
        return transaction

    def _pagadirect_form_validate(self, data):
        self.ensure_one()
        environment = 'prod' if self.state == 'enabled' else 'test'
        url = self.acquirer_id._get_pagadirect_urls(environment)['pagadirect_form_url']
        headers = {
            'PagaDirect-Api-Key': self.acquirer_id.pagadirect_merchant_key,
        }
        r = requests.get(urls.url_join(url, 'payments/{transaction_id}'.format(transaction_id=self.acquirer_reference)), headers=headers)
        if r.status_code == 200:
            resp_dict = r.json()
            if resp_dict['success'] == True and resp_dict['status'] == 'paid':
                self._set_transaction_done()
            else:
                self._set_transaction_pending()
        else:
            self._set_transaction_cancel()
        return True
