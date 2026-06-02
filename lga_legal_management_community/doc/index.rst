.. contents:: Table of Contents
   :depth: 3
   :local:

User Manual - Legal Case Management Module
==========================================


Table of Contents
=================


1. Introduction
2. Installation & Setup 
3. Dashboard
4. Case Management
5. Audience Management
6. Deadline Management
7. Document Management
8. Time Tracking & Invoicing
9. Client Portal
10. GDPR Compliance
11. Country Configuration
12. Reports & Analytics
13. Troubleshooting


Introduction
============


The **Legal Case Management Module** is a comprehensive solution for law firms and legal departments. It provides tools for managing legal cases, hearings, deadlines, documents, time tracking, and client communications.

Key Features
------------


- * Complete case lifecycle management
- * Hearing and court date tracking
- * Deadline and statute of limitations monitoring
- * Document management with secure storage
- * Time tracking and billing
- * Client portal for self-service
- * GDPR compliance tools
- * Multi-country legal system support
- * Multi-language interface


Installation & Setup
====================


Installation Steps
------------------

1. **Copy the module** to your Odoo addons directory:
.. code-block:: bash

   cp -r lga_legal_management /odoo/addons/


2. **Update the module list**:
   - Go to **Apps** → **Update Apps List**

3. **Install the module**:
   - Search for "Legal Case Management"
   - Click **Install**

4. **Configure your country**:
   - Go to **Legal** → **Configuration** → **Configure Country**
   - Select your country and click **Apply Configuration**

Initial Configuration
---------------------


Create User Groups
~~~~~~~~~~~~~~~~~~


.. list-table::
   :header-rows: 1

   * - Group
     - Permissions
   * - **User / Lawyer**
     - Create and manage own cases
   * - **Manager / Lead Lawyer**
     - Full access to all cases
   * - **Legal Administrator**
     - System configuration

Create Employees (Lawyers)
~~~~~~~~~~~~~~~~~~~~~~~~~~


1. Go to **Lawyers & Assistants**
2. Click **New**
3. Fill in:
   - Name, work email, etc.
   - **Is Lawyer** (check this box) in Legal Tab
   - **Hourly Rate** in Legal Tab
4. Save

Create Clients
~~~~~~~~~~~~~~


1. Go to **Client & Parties**
2. Click **New**
3. Fill in:
   - Name
   - Email
   - Phone
   - **Is Client** (check this box)
4. Save


Dashboard
=========


The dashboard provides an overview of your legal activities.

Accessing the Dashboard
-----------------------


**Menu:** Legal → Dashboard

Dashboard Components
--------------------


.. list-table::
   :header-rows: 1

   * - Component
     - Description
   * - **Active Cases**
     - Number of cases currently in progress
   * - **Today's Hearings**
     - Hearings scheduled for today
   * - **Urgent Deadlines**
     - Deadlines due within 7 days
   * - **Recent Cases**
     - Latest 5 cases created
   * - **Upcoming Hearings**
     - Next 5 scheduled hearings
   * - **Urgent Deadlines List**
     - Deadlines requiring immediate attention

Quick Actions
-------------


From the dashboard, you can:
- Click on any statistic to see details
- Use the **Quick Actions** buttons:
- **New Case**
- **New Hearing**
- **Log Time**
- **New Invoice**


Case Management
===============


Creating a New Case
-------------------


**Menu:** Legal → Cases → Create

**Required Fields:**

.. list-table::
   :header-rows: 1

   * - Field
     - Description
     - Example
   * - **Subject**
     - Brief case description
     - "Commercial dispute - Contract breach"
   * - **Main Client**
     - Client name
     - "ABC Corporation"
   * - **Lead Lawyer**
     - Responsible attorney
     - "Me Jean "
   * - **Case Type**
     - Legal domain
     - "Commercial Law"

**Optional Fields:**

