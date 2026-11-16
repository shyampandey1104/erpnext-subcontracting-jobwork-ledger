# Copyright (c) 2026, Shyamkumar Pandey and contributors
# For license information, please see license.txt

app_name = "subcontracting"
app_title = "Erpnext Subcontracting Jobwork Ledger"
app_publisher = "Shyamkumar Pandey"
app_description = "Erpnext Subcontracting Jobwork Ledger for Frappe and ERPNext"
app_email = "shyampandey1104@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------
app_include_css = "/assets/subcontracting/css/subcontracting.bundle.css"
app_include_js = "/assets/subcontracting/js/subcontracting.bundle.js"

# Document Events
# ---------------
doc_events = {
    "DocType Event": {
        "on_submit": "subcontracting.engine.on_document_submit",
        "on_cancel": "subcontracting.engine.on_document_cancel"
    }
}

# Scheduled Tasks
# ---------------
scheduler_events = {
    "daily": [
        "subcontracting.engine.daily_scheduled_sync"
    ]
}
