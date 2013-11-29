{
    "name" : "Products Customer Code",
    "version" : "1.0",
    "author" : "Vauxoo modify jmesteve",
    "website" : "",
    "license" : "AGPL-3",
    "category" : "Generic Modules/Product",
    "depends" : ["base", "product", "stock","sale_stock"],
    "init_xml" : [],
    "demo_xml" : [],
    "description": """
Add manies Codes of Customer's in product
     """,
    "update_xml" : ["security/product_customer_code_security.xml",
                    "security/ir.model.access.csv",
                    "product_customer_code_view.xml",
                    "product_product_view.xml",
                    'sale_extend.xml',
                    ],
    "active": False,
    "installable": True,
}