.. list-table::
   :header-rows: 1

   * - Field
     - Description
   * - **Reference**
     - Client's internal reference
   * - **Associate Lawyers**
     - Additional lawyers on the case
   * - **Legal Assistants**
     - Paralegals or assistants
   * - **Opposing Parties**
     - Counterparties in the dispute
   * - **Lead Parties**
     - Main parties involved
   * - **Jurisdiction**
     - Court or arbitration venue
   * - **Dispute Amount**
     - Value in dispute
   * - **Estimated Fees**
     - Projected legal fees
   * - **Priority**
     - Low/Normal/High/Urgent/Critical
   * - **Deadline Date**
     - Target completion date

Viewing Case Details
--------------------


**Menu:** Legal → Cases → Click on any case

The case detail page has several tabs:

Information Tab
~~~~~~~~~~~~~~~

- Case reference and subject
- Client and lawyer information
- Opposing parties
- Dates (opening, closing, deadline)

Legal Tab
~~~~~~~~~

- Detailed description
- Facts and history
- Claims and demands
- Legal basis
- Applicable jurisprudence
- Legal strategy

Finance Tab
~~~~~~~~~~~

- Dispute amount
- Estimated vs actual fees
- Estimated vs actual costs
- Billing type
- Invoice summary

Audiences Tab
~~~~~~~~~~~~~

- List of all hearings for this case
- Add new hearing button

Deadlines Tab
~~~~~~~~~~~~~

- List of all deadlines for this case
- Add new deadline button

Documents Tab
~~~~~~~~~~~~~

- List of all documents for this case
- Upload new document button

Case Workflow
-------------


.. code-block:: text

   Draft → Pending → Active → Suspended → Closed → Archived


.. list-table::
   :header-rows: 1

   * - Action
     - Button
     - When to use
   * - **Activate**
     - Activate
     - When case is ready to start
   * - **Suspend**
     - Suspend
     - When case is on hold
   * - **Close**
     - Close
     - When case is resolved
   * - **Reopen**
     - Reopen
     - When closed case needs attention
   * - **Archive**
     - Archive
     - For completed cases (read-only)

Searching and Filtering Cases
-----------------------------


**Menu:** Legal → Cases

**Search Options:**
- By reference number
- By subject
- By client name

**Filters:**
- **My Cases** - Cases assigned to you
- **Active** - Cases in progress
- **Urgent** - High priority cases
- **Overdue** - Cases past deadline

**Group By:**
- Case Type
- Lawyer
- Status
- Priority


Audience Management
===================


Creating a Hearing
------------------


**Menu:** Legal → Audiences → Create

**Required Fields:**

.. list-table::
   :header-rows: 1

   * - Field
     - Description
   * - **Case**
     - Associated case
   * - **Type**
     - Preliminary, Hearing, Judgment, Appeal, etc.
   * - **Date**
     - Hearing date
   * - **Start Time**
     - Beginning time
   * - **Purpose**
     - Hearing objective

**Optional Fields:**

.. list-table::
   :header-rows: 1

   * - Field
     - Description
   * - **End Time**
     - Estimated end time
   * - **Court**
     - Jurisdiction name
   * - **Courtroom**
     - Room number
   * - **Judge**
     - Presiding judge
   * - **Clerk**
     - Court clerk
   * - **Prosecutor**
     - Prosecutor (if applicable)
   * - **Lawyers Present**
     - Attending attorneys
   * - **Clients Present**
     - Attending clients

Hearing Workflow
----------------


.. code-block:: text

   Scheduled → Confirmed → In Progress → Held → Postponed → Cancelled


.. list-table::
   :header-rows: 1

   * - Action
     - Description
   * - **Confirm**
     - Confirm the hearing with all parties
   * - **Start**
     - Begin the hearing (changes to In Progress)
   * - **Hold**
     - Mark as completed
   * - **Postpone**
     - Reschedule for another date
   * - **Cancel**
     - Cancel the hearing

