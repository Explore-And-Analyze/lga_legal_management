# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError
from datetime import date, timedelta

class TestLegalCase(TransactionCase):
    
    def setUp(self):
        super(TestLegalCase, self).setUp()
        
        # Création des données de test
        self.client = self.env['res.partner'].create({
            'name': 'Client Test',
            'is_client': True,
        })
        
        self.lawyer = self.env['legal.lawyer'].create({
            'name': 'Avocat Test',
            'is_lawyer': True,
        })
        
        self.case_type = self.env['legal.case.type'].create({
            'name': 'Type Test',
            'code': 'TEST',
        })
        
        self.case = self.env['legal.case'].create({
            'client_id': self.client.id,
            'lead_lawyer_id': self.lawyer.id,
            'case_type_id': self.case_type.id,
            'subject': 'Test Case',
            'opening_date': date.today(),
        })
    
    def test_case_creation(self):
        """Test de création d'un dossier"""
        self.assertTrue(self.case.name)
        self.assertEqual(self.case.state, 'draft')
        self.assertEqual(self.case.subject, 'Test Case')
    
    def test_case_workflow(self):
        """Test du workflow de dossier"""
        self.case.action_activate()
        self.assertEqual(self.case.state, 'active')
        
        self.case.action_suspend()
        self.assertEqual(self.case.state, 'suspended')
        
        self.case.action_close()
        self.assertEqual(self.case.state, 'closed')
        self.assertTrue(self.case.closing_date)
    
    def test_computed_fields(self):
        """Test des champs calculés"""
        # Test audience_count
        self.env['legal.audience'].create({
            'case_id': self.case.id,
            'audience_type': 'preliminary',
            'date': date.today() + timedelta(days=5),
            'start_time': 9.0,
            'purpose': 'Test Audience',
        })
        self.assertEqual(self.case.audience_count, 1)
        
        # Test deadline_status
        self.env['legal.deadline'].create({
            'case_id': self.case.id,
            'name': 'Test Deadline',
            'deadline_type': 'procedure',
            'deadline_date': date.today() + timedelta(days=3),
        })
        self.case._compute_deadline_status()
        self.assertEqual(self.case.deadline_status, 'warning')


class TestLegalAudience(TransactionCase):
    
    def setUp(self):
        super(TestLegalAudience, self).setUp()
        
        self.case = self.env['legal.case'].create({
            'client_id': self.env['res.partner'].create({'name': 'Client Test', 'is_client': True}).id,
            'lead_lawyer_id': self.env['legal.lawyer'].create({'name': 'Avocat Test', 'is_lawyer': True}).id,
            'case_type_id': self.env['legal.case.type'].create({'name': 'Type Test', 'code': 'TEST'}).id,
            'subject': 'Test Case',
        })
        
        self.audience = self.env['legal.audience'].create({
            'case_id': self.case.id,
            'audience_type': 'preliminary',
            'date': date.today() + timedelta(days=10),
            'start_time': 9.0,
            'purpose': 'Test Audience',
        })
    
    def test_audience_creation(self):
        """Test de création d'une audience"""
        self.assertTrue(self.audience.name)
        self.assertEqual(self.audience.state, 'scheduled')
        self.assertEqual(self.audience.case_id, self.case)
    
    def test_audience_workflow(self):
        """Test du workflow d'audience"""
        self.audience.action_confirm()
        self.assertEqual(self.audience.state, 'confirmed')
        
        self.audience.action_start()
        self.assertEqual(self.audience.state, 'in_progress')
        
        self.audience.action_held()
        self.assertEqual(self.audience.state, 'held')
    
    def test_audience_postpone(self):
        """Test du report d'audience"""
        old_date = self.audience.date
        new_date = date.today() + timedelta(days=20)
        
        wizard = self.env['legal.audience.postpone.wizard'].create({
            'audience_id': self.audience.id,
            'new_date': new_date,
            'new_start_time': 10.0,
            'reason': 'Test report',
        })
        
        wizard.action_postpone()
        
        self.assertEqual(self.audience.date, new_date)
        self.assertEqual(self.audience.state, 'postponed')
        self.assertEqual(self.audience.postponement_reason, 'Test report')


