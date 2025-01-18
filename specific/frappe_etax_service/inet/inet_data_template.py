def prepare_data(doc):
    if doc._name == "account.invoice":  # Invoice
        return prepare_data_invoice(doc)
    if doc._name == "account.voucher":
        return prepare_data_payment(doc)

def calculate_tax_amount(price_subtotal, tax_rate):
    return price_subtotal * tax_rate

def prepare_data_invoice(doc):
    d = {}
    d["currency_code"] = doc.currency_id.name
    d["document_type_code"] = doc.etax_doctype
    d["document_id"] = doc.preprint_number
    d["document_issue_dtm"] = doc.date_invoice + "T00:00:00"
    d["create_purpose_code"] = doc.create_purpose_code
    d["create_purpose"] = doc.create_purpose
    d["ref_document_id"] = doc._get_origin_data()[2]
    d["ref_document_issue_dtm"] = doc._get_origin_data()[0]
    d["ref_document_type_code"] = doc._get_origin_data()[1]
    d["buyer_ref_document"] = doc.origin and doc.origin or ""
    d["seller_branch_id"] = doc._get_branch_id() or doc.company_id.partner_id.taxbranch
    d["source_system"] = (
        doc.env["ir.config_parameter"].sudo().get_param("web.base.url", "")
    )
    d["send_mail"] = 'Y' if doc.env["ir.config_parameter"].sudo().get_param("frappe_etax_service.is_send_etax_email") == 'True' else 'N'
    d["seller_tax_id"] = doc.company_id.vat
    d["buyer_name"] = doc.partner_id.name
    d["buyer_type"] = "TXID"  # TXID, NIDN, CCPT, OTHR (no taxid)
    d["buyer_tax_id"] = doc.partner_id.vat
    d["buyer_branch_id"] = doc.partner_id.taxbranch or "00000"
    d["buyer_email"] = doc.partner_id.email_etax
    d["buyer_zip"] = doc.partner_id.zip
    d["buyer_building_name"] = ""
    d["buyer_building_no"] = ""
    d["buyer_address_line1"] = doc.partner_id.street
    d["buyer_address_line2"] = doc.partner_id.street2
    d["buyer_address_line3"] = ""
    # buyer_address_line4 use for send PO number
    d["buyer_address_line4"] = doc._get_po_number_payment_terms()[0]
    # buyer_address_line5 use for payment term
    d["buyer_address_line5"] = doc._get_po_number_payment_terms()[1]
    d["buyer_city_name"] = doc.partner_id.city
    d["buyer_country_code"] = (
        doc.partner_id.country_id and doc.partner_id.country_id.code or ""
    )
    doc_lines = []
    for line in doc.invoice_line.filtered(
        lambda inv_line: inv_line.price_unit > 0
    ):
        doc_lines.append(
            {
                "product_code": line.product_id and line.product_id.default_code or "",
                "product_name": line.name,
                "product_price": line.price_unit,
                "product_quantity": line.quantity,
                "product_unit_code": line.uos_id and line.uos_id.name or "PCS",
                "line_tax_type_code": line.invoice_line_tax_id.name and "VAT" or "FRE",
                "line_tax_rate": line.invoice_line_tax_id and line.invoice_line_tax_id[0].amount or 0.00,
                "line_base_amount": line.invoice_line_tax_id and line.price_subtotal or 0.00,
                "line_tax_amount": line.invoice_line_tax_id
                and calculate_tax_amount(line.price_subtotal, line.invoice_line_tax_id[0].amount)
                or 0.0,
                "line_total_amount": line.invoice_line_tax_id
                and line.price_subtotal + calculate_tax_amount(line.price_subtotal, line.invoice_line_tax_id[0].amount)
                or 0.0,
            }
        )
    d["line_item_information"] = doc_lines
    d["original_amount_untaxed"] = doc._get_additional_amount()[0]
    d["final_amount_untaxed"] = doc._get_additional_amount()[2]
    d["adjust_amount_untaxed"] = doc._get_additional_amount()[1]
    return d


def prepare_data_payment(doc):
    d = {}
    d["currency_code"] = doc.currency_id.name
    d["document_type_code"] = doc.etax_doctype
    d["document_id"] = doc.number
    d["document_issue_dtm"] = doc.date and doc.date + "T00:00:00"
    # As of now, no use for payment
    d["create_purpose_code"] = ""
    d["create_purpose"] = ""
    d["ref_document_id"] = ""
    d["ref_document_issue_dtm"] = ""
    d["ref_document_type_code"] = ""
    # --
    d["buyer_ref_document"] = doc.reference
    d["seller_branch_id"] = doc.company_id.partner_id.taxbranch
    d["source_system"] = (
        doc.env["ir.config_parameter"].sudo().get_param("web.base.url", "")
    )
    d["send_mail"] = 'Y' if doc.env["ir.config_parameter"].sudo().get_param("frappe_etax_service.is_send_etax_email") == 'True' else 'N'
    d["seller_tax_id"] = doc.company_id.vat
    d["buyer_name"] = doc.partner_id.name
    d["buyer_type"] = "TXID"  # TXID, NIDN, CCPT, OTHR (no taxid)
    d["buyer_tax_id"] = doc.partner_id.vat
    d["buyer_branch_id"] = doc.partner_id.taxbranch or "00000"
    d["buyer_email"] = doc.partner_id.email_etax
    d["buyer_zip"] = doc.partner_id.zip
    d["buyer_building_name"] = ""
    d["buyer_building_no"] = ""
    d["buyer_address_line1"] = doc.partner_id.street
    d["buyer_address_line2"] = doc.partner_id.street2
    d["buyer_address_line3"] = ""
    d["buyer_address_line4"] = ""
    d["buyer_address_line5"] = ""
    d["buyer_city_name"] = doc.partner_id.city
    d["buyer_country_code"] = (
        doc.partner_id.country_id and doc.partner_id.country_id.code or ""
    )
    doc_lines = []
    for line in doc.tax_line_normal:
        doc_lines.append(
            {
                "product_code": line.invoice_id.preprint_number,
                "product_name": line.invoice_id.preprint_number,
                "product_price": line.base,
                "product_quantity": 1,
                "line_tax_type_code": line.tax_id.name and "VAT" or "FRE",
                "line_tax_rate": line.tax_id.amount,
                "line_base_amount": line.base,
                "line_tax_amount": line.amount,
                "line_total_amount": line.base + line.amount,
            }
        )
    d["line_item_information"] = doc_lines
    # As of now, no use for payment
    d["original_amount_untaxed"] = False
    d["final_amount_untaxed"] = False
    d["adjust_amount_untaxed"] = False
    # --
    return d
