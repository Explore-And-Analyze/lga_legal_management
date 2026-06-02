# -*- coding: utf-8 -*-

# Systèmes judiciaires internationaux
from odoo import models, fields, api, _


class LegalCourt(models.Model):
    _name = 'legal.court'
    _description = 'Juridiction'
    _order = 'country_id, level, name'

    # ==================== CHAMPS DE BASE ====================
    name = fields.Char(string='Nom', required=True, translate=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(string='Actif', default=True)

    # ==================== CHAMPS DYNAMIQUES PAYS ====================
    country_id = fields.Many2one(
        'res.country',
        string='Pays',
        required=True,
        ondelete='cascade'
    )

    # ==================== NIVEAUX DYNAMIQUES ====================
    level = fields.Selection(
        selection='_get_level_selection',
        string='Niveau',
        required=True
    )

    level_name = fields.Char(
        string='Nom du niveau',
        compute='_compute_level_name',
        store=True
    )

    # ==================== SPÉCIALISATION ====================
    specialization = fields.Selection([
        ('general', 'Compétence générale'),
        ('civil', 'Civil'),
        ('criminal', 'Pénal'),
        ('commercial', 'Commercial'),
        ('labor', 'Social/Travail'),
        ('family', 'Famille'),
        ('administrative', 'Administratif'),
        ('tax', 'Fiscal'),
        ('constitutional', 'Constitutionnel'),
        ('international', 'International'),
    ], string='Spécialisation', required=True, default='general')

    # ==================== INFORMATIONS PRATIQUES ====================
    city = fields.Char(string='Ville')
    address = fields.Text(string='Adresse')
    phone = fields.Char(string='Téléphone')
    email = fields.Char(string='Email')
    website = fields.Char(string='Site web')
    notes = fields.Text(string='Notes')

    # ==================== FONCTIONNALITÉS MODERNES ====================
    e_court_enabled = fields.Boolean(string='E-Court disponible')
    video_conference = fields.Boolean(string='Visioconférence disponible')
    electronic_filing = fields.Boolean(string='Dépôt électronique disponible')
    remote_hearing = fields.Boolean(string='Audience à distance possible')

    # ==================== HIÉRARCHIE ====================
    parent_id = fields.Many2one(
        'legal.court',
        string='Juridiction supérieure',
        domain="[('country_id', '=', country_id), ('level', '<', level)]"
    )

    child_ids = fields.One2many(
        'legal.court',
        'parent_id',
        string='Juridictions inférieures'
    )

    # ==================== MÉTHODES DYNAMIQUES ====================
    @api.model
    def _get_level_selection(self):
        """Récupère dynamiquement les niveaux d'instance selon la configuration pays"""

        # Niveaux par défaut
        default_levels = [
            ('first', 'Première instance'),
            ('appeal', 'Cour d\'appel'),
            ('supreme', 'Cour suprême'),
            ('constitutional', 'Cour constitutionnelle'),
        ]

        return default_levels

    @api.depends('level')
    def _compute_level_name(self):
        """Récupère le nom affiché du niveau selon la configuration"""
        for court in self:
            if court.level:
                selection = dict(self._get_level_selection())
                court.level_name = selection.get(court.level, court.level)
            else:
                court.level_name = False

    @api.model
    def _get_court_types(self):
        """Récupère les types de juridictions selon le système judiciaire du pays"""
        return [
            ('local', 'Tribunal de proximité'),
            ('district', 'Tribunal de grande instance'),
            ('appeal', 'Cour d\'appel'),
            ('supreme', 'Cour de cassation'),
            ('constitutional', 'Cour constitutionnelle'),
        ]

    @api.onchange('country_id')
    def _onchange_country(self):
        """Met à jour les niveaux disponibles quand le pays change"""
        self.level = False
        # CORRECTION: Supprimer l'appel à _reload_models qui n'existe pas
        # Remplacer par une mise à jour du domaine si nécessaire
        return {
            'domain': {
                'parent_id': [('country_id', '=', self.country_id.id), ('level', '<', self.level)] if self.level else [('id', '=', False)]
            }
        }

    # ==================== MÉTHODES D'AIDE ====================
    def get_full_name(self):
        """Retourne le nom complet avec la ville et le niveau"""
        parts = [self.name]
        if self.city:
            parts.append(self.city)
        if self.level_name:
            parts.append(f"({self.level_name})")
        return ' - '.join(parts)

    def get_appeal_court(self):
        """Retourne la juridiction d'appel supérieure"""
        if self.parent_id:
            return self.parent_id

        # Chercher la juridiction supérieure par niveau
        level_order = {'first': 1, 'appeal': 2, 'supreme': 3, 'constitutional': 4}
        current_level = level_order.get(self.level, 0)

        for level, order in level_order.items():
            if order > current_level:
                court = self.search([
                    ('country_id', '=', self.country_id.id),
                    ('level', '=', level)
                ], limit=1)
                if court:
                    return court

        return False