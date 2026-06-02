# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime, timedelta
import logging
import re

_logger = logging.getLogger(__name__)

class LegalCase(models.Model):
    _name = 'legal.case'
    _description = 'Dossier Juridique'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'create_date desc'
    _rec_name = 'display_name'
    
    # ==================== CHAMPS DE BASE ====================
    name = fields.Char(
        string='Référence Dossier',
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: _('Nouveau'),
        tracking=True
    )
    
    display_name = fields.Char(
        string='Affichage',
        compute='_compute_display_name',
        store=True
    )
    
    ref_client = fields.Char(
        string='Référence Client',
        help="Référence interne du client pour ce dossier",
        tracking=True
    )
    
    # ==================== RELATIONS PRINCIPALES ====================
    client_id = fields.Many2one(
        'res.partner',
        string='Client Principal',
        required=True,
        domain=[('is_client', '=', True)],
        tracking=True,
        index=True,
        ondelete='restrict'
    )
    
    lead_partner_ids = fields.Many2many(
        'res.partner',
        'legal_case_lead_partner_rel',      # Table de liaison
        'case_id',                           # Colonne pour legal.case
        'partner_id',                    # Colonne pour res.partner (pas 'partner_id')
        string='Parties Leaders',
        domain=[('is_lead_partner', '=', True)]
    )
    
    opponent_ids = fields.Many2many(
        'res.partner',
        'legal_case_opponent_rel',           # Table de liaison
        'case_id',                           # Colonne pour legal.case
        'partner_id',                        # Colonne pour res.partner (pas 'partner_id')
        string='Parties Adverse',
        domain=[('is_opponent', '=', True)]
    )
    
    # ==================== RELATIONS AVOCATS ====================
    lead_lawyer_id = fields.Many2one(
        'legal.lawyer',
        string='Avocat Principal',
        required=True,
        domain=[('is_lawyer', '=', True)],
        tracking=True,
        index=True
    )
    
    associate_lawyer_ids = fields.Many2many(
        'legal.lawyer',
        'legal_case_associate_lawyer_rel',
        'case_id',
        'lawyer_id',
        string='Avocats Associés',
        domain=[('is_lawyer', '=', True)]
    )
    
    assistant_ids = fields.Many2many(
        'legal.lawyer',
        'legal_case_assistant_rel',
        'case_id',
        'lawyer_id',
        string='Assistants Juridiques',
        domain=[('is_assistant', '=', True)]
    )
    
    # ==================== CATÉGORISATION ====================
    case_type_id = fields.Many2one(
        'legal.case.type',
        string='Type de Dossier',
        required=True,
        tracking=True
    )
    
    case_subtype = fields.Selection([
        ('consultation', 'Consultation'),
        ('contentieux', 'Contentieux'),
        ('transaction', 'Transaction'),
        ('arbitrage', 'Arbitrage'),
        ('mediation', 'Médiation'),
        ('redaction', 'Rédaction d\'actes'),
        ('conseil', 'Conseil Juridique'),
        ('expertise', 'Expertise'),
    ], string='Sous-type', tracking=True)
    
    case_stage_id = fields.Many2one(
        'legal.case.stage',
        string='Étape',
        group_expand='_read_group_stage_ids',
        default=lambda self: self._default_stage(),
        tracking=True
    )
    
    priority = fields.Selection([
        ('0', 'Basse'),
        ('1', 'Normale'),
        ('2', 'Haute'),
        ('3', 'Urgente'),
        ('4', 'Critique'),
    ], string='Priorité', default='1', tracking=True)
    
    # ==================== DATES IMPORTANTES ====================
    opening_date = fields.Date(
        string='Date d\'ouverture',
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )
    
    closing_date = fields.Date(
        string='Date de clôture',
        readonly=True,
        tracking=True
    )
    
    deadline_date = fields.Date(
        string='Date limite',
        help="Date limite globale pour le dossier",
        tracking=True,
        index=True
    )
    
    estimated_duration = fields.Integer(
        string='Durée estimée (jours)',
        help="Durée estimée de traitement du dossier"
    )
    
    actual_duration = fields.Integer(
        string='Durée réelle (jours)',
        compute='_compute_actual_duration',
        store=True
    )
    
    # ==================== INFORMATIONS JURIDIQUES ====================
    subject = fields.Char(
        string='Objet du dossier',
        required=True,
        tracking=True
    )
    
    description = fields.Html(
        string='Description détaillée'
    )
    
    facts = fields.Html(
        string='Faits et historique'
    )
    
    claims = fields.Html(
        string='Prétentions des parties'
    )
    
    legal_basis = fields.Html(
        string='Base légale'
    )
    
    jurisprudence = fields.Html(
        string='Jurisprudence applicable'
    )
    
    strategy = fields.Html(
        string='Stratégie juridique'
    )
    
    notes = fields.Text(
        string='Notes internes'
    )
    
    # ==================== JURIDICTION ET PROCÉDURE ====================
    court_id = fields.Many2one(
        'legal.court',
        string='Juridiction'
    )
    
    court_division = fields.Char(
        string='Chambre/Formation'
    )
    
    instance_level = fields.Selection([
        ('first', 'Première instance'),
        ('appeal', 'Cour d\'appel'),
        ('cassation', 'Cour de cassation'),
        ('administrative', 'Juridiction administrative'),
        ('arbitral', 'Juridiction arbitrale'),
        ('constitutional', 'Cour constitutionnelle'),
    ], string='Niveau d\'instance')
    
    case_number = fields.Char(
        string='N° de rôle/RG',
        help="Numéro attribué par la juridiction"
    )
    
    jurisdiction = fields.Selection([
        ('civil', 'Civil'),
        ('commercial', 'Commercial'),
        ('criminal', 'Pénal'),
        ('social', 'Social'),
        ('administrative', 'Administratif'),
        ('family', 'Famille'),
        ('international', 'International'),
    ], string='Compétence', required=True)
    
    procedure_type = fields.Selection([
        ('summary', 'Référé'),
        ('ordinary', 'Procédure ordinaire'),
        ('written', 'Procédure écrite'),
        ('oral', 'Procédure orale'),
    ], string='Type de procédure')
    
    # ==================== ASPECTS FINANCIERS ====================
    dispute_amount = fields.Monetary(
        string='Montant du litige',
        currency_field='currency_id',
        tracking=True
    )
    
    estimated_fees = fields.Monetary(
        string='Honoraires estimés',
        currency_field='currency_id',
        tracking=True
    )
    
    actual_fees = fields.Monetary(
        string='Honoraires réels',
        currency_field='currency_id',
        compute='_compute_actual_fees',
        store=True
    )
    
    estimated_costs = fields.Monetary(
        string='Frais estimés',
        currency_field='currency_id'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id
    )
    
    billing_type = fields.Selection([
        ('hourly', 'Au temps passé'),
        ('fixed', 'Forfait'),
        ('success', 'Au résultat'),
        ('mixed', 'Mixte'),
    ], string='Mode de facturation', default='hourly')
    
    # ==================== RELATIONS AVEC AUTRES MODÈLES ====================
    audience_ids = fields.One2many(
        'legal.audience',
        'case_id',
        string='Audiences'
    )
    
    deadline_ids = fields.One2many(
        'legal.deadline',
        'case_id',
        string='Délais et échéances'
    )
    
    timesheet_ids = fields.One2many(
        'legal.timesheet',
        'case_id',
        string='Feuilles de temps'
    )
    
    document_ids = fields.One2many(
        'legal.document',
        'case_id',
        string='Documents'
    )
    
    # ==================== CHAMPS CALCULÉS ====================
    audience_count = fields.Integer(
        string='Nombre d\'audiences',
        compute='_compute_audience_count',
        store=True
    )
    
    deadline_count = fields.Integer(
        string='Nombre de délais',
        compute='_compute_deadline_count',
        store=True
    )
    
    deadline_urgent_count = fields.Integer(
        string='Délais urgents',
        compute='_compute_deadline_urgent_count',
        store=True
    )
    
    document_count = fields.Integer(
        string='Nombre de documents',
        compute='_compute_document_count',
        store=True
    )
    
    timesheet_total_hours = fields.Float(
        string='Total heures',
        compute='_compute_timesheet_total',
        store=True
    )
    
    timesheet_total_amount = fields.Monetary(
        string='Montant total temps',
        compute='_compute_timesheet_total',
        store=True
    )
    
    days_until_deadline = fields.Integer(
        string='Jours avant échéance',
        compute='_compute_days_until_deadline',
        store=True
    )
    
    deadline_status = fields.Selection([
        ('ok', 'Dans les délais'),
        ('warning', 'Échéance proche'),
        ('urgent', 'Urgent'),
        ('overdue', 'Dépassé'),
    ], string='Statut délai', compute='_compute_deadline_status', store=True)
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('pending', 'En attente'),
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
        ('closed', 'Clôturé'),
        ('archived', 'Archivé'),
    ], string='État', default='draft', tracking=True)
    
    has_jury = fields.Boolean(
        string='Jury populaire',
        default=False
    )
    
    effective_hourly_rate = fields.Float(
        string='Taux horaire effectif',
        compute='_compute_effective_hourly_rate',
        store=True
    )

    
    # ==================== MÉTHODES COMPUTE ====================
    @api.depends('name', 'subject', 'client_id')
    def _compute_display_name(self):
        for record in self:
            if record.name and record.client_id:
                record.display_name = f"{record.name} - {record.client_id.name}"
            elif record.name:
                record.display_name = record.name
            else:
                record.display_name = "Nouveau dossier"
    
    @api.depends('opening_date', 'closing_date')
    def _compute_actual_duration(self):
        for record in self:
            if record.opening_date:
                end_date = record.closing_date or fields.Date.today()
                delta = end_date - record.opening_date
                record.actual_duration = delta.days
            else:
                record.actual_duration = 0
    
    @api.depends('timesheet_ids', 'timesheet_ids.cost_amount')
    def _compute_actual_fees(self):
        for record in self:
            record.actual_fees = sum(record.timesheet_ids.mapped('cost_amount'))
    
    @api.depends('timesheet_ids', 'timesheet_ids.duration_hours')
    def _compute_timesheet_total(self):
        for record in self:
            total_hours = sum(record.timesheet_ids.mapped('duration_hours'))
            total_amount = sum(record.timesheet_ids.mapped('cost_amount'))
            record.timesheet_total_hours = total_hours
            record.timesheet_total_amount = total_amount
    
    @api.depends('deadline_date')
    def _compute_days_until_deadline(self):
        today = fields.Date.today()
        for record in self:
            if record.deadline_date:
                delta = (record.deadline_date - today).days
                record.days_until_deadline = delta
            else:
                record.days_until_deadline = 0
    
    @api.depends('deadline_date', 'state')
    def _compute_deadline_status(self):
        today = fields.Date.today()
        for record in self:
            if not record.deadline_date or record.state in ['closed', 'archived']:
                record.deadline_status = 'ok'
                continue
                
            days = (record.deadline_date - today).days
            if days < 0:
                record.deadline_status = 'overdue'
            elif days <= 3:
                record.deadline_status = 'urgent'
            elif days <= 7:
                record.deadline_status = 'warning'
            else:
                record.deadline_status = 'ok'
    
    @api.depends('audience_ids')
    def _compute_audience_count(self):
        for record in self:
            record.audience_count = len(record.audience_ids)
    
    @api.depends('deadline_ids')
    def _compute_deadline_count(self):
        for record in self:
            record.deadline_count = len(record.deadline_ids)
    
    @api.depends('deadline_ids')
    def _compute_deadline_urgent_count(self):
        for record in self:
            record.deadline_urgent_count = len(record.deadline_ids.filtered(
                lambda d: d.days_remaining <= 7 and d.state == 'active'
            ))
    
    @api.depends('document_ids')
    def _compute_document_count(self):
        for record in self:
            record.document_count = len(record.document_ids)
    
    # ==================== MÉTHODES DE WORKFLOW ====================
    def action_activate(self):
        """Activer le dossier"""
        self.write({'state': 'active'})
        self.message_post(body=_("Dossier activé"))
        return True
    
    def action_suspend(self):
        """Suspendre le dossier"""
        self.write({'state': 'suspended'})
        self.message_post(body=_("Dossier suspendu"))
        return True
    
    def action_close(self):
        """Clôturer le dossier"""
        self.write({
            'state': 'closed',
            'closing_date': fields.Date.today()
        })
        self.message_post(body=_("Dossier clôturé"))
        return True
    
    def action_archive(self):
        """Archiver le dossier"""
        self.write({
            'state': 'archived',
            'active': False
        })
        self.message_post(body=_("Dossier archivé"))
        return True
    
    def action_reopen(self):
        """Réouvrir le dossier"""
        self.write({
            'state': 'active',
            'closing_date': False,
            'active': True
        })
        self.message_post(body=_("Dossier réouvert"))
        return True
    
    # ==================== MÉTHODES CRUD ====================
    @api.model
    def create(self, vals):
        """Créer un nouveau dossier avec gestion des Many2many et auto-remplissage"""
        
        # 🔴 AUTO-REMPLISSAGE : Avocat principal avec l'utilisateur connecté
        if not vals.get('lead_lawyer_id'):
            # Chercher l'employé correspondant à l'utilisateur connecté
            user = self.env.user
            if user.lawyer_id:
                # Si l'utilisateur a un employé associé
                vals['lead_lawyer_id'] = user.lawyer_id.id
            else:
                # Chercher un employé avec le même nom que l'utilisateur
                employee = self.env['legal.lawyer'].search([
                    ('name', 'ilike', user.name),
                    ('is_lawyer', '=', True)
                ], limit=1)
                if employee:
                    vals['lead_lawyer_id'] = employee.id
        
        # Gestion du nom
        if vals.get('name', _('Nouveau')) == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('legal.case') or _('Nouveau')
        
        # Extraire les champs Many2many AVANT la création
        m2m_fields = {}
        for field in ['lead_partner_ids', 'opponent_ids', 'associate_lawyer_ids', 'assistant_ids']:
            if field in vals:
                m2m_fields[field] = vals.pop(field)
        
        
        # Créer le dossier avec les champs simples
        case = super(LegalCase, self).create(vals)
        
        # Ajouter les relations Many2many
        for field_name, value in m2m_fields.items():
            if value:
                try:
                    case.write({field_name: value})
                except Exception as e:
                    _logger.error(f"Erreur lors de l'écriture du champ {field_name}: {e}")
        
        # Créer automatiquement un projet associé
        # if not case.task_ids:
        #     project_vals = {
        #         'name': f"{case.name} - {case.subject}",
        #         'partner_id': case.client_id.id,
        #         'legal_case_id': case.id,
        #     }
        #     if case.lead_lawyer_id and case.lead_lawyer_id.user_id:
        #         project_vals['user_id'] = case.lead_lawyer_id.user_id.id
            
        #     self.env['project.project'].create(project_vals)
        
        return case

    def write(self, vals):
        """Mettre à jour un dossier avec gestion des Many2many"""
        
        # Extraire les champs Many2many AVANT la mise à jour
        m2m_updates = {}
        for field in ['lead_partner_ids', 'opponent_ids', 'associate_lawyer_ids', 'assistant_ids']:
            if field in vals:
                m2m_updates[field] = vals.pop(field)
        
        # Mettre à jour les champs simples
        result = True
        if vals:
            result = super(LegalCase, self).write(vals)
        
        # Mettre à jour les relations Many2many
        for field_name, value in m2m_updates.items():
            if value is not None:
                try:
                    # La valeur est déjà au format Odoo
                    super(LegalCase, self).write({field_name: value})
                except Exception as e:
                    result = False
        
        return result
    
    def unlink(self):
        for record in self:
            if record.state not in ['draft', 'archived']:
                raise UserError(_("Vous ne pouvez supprimer que les dossiers en brouillon ou archivés."))
        return super(LegalCase, self).unlink()
    
    # ==================== MÉTHODES D'AIDE ====================
    @api.model
    def _default_stage(self):
        return self.env['legal.case.stage'].search([], limit=1).id
    
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['legal.case.stage'].search([])
    
    def get_related_data(self):
        """Récupère toutes les données liées au dossier pour l'API"""
        self.ensure_one()
        return {
            'case': self.read()[0],
            'audiences': self.audience_ids.read(),
            'deadlines': self.deadline_ids.read(),
            'documents': self.document_ids.read(),
            'timesheets': self.timesheet_ids.read(),
        }
    
    # ==================== CONTRAINTES ====================
    @api.constrains('opening_date', 'closing_date')
    def _check_dates(self):
        for record in self:
            if record.closing_date and record.closing_date < record.opening_date:
                raise ValidationError(_("La date de clôture ne peut être antérieure à la date d'ouverture."))
    
    @api.constrains('estimated_duration')
    def _check_duration(self):
        for record in self:
            if record.estimated_duration and record.estimated_duration <= 0:
                raise ValidationError(_("La durée estimée doit être positive."))


class LegalCaseType(models.Model):
    _name = 'legal.case.type'
    _description = 'Type de Dossier Juridique'
    _order = 'sequence, name'
    
    name = fields.Char(string='Nom', required=True, translate=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Séquence', default=10)
    active = fields.Boolean(string='Actif', default=True)
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Le nom du type doit être unique !'),
        ('code_uniq', 'unique(code)', 'Le code du type doit être unique !'),
    ]


class LegalCaseStage(models.Model):
    _name = 'legal.case.stage'
    _description = 'Étape de Dossier'
    _order = 'sequence, id'
    
    name = fields.Char(string='Nom', required=True, translate=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Séquence', default=10)
    fold = fields.Boolean(string='Replié dans kanban')
    active = fields.Boolean(string='Actif', default=True)
    code = fields.Char(string='Code technique')
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Le nom de l\'étape doit être unique !'),
    ]