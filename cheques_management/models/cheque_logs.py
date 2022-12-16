from odoo import models, fields, api,_
from odoo.exceptions import *


class ChequeLogs(models.Model):
    _name = "cheque.logs"
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Logs for Cheques"

    name = fields.Char(string="Cheque Number", readonly="1", copy="False", index="True", default=lambda self: _('New'))
    journal_id = fields.Many2one("account.journal",string="Journal")
    partner_id = fields.Many2one("res.partner", string="Customer")
    cheque_number = fields.Char(string="Cheque Number")
    cheque_amount = fields.Float(string="Amount")
    balance = fields.Float(string="Balance", store=True, compute="calculate_balance")
    receive_date = fields.Date(string="Receiving Date")
    post_date = fields.Date(string="Post Date")
    ref = fields.Char(string="Reference")
    payment_id = fields.Many2one("account.payment")
    state = fields.Selection([
        ('draft', 'New'),
        ('confirmed', 'Confirmed'),
        ('deposited', 'Deposited'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('payment', 'Payment Created')
    ], string="Status", index=True, copy=False, default='draft', tracking=True)
    invoices = fields.One2many("cheque.logs.line","cheque_logs_id")
    trigger = fields.Boolean(string="Refresh Invoice List")
    payment_show_or_hide = fields.Boolean(string="Payment Hide or Show", compute="payment_show_hide")


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('cheque.seq') or _('New')
            res = super(ChequeLogs,self).create(vals)
            return res

    @api.onchange('state','trigger')
    def onchange_state(self):
        for record in self:
            invoice_list = record.env['account.move'].search(['&', '&', '&',('partner_id','=',record.partner_id.id),('move_type','=','out_invoice'),('amount_to_apply','>',0),('state','=','posted')])
            datas = []
            for i in invoice_list:
                if not i.id in record.invoices.invoice.ids:
                    datas.append((0, 0, {
                        'invoice': i._origin.id,
                    }))
                else:
                    pass
            record.write({
                'invoices': datas
            })

    @api.depends('cheque_amount')
    def calculate_balance(self):
        for record in self:
            if record.state == 'draft':
                record['balance'] = record.cheque_amount

    def state_confirmed(self):
        for record in self:
            record['state'] = 'confirmed'
            invoice_list = record.env['account.move'].search(
                [('partner_id', '=', record.partner_id.id), ('move_type', '=', 'out_invoice'),
                 ('amount_to_apply', '!=', 0), ('state', '=', 'posted')])
            datas = []
            for i in invoice_list:
                if not i.id in record.invoices.invoice.ids:
                    datas.append((0, 0, {
                        'invoice': i._origin.id,
                    }))
                else:
                    pass
            record.write({
                'invoices': datas
            })

    def reset_to_draft(self):
        for record in self:
            flag = 0
            for i in record.invoices:
                if i.applied == True:
                    flag += 1
            if flag > 0:
                raise UserError(_('Please unapply any applied invoices before returning the cheque to draft'))
            else:
                record['state'] = 'draft'


    def state_accepted(self):
        for record in self:
            record['state'] = 'accepted'
    def state_rejected(self):
        for record in self:
            record['state'] = 'rejected'
    def state_deposited(self):
        for record in self:
            if record.balance <= 0 or record.balance <= 2.2737367544323206e-13:
                record['state'] = 'deposited'
            else:
                raise UserError(_('The cheque balance should be at 0 before depositing.'))
    def state_create_payment(self):
        for record in self:
            record['state'] = 'payment'
            record.payment_id = record.env['account.payment'].create({
                'partner_id':record.partner_id.id,
                'amount':record.cheque_amount,
                'date':record.post_date,
                'ref':record.ref,
                'journal_id':record.journal_id.id
            }).id

    @api.depends('payment_id')
    def payment_show_hide(self):
        for record in self:
            if record.payment_id.id == 0 and record.state in ['accepted','payment']:
                record['payment_show_or_hide'] = True
            else:
                record['payment_show_or_hide'] = False

    def unlink(self):
        for record in self:
            if record.state in ['draft','confirmed','rejected']:
                for i in record.invoices:
                    if i.applied == True:
                        raise UserError(_('Please Unapply any Applied invoices before deleting this cheque'))
                    else:
                        pass
            elif record.state in ['accepted','deposited','payment']:
                raise UserError(_('You are not allowed to delete cheques that are already in Deposited, Accepted and Payment Created stage'))
        self.invoices.write({'invoice':[(5, 0, 0)]})
        return super(ChequeLogs, self).unlink()