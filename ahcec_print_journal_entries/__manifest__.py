# -*- coding: utf-8 -*-
{
	"name": "Print Journal Entries ",
	"author": "Aneesh.AV",
	"website": "https:www.softhealer.com",
	"support": "support@softhealer.com",
	"version" : "13.0.1",
	"category": "Accounting",
	"summary": """print journal report app, print multiple journal module, print journal entry odoo""",
	"description": """This module useful to print journal entries.
print journal report app, print multiple journal module, print journal entry odoo
	""",
	"depends" :  ['account'],
	"data": [
        "reports/report_account_journal_entries.xml",    
    ],
	"installable": True,
	"application": True,
	"auto_install": False,
}
