# -*- coding: utf-8 -*-
{
	"name": "Print Journal Entries ",
	"author": "Aneesh.AV",
	"version" : "15.0.1",
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
	"license": "LGPL-3",
}