Adding a Hearing Report
-----------------------


After the hearing, you can add:
- **Report** - Detailed minutes of the hearing
- **Decision** - Court's ruling or decision
- **Next Steps** - Actions to take following the hearing

Hearing Calendar View
---------------------


**Menu:** Legal → Audiences → Calendar

The calendar shows all scheduled hearings with color coding:
- 🟢 **Green** - Confirmed
- 🟡 **Yellow** - Scheduled
- 🔴 **Red** - Urgent/Cancelled


Deadline Management
===================


Creating a Deadline
-------------------


**Menu:** Legal → Deadlines → Create

**Required Fields:**

.. list-table::
   :header-rows: 1

   * - Field
     - Description
     - Examples
   * - **Case**
     - Associated case
     - "DOS/2025/0001"
   * - **Title**
     - Deadline description
     - "File appeal brief"
   * - **Type**
     - Deadline category
     - Procedure, Appeal, Payment
   * - **Due Date**
     - Expiration date
     - "2025-04-15"

**Optional Fields:**

.. list-table::
   :header-rows: 1

   * - Field
     - Description
   * - **Start Date**
     - Beginning of the period
   * - **Responsible**
     - Assigned lawyer
   * - **Priority**
     - Low/Medium/High/Critical
   * - **Description**
     - Detailed explanation
   * - **Consequences**
     - What happens if missed
   * - **Required Action**
     - What needs to be done
   * - **Legal Text**
     - Applicable law reference

Deadline Types
--------------


.. list-table::
   :header-rows: 1

   * - Type
     - Description
   * - **Procedure**
     - Court filing deadlines
   * - **Appeal**
     - Time to file an appeal
   * - **Prescription**
     - Statute of limitations
   * - **Deliberation**
     - Judgment deliberation period
   * - **Judgment**
     - Judgment pronouncement
   * - **Execution**
     - Enforcement of judgment
   * - **Payment**
     - Fee or cost payment
   * - **Communication**
     - Document exchange
   * - **Expertise**
     - Expert report submission

Deadline Status
---------------


.. list-table::
   :header-rows: 1

   * - Status
     - Color
     - Description
   * - **Draft**
     - Gray
     - Not yet activated
   * - **Active**
     - Blue
     - Currently counting down
   * - **Completed**
     - Green
     - Successfully met
   * - **Extended**
     - Yellow
     - Due date postponed
   * - **Overdue**
     - Red
     - Past due date
   * - **Cancelled**
     - Gray
     - No longer applicable

Deadline Alerts
---------------


The system automatically creates reminders at:
- **7 days** before deadline
- **3 days** before deadline
- **1 day** before deadline

Alerts appear in:
- Dashboard notifications
- Email notifications
- System activities


Document Management
===================


Uploading a Document
--------------------


**Menu:** Legal → Documents → Add Document

**Required Fields:**

.. list-table::
   :header-rows: 1

   * - Field
     - Description
   * - **Name**
     - Document title
   * - **Case**
     - Associated case
   * - **Type**
     - Contract, Pleading, Evidence, etc.
   * - **Category**
     - Legal, Procedural, Financial, etc.

**File Upload:**
- Click **Select File** to choose a document
- Supported formats: PDF, DOC, DOCX, XLS, XLSX, JPG, PNG
- Maximum size: 50 MB

Document Types
--------------


.. list-table::
   :header-rows: 1

   * - Type
     - Description
   * - **Contract**
     - Agreements and contracts
   * - **Pleading**
     - Court submissions
   * - **Brief**
     - Legal memoranda
   * - **Evidence**
     - Exhibits and proof
   * - **Correspondence**
     - Emails and letters
   * - **Judgment**
     - Court decisions
   * - **Order**
     - Court orders
   * - **Expertise**
     - Expert reports
   * - **Invoice**
     - Billing documents
   * - **Note**
     - Internal notes
   * - **Legal Basis**
     - Laws and regulations
   * - **Jurisprudence**
     - Case law

Document Actions
----------------


.. list-table::
   :header-rows: 1

   * - Action
     - Description
   * - **Download**
     - Save document to your computer
   * - **Send by Email**
     - Email document to client or colleague
   * - **Create Revision**
     - Create a new version of the document
   * - **Delete**
     - Remove document (requires confirmation)

Document Tags
-------------


You can add tags to documents for better organization:
- **Confidential** - Sensitive information
- **Urgent** - Requires immediate attention
- **Important** - Key document
- **To Archive** - Ready for archiving


Time Tracking & Invoicing
=========================


Logging Time
------------


**Menu:** Legal → Timesheets → Create

**Required Fields:**

.. list-table::
   :header-rows: 1

   * - Field
     - Description
   * - **Case**
     - Associated case
   * - **Date**
     - Work date
   * - **Start Time**
     - Beginning time
   * - **End Time**
     - Ending time
   * - **Activity Type**
     - Type of work performed
   * - **Description**
     - Brief explanation

Activity Types
--------------


.. list-table::
   :header-rows: 1

   * - Type
     - Description
   * - **Consultation**
     - Client meetings
   * - **Legal Research**
     - Case law and legislation research
   * - **Drafting**
     - Document preparation
   * - **Correspondence**
     - Emails and letters
   * - **Hearing**
     - Court appearances
   * - **Travel**
     - Time spent traveling
   * - **Meeting**
     - Internal meetings
   * - **Phone Call**
     - Telephone consultations
   * - **Administration**
     - Administrative tasks
   * - **Review**
     - Document review
   * - **Negotiation**
     - Settlement discussions
   * - **Expertise**
     - Expert analysis

Time Entry Workflow
-------------------


.. code-block:: text

   Draft → Submitted → Validated → Invoiced → Rejected


.. list-table::
   :header-rows: 1

   * - Action
     - Description
   * - **Submit**
     - Send for validation (lawyer)
   * - **Validate**
     - Approve time entry (manager)
   * - **Reject**
     - Return with rejection reason
   * - **Invoice**
     - Create invoice from time entry

Creating an Invoice
-------------------


1. Go to **Legal** → **Timesheets**
2. Select validated time entries
3. Click **Invoice**
4. Review invoice details
5. Click **Confirm**

Invoice Status
--------------


.. list-table::
   :header-rows: 1

   * - Status
     - Description
   * - **Draft**
     - Not yet confirmed
   * - **Posted**
     - Confirmed and sent
   * - **Paid**
     - Payment received
   * - **Canceled**
     - Invoice voided


Client Portal
=============


Overview
--------


The client portal allows clients to:
- View their cases
- See upcoming hearings
- Track deadlines
- Download documents
- Manage GDPR consent

Accessing the Portal
--------------------


**URL:** `http://your-odoo.com/my`

Enabling Portal Access for a Client
-----------------------------------


1. Go to **Contacts** → Select client
2. Go to **GDPR** tab
3. Check **Portal Access**
4. Click **Invite to Portal**

The client will receive an email with login instructions.

Client Portal Features
----------------------


Dashboard
~~~~~~~~~

- Case count
- Upcoming hearings
- Urgent deadlines
- Document count

My Cases
~~~~~~~~

- List of all client cases
- Case details (subject, status, dates)
- Access to case documents

My Hearings
~~~~~~~~~~~

- List of scheduled hearings
- Hearing details (date, time, court)
- Hearing status

My Deadlines
~~~~~~~~~~~~

- List of deadlines
- Days remaining
- Urgent deadlines highlighted

My Documents
~~~~~~~~~~~~

- List of case documents
- Document download

GDPR Consent
~~~~~~~~~~~~

- View consent status
- Give or withdraw consent
- Request data access
- Export personal data
- Request data deletion


GDPR Compliance
===============


Overview
--------


The module includes complete GDPR compliance tools:

- **Consent Management** - Record client consent
- **Data Access Requests** - Handle access requests
- **Data Portability** - Export client data (JSON)
- **Right to Erasure** - Anonymize client data
- **Audit Logs** - Track data access

Managing Client Consent
-----------------------


**Menu:** Legal → GDPR → Consentements

Giving Consent
~~~~~~~~~~~~~~


1. Go to client record
2. Open **GDPR** tab
3. Click **Give My Consent**
4. Accept terms and privacy policy
5. Submit

Withdrawing Consent
~~~~~~~~~~~~~~~~~~~


1. Go to client record
2. Open **GDPR** tab
3. Enter withdrawal reason
4. Click **Withdraw My Consent**

Data Access Requests
--------------------


**Menu:** Legal → GDPR → Requests

Types of Requests
~~~~~~~~~~~~~~~~~


.. list-table::
   :header-rows: 1

   * - Type
     - Description
   * - **Access**
     - Request copy of personal data
   * - **Rectification**
     - Request data correction
   * - **Erasure**
     - Request data deletion (Right to be forgotten)
   * - **Restriction**
     - Request processing restriction
   * - **Portability**
     - Request data export
   * - **Objection**
     - Object to data processing

Processing a Request
~~~~~~~~~~~~~~~~~~~~


1. Request appears in **GDPR Requests** list
2. Click **Process**
3. For portability: Data is automatically exported (JSON)
4. For erasure: Data is anonymized
5. Request status changes to **Completed**


Audit Logs
----------


**Menu:** Legal → GDPR → Audit Log

The audit log records:
- Who accessed what data
- When the access occurred
- What action was performed (read, write, delete)
- IP address and user agent


Country Configuration
=====================


Overview
--------


The module supports legal systems from multiple countries. You can configure country-specific legal parameters.

Configuring Your Country
------------------------


**Menu:** Legal → Configuration → Configure Country

1. Select your country from the list
2. Review the configuration:
   - Legal system (Civil law, Common law, Mixed)
   - Court system (Unified, Federal, Dual)
   - Statute of limitations (years)
   - Appeal deadline (days)
   - Cassation deadline (days)
   - VAT rate
3. Click **Apply Configuration**

Pre-configured Countries
------------------------


.. list-table::
   :header-rows: 1

   * - Country
     - Legal System
     - Appeal Deadline
     - VAT Rate
   * - France
     - Civil Law
     - 30 days
     - 20%
   * - Germany
     - Civil Law
     - 30 days
     - 19%
   * - United Kingdom
     - Common Law
     - 21 days
     - 20%
   * - United States
     - Common Law
     - 30 days
     - 0%
   * - Japan
     - Civil Law
     - 14 days
     - 10%
   * - Brazil
     - Civil Law
     - 15 days
     - 0%
   * - China
     - Socialist Law
     - 15 days
     - 6%

Adding a New Country
--------------------


1. Go to **Legal** → **Configuration** → **Country Configurations**
2. Click **Create**
3. Fill in all legal parameters
4. Save
5. Click **Activate** to make it active

What Changes When You Change Country
------------------------------------


.. list-table::
   :header-rows: 1

   * - Component
     - Effect
   * - **Deadlines**
     - Appeal and cassation deadlines update
   * - **VAT Rate**
     - Invoice tax calculation updates
   * - **Court System**
     - Available court levels update
   * - **Legal Texts**
     - Procedure code references update
   * - **Language**
     - Legal terms adapt to country language


Reports & Analytics
===================


Financial Reports
-----------------


**Menu:** Legal → Finance → Financial Reports

Available reports:

.. list-table::
   :header-rows: 1

   * - Report
     - Description
   * - **Case Profitability**
     - Profitability per case
   * - **Lawyer Performance**
     - Hours and billings per lawyer
   * - **Outstanding Invoices**
     - Unpaid invoices
   * - **Revenue by Case Type**
     - Revenue breakdown

