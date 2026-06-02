# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # ==================== CHAMPS SPÉCIFIQUES CLIENTS ====================
    is_client = fields.Boolean(
        string='Est un client',
        default=False
    )
    
    is_opponent = fields.Boolean(
        string='Est une partie adverse',
        default=False
    )
    
    is_lead_partner = fields.Boolean(
        string='Est une partie leader',
        default=False
    )
    
    client_type = fields.Selection([
        ('individual', 'Personne physique'),
        ('company', 'Entreprise'),
        ('association', 'Association'),
        ('institution', 'Institution'),
        ('public', 'Organisme public'),
    ], string='Type de client')
    
    client_since = fields.Date(
        string='Client depuis'
    )
    
    client_reference = fields.Char(
        string='Référence client'
    )
    
    preferred_contact_method = fields.Selection([
        ('email', 'Email'),
        ('phone', 'Téléphone'),
        ('mail', 'Courrier'),
        ('any', 'Indifférent'),
    ], string='Mode de contact préféré', default='any')
    
    # ==================== INFORMATIONS JURIDIQUES ====================
    legal_form = fields.Char(
        string='Forme juridique'
    )
    
    registration_number = fields.Char(
        string="Numéro d'enregistrement"
    )
    
    tax_id = fields.Char(
        string='Identifiant fiscal'
    )
    
    national_id = fields.Char(
        string="N° d'identité nationale"
    )
    
    legal_representative = fields.Char(
        string='Représentant légal'
    )
    
    # ==================== CHAMPS INTERNATIONAUX ====================
    
    has_international_activities = fields.Boolean(
        string='Activités internationales',
        default=False
    )
    
    # ==================== RELATIONS ====================
    case_ids = fields.One2many(
        'legal.case',
        'client_id',
        string='Dossiers comme client'
    )
    
    opponent_case_ids = fields.Many2many(
        'legal.case',
        'legal_case_opponent_rel',
        'partner_id',
        'case_id',
        string='Dossiers comme partie adverse'
    )
    
    lead_case_ids = fields.Many2many(
        'legal.case',
        'legal_case_lead_partner_rel',
        'partner_id',
        'case_id',
        string='Dossiers comme partie leader'
    )
    
    # ==================== STATISTIQUES ====================
    case_count = fields.Integer(
        string='Nombre de dossiers',
        compute='_compute_case_stats',
        store=True
    )
    
    active_case_count = fields.Integer(
        string='Dossiers actifs',
        compute='_compute_case_stats',
        store=True
    )
    
    opponent_case_count = fields.Integer(
        string='Dossiers comme adverse',
        compute='_compute_case_stats',
        store=True
    )
    
    lead_case_count = fields.Integer(
        string='Dossiers comme leader',
        compute='_compute_case_stats',
        store=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id
    )
    
    # ==================== MÉTHODES CRUD ====================
    @api.model
    def create(self, vals):
        """Forcer les flags à True selon le contexte"""
        context = self.env.context
        
        if context.get('default_is_client'):
            vals['is_client'] = True
        if context.get('default_is_opponent'):
            vals['is_opponent'] = True
        if context.get('default_is_lead_partner'):
            vals['is_lead_partner'] = True
            
        return super(ResPartner, self).create(vals)
    
    def write(self, vals):
        """Mise à jour avec gestion des contextes"""
        return super(ResPartner, self).write(vals)
    
    # ==================== MÉTHODES COMPUTE ====================
    @api.depends('case_ids', 'case_ids.state')
    def _compute_case_stats(self):
        for partner in self:
            partner.case_count = len(partner.case_ids)
            partner.active_case_count = len(partner.case_ids.filtered(
                lambda c: c.state == 'active'
            ))
            partner.opponent_case_count = len(partner.opponent_case_ids)
            partner.lead_case_count = len(partner.lead_case_ids)
    
    # ==================== ACTIONS ====================
    def action_view_cases(self):
        """Voir les dossiers du client"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Dossiers - {self.name}',
            'res_model': 'legal.case',
            'view_mode': 'tree,form',
            'domain': [('client_id', '=', self.id)],
            'context': {'default_client_id': self.id},
        }
    
    def action_view_opponent_cases(self):
        """Voir les dossiers où le client est partie adverse"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Dossiers adverses - {self.name}',
            'res_model': 'legal.case',
            'view_mode': 'tree,form',
            'domain': [('opponent_ids', 'in', self.id)],
        }