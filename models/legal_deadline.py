# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta

import logging
import re

_logger = logging.getLogger(__name__)

class LegalDeadline(models.Model):
    _name = 'legal.deadline'
    _description = 'Délai et Échéance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'deadline_date asc, priority desc'

    # ==================== CHAMPS DE BASE ====================
    name = fields.Char(
        string='Intitulé',
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

    # ==================== TYPE DE DÉLAI ====================
    deadline_type = fields.Selection([
        ('procedure', 'Délai de procédure'),
        ('appeal', 'Délai de recours'),
        ('prescription', 'Délai de prescription'),
        ('deliberation', 'Délai de délibéré'),
        ('judgment', 'Prononcé du jugement'),
        ('execution', 'Délai d\'exécution'),
        ('payment', 'Délai de paiement'),
        ('communication', 'Communication de pièces'),
        ('expertise', 'Délai d\'expertise'),
        ('administrative', 'Délai administratif'),
        ('response', 'Réponse à requête'),
        ('discovery', 'Discovery'),
    ], string='Type de délai', required=True, tracking=True)

    deadline_category = fields.Selection([
        ('legal', 'Délai légal'),
        ('judicial', 'Délai judiciaire'),
        ('contractual', 'Délai contractuel'),
        ('internal', 'Délai interne'),
    ], string='Catégorie', required=True, default='legal')

    # ==================== DATES ====================
    start_date = fields.Date(
        string='Date de début',
        default=fields.Date.context_today,
        required=True
    )

    deadline_date = fields.Date(
        string='Date d\'échéance',
        required=True,
        tracking=True,
        index=True
    )

    completion_date = fields.Date(
        string='Date de réalisation'
    )

    # ==================== CALCULS ====================
    duration_days = fields.Integer(
        string='Durée (jours)',
        compute='_compute_duration',
        store=True
    )

    days_remaining = fields.Integer(
        string='Jours restants',
        compute='_compute_days_remaining',
        store=True
    )

    progress_percentage = fields.Float(
        string='% écoulé',
        compute='_compute_progress',
        store=True
    )

    is_overdue = fields.Boolean(
        string='En retard',
        compute='_compute_is_overdue',
        store=True
    )

    # ==================== STATUT ET PRIORITÉ ====================
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('completed', 'Réalisé'),
        ('extended', 'Prolongé'),
        ('overdue', 'Dépassé'),
        ('cancelled', 'Annulé'),
    ], string='Statut', default='draft', tracking=True)

    priority = fields.Selection([
        ('0', 'Basse'),
        ('1', 'Moyenne'),
        ('2', 'Haute'),
        ('3', 'Critique'),
    ], string='Priorité', default='1')

    # ==================== DESCRIPTION ====================
    description = fields.Text(
        string='Description'
    )

    consequences = fields.Html(
        string='Conséquences du non-respect'
    )

    required_action = fields.Html(
        string='Action requise'
    )

    legal_text = fields.Text(
        string='Texte légal applicable'
    )

    notes = fields.Text(
        string='Notes'
    )

    # ==================== RESPONSABILITÉ ====================
    responsible_id = fields.Many2one(
        'legal.lawyer',
        string='Responsable',
        domain=[('is_lawyer', '=', True)],
        tracking=True,
        ondelete='restrict'
    )

    # ==================== RELATIONS ====================
    generating_audience_id = fields.Many2one(
        'legal.audience',
        string='Généré par audience',
        ondelete='set null'
    )

    generating_document_id = fields.Many2one(
        'legal.document',
        string='Généré par document',
        ondelete='set null'
    )

    task_id = fields.Many2one(
        'project.task',
        string='Tâche associée',
        ondelete='set null'
    )

    reminder_ids = fields.One2many(
        'legal.deadline.reminder',
        'deadline_id',
        string='Rappels'
    )

    extension_ids = fields.One2many(
        'legal.deadline.extension',
        'deadline_id',
        string='Prolongations'
    )

    # ==================== CHAMPS ADAPTATIFS (Configuration Pays) ====================
    default_appeal_days = fields.Integer(
        string='Délai d\'appel par défaut',
        compute='_compute_default_deadlines',
        store=False
    )

    default_cassation_days = fields.Integer(
        string='Délai de pourvoi par défaut',
        compute='_compute_default_deadlines',
        store=False
    )

    default_prescription_years = fields.Integer(
        string='Délai de prescription par défaut',
        compute='_compute_default_deadlines',
        store=False
    )

    # ==================== MÉTHODES COMPUTE ====================
    @api.depends('start_date', 'deadline_date')
    def _compute_duration(self):
        for deadline in self:
            if deadline.start_date and deadline.deadline_date:
                delta = deadline.deadline_date - deadline.start_date
                deadline.duration_days = delta.days
            else:
                deadline.duration_days = 0

    @api.depends('deadline_date', 'state', 'completion_date')
    def _compute_days_remaining(self):
        today = fields.Date.today()
        for deadline in self:
            if deadline.state == 'completed':
                deadline.days_remaining = 0
            elif deadline.state == 'overdue':
                deadline.days_remaining = -((today - deadline.deadline_date).days)
            elif deadline.deadline_date:
                if deadline.deadline_date < today:
                    deadline.days_remaining = -((today - deadline.deadline_date).days)
                else:
                    deadline.days_remaining = (deadline.deadline_date - today).days
            else:
                deadline.days_remaining = 0

    @api.depends('start_date', 'deadline_date')
    def _compute_progress(self):
        today = fields.Date.today()
        for deadline in self:
            if deadline.start_date and deadline.deadline_date:
                total = (deadline.deadline_date - deadline.start_date).days
                if total > 0:
                    elapsed = (today - deadline.start_date).days
                    progress = min(max((elapsed / total) * 100, 0), 100)
                    deadline.progress_percentage = progress
                else:
                    deadline.progress_percentage = 100
            else:
                deadline.progress_percentage = 0

    @api.depends('deadline_date', 'state', 'completion_date')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for deadline in self:
            deadline.is_overdue = (
                deadline.state in ['active', 'draft'] and
                deadline.deadline_date and
                deadline.deadline_date < today
            )

    # ==================== MÉTHODES DE WORKFLOW ====================
    def action_activate(self):
        """Activer le délai"""
        self.write({'state': 'active'})
        self._create_reminders()
        return True

    def action_complete(self):
        """Marquer comme réalisé"""
        self.write({
            'state': 'completed',
            'completion_date': fields.Date.today()
        })
        return True

    def action_extend(self):
        """Prolonger le délai"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prolonger le délai',
            'res_model': 'legal.deadline.extension.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_deadline_id': self.id},
        }

    def action_cancel(self):
        """Annuler le délai"""
        self.write({'state': 'cancelled'})
        return True

    # ==================== RAPPELS ====================

    def _get_reminder_message(self, deadline, days, lang, urgent=False):
        """Génère un message de rappel adapté à la langue"""
        if lang.startswith('fr'):
            urgency = "URGENT: " if urgent else ""
            return f"{urgency}Le délai \"{deadline.name}\" expire dans {days} jours."
        elif lang.startswith('en'):
            urgency = "URGENT: " if urgent else ""
            return f"{urgency}The deadline \"{deadline.name}\" expires in {days} days."
        elif lang.startswith('es'):
            urgency = "URGENTE: " if urgent else ""
            return f"{urgency}El plazo \"{deadline.name}\" vence en {days} días."
        elif lang.startswith('de'):
            urgency = "DRINGEND: " if urgent else ""
            return f"{urgency}Die Frist \"{deadline.name}\" läuft in {days} Tagen ab."
        else:
            return f"The deadline \"{deadline.name}\" expires in {days} days."


    # ==================== CRUD ====================
    @api.model
    def create(self, vals):
        """Surcharge pour appliquer les délais par défaut selon le pays"""

        # Appliquer le délai d'appel par défaut si non spécifié
        if vals.get('deadline_type') == 'appeal' and 'deadline_date' not in vals:
            vals['deadline_date'] = self.get_default_deadline_date('appeal')

        # Appliquer le délai de pourvoi par défaut
        if vals.get('deadline_type') == 'cassation' and 'deadline_date' not in vals:
            vals['deadline_date'] = self.get_default_deadline_date('cassation')

        deadline = super(LegalDeadline, self).create(vals)

        # Créer automatiquement une tâche si nécessaire
        try:
            if not deadline.task_id and deadline.responsible_id:
                # Trouver un projet par défaut
                project_id = False
                if deadline.case_id and deadline.case_id.task_ids:
                    project_id = deadline.case_id.task_ids[0].project_id.id

                if not project_id and deadline.case_id and deadline.case_id.project_id:
                    project_id = deadline.case_id.project_id.id

                if not project_id:
                    project_name = f"Délais"
                    if deadline.case_id:
                        project_name += f" - {deadline.case_id.name}"

                    project = self.env['project.project'].create({
                        'name': project_name,
                    })
                    project_id = project.id

                # Préparer les valeurs de la tâche
                task_vals = {
                    'name': f"Délai: {deadline.name}",
                    'project_id': project_id,
                    'date_deadline': deadline.deadline_date,
                    'description': deadline.required_action or deadline.description,
                }

                if deadline.case_id:
                    task_vals['legal_case_id'] = deadline.case_id.id
                if deadline.id:
                    task_vals['legal_deadline_id'] = deadline.id
                if deadline.responsible_id and deadline.responsible_id.user_id:
                    task_vals['user_ids'] = [(4, deadline.responsible_id.user_id.id)]

                task = self.env['project.task'].create(task_vals)
                deadline.task_id = task.id

        except Exception as e:
            _logger.warning(f"Erreur lors de la création de la tâche: {e}")

        return deadline


class LegalDeadlineReminder(models.Model):
    _name = 'legal.deadline.reminder'
    _description = 'Rappel de Délai'
    _order = 'reminder_date asc'
    
    deadline_id = fields.Many2one(
        'legal.deadline',
        string='Délai',
        required=True,
        ondelete='cascade'
    )
    
    reminder_date = fields.Date(
        string='Date du rappel',
        required=True
    )
    
    reminder_type = fields.Selection([
        ('email', 'Email'),
        ('notification', 'Notification'),
        ('sms', 'SMS'),
        ('task', 'Tâche'),
    ], string='Type', required=True)
    
    message = fields.Text(
        string='Message',
        required=True
    )
    
    state = fields.Selection([
        ('pending', 'En attente'),
        ('sent', 'Envoyé'),
        ('failed', 'Échoué'),
    ], string='Statut', default='pending')
    
    sent_date = fields.Datetime(
        string='Date d\'envoi'
    )
    
    def action_send(self):
        """Envoyer le rappel"""
        for reminder in self:
            # Logique d'envoi selon le type
            if reminder.reminder_type == 'email' and reminder.deadline_id.responsible_id:
                template = self.env.ref('lga_legal_management_community.email_template_deadline_reminder')
                template.send_mail(reminder.id)
            
            reminder.write({
                'state': 'sent',
                'sent_date': fields.Datetime.now(),
            })
    
    @api.model
    def cron_send_reminders(self):
        """Cron pour envoyer les rappels programmés"""
        today = fields.Date.today()
        reminders = self.search([
            ('reminder_date', '<=', today),
            ('state', '=', 'pending')
        ])
        reminders.action_send()


class LegalDeadlineExtension(models.Model):
    _name = 'legal.deadline.extension'
    _description = 'Prolongation de Délai'
    _order = 'create_date desc'
    
    deadline_id = fields.Many2one(
        'legal.deadline',
        string='Délai',
        required=True,
        ondelete='cascade'
    )
    
    old_date = fields.Date(
        string='Ancienne date',
        required=True
    )
    
    new_date = fields.Date(
        string='Nouvelle date',
        required=True
    )
    
    reason = fields.Text(
        string='Motif',
        required=True
    )
    
    authorized_by_id = fields.Many2one(
        'res.users',
        string='Autorisé par',
        default=lambda self: self.env.user
    )
    
    extension_days = fields.Integer(
        string='Jours de prolongation',
        compute='_compute_extension_days',
        store=True
    )
    
    @api.depends('old_date', 'new_date')
    def _compute_extension_days(self):
        for ext in self:
            ext.extension_days = (ext.new_date - ext.old_date).days


class LegalDeadlineExtensionWizard(models.TransientModel):
    _name = 'legal.deadline.extension.wizard'
    _description = 'Assistant de prolongation de délai'
    
    deadline_id = fields.Many2one(
        'legal.deadline',
        string='Délai',
        required=True
    )
    
    new_date = fields.Date(
        string='Nouvelle date d\'échéance',
        required=True
    )
    
    reason = fields.Text(
        string='Motif de la prolongation',
        required=True
    )
    
    def action_extend(self):
        self.ensure_one()
        deadline = self.deadline_id
        
        # Créer l'extension
        self.env['legal.deadline.extension'].create({
            'deadline_id': deadline.id,
            'old_date': deadline.deadline_date,
            'new_date': self.new_date,
            'reason': self.reason,
        })
        
        # Mettre à jour le délai
        deadline.write({
            'deadline_date': self.new_date,
            'state': 'extended',
        })
        
        # Ajouter un message
        deadline.message_post(
            body=f"Délai prolongé du {deadline.deadline_date} au {self.new_date}. Motif: {self.reason}"
        )
        
        return {'type': 'ir.actions.act_window_close'}