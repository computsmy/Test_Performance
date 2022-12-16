from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = "account.move"
    amount_to_apply = fields.Float(string="Amount to Allocate", store=True, compute="calc_amount_to_apply")
    cheques = fields.One2many("cheque.logs.line", "invoice")
    cheques_allocation = fields.Selection([
        ('n','None'),
        ('p','Partial'),
        ('f','Fully')
    ], store=True, compute="cheque_payment")

    @api.depends('cheques','cheques.balance','invoice_line_ids','amount_residual')
    def calc_amount_to_apply(self):
        for record in self:
            cheques = sum(record.cheques.mapped('allocated'))
            if cheques > 0:
                record['amount_to_apply'] = record.amount_residual - cheques
            else:
                record['amount_to_apply'] = record.amount_residual

    @api.depends('cheques','cheques.balance','invoice_line_ids','amount_residual','amount_to_apply')
    def cheque_payment(self):
        for record in self:
            if record.amount_residual == record.amount_to_apply and len(record.cheques) == 0:
                record['cheques_allocation'] = 'n'
            elif record.amount_residual == record.amount_to_apply and len(record.cheques) > 0:
                record['cheques_allocation'] = 'p'
            elif record.amount_residual != record.amount_to_apply:
                record['cheques_allocation'] = 'p'
            elif record.amount_residual != record.amount_to_apply and record.amount_to_apply == 0:
                record['cheques_allocation'] = 'f'
