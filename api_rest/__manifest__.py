{
    "name": "api_rest",
    "summary": """
        api addon for Base REST""",
    "version": "13.0.2.0.1",
    "development_status": "Beta",
    "license": "LGPL-3",
    "author": "ACSONE SA/NV, " "Odoo Community Association (OCA)",
    "maintainers": ["lmignon"],
    "website": "https://acsone.eu/",
    "depends": ["base_rest", "component", "mrp","mrp_workorder"],
    "data": [
        'views/mrp_workcenter_productivity_loss_view.xml',
    ],
    "demo": [],
    "external_dependencies": {"python": ["jsondiff"]},
    "installable": True,
}