class TestLegalDeadline(TransactionCase):
    
    def setUp(self):
        super(TestLegalDeadline, self).setUp()
        
        self.case = self.env['legal.case'].create({
            'client_id': self.env['res.partner'].create({'name': 'Client Test', 'is_client': True}).id,
            'lead_lawyer_id': self.env['legal.lawyer'].create({'name': 'Avocat Test', 'is_lawyer': True}).id,
            'case_type_id': self.env['legal.case.type'].create({'name': 'Type Test', 'code': 'TEST'}).id,
            'subject': 'Test Case',
        })
        
        self.deadline = self.env['legal.deadline'].create({
            'case_id': self.case.id,
            'name': 'Test Deadline',
            'deadline_type': 'procedure',
            'deadline_date': date.today() + timedelta(days=15),
        })
    
    def test_deadline_creation(self):
        """Test de création d'un délai"""
        self.assertEqual(self.deadline.state, 'draft')
        self.assertEqual(self.deadline.duration_days, 15)
    
    def test_deadline_activation(self):
        """Test d'activation d'un délai"""
        self.deadline.action_activate()
        self.assertEqual(self.deadline.state, 'active')
    
    def test_deadline_completion(self):
        """Test de complétion d'un délai"""
        self.deadline.action_activate()
        self.deadline.action_complete()
        self.assertEqual(self.deadline.state, 'completed')
        self.assertEqual(self.deadline.completion_date, date.today())
    
    def test_deadline_extension(self):
        """Test de prolongation d'un délai"""
        self.deadline.action_activate()
        old_date = self.deadline.deadline_date
        new_date = old_date + timedelta(days=10)
        
        wizard = self.env['legal.deadline.extension.wizard'].create({
            'deadline_id': self.deadline.id,
            'new_date': new_date,
            'reason': 'Test extension',
        })
        
        wizard.action_extend()
        
        self.assertEqual(self.deadline.deadline_date, new_date)
        self.assertEqual(self.deadline.state, 'extended')


class TestLegalTimesheet(TransactionCase):
    
    def setUp(self):
        super(TestLegalTimesheet, self).setUp()
        
        self.case = self.env['legal.case'].create({
            'client_id': self.env['res.partner'].create({'name': 'Client Test', 'is_client': True}).id,
            'lead_lawyer_id': self.env['legal.lawyer'].create({
                'name': 'Avocat Test',
                'is_lawyer': True,
                'hourly_rate': 200.0,
            }).id,
            'case_type_id': self.env['legal.case.type'].create({'name': 'Type Test', 'code': 'TEST'}).id,
            'subject': 'Test Case',
        })
        
        self.timesheet = self.env['legal.timesheet'].create({
            'case_id': self.case.id,
            'lawyer_id': self.case.lead_lawyer_id.id,
            'date': date.today(),
            'start_time': 9.0,
            'end_time': 12.0,
            'activity_type': 'research',
            'name': 'Test Timesheet',
        })
    
    def test_timesheet_creation(self):
        """Test de création d'une feuille de temps"""
        self.assertEqual(self.timesheet.duration_hours, 3.0)
        self.assertEqual(self.timesheet.duration_minutes, 180)
        self.assertEqual(self.timesheet.cost_amount, 600.0)  # 3h * 200€
        self.assertEqual(self.timesheet.state, 'draft')
    
    def test_timesheet_workflow(self):
        """Test du workflow de feuille de temps"""
        self.timesheet.action_submit()
        self.assertEqual(self.timesheet.state, 'submitted')
        
        self.timesheet.action_validate()
        self.assertEqual(self.timesheet.state, 'validated')
    
    def test_timesheet_rejection(self):
        """Test de rejet d'une feuille de temps"""
        self.timesheet.action_submit()
        
        wizard = self.env['legal.timesheet.reject.wizard'].create({
            'timesheet_id': self.timesheet.id,
            'reason': 'Heures non justifiées',
        })
        
        wizard.action_reject()
        
        self.assertEqual(self.timesheet.state, 'rejected')
        self.assertEqual(self.timesheet.rejection_reason, 'Heures non justifiées')