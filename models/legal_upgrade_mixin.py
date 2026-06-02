# -*- coding: utf-8 -*-
from odoo import models, api, _

class LegalUpgradeMixin(models.AbstractModel):
    _name = 'legal.upgrade.mixin'
    _description = 'Mixin pour les fonctionnalités premium'
    
    def _check_premium_feature(self, feature_name, message=None):
        """Vérifie si une fonctionnalité premium est disponible"""
        if not message:
            message = _(
                "Cette fonctionnalité est disponible dans la version payante.\n\n"
                "✨ Version Basic (€299/an):\n"
                "• Facturation et devis\n"
                "• Portail client\n"
                "• API REST\n"
                "• Rapports avancés\n\n"
                "🏢 Version Enterprise (sur devis):\n"
                "• Intelligence artificielle\n"
                "• Application mobile\n"
                "• OCR avancé\n"
                "• Support prioritaire\n\n"
                "👉 Contactez-nous pour un devis personnalisé: sales@cabinet-mukendi.cd"
            )
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Version payante requise',
            'res_model': 'legal.upgrade.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_version_type': 'basic', 'default_message': message},
        }
    
    def action_upgrade_required(self):
        """Action appelée quand une fonctionnalité premium est bloquée"""
        return self._check_premium_feature('feature')