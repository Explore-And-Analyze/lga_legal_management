# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import base64
import hashlib
import binascii


class LegalDocument(models.Model):
    _name = 'legal.document'
    _description = 'Document Juridique'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    # ==================== CHAMPS DE BASE ====================
    name = fields.Char(
        string='Nom du document',
        required=True,
        tracking=True
    )
    
    case_id = fields.Many2one(
        'legal.case',
        string='Dossier',
        ondelete='cascade',
        index=True
    )
    
    audience_id = fields.Many2one(
        'legal.audience',
        string='Audience',
        ondelete='set null'
    )
    
    # ==================== FICHIER ====================
    file_data = fields.Binary(
        string='Fichier',
        attachment=True,
        help="Fichier du document"
    )
    
    file_name = fields.Char(
        string='Nom du fichier',
        help="Nom du fichier"
    )
    
    file_size = fields.Integer(
        string='Taille (octets)',
        compute='_compute_file_size',
        store=True
    )
    
    file_type = fields.Char(
        string='Type MIME',
        compute='_compute_file_type',
        store=True
    )
    
    # ==================== MÉTADONNÉES ====================
    document_type = fields.Selection([
        ('contract', 'Contrat'),
        ('pleading', 'Conclusions'),
        ('brief', 'Mémoire'),
        ('evidence', 'Pièce'),
        ('correspondence', 'Correspondance'),
        ('judgment', 'Jugement'),
        ('order', 'Ordonnance'),
        ('expertise', 'Rapport d\'expertise'),
        ('invoice', 'Facture'),
        ('note', 'Note interne'),
        ('legal_basis', 'Base légale'),
        ('jurisprudence', 'Jurisprudence'),
        ('doctrine', 'Doctrine'),
        ('form', 'Formulaire'),
        ('other', 'Autre'),
    ], string='Type de document', required=True, tracking=True)
    
    document_category = fields.Selection([
        ('procedural', 'Document de procédure'),
        ('evidence', 'Pièce justificative'),
        ('administrative', 'Document administratif'),
        ('financial', 'Document financier'),
        ('legal', 'Document juridique'),
        ('correspondence', 'Correspondance'),
    ], string='Catégorie', required=True)
    
    document_date = fields.Date(
        string='Date du document'
    )
    
    document_number = fields.Char(
        string='N° de document'
    )
    
    author = fields.Char(
        string='Auteur'
    )
    
    source = fields.Char(
        string='Source'
    )
    
    language = fields.Selection([
        ('fr', 'Français'),
        ('en', 'Anglais'),
        ('nl', 'Néerlandais'),
        ('de', 'Allemand'),
        ('other', 'Autre'),
    ], string='Langue', default='fr')
    
    # ==================== CONTENU ====================
    description = fields.Text(
        string='Description'
    )
    
    keywords = fields.Char(
        string='Mots-clés'
    )
    
    notes = fields.Text(
        string='Notes'
    )
    
    extracted_text = fields.Text(
        string='Texte extrait'
    )
    
    # ==================== CLASSIFICATION ====================
    confidentiality = fields.Selection([
        ('public', 'Public'),
        ('internal', 'Interne'),
        ('restricted', 'Restreint'),
        ('confidential', 'Confidentiel'),
        ('secret', 'Secret'),
    ], string='Confidentialité', default='internal')
    
    version = fields.Float(
        string='Version',
        default=1.0,
        required=True,
        readonly=True,
        help="Version automatique du document"
    )
    
    is_original = fields.Boolean(
        string='Document original',
        default=True
    )
    
    original_id = fields.Many2one(
        'legal.document',
        string='Document original'
    )
    
    revision_ids = fields.One2many(
        'legal.document',
        'original_id',
        string='Révisions'
    )
    
    # ==================== STATUT ====================
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('validated', 'Validé'),
        ('sent', 'Envoyé'),
        ('received', 'Reçu'),
        ('archived', 'Archivé'),
    ], string='Statut', default='draft', tracking=True)
    
    validated_by_id = fields.Many2one(
        'res.users',
        string='Validé par'
    )
    
    validation_date = fields.Datetime(
        string='Date de validation'
    )
    
    # ==================== TAGS ====================
    tag_ids = fields.Many2many(
        'legal.document.tag',
        'legal_document_tag_rel',
        'document_id', 'tag_id',
        string='Étiquettes'
    )
    
    # ==================== RELATIONS ====================
    created_by_id = fields.Many2one(
        'res.users',
        string='Créé par',
        default=lambda self: self.env.user
    )
    
    # ==================== CHAMPS CALCULÉS ====================
    file_hash = fields.Char(
        string='Empreinte SHA256',
        compute='_compute_file_hash',
        store=True
    )
    
    attachment_id = fields.Integer(
        string='ID Attachment',
        compute='_compute_attachment_id',
        store=False
    )
    
    @api.depends('file_data')
    def _compute_file_hash(self):
        for doc in self:
            if not doc.file_data:
                doc.file_hash = False
                continue
            
            try:
                file_data_str = doc.file_data.strip() if doc.file_data else ''
                if not file_data_str:
                    doc.file_hash = False
                    continue
                    
                missing_padding = len(file_data_str) % 4
                if missing_padding:
                    file_data_str += '=' * (4 - missing_padding)
                
                file_data = base64.b64decode(file_data_str)
                doc.file_hash = hashlib.sha256(file_data).hexdigest()
            except Exception as e:
                doc.file_hash = False
    
    @api.depends('file_data')
    def _compute_file_size(self):
        for doc in self:
            if not doc.file_data:
                doc.file_size = 0
                continue
            
            try:
                file_data_str = doc.file_data.strip() if doc.file_data else ''
                if not file_data_str:
                    doc.file_size = 0
                    continue
                    
                missing_padding = len(file_data_str) % 4
                if missing_padding:
                    file_data_str += '=' * (4 - missing_padding)
                
                file_data = base64.b64decode(file_data_str)
                doc.file_size = len(file_data)
            except Exception as e:
                doc.file_size = 0
    
    @api.depends('file_name')
    def _compute_file_type(self):
        for doc in self:
            if doc.file_name and '.' in doc.file_name:
                doc.file_type = doc.file_name.split('.')[-1].lower()
            else:
                doc.file_type = False
    
    def _compute_attachment_id(self):
        """Trouver l'ID de l'attachment associé"""
        for doc in self:
            if doc.file_data and doc.file_name:
                attachment = self.env['ir.attachment'].search([
                    ('res_model', '=', 'legal.document'),
                    ('res_id', '=', doc.id),
                    ('name', '=', doc.file_name)
                ], limit=1)
                doc.attachment_id = attachment.id if attachment else False
            else:
                doc.attachment_id = False
    
    # ==================== MÉTHODES DE WORKFLOW ====================
    def action_validate(self):
        self.write({
            'state': 'validated',
            'validated_by_id': self.env.user.id,
            'validation_date': fields.Datetime.now(),
        })
        return True
    
    def action_archive(self):
        self.write({'state': 'archived'})
        return True
    
    def action_create_revision(self):
        self.ensure_one()
        
        revision = self.copy({
            'original_id': self.id,
            'version': (self.version or 1.0) + 1.0,
            'is_original': False,
            'state': 'draft',
            'name': f"{self.name} (v{(self.version or 1.0) + 1.0})",
            'file_data': self.file_data,
            'file_name': self.file_name,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nouvelle révision',
            'res_model': 'legal.document',
            'res_id': revision.id,
            'view_mode': 'form',
        }
    
    def action_download(self):
        """Télécharger le document"""
        self.ensure_one()
        if not self.file_data:
            raise UserError(_("Aucun fichier attaché à ce document."))
        
        # Chercher l'attachment associé
        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', 'legal.document'),
            ('res_id', '=', self.id),
            ('name', '=', self.file_name)
        ], limit=1)
        
        if attachment:
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}/{self.file_name}?download=true',
                'target': 'self',
            }
        else:
            # Si pas d'attachment trouvé, régénérer
            if self.file_data and self.file_name:
                attachment = self.env['ir.attachment'].create({
                    'name': self.file_name,
                    'datas': self.file_data,
                    'res_model': 'legal.document',
                    'res_id': self.id,
                    'type': 'binary',
                })
                return {
                    'type': 'ir.actions.act_url',
                    'url': f'/web/content/{attachment.id}/{self.file_name}?download=true',
                    'target': 'self',
                }
            else:
                raise UserError(_("Impossible de télécharger le fichier."))
    
    def action_send_by_email(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Envoyer par email',
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_composition_mode': 'comment',
                'default_model': 'legal.document',
                'default_res_id': self.id,
                'default_subject': f"Document: {self.name}",
            },
        }
    
    # ==================== CONTRÔLES ====================
    @api.constrains('file_size')
    def _check_file_size(self):
        for doc in self:
            if doc.file_size > 50 * 1024 * 1024:  # 50 MB
                raise ValidationError(_("La taille du fichier ne peut pas dépasser 50 MB."))
    
    @api.constrains('file_hash')
    def _check_duplicate(self):
        for doc in self:
            if doc.file_hash and doc.case_id:
                duplicate = self.search([
                    ('file_hash', '=', doc.file_hash),
                    ('id', '!=', doc.id),
                    ('case_id', '=', doc.case_id.id),
                ])
                if duplicate:
                    raise ValidationError(_("Ce document existe déjà dans le dossier."))
    
    # ==================== CRUD ====================
    @api.model
    def create(self, vals):
        if 'attachment_id' in vals:
            del vals['attachment_id']
        
        # Nettoyer les données base64
        if vals.get('file_data'):
            try:
                file_data_str = vals['file_data'].strip()
                missing_padding = len(file_data_str) % 4
                if missing_padding:
                    file_data_str += '=' * (4 - missing_padding)
                base64.b64decode(file_data_str)
                vals['file_data'] = file_data_str
            except Exception as e:
                vals['file_data'] = False
        
        if 'version' in vals:
            if isinstance(vals['version'], str):
                try:
                    vals['version'] = float(vals['version'])
                except (ValueError, TypeError):
                    vals['version'] = 1.0
        else:
            vals['version'] = 1.0
        
        if not vals.get('created_by_id'):
            vals['created_by_id'] = self.env.user.id
        
        doc = super(LegalDocument, self).create(vals)
        
        # Forcer la création de l'attachment
        if doc.file_data and doc.file_name:
            self.env['ir.attachment'].create({
                'name': doc.file_name,
                'datas': doc.file_data,
                'res_model': 'legal.document',
                'res_id': doc.id,
                'type': 'binary',
            })
        
        return doc


class LegalDocumentTag(models.Model):
    _name = 'legal.document.tag'
    _description = 'Étiquette de document'
    
    name = fields.Char(string='Nom', required=True)
    color = fields.Integer(string='Couleur')
    document_ids = fields.Many2many(
        'legal.document',
        'legal_document_tag_rel',
        'tag_id', 'document_id',
        string='Documents'
    )
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Le nom de l\'étiquette doit être unique !'),
    ]