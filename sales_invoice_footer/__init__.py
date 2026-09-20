from . import models


def _post_init_set_paperformat(env):
    paperformat = env.ref("sales_invoice_footer.paperformat_bank_footer", raise_if_not_found=False)
    if not paperformat:
        return
    for xmlid in ("sale.action_report_saleorder", "account.account_invoices"):
        report = env.ref(xmlid, raise_if_not_found=False)
        if report:
            report.paperformat_id = paperformat
