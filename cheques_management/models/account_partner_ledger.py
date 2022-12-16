from odoo import _,models, fields, api
from datetime import datetime

class ReportPartnerLedger(models.AbstractModel):
    _inherit = "account.partner.ledger"

    #To run the query to get the needed data
    @api.model
    def _get_query_amls(self, options, expanded_partner=None, offset=None, limit=None):
        ''' Construct a query retrieving the account.move.lines when expanding a report line with or without the load
        more.
        :param options:             The report options.
        :param expanded_partner:    The res.partner record corresponding to the expanded line.
        :param offset:              The offset of the query (used by the load more).
        :param limit:               The limit of the query (used by the load more).
        :return:                    (query, params)
        '''
        unfold_all = options.get('unfold_all') or (self._context.get('print_mode') and not options['unfolded_lines'])

        # Get sums for the account move lines.
        # period: [('date' <= options['date_to']), ('date', '>=', options['date_from'])]
        if expanded_partner is not None:
            domain = [('partner_id', '=', expanded_partner.id)]
        elif unfold_all:
            domain = []
        elif options['unfolded_lines']:
            domain = [('partner_id', 'in', [int(line[8:]) for line in options['unfolded_lines']])]

        new_options = self._get_options_sum_balance(options)
        tables, where_clause, where_params = self._query_get(new_options, domain=domain)
        ct_query = self.env['res.currency']._get_query_currency_table(options)

        query = '''
                SELECT
                    account_move_line.id,
                    account_move_line.date,
                    account_move_line.date_maturity,
                    account_move_line.name,
                    account_move_line.ref,
                    account_move_line.company_id,
                    account_move_line.account_id,
                    account_move_line.payment_id,
                    account_move_line.partner_id,
                    account_move_line.currency_id,
                    account_move_line.amount_currency,
                    account_move_line.matching_number,
                    ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)   AS debit,
                    ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)  AS credit,
                    ROUND(account_move_line.balance * currency_table.rate, currency_table.precision) AS balance,
                    account_move_line__move_id.name         AS move_name,
                    company.currency_id                     AS company_currency_id,
                    partner.name                            AS partner_name,
                    account_move_line__move_id.move_type    AS move_type,
                    account.code                            AS account_code,
                    account.name                            AS account_name,
                    journal.code                            AS journal_code,
                    journal.name                            AS journal_name,
                    account_move_line__move_id.invoice_date AS invoice_date,
                    account_move_line__move_id.cheques_allocation AS cheque_allocation
                FROM %s
                LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
                LEFT JOIN res_company company               ON company.id = account_move_line.company_id
                LEFT JOIN res_partner partner               ON partner.id = account_move_line.partner_id
                LEFT JOIN account_account account           ON account.id = account_move_line.account_id
                LEFT JOIN account_journal journal           ON journal.id = account_move_line.journal_id
                WHERE %s
                ORDER BY account_move_line.date, account_move_line.id
            ''' % (tables, ct_query, where_clause)

        if offset:
            query += ' OFFSET %s '
            where_params.append(offset)
        if limit:
            query += ' LIMIT %s '
            where_params.append(limit)

        return query, where_params

    #To add the column into the table
    def _get_columns_name(self, options):
        columns = super(ReportPartnerLedger, self)._get_columns_name(options)
        columns.insert(4,{'name': _('Invoice Date'),'class': 'date'})
        columns.insert(5,{'name': _('Customer Reference')})
        columns.insert(14,{'name':_('PDC')})
        return columns

    #To add the data into the table
    @api.model
    def _get_report_line_move_line(self, options, partner, aml, cumulated_init_balance, cumulated_balance):
        res = super(ReportPartnerLedger, self)._get_report_line_move_line(options, partner, aml, cumulated_init_balance,cumulated_balance)
        if aml['invoice_date']:
            new_date_format = aml['invoice_date'].strftime("%d/%m/%Y")
            res['columns'].insert(3,{'name': new_date_format,'class': 'date'})
        else:
            res['columns'].insert(3, {'name': aml['invoice_date'], 'class': 'date'})
        res['columns'].insert(4,{'name': aml['ref']})
        res['columns'].insert(12,{'name': aml['cheque_allocation']})
        return res
