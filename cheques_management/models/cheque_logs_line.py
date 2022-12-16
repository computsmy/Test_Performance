from odoo import api, fields, models, _

class ChequeLogsLine(models.Model):
    _name = "cheque.logs.line"
    _description = "Cheque Logs Line"

    name = fields.Char(compute="_auto_name_fill")
    cheque_logs_id = fields.Many2one("cheque.logs")
    invoice = fields.Many2one("account.move")
    currency_id = fields.Many2one("res.currency")
    amount_residual = fields.Monetary(string="Amount Due", related="invoice.amount_residual")
    amount_to_apply = fields.Float(string="Amount to Apply", related="invoice.amount_to_apply")
    allocated = fields.Float(string="Applied")
    eligible = fields.Float(string="Eligible Amount", compute="eligible_amount")
    balance = fields.Float(string="Balance", related="cheque_logs_id.balance")
    applied = fields.Boolean(string="Applied")
    balance = fields.Float(string="Balance", related="cheque_logs_id.balance")
    state = fields.Selection(related="cheque_logs_id.state")
    allocate_different = fields.Float(store=True, string="Allocate Different")

    def _auto_name_fill(self):
        for record in self:
            record['name'] = record.invoice.name

    @api.depends('cheque_logs_id','cheque_logs_id.balance','amount_to_apply','allocate_different')
    def eligible_amount(self):
        for record in self:
            if record.allocate_different < 1 and not record.applied:
                balance = record.cheque_logs_id.balance
                if record.amount_to_apply > balance:
                    var = record.amount_to_apply
                else:
                    var = balance
                eligible = var - (abs(record.amount_to_apply - balance))
                record['eligible'] = float("{:.2f}".format(eligible))
            else:
                record['eligible'] = float("{:.2f}".format(record.allocate_different))


    def ApplyToInvoice(self):
        for record in self:
            eligible = record.eligible
            record['allocated'] += eligible
            record.cheque_logs_id['balance'] -= float("{:.2f}".format(eligible))

            record['applied'] = 1

    def UnApplyToInvoice(self):
        for record in self:
            record['eligible'] += record.allocated
            record.cheque_logs_id['balance'] += float("{:.2f}".format(record.allocated))
            record['allocated'] = 0
            record['applied'] = 0




