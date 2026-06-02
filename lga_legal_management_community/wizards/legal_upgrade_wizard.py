# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import urllib.parse

class LegalUpgradeWizard(models.TransientModel):
    _name = 'legal.upgrade.wizard'
    _description = 'Assistant de mise à niveau'
    
    version_type = fields.Selection([
        ('basic', 'Version Basic (€299/an)'),
        ('enterprise', 'Version Enterprise (€1500-5000/an)'),
    ], string='Version souhaitée', required=True, default='basic')
    
    company_name = fields.Char(string='Nom du cabinet', required=True)
    contact_name = fields.Char(string='Nom du contact', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Téléphone')
    company_size = fields.Selection([
        ('1-5', '1-5 avocats'),
        ('6-20', '6-20 avocats'),
        ('21-50', '21-50 avocats'),
        ('50+', 'Plus de 50 avocats'),
    ], string='Taille du cabinet', required=True)
    
    message = fields.Text(string='Message / Besoins spécifiques')
    
    def action_request_quote(self):
        """Rediriger vers le formulaire externe avec données pré-remplies"""
        self.ensure_one()
        
        # URL de votre formulaire externe
        base_url = "https://eanda.tech/odoo/lga/quote-request"
        
        # Préparer les paramètres
        params = {
            'version': self.version_type,
            'company_name': self.company_name,
            'contact_name': self.contact_name,
            'email': self.email,
            'phone': self.phone or '',
            'message': self.message or '',
            'source': 'odoo_module',
            'module_version': '18.0.1.0.0',
        }
        
        # Encoder les paramètres dans l'URL
        query_string = urllib.parse.urlencode(params)
        full_url = f"{base_url}?{query_string}"
        
        # Ouvrir le formulaire externe
        return {
            'type': 'ir.actions.act_url',
            'url': full_url,
            'target': 'new',
        }
    
    def action_buy_now(self):
        """Rediriger vers la page d'achat"""
        self.ensure_one()
        
        if self.version_type == 'basic':
            url = self.env['ir.config_parameter'].sudo().get_param('legal.upgrade.url.basic')
        else:
            url = self.env['ir.config_parameter'].sudo().get_param('legal.upgrade.url.enterprise')
        
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
    
    def _get_sales_team(self):
        """Récupérer l'équipe commerciale"""
        team = self.env['crm.team'].search([('name', 'ilike', 'Ventes')], limit=1)
        if not team:
            team = self.env['crm.team'].search([], limit=1)
        return team
    
    def _send_notification_email(self):
        """Envoyer un email de notification"""
        template = self.env.ref('lga_legal_management_community.email_upgrade_request', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)


class LegalUpgradeBanner(models.TransientModel):
    _name = 'legal.upgrade.banner'
    _description = 'Bannière de mise à niveau'
    
    def action_show_upgrade_wizard(self):
        """Afficher l'assistant de mise à niveau"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Passer à la version payante',
            'res_model': 'legal.upgrade.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_version_type': 'basic'},
        }
    
    def action_dismiss_banner(self):
        """Fermer la bannière"""
        self.env['ir.config_parameter'].sudo().set_param('legal.upgrade.banner_dismissed', '1')
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }