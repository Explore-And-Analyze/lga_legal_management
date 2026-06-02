# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class LegalTimesheet(models.Model):
    _name = 'legal.timesheet'
    _description = 'Feuille de temps juridique'
    _inherit = ['mail.thread']
    _order = 'date desc, start_time desc'

    # ==================== CHAMPS DE BASE ====================
    name = fields.Char(
        string='Description',
        required=True,
        tracking=True
    )

    case_id = fields.Many2one(
        'legal.case',
        string='Dossier',
        required=True,
        ondelete='cascade',
        index=True
    )

    lawyer_id = fields.Many2one(
        'legal.lawyer',
        string='Avocat',
        required=True,
        domain=[('is_lawyer', '=', True)],
        tracking=True,
        ondelete='restrict'
    )

    # ==================== TEMPS ====================
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
        index=True
    )

    start_time = fields.Float(
        string='Heure de début',
        required=True
    )

    end_time = fields.Float(
        string='Heure de fin',
        required=True
    )

    duration_hours = fields.Float(
        string='Durée (heures)',
        compute='_compute_duration',
        store=True
    )

    duration_minutes = fields.Integer(
        string='Durée (minutes)',
        compute='_compute_duration_minutes',
        store=True
    )

    # ==================== ACTIVITÉ ====================
    activity_type = fields.Selection([
        ('consultation', 'Consultation'),
        ('research', 'Recherche juridique'),
        ('drafting', 'Rédaction'),
        ('correspondence', 'Correspondance'),
        ('audience', 'Audience'),
        ('travel', 'Déplacement'),
        ('meeting', 'Réunion'),
        ('phone', 'Téléphone'),
        ('administration', 'Administration'),
        ('review', 'Analyse de documents'),
        ('negotiation', 'Négociation'),
        ('expertise', 'Expertise'),
    ], string='Type d\'activité', required=True, tracking=True)

    activity_subtype = fields.Selection([
        ('urgent', 'Urgent'),
        ('regular', 'Régulier'),
        ('followup', 'Suivi'),
        ('preparatory', 'Préparatoire'),
    ], string='Sous-type', default='regular')

    detailed_description = fields.Html(
        string='Description détaillée'
    )

    # ==================== FACTURATION ====================

    cost_amount = fields.Float(
        string='Montant HT',
        compute='_compute_cost',
        store=True
    )

    vat_amount = fields.Float(
        string='Montant TVA',
        compute='_compute_vat_amount',
        store=True
    )

    total_amount = fields.Float(
        string='Montant TTC',
        compute='_compute_total_amount',
        store=True
    )

    billable = fields.Boolean(
        string='Facturable',
        default=True
    )

    billing_status = fields.Selection([
        ('draft', 'Brouillon'),
        ('to_invoice', 'À facturer'),
        ('invoiced', 'Facturé'),
        ('non_billable', 'Non facturable'),
    ], string='Statut facturation', default='draft', tracking=True)

    invoice_id = fields.Many2one(
        'account.move',
        string='Facture associée',
        ondelete='set null'
    )

    invoice_line_id = fields.Many2one(
        'account.move.line',
        string='Ligne de facture',
        ondelete='set null'
    )

    # ==================== VALIDATION ====================
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('submitted', 'Soumis'),
        ('validated', 'Validé'),
        ('rejected', 'Rejeté'),
        ('invoiced', 'Facturé'),
    ], string='Statut', default='draft', tracking=True)

    validated_by_id = fields.Many2one(
        'res.users',
        string='Validé par',
        ondelete='set null'
    )

    validation_date = fields.Datetime(
        string='Date de validation'
    )

    rejection_reason = fields.Text(
        string='Motif du rejet'
    )

    # ==================== NOTES ====================
    notes = fields.Text(
        string='Notes internes'
    )

    currency_symbol = fields.Char(
        string='Symbole devise',
        compute='_compute_currency_info',
        store=False
    )

    # ==================== MÉTHODES COMPUTE ====================
    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for ts in self:
            ts.duration_hours = ts.end_time - ts.start_time

    @api.depends('duration_hours')
    def _compute_duration_minutes(self):
        for ts in self:
            ts.duration_minutes = int(ts.duration_hours * 60)


    @api.depends('cost_amount', 'vat_amount')
    def _compute_total_amount(self):
        for ts in self:
            ts.total_amount = ts.cost_amount + ts.vat_amount

    # ==================== MÉTHODES DE WORKFLOW ====================
    def action_submit(self):
        """Soumettre pour validation"""
        self.write({'state': 'submitted'})
        return True

    def action_validate(self):
        """Valider la saisie"""
        self.write({
            'state': 'validated',
            'validated_by_id': self.env.user.id,
            'validation_date': fields.Datetime.now(),
        })
        return True

    def action_reject(self):
        """Rejeter la saisie"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Motif du rejet',
            'res_model': 'legal.timesheet.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_timesheet_id': self.id},
        }

    def _get_default_account(self):
        """Récupère le compte comptable par défaut"""
        account = self.env['account.account'].search([
            ('account_type', '=', 'income'),
            ('deprecated', '=', False),
        ], limit=1)

        if not account:
            account = self.env['account.account'].search([
                ('code', '=like', '7%'),
                ('deprecated', '=', False),
            ], limit=1)

        if not account:
            account = self.env['account.account'].search([
                ('deprecated', '=', False),
            ], limit=1)

        if not account:
            raise UserError(_("Aucun compte comptable trouvé."))

        return account

    # ==================== CONTRÔLES ====================
    @api.constrains('start_time', 'end_time')
    def _check_times(self):
        for ts in self:
            if ts.end_time <= ts.start_time:
                raise ValidationError(_("L'heure de fin doit être postérieure à l'heure de début."))
            if ts.duration_hours > 24:
                raise ValidationError(_("La durée ne peut pas dépasser 24 heures."))

    @api.constrains('date')
    def _check_date(self):
        for ts in self:
            if ts.date > fields.Date.today():
                raise ValidationError(_("La date ne peut pas être dans le futur."))

    # ==================== CRUD ====================
    @api.model
    def create(self, vals):
        ts = super(LegalTimesheet, self).create(vals)

        # Notification si durée importante
        if ts.duration_hours > 8:
            ts.message_post(
                body=f"Attention: Saisie de {ts.duration_hours} heures pour {ts.case_id.name}",
                subtype_xmlid='mail.mt_comment'
            )

        return ts


class LegalTimesheetRejectWizard(models.TransientModel):
    _name = 'legal.timesheet.reject.wizard'
    _description = 'Assistant de rejet de saisie de temps'
    
    timesheet_id = fields.Many2one(
        'legal.timesheet',
        string='Saisie',
        required=True
    )
    
    reason = fields.Text(
        string='Motif du rejet',
        required=True
    )
    
    def action_reject(self):
        self.ensure_one()
        self.timesheet_id.write({
            'state': 'rejected',
            'rejection_reason': self.reason,
        })
        
        self.timesheet_id.message_post(
            body=f"Saisie rejetée. Motif: {self.reason}"
        )
        
        return {'type': 'ir.actions.act_window_close'}