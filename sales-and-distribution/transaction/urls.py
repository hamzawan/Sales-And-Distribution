from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='transaction-home'),

    path('chart_of_account/', views.chart_of_account, name='chart-of-account'),
    path('chart_of_account/edit', views.edit_chart_of_account, name='edit-chart-of-account'),
    path('chart_of_account/delete/<pk>', views.delete_account, name='delete-account'),
    path('nested_account/<id>', views.nested_account, name='nested-account'),
    
    # path('correct_db/', views.correct_DB, name='db-correct'),
    # path('correct_db_purchase/', views.correct_DB_purchase, name='db-correct-purchase'),

    path('reports/', views.reports, name='reports'),

    path('purchase/', views.purchase, name='purchase'),
    path('purchase/new/', views.new_purchase, name='new-purchase'),
    path('purchase_return/', views.purchase_return_summary, name='purchase-return'),
    path('purchase_return/new', views.new_purchase_return, name='new-purchase-return'),
    path('purchase/print/<pk>', views.print_purchase, name='purchase-print'),
    path('purchase/edit/<int:pk>', views.edit_purchase, name='edit-purchase'),
    path('purchase/delete/<pk>', views.delete_purchase, name='delete-purchase'),

    path('sale/', views.sale, name='sale'),
    path('sale/new/', views.new_sale, name='new-sale'),
    path('sale_return/', views.sale_return_summary, name='sale-return'),
    path('sale_return/new', views.new_sale_return, name='new-sale-return'),
    path('sale_return/edit/<pk>', views.edit_sale_return, name='edit-sale-return'),
    path('sale/commercial-print/<int:pk>', views.print_sale, name='sale-print-commercial'),
    path('sale/sales-tax-print/<int:pk>', views.print_sale_tax, name='sale-tax-print'),
    path('sale/edit/<pk>', views.edit_sale, name='edit-sale'),
    path('sale/delete/<pk>', views.delete_sale, name='delete-sale'),

    path('journal_voucher/new', views.journal_voucher, name='journal-voucher'),
    path('journal_voucher', views.journal_voucher_summary, name='journal-voucher-summary'),
    path('journal_voucher/edit/<pk>', views.edit_journal_voucher, name='edit-journal-voucher'),
    path('journal_voucher/delete/<pk>', views.delete_journal_voucher, name='delete-journal-voucher'),
    path('jv_pdf/<pk>', views.jv_pdf, name='jv-pdf'),

    path('bank_receiving_voucher', views.bank_receiving_voucher, name='bank-receiving-voucher'),
    path('bank_receiving_voucher/new', views.new_bank_receiving_voucher, name='new-bank-receiving'),
    path('bank_payment_voucher/', views.bank_payment_voucher, name='bank-payment-voucher'),
    path('bank_payment_voucher/new', views.new_bank_payment_voucher, name='new-bank-payment'),
    path('bank_payment_voucher/edit/<pk>', views.edit_bank_payment_voucher, name='edit-bank-payment'),
    path('bank_receiving_voucher/edit/<pk>', views.edit_bank_receiving_voucher, name='edit-bank-receiving'),
    path('trial_balance/pdf/<from_date>/<to_date>/<pk>', views.trial_balance, name = 'trial-balance'),
    path('account_ledger/pdf/<pk>/<from_date>/<to_date>', views.account_ledger, name='account-ledger'),
    path('account_ledger/credit_days/pdf/', views.account_ledger_with_credit_days, name='account-ledger-credit-days'),
    path('receivable_ledger/pdf/<pk>', views.receivable_ledger, name='receivable-ledger'),
    path('all_receivable_ledger/pdf/<pk>', views.all_receivable_ledger, name='all-receivable-ledger'),
    path('payable_ledger/pdf/<pk>', views.payable_ledger, name='payable-ledger'),
    path('sale_detail_report/pdf/<from_date>/<to_date>', views.sale_detail_report, name='sale-detail'),
    path('daily_report/pdf/<from_date>/<to_date>', views.daily_report, name='daily-report'),
    path('reports/report_sales_tax_print/<pk>', views.report_print_sale_tax, name='report-sale-tax-print'),
    path('reports/reports_all_sales_tax_inv/', views.reports_all_sales_tax_inv, name='report-all-sale-tax-inv'),


    path('cash_receiving_voucher', views.cash_receiving_voucher, name='cash-receiving-voucher'),
    path('cash_receiving_voucher/new/', views.new_cash_receiving_voucher, name='new-cash-receiving-voucher'),
    path('cash_receiving_voucher/view/<pk>', views.view_cash_receiving, name='view-cash-receiving'),
    path('cash_receiving_voucher/delete/<pk>', views.delete_cash_receiving, name='delete-cash-receiving'),
    path('crv_pdf/<pk>', views.crv_pdf, name='crv'),


    path('cash_payment_voucher', views.cash_payment_voucher, name='cash-payment-voucher'),
    path('cash_payment_voucher/new/', views.new_cash_payment_voucher, name='new-cash-payment-voucher'),
    path('cash_payment_voucher/view/<pk>', views.view_cash_payment, name='view-cash-payment'),
    path('cash_payment_voucher/delete/<pk>', views.delete_cash_payment, name='delete-cash-payment'),
    # path('check_cash_payment_voucher/new/', views.check_new_cash_payment_voucher, name='check-new-cash-payment-voucher'),
    path('cpv_pdf/<pk>', views.cpv_pdf, name='cpv'),

    path('job_order/', views.job_order, name='job-order'),
    path('job_order/new/', views.new_job_order, name='new-job-order'),
    path('job_order/edit/<pk>', views.edit_job_order, name='edit-job-order'),
    path('job_order/delete/<pk>', views.delete_job_order, name='delete-job-order'),

    path('test', views.new_test, name='new-test'),
    path('backup/db/', views.back_up_db, name = 'back-up-db'),
    path('backup/done/', views.back_up_done, name = 'back-up-done'),



]