Profitability Analysis
----------------------


**Menu:** Legal → Finance → Profitability Analysis

Parameters:
- **Date Range** - Analysis period
- **Lawyers** - Select specific lawyers
- **Case Types** - Filter by case type
- **Group By** - Lawyer, Case Type, Client, Month

Results include:
- Total hours
- Total invoiced
- Total paid
- Outstanding amount
- Profitability percentage
- Realization rate

Exporting Reports
-----------------


Reports can be exported to:
- **Excel** (.xlsx)
- **CSV** (.csv)
- **PDF** (.pdf)


Troubleshooting
===============


Common Issues and Solutions
---------------------------


Issue: Cannot create a case
~~~~~~~~~~~~~~~~~~~~~~~~~~~


**Solution:**
1. Verify you have created at least one client and one lawyer
2. Check that you have the required user permissions
3. Ensure all required fields are filled

Issue: Client cannot access portal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


**Solution:**
1. Verify client has an email address
2. Check **Portal Access** is enabled in client record
3. Resend invitation email
4. Check spam folder

Issue: Deadlines not showing alerts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


**Solution:**
1. Verify the deadline is in **Active** status
2. Check that reminders are enabled in configuration
3. Run the scheduled action manually

Issue: Documents not uploading
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


**Solution:**
1. Check file size (max 50 MB)
2. Verify file format is supported
3. Check browser console for errors
4. Try a different browser

Issue: Time entries cannot be invoiced
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


**Solution:**
1. Verify time entry is **Validated**
2. Check that **Billable** is checked
3. Ensure client has a valid billing address
4. Check accounting configuration

Issue: GDPR data export not working
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


**Solution:**
1. Verify the client has given consent
2. Check that the request is in **Processing** status
3. Ensure the client has an email address
4. Check server logs for errors

Support
-------


For technical support:
- **Email:** support@eanda.tech
- **Documentation:** https://eanda.tech


Keyboard Shortcuts
==================


.. list-table::
   :header-rows: 1

   * - Shortcut
     - Action
   * - `Ctrl + S`
     - Save current form
   * - `Ctrl + Shift + D`
     - Duplicate record
   * - `Ctrl + Shift + A`
     - Add new line in list
   * - `Ctrl + Shift + R`
     - Remove line from list
   * - `Alt + Enter`
     - Save and edit next
   * - `Ctrl + E`
     - Export current view


Glossary
========


.. list-table::
   :header-rows: 1

   * - Term
     - Definition
   * - **Case**
     - A legal matter or dispute handled by the firm
   * - **Hearing**
     - A court session where arguments are presented
   * - **Deadline**
     - A date by which an action must be completed
   * - **Statute of Limitations**
     - Time limit for filing a lawsuit
   * - **Appeal**
     - Request to review a court decision
   * - **Cassation**
     - Appeal to the Supreme Court
   * - **Prescription**
     - Expiration of legal rights over time
   * - **GDPR**
     - General Data Protection Regulation
   * - **DPO**
     - Data Protection Officer
   * - **Lead Lawyer**
     - Primary attorney responsible for a case
   * - **Associate Lawyer**
     - Secondary attorney assisting on a case
   * - **Opposing Party**
     - Counterparty in a legal dispute
   * - **Jurisdiction**
     - Court's authority to hear a case


Version History
===============


.. list-table::
   :header-rows: 1

   * - Version
     - Date
     - Changes
   * - 1.0.0
     - 2025-04-05
     - Initial release
   * - 1.1.0
     - 2025-04-06
     - Added GDPR compliance
   * - 1.2.0
     - 2025-04-06
     - Added client portal
   * - 1.3.0
     - 2025-04-06
     - Added multi-country support


© 2025 E&A Tech. All rights reserved.