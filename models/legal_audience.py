# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
import logging
import re

_logger = logging.getLogger(__name__)

class LegalAudience(models.Model):
    _name = 'legal.audience'
    _description = 'Audience'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, start_time desc'
    _rec_name = 'display_name'
    
    # ==================== CHAMPS DE BASE ====================
    name = fields.Char(
        string='Référence',
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: _('Nouvelle audience')
    )
    
    display_name = fields.Char(
        string='Affichage',
        compute='_compute_display_name',
        store=True
    )
    
    case_id = fields.Many2one(
        'legal.case',
        string='Dossier',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    # ==================== TYPE ET NATURE ====================
    audience_type = fields.Selection([
        ('preliminary', 'Préliminaire'),
        ('pre_trial', 'Mise en état'),
        ('hearing', 'Plaidoirie'),
        ('deliberation', 'Délibéré'),
        ('judgment', 'Prononcé du jugement'),
        ('appeal', 'Appel'),
        ('cassation', 'Cassation'),
        ('conciliation', 'Conciliation'),
        ('mediation', 'Médiation'),
        ('expertise', 'Expertise'),
        ('enquiry', 'Enquête'),
    ], string='Type d\'audience', required=True, tracking=True)
    
    audience_subtype = fields.Selection([
        ('public', 'Publique'),
        ('private', 'Chambre du conseil'),
        ('remote', 'Visioconférence'),
        ('written', 'Procédure écrite'),
    ], string='Sous-type', default='public')
    
    # ==================== DATES ET HEURES ====================
    date = fields.Date(
        string='Date',
        required=True,
        tracking=True,
        index=True
    )
    
    start_time = fields.Float(
        string='Heure de début',
        required=True
    )
    
    end_time = fields.Float(
        string='Heure de fin'
    )
    
    duration_hours = fields.Float(
        string='Durée (heures)',
        compute='_compute_duration',
        store=True
    )
    
    is_today = fields.Boolean(
        string="Aujourd'hui",
        compute='_compute_is_today',
        store=True
    )
    
    is_past = fields.Boolean(
        string='Passée',
        compute='_compute_is_past',
        store=True
    )
    
    # ==================== LIEU ====================
    court_id = fields.Many2one(
        'legal.court',
        string='Juridiction',
        ondelete='restrict',
        tracking=True
    )
    
    courtroom = fields.Char(
        string='Salle d\'audience'
    )
    
    location_details = fields.Text(
        string='Détails du lieu'
    )
    
    # ==================== PARTICIPANTS ====================
    judge_name = fields.Char(
        string='Magistrat'
    )
    
    clerk_name = fields.Char(
        string='Greffier'
    )
    
    prosecutor_name = fields.Char(
        string='Procureur'
    )
    
    lawyer_ids = fields.Many2many(
        'legal.lawyer',
        'legal_audience_lawyer_rel',
        'audience_id', 
        'lawyer_id',
        string='Avocats présents',
        domain=[('is_lawyer', '=', True)]
    )
    
    client_ids = fields.Many2many(
        'res.partner',
        'legal_audience_client_rel',
        'audience_id', 
        'client_id',
        string='Clients présents',
        domain=[('is_client', '=', True)]
    )
    
    opponent_lawyer_ids = fields.Many2many(
        'res.partner',
        'legal_audience_opponent_lawyer_rel',
        'audience_id', 
        'partner_id',
        string='Avocats adverses'
    )
    
    other_participants = fields.Text(
        string='Autres participants'
    )
    
    # ==================== OBJET ET CONTENU ====================
    purpose = fields.Text(
        string='Objet de l\'audience',
        required=True
    )
    
    report = fields.Html(
        string='Compte-rendu'
    )
    
    decision = fields.Html(
        string='Décision'
    )
    
    next_steps = fields.Html(
        string='Prochaines étapes'
    )
    
    notes = fields.Text(
        string='Notes internes'
    )
    
    # ==================== DOCUMENTS ====================
    document_ids = fields.One2many(
        'legal.document',
        'audience_id',
        string='Documents associés'
    )
    
    document_count = fields.Integer(
        string='Nombre de documents',
        compute='_compute_document_count'
    )
    
    # ==================== STATUT ET SUIVI ====================
    state = fields.Selection([
        ('scheduled', 'Planifiée'),
        ('confirmed', 'Confirmée'),
        ('in_progress', 'En cours'),
        ('held', 'Tenue'),
        ('postponed', 'Reportée'),
        ('cancelled', 'Annulée'),
        ('pending_judgment', 'En attente de jugement'),
    ], string='Statut', default='scheduled', tracking=True)
    
    postponement_reason = fields.Text(
        string='Motif du report'
    )
    
    cancellation_reason = fields.Text(
        string='Motif d\'annulation'
    )
    
    result = fields.Selection([
        ('favorable', 'Favorable'),
        ('partially_favorable', 'Partiellement favorable'),
        ('unfavorable', 'Défavorable'),
        ('postponed', 'Reporté'),
        ('settlement', 'Accord/Transaction'),
    ], string='Résultat')
    
    # ==================== RELATIONS ====================
    generated_deadline_ids = fields.One2many(
        'legal.deadline',
        'generating_audience_id',
        string='Délais générés'
    )

    generated_document_ids = fields.One2many(
        'legal.document',
        'audience_id',
        string='Documents générés'
    )
    
    calendar_event_id = fields.Many2one(
        'calendar.event',
        string='Événement calendrier'
    )
    
    # ==================== MÉTHODES COMPUTE ====================
    @api.depends('name', 'case_id', 'date')
    def _compute_display_name(self):
        for audience in self:
            if audience.case_id and audience.date:
                audience.display_name = f"{audience.name} - {audience.case_id.name} - {audience.date}"
            else:
                audience.display_name = audience.name
    
    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for audience in self:
            if audience.start_time and audience.end_time:
                audience.duration_hours = audience.end_time - audience.start_time
            else:
                audience.duration_hours = 0
    
    @api.depends('date')
    def _compute_is_today(self):
        today = fields.Date.today()
        for audience in self:
            audience.is_today = audience.date == today
    
    @api.depends('date')
    def _compute_is_past(self):
        today = fields.Date.today()
        for audience in self:
            audience.is_past = audience.date < today
    
    @api.depends('document_ids')
    def _compute_document_count(self):
        for audience in self:
            audience.document_count = len(audience.document_ids)
    
    # ==================== MÉTHODES DE WORKFLOW ====================
    def action_confirm(self):
        """Confirmer l'audience"""
        self.write({'state': 'confirmed'})
        self._send_confirmation_notification()
        return True
    
    def action_start(self):
        """Démarrer l'audience"""
        self.write({'state': 'in_progress'})
        return True
    
    def action_held(self):
        """Marquer comme tenue"""
        self.write({'state': 'held'})
        self._generate_followup_deadlines()
        return True
    
    def action_postpone(self):
        """Reporter l'audience"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reporter l\'audience',
            'res_model': 'legal.audience.postpone.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_audience_id': self.id},
        }
    
    def action_cancel(self):
        """Annuler l'audience"""
        self.write({'state': 'cancelled'})
        if self.calendar_event_id:
            self.calendar_event_id.unlink()
        return True
    
    # ==================== MÉTHODES D'AIDE ====================
    def _send_confirmation_notification(self):
        """Envoyer des notifications de confirmation"""
        template = self.env.ref('lga_legal_management_community.email_template_audience_confirmation')
        for audience in self:
            if audience.client_ids:
                for client in audience.client_ids:
                    template.send_mail(audience.id, email_values={
                        'email_to': client.email,
                    })
    
    def _generate_followup_deadlines(self):
        """Générer automatiquement des délais après audience"""
        Deadline = self.env['legal.deadline']
        for audience in self:
            if audience.audience_type == 'hearing':
                # Délai pour le jugement (généralement 15 jours)
                Deadline.create({
                    'name': f'Jugement - {audience.case_id.name}',
                    'case_id': audience.case_id.id,
                    'generating_audience_id': audience.id,
                    'deadline_type': 'judgment',
                    'deadline_date': audience.date + timedelta(days=15),
                    'description': 'Délai pour le prononcé du jugement',
                    'responsible_id': audience.case_id.lead_lawyer_id.id,
                })
    
    # ==================== CRUD ====================
    @api.model
    def create(self, vals):
        """Créer une nouvelle audience"""
        
        # Gestion du nom
        if vals.get('name', _('Nouvelle audience')) == _('Nouvelle audience'):
            case = self.env['legal.case'].browse(vals.get('case_id'))
            seq = self.env['ir.sequence'].next_by_code('legal.audience')
            vals['name'] = f"AUD/{case.name}/{seq}"
        
        # Extraire les champs Many2many AVANT la création
        m2m_fields = {}
        for field in ['lawyer_ids', 'client_ids', 'opponent_lawyer_ids']:
            if field in vals:
                m2m_fields[field] = vals.pop(field)
        
        # Créer l'audience avec les champs simples
        audience = super(LegalAudience, self).create(vals)
        
        # Ajouter les relations Many2many
        for field_name, value in m2m_fields.items():
            if value:
                if isinstance(value, list):
                    if value and isinstance(value[0], (list, tuple)):
                        # Déjà au format Odoo
                        audience.write({field_name: value})
                    else:
                        # Format simple [id1, id2, ...]
                        audience.write({field_name: [(6, 0, value)]})
        
        # Créer l'événement calendrier
        try:
            audience._create_calendar_event()
        except Exception as e:
            _logger.error(f"Erreur lors de la création de l'événement calendrier pour l'audience {audience.id}: {e}")
        
        return audience

    def write(self, vals):
        """Mettre à jour une audience"""
        
        # Extraire les champs Many2many AVANT la mise à jour
        m2m_updates = {}
        for field in ['lawyer_ids', 'client_ids', 'opponent_lawyer_ids']:
            if field in vals:
                m2m_updates[field] = vals.pop(field)
        
        # Mettre à jour les champs simples
        result = True
        if vals:
            result = super(LegalAudience, self).write(vals)
        
        # Mettre à jour les relations Many2many
        for field_name, value in m2m_updates.items():
            if value:
                
                # Préparer la valeur au format Odoo
                if isinstance(value, list):
                    if value and isinstance(value[0], (list, tuple)):
                        # Déjà au format Odoo
                        write_val = value
                    else:
                        # Format simple [id1, id2, ...]
                        write_val = [(6, 0, value)]
                else:
                    continue
                
                # Mettre à jour le champ Many2many - UTILISER super() pour éviter la récursion
                super(LegalAudience, self).write({field_name: write_val})
        
        return result
    
    def _create_calendar_event(self):
        """Créer un événement dans le calendrier"""
        for audience in self:
            if not audience.calendar_event_id:
                try:
                    # Calcul des heures et minutes
                    start_hour = int(audience.start_time)
                    start_minute = int((audience.start_time % 1) * 60)
                    
                    # Formater correctement la date/heure
                    start_datetime_str = f"{audience.date} {start_hour:02d}:{start_minute:02d}:00"
                    start_datetime = fields.Datetime.from_string(start_datetime_str)
                    
                    # Calcul de l'heure de fin (par défaut +1 heure)
                    if audience.end_time:
                        end_hour = int(audience.end_time)
                        end_minute = int((audience.end_time % 1) * 60)
                        end_datetime_str = f"{audience.date} {end_hour:02d}:{end_minute:02d}:00"
                        end_datetime = fields.Datetime.from_string(end_datetime_str)
                    else:
                        end_datetime = start_datetime + timedelta(hours=1)
                    
                    # Créer l'événement
                    event = self.env['calendar.event'].create({
                        'name': f"Audience: {audience.case_id.name} - {audience.audience_type}",
                        'start': start_datetime,
                        'stop': end_datetime,
                        'allday': False,
                        'location': audience.courtroom or '',
                        'description': audience.purpose or '',
                        'user_id': audience.env.user.id,
                        'partner_ids': [(4, p.id) for p in audience.client_ids] if audience.client_ids else [],
                    })
                    audience.calendar_event_id = event.id
                    
                except Exception as e:
                    # Ne pas bloquer la création de l'audience si l'événement échoue
                    pass


class LegalAudiencePostponeWizard(models.TransientModel):
    _name = 'legal.audience.postpone.wizard'
    _description = 'Assistant de report d\'audience'
    
    audience_id = fields.Many2one(
        'legal.audience',
        string='Audience',
        required=True
    )
    
    new_date = fields.Date(
        string='Nouvelle date',
        required=True
    )
    
    new_start_time = fields.Float(
        string='Nouvelle heure de début',
        required=True
    )
    
    reason = fields.Text(
        string='Motif du report',
        required=True
    )
    
    def action_postpone(self):
        self.ensure_one()
        audience = self.audience_id
        
        old_date = audience.date
        audience.write({
            'date': self.new_date,
            'start_time': self.new_start_time,
            'state': 'postponed',
            'postponement_reason': self.reason,
        })
        
        # Mettre à jour l'événement calendrier
        if audience.calendar_event_id:
            start_datetime = fields.Datetime.from_string(
                f"{self.new_date} {int(self.new_start_time)}:{int((self.new_start_time % 1) * 60)}:00"
            )
            audience.calendar_event_id.write({
                'start': start_datetime,
                'stop': start_datetime + timedelta(hours=1),
            })
        
        # Ajouter une note
        audience.message_post(
            body=f"Audience reportée du {old_date} au {self.new_date}. Motif: {self.reason}"
        )
        
        return {'type': 'ir.actions.act_window_close'}