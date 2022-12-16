from odoo import api,fields,models,_

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    cheque_log_id = fields.Many2one('cheque.logs')
    cheque_received_date = fields.Date(related='cheque_log_id.receive_date')

