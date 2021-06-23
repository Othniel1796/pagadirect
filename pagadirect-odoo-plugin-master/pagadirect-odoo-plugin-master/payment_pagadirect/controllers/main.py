import werkzeug

from odoo import http
from odoo.http import request


class PagaDirectController(http.Controller):
    @http.route(['/payment/pagadirect/return'], type='http', auth='public', csrf=False)
    def pagadirect_return(self, **post):
        request.env['payment.transaction'].sudo().form_feedback(post, 'pagadirect')
        return werkzeug.utils.redirect('/payment/process')
