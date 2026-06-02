# -*- coding: utf-8 -*-
from odoo import models, fields, api

class LegalLawyer(models.Model):
    """
    Modèle simplifié pour les avocats - Version Community
    N'hérite pas de hr.employe pour éviter les dépendances
    """
    _name = 'legal.lawyer'
    _description = 'Avocat'
    _order = 'name'
    _rec_name = 'name'
    
    # ==================== CHAMPS DE BASE ====================
    name = fields.Char(
        string='Nom',
        required=True
    )
    
    email = fields.Char(
        string='Email'
    )
    
    phone = fields.Char(
        string='Téléphone'
    )
    
    is_active = fields.Boolean(
        string='Actif',
        default=True
    )
    
    # ==================== CHAMPS JURIDIQUES ====================
    is_lawyer = fields.Boolean(
        string='Est avocat',
        default=True
    )
    
    is_assistant = fields.Boolean(
        string='Est assistant juridique',
        default=False
    )
    
    bar_number = fields.Char(
        string="N° de barreau"
    )
    
    bar_admission_date = fields.Date(
        string="Date d'admission au barreau"
    )
    
    hourly_rate = fields.Float(
        string='Taux horaire',
        default=0.0
    )
    
    # ==================== RELATIONS AVEC LES DOSSIERS ====================
    # Dossiers où l'avocat est principal
    lead_case_ids = fields.One2many(
        'legal.case',
        'lead_lawyer_id',
        string='Dossiers principaux'
    )
    
    # Dossiers où l'avocat est associé
    associate_case_ids = fields.Many2many(
        'legal.case',
        'legal_case_associate_lawyer_rel',
        'lawyer_id',
        'case_id',
        string='Dossiers associés'
    )
    
    # Dossiers où l'avocat est assistant
    assistant_case_ids = fields.Many2many(
        'legal.case',
        'legal_case_assistant_rel',
        'lawyer_id',
        'case_id',
        string='Dossiers assistants'
    )
    
    # ==================== RELATIONS AVEC LES AUDIENCES ====================
    audience_ids = fields.Many2many(
        'legal.audience',
        'legal_audience_lawyer_rel',
        'lawyer_id',
        'audience_id',
        string='Audiences'
    )
    
    # ==================== RELATIONS AVEC LES FEUILLES DE TEMPS ====================
    timesheet_ids = fields.One2many(
        'legal.timesheet',
        'lawyer_id',
        string='Feuilles de temps'
    )
    
    # ==================== CHAMPS CALCULÉS ====================
    lead_case_count = fields.Integer(
        string='Dossiers principaux',
        compute='_compute_case_stats',
        store=True
    )
    
    associate_case_count = fields.Integer(
        string='Dossiers associés',
        compute='_compute_case_stats',
        store=True
    )
    
    assistant_case_count = fields.Integer(
        string='Dossiers assistants',
        compute='_compute_case_stats',
        store=True
    )
    
    total_cases = fields.Integer(
        string='Total dossiers',
        compute='_compute_case_stats',
        store=True
    )
    
    total_hours = fields.Float(
        string='Heures totales',
        compute='_compute_totals',
        store=True
    )
    
    total_billable = fields.Float(
        string='Montant facturable',
        compute='_compute_totals',
        store=True
    )
    
    audience_count = fields.Integer(
        string='Nombre d\'audiences',
        compute='_compute_audience_count',
        store=True
    )
    
    # ==================== MÉTHODES COMPUTE ====================
    @api.depends('lead_case_ids', 'associate_case_ids', 'assistant_case_ids')
    def _compute_case_stats(self):
        """Calcule les statistiques des dossiers"""
        for lawyer in self:
            lawyer.lead_case_count = len(lawyer.lead_case_ids)
            lawyer.associate_case_count = len(lawyer.associate_case_ids)
            lawyer.assistant_case_count = len(lawyer.assistant_case_ids)
            lawyer.total_cases = (lawyer.lead_case_count + 
                                  lawyer.associate_case_count + 
                                  lawyer.assistant_case_count)
    
    @api.depends('timesheet_ids', 'timesheet_ids.duration_hours', 'timesheet_ids.cost_amount')
    def _compute_totals(self):
        """Calcule les totaux des feuilles de temps"""
        for lawyer in self:
            total_hours = sum(lawyer.timesheet_ids.mapped('duration_hours'))
            total_billable = sum(lawyer.timesheet_ids.filtered(
                lambda t: t.billable
            ).mapped('cost_amount'))
            lawyer.total_hours = total_hours
            lawyer.total_billable = total_billable
    
    @api.depends('audience_ids')
    def _compute_audience_count(self):
        """Calcule le nombre d'audiences"""
        for lawyer in self:
            lawyer.audience_count = len(lawyer.audience_ids)
    
    # ==================== ACTIONS ====================
    def action_view_lead_cases(self):
        """Voir les dossiers principaux"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Dossiers principaux - {self.name}',
            'res_model': 'legal.case',
            'view_mode': 'tree,form',
            'domain': [('lead_lawyer_id', '=', self.id)],
        }
    
    def action_view_associate_cases(self):
        """Voir les dossiers associés"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Dossiers associés - {self.name}',
            'res_model': 'legal.case',
            'view_mode': 'tree,form',
            'domain': [('associate_lawyer_ids', 'in', self.id)],
        }
    
    def action_view_all_cases(self):
        """Voir tous les dossiers"""
        self.ensure_one()
        all_cases = self.lead_case_ids | self.associate_case_ids | self.assistant_case_ids
        return {
            'type': 'ir.actions.act_window',
            'name': f'Tous les dossiers - {self.name}',
            'res_model': 'legal.case',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', all_cases.ids)],
        }
    
    def action_view_timesheets(self):
        """Voir les feuilles de temps"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Feuilles de temps - {self.name}',
            'res_model': 'legal.timesheet',
            'view_mode': 'tree,form',
            'domain': [('lawyer_id', '=', self.id)],
            'context': {'default_lawyer_id': self.id},
        }
    
    def action_view_audiences(self):
        """Voir les audiences"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Audiences - {self.name}',
            'res_model': 'legal.audience',
            'view_mode': 'tree,form,calendar',
            'domain': [('lawyer_ids', 'in', self.id)],
        }


class LegalSpecialization(models.Model):
    """
    Spécialisations juridiques
    """
    _name = 'legal.specialization'
    _description = 'Spécialisation juridique'
    
    name = fields.Char(
        string='Nom',
        required=True
    )
    
    code = fields.Char(
        string='Code'
    )
    
    description = fields.Text(
        string='Description'
    )
    
    # Relation avec les avocats (modèle simplifié)
    lawyer_ids = fields.Many2many(
        'legal.lawyer',
        'legal_lawyer_specialization_rel',
        'specialization_id',
        'lawyer_id',
        string='Avocats'
    )
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Le nom de la spécialisation doit être unique !'),
        ('code_uniq', 'unique(code)', 'Le code de la spécialisation doit être unique !'),
    ]