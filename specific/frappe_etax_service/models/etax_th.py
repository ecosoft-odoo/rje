# -*- coding: utf-8 -*-
##############################################################################
# Copyright 2023 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
##############################################################################

import base64
import json
import requests

from openerp.osv import fields, osv
from openerp import api
from openerp.exceptions import ValidationError
from openerp.tools.translate import _

from ..inet import inet_data_template as data_template

ETAX_SYSTEMS = ["INET ETax Document"]

class ETaxTH(osv.AbstractModel):
    _name = "etax.th"
    _description = "ETax Abstract Model"
    _columns = {
        'etax_doctype': fields.selection(
            [
                ('388', 'ใบกํากับภาษี'),
                ('T02', 'ใบแจ้งหนี้/ใบกํากับภาษี'),
                ('T03', 'ใบเสร็จรับเงิน/ใบกํากับภาษี'),
                ('T04', 'ใบส่งของ/ใบกํากับภาษี'),
                ('T05', 'ใบกํากับภาษี อย่างย่อ'),
                ('T01', 'ใบรับ (ใบเสร็จรับเงิน)'),
                ('80', 'ใบเพิมหนี้'),
                ('81', 'ใบลดหนี้'),
            ],
            'eTax Doctype',
            copy=False,
        ),
        'etax_status': fields.selection(
            [
                ('success', 'Success'),
                ('error', 'Error'),
                ('processing', 'Processing'),
                ('to_process', 'To Process'),
            ],
            'eTax Status',
            readonly=False,
            copy=False,
        ),
        'etax_error_code': fields.char(copy=False),
        'etax_error_message': fields.text(copy=False),
        'etax_transaction_code': fields.char(copy=False),
        'create_purpose_code': fields.char(copy=False),
        'create_purpose': fields.char(copy=False),
        'replaced_entry_id': fields.many2one(
            'account.invoice',
            'Replaced Document',
            readonly=True,
            copy=False,
            help='Currently this field only support invoice and not payment',
        ),
        'is_send_frappe': fields.boolean(copy=False),
        'doc_name_template': fields.many2one(
            'doc.type',
            'Invoice template',
            copy=False,
        ),
    }


    def _get_field_api(self):
        return [
            "status",
            "transaction_code",
            "error_code",
            "error_message",
            "pdf_url",
            "xml_url",
        ]

    def update_processing_document(self):
        if self.etax_status != "processing":
            return
        auth_token, server_url = self._get_connection()
        field_api = self._get_field_api()
        url = (
            "{}/api/resource/INET ETax Document?filters="
            '[["transaction_code","=","{}"]]'
            "&fields={}".format(server_url, self.etax_transaction_code, field_api)
        )
        print("url: ", url)
        authorization = "token %s" % auth_token
        print("auth_token: ", authorization)
        x=3/0
        res = requests.get(
            url,
            headers={"Authorization": "token %s" % auth_token},
            timeout=20,
        ).json()
        if not res.get("data"):
            return
        response = res.get("data")[0]
        self.write({
            'etax_status': response.get("status").lower(),
            'etax_error_code': response.get("error_code"),
            'etax_error_message': response.get("error_message"),
        })
        if self.etax_status == "success":
            pdf_url, xml_url = [response.get("pdf_url"), response.get("xml_url")]
            if pdf_url:
                self.env["ir.attachment"].create({
                    "name": "%s_signed.pdf" % self.display_name,
                    "datas": base64.b64encode(requests.get(pdf_url).content),
                    "type": "binary",
                    "res_model": self._name,
                    "res_id": self.id,
                })
            if xml_url:
                self.env["ir.attachment"].create({
                    "name": "%s_signed.xml" % self.display_name,
                    "datas": base64.b64encode(requests.get(xml_url).content),
                    "type": "binary",
                    "res_model": self._name,
                    "res_id": self.id,
                })

    def run_update_processing_document(self, cr, uid, context=None):
        records = self.pool.get('account.invoice').search(cr, uid, [("etax_status", "=", "processing")], context=context)
        for record in self.pool.get('account.invoice').browse(cr, uid, records, context=context):
            try:
                record.update_processing_document()
                cr.commit()
            except Exception:
                continue

    def sign_etax(self):
        self.ensure_one()
        form_type = self.doc_name_template.doc_source_template or False
        form_name = self.doc_name_template.name or False
        self._pre_validation(form_type, form_name)
        pdf_content = self._get_odoo_form(form_type, form_name)
        doc_data = data_template.prepare_data(self)
        self._send_to_frappe(doc_data, form_type, form_name, pdf_content)

    def run_sign_etax(self, cr, uid, context=None):
        records = self.pool.get('account.invoice').search(cr, uid, [("etax_status", "=", "to_process")], context=context)
        for record in self.pool.get('account.invoice').browse(cr, uid, records, context=context):
            try:
                record.sign_etax()
            except Exception as e:
                record.write({'etax_error_message': str(e)})
            cr.commit()

    def _pre_validation(self, form_type, form_name):
        if form_type not in ["odoo", "frappe"]:
            raise ValidationError(_("Form Type not in ['odoo', 'frappe']"))
        if form_type and not form_name:
            raise ValidationError(
                _("form_name is not specified for form_type=%s") % form_type
            )

    def _get_connection(self):
        auth_token = self.env["ir.config_parameter"].get_param("frappe_etax_service.frappe_auth_token")
        server_url = self.env["ir.config_parameter"].get_param("frappe_etax_service.frappe_server_url")
        if not auth_token or not server_url:
            raise ValidationError(
                _("Cannot connect to Frappe Server.\nFrappe Server URL or Frappe Auth Token are not defined.")
            )
        return (auth_token, server_url)

    def _get_odoo_form(self, form_type, form_name):
        if form_type == "odoo":
            ir_actions_report = self.pool.get('ir.actions.report.xml')
            matching_reports = ir_actions_report.search(self._cr, self._uid, [('name', '=', form_name)])
            if len(matching_reports) != 1:
                raise ValidationError(
                    _("Cannot find form - %s\nOr > 1 form with the same name") % form_name
                )
            report_obj = ir_actions_report.browse(self._cr, self._uid, matching_reports[0])
            report_type = report_obj.report_type
            if report_obj.report_type in ['qweb-html', 'qweb-pdf']:
                result, content_type = self.pool['report'].get_pdf(self._cr, self._uid, [self.id], report_obj.report_name,), 'pdf' 
                result = base64.b64encode(result)
                return result
        return ""

    def _send_to_frappe(self, doc_data, form_type, form_name, pdf_content):
        auth_token, server_url = self._get_connection()
        # # for test only

        print("doc_data: ", json.dumps(doc_data))
        # x=1/0
        try:
            res = requests.post(
                url="{}{}".format(server_url.replace("u'","").replace("'",""), "/api/method/etax_inet.api.etax.sign_etax_document"),
                headers={
                    "Authorization": "token {}".format(auth_token.replace("u'","").replace("'","")),
                },
                data={
                    "doc_data": json.dumps(doc_data),
                    "form_type": form_type,
                    "form_name": form_name,
                    "pdf_content": pdf_content,
                },
                timeout=20,
            ).json()
            response = res.get("message")
            if not response:
                self.write({
                    'etax_status': "error",
                    'etax_error_message': res.get("exception", res.get("_server_messages")),
                })
                return
            self.write({
                'etax_status': response.get("status").lower(),
                'etax_transaction_code': response.get("transaction_code"),
                'etax_error_code': response.get("error_code"),
                'etax_error_message': response.get("error_message"),
            })
            if self.etax_status == "success":
                pdf_url, xml_url = [response.get("pdf_url"), response.get("xml_url")]
                if pdf_url:
                    self.env["ir.attachment"].create({
                        "name": "%s_signed.pdf" % self.display_name,
                        "datas": base64.b64encode(requests.get(pdf_url).content),
                        "type": "binary",
                        "res_model": self._name,
                        "res_id": self.id,
                    })
                if xml_url:
                    self.env["ir.attachment"].create({
                        "name": "%s_signed.xml" % self.display_name,
                        "datas": base64.b64encode(requests.get(xml_url).content),
                        "type": "binary",
                        "res_model": self._name,
                        "res_id": self.id,
                    })
        except Exception as e:
            self.write({
                'etax_status': "error",
                'etax_error_message': str(e),
            })

    def button_etax_invoices(self, cr, uid, ids, context=None):
        return {
            "name": _("Sign e-Tax Invoice"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "wizard.select.etax.doctype",
            "target": "new",
        }
