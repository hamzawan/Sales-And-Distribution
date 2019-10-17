from django.shortcuts import render, redirect
from inventory.models import Add_item
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from .models import (ChartOfAccount, PurchaseHeader, PurchaseReturnHeader, PurchaseDetail, SaleHeader, SaleDetail,
                    Company_info, SaleReturnDetail, SaleReturnHeader, VoucherHeader, VoucherDetail, Transactions,
                    JobOrderHeader, JobOrderDetail)
import datetime, json
from .utils import render_to_pdf
from django.template.loader import get_template
from django.db import connection, IntegrityError
from django.contrib import messages
from django.db.models import Q,Count, Sum
from num2words import num2words
from decimal import Decimal




@login_required()
def home(request):
    return render(request, 'transaction/index.html')


@login_required()
def purchase(request):
    all_purchases = PurchaseHeader.objects.all()
    return render(request, 'transaction/purchase.html', {'all_purchases': all_purchases})


@login_required()
def new_purchase(request):
    total_amount = 0
    net = 0
    serial = "1"
    last_purchase_no = PurchaseHeader.objects.last()
    all_item_code = Add_item.objects.all()
    customer = Q(parent_id = 7)
    vendor = Q(parent_id = 16)
    all_accounts = ChartOfAccount.objects.filter(customer|vendor).all()
    all_pcs = Add_item.objects.filter(unit='pcs').all()
    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if last_purchase_no:
        last_purchase_no = last_purchase_no.purchase_no[6:]
        serial = str((int(last_purchase_no) + 1))
        last_purchase_no = date[2:]+'PI'+serial
    else:
        last_purchase_no =  date[2:]+'PI1'

    item_code = request.POST.get('item_code_purchase')
    x_stand = request.POST.get('x_stand')
    if x_stand:
        items = Add_item.objects.filter(item_code=x_stand)
        items = serializers.serialize('json', items)
        return JsonResponse({"items": items})
    if item_code:
        items = Add_item.objects.filter(item_code = item_code)
        print(items)
        items = serializers.serialize('json', items)
        return JsonResponse({"items": items})
    current_user = request.user
    if request.method == "POST":
        current_user = request.user
        purchase_id = request.POST.get('purchase_id',False)
        vendor = request.POST.get('vendor',False)
        follow_up = request.POST.get('follow_up',False)
        payment_method = request.POST.get('payment_method',False)
        footer_desc = request.POST.get('footer_desc',False)
        account_id = ChartOfAccount.objects.get(account_title = vendor)
        date = datetime.date.today()

        if follow_up:
            follow_up = follow_up
        else:
            follow_up = '2010-06-10'

        purchase_header = PurchaseHeader(purchase_no = purchase_id, date = date, footer_description = footer_desc, payment_method = payment_method, account_id = account_id, follow_up = follow_up, user = current_user)
        items = json.loads(request.POST.get('items'))
        purchase_header.save()
        header_id = PurchaseHeader.objects.get(purchase_no = purchase_id)
        for value in items:
            item_id = Add_item.objects.get(item_code = value["item_code"])
            if value["width"] == "0" and value["height"] == "0":
                pcs_amount = float(value["rate"]) * float(value["quantity"])
                total_amount = total_amount + pcs_amount
                purchase_detail = PurchaseDetail(item_id=item_id, item_description="", width=0, height=0, quantity = 0 ,meas='pieces', rate=value['rate'], purchase_id=header_id, total_amount=pcs_amount, total_square_fit=0, total_pcs=value['quantity'])
            else:
                amount = float(value["sqft"]) * float(value["rate"])
                total_amount = total_amount + amount
                total_square_fit = value["sqft"]
                purchase_detail = PurchaseDetail(item_id = item_id, item_description = "", width = value["width"], height = value["height"], quantity = value["quantity"], meas = value["measurment"], rate = value["rate"], purchase_id = header_id, total_amount = amount,total_square_fit=total_square_fit ,total_pcs=0)
            purchase_detail.save()
            net += total_amount
        header_id = header_id.id
        cash_in_hand = ChartOfAccount.objects.get(account_title = 'Cash')
        if payment_method == 'Cash':
            tran2 = Transactions(refrence_id = header_id, refrence_date = date, account_id = account_id, tran_type = "Purchase Invoice", amount = total_amount, date = date, remarks = purchase_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran2.save()
            tran1 = Transactions(refrence_id = header_id, refrence_date = date, account_id = cash_in_hand, tran_type = "Purchase Invoice", amount = -abs(total_amount), date = date, remarks = purchase_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran1.save()
        else:
            purchase_account = ChartOfAccount.objects.get(account_title = 'Purchases')
            tran1 = Transactions(refrence_id = header_id, refrence_date = date, account_id = account_id, tran_type = "Purchase Invoice", amount = -abs(total_amount), date = date, remarks = purchase_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran1.save()
            tran2 = Transactions(refrence_id = header_id, refrence_date = date, account_id = purchase_account, tran_type = "Purchase Invoice", amount = total_amount, date = date, remarks = purchase_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran2.save()
        return JsonResponse({'result':'success'})
    return render(request, 'transaction/new_purchase.html',{"all_accounts":all_accounts,"last_purchase_no":last_purchase_no, 'all_item_code':all_item_code, 'all_pcs': all_pcs})


def voucher_avaliable_purchase(pk):
    cusror = connection.cursor()
    row = cusror.execute('''select case
                            when exists (select id from transaction_voucherdetail  where  invoice_id = %s)
                            then 'y'
                            else 'n'
                            end''',[pk])
    row = row.fetchall()
    res_list = [x[0] for x in row]
    if res_list[0] == "n":
        refrence_id = Q(refrence_id = pk)
        tran_type = Q(tran_type = "Purchase Invoice")
        ref_inv_tran_id = Q(ref_inv_tran_id = pk)
        ref_inv_tran_type = Q(ref_inv_tran_type = "Purchase CPV")
        Transactions.objects.filter(refrence_id , tran_type).all().delete()
        Transactions.objects.filter(ref_inv_tran_id , ref_inv_tran_type).all().delete()
        PurchaseDetail.objects.filter(purchase_id = pk).all().delete()
        PurchaseHeader.objects.filter(id = pk).delete()
        return True
    else:
        return False

@login_required
def delete_purchase(request, pk):
    item = voucher_avaliable_purchase(pk)
    if item == True:
        messages.add_message(request, messages.SUCCESS, "Purchase Invoice Deleted.")
        return redirect('purchase')
    else:
        messages.add_message(request, messages.ERROR, "You cannot delete this item, kindly delet it's voucher first.")
        return redirect('purchase')


@login_required()
def edit_purchase(request, pk):
    total_amount = 0
    net = 0
    all_item_code = Add_item.objects.all()
    purchase_header = PurchaseHeader.objects.filter(id=pk).first()
    purchase_detail = PurchaseDetail.objects.filter(purchase_id=pk).all()
    all_accounts = ChartOfAccount.objects.all()
    all_pcs = Add_item.objects.filter(unit = "pcs").all()
    item_code_purchase = request.POST.get('item_code_purchase', False)
    x_stand = request.POST.get('x_stand_edit')
    if x_stand:
        items = Add_item.objects.filter(item_code = x_stand)
        items = serializers.serialize('json',items)
        return JsonResponse({"items":items})
    if item_code_purchase:
        data = Add_item.objects.filter(item_code = item_code_purchase)
        items = serializers.serialize('json', data)
        return HttpResponse(json.dumps({'items': items}))
    if request.method == 'POST':
        purchase_detail.delete()
        purchase_id = request.POST.get('purchase_id', False)
        supplier = request.POST.get('supplier', False)
        follow_up = request.POST.get('follow_up', False)
        payment_method = request.POST.get('payment_method', False)
        footer_desc = request.POST.get('footer_desc', False)
        account_id = ChartOfAccount.objects.get(account_title=supplier)
        if follow_up:
            follow_up = follow_up
        else:
            follow_up = '2010-06-10'
        date = datetime.date.today()
        purchase_header.follow_up = follow_up
        purchase_header.payment_method = payment_method
        purchase_header.footer_description = footer_desc
        purchase_header.account_id = account_id

        purchase_header.save()

        items = json.loads(request.POST.get('items'))
        purchase_header.save()
        header_id = PurchaseHeader.objects.get(purchase_no=purchase_id)
        for value in items:
            item_id = Add_item.objects.get(id = value["id"])
            if value["width"] == "0.00" or value["width"] == "0" and value["height"] == "0.00" or value["height"] == "0":
                pcs_amount = float(value["rate"]) * float(value["quantity"])
                total_amount = total_amount + pcs_amount
                purchase_detail = PurchaseDetail(item_id = item_id, item_description = "", width = 0, height = 0, quantity = 0, meas = "pieces", rate = value["rate"], purchase_id = header_id, total_amount = pcs_amount, total_square_fit = 0, total_pcs = value["quantity"])
                print(total_amount)
            else:
                amount = float(value["sqft"]) * float(value["rate"])
                total_amount = total_amount + amount
                total_square_fit = value["sqft"]
                purchase_detail = PurchaseDetail(item_id = item_id, item_description = "", width = value["width"], height = value["height"], quantity = value["quantity"], meas = value["measurment"], rate = value["rate"], purchase_id = header_id, total_amount = amount, total_square_fit = total_square_fit, total_pcs = 0)
                net = net + total_amount
            print(total_amount)
            purchase_detail.save()

        cash_in_hand = ChartOfAccount.objects.get(account_title = 'Cash')
        if payment_method == 'Cash':
            refrence_id = Q(refrence_id = pk)
            tran_type = Q(tran_type = "Purchase Invoice")
            ref_inv_tran_id = Q(ref_inv_tran_id = pk)
            ref_inv_tran_type = Q(ref_inv_tran_type = "Purchase CPV")
            Transactions.objects.filter(refrence_id , tran_type).all().delete()
            Transactions.objects.filter(ref_inv_tran_id , ref_inv_tran_type).all().delete()
            tran2 = Transactions(refrence_id = header_id.id, refrence_date = purchase_header.date, account_id = account_id, tran_type = "Purchase Invoice", amount = total_amount, date = date, remarks = purchase_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran2.save()
            tran1 = Transactions(refrence_id = header_id.id, refrence_date = purchase_header.date, account_id = cash_in_hand, tran_type = "Purchase Invoice", amount = -abs(total_amount), date = date, remarks = purchase_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran1.save()
        else:
            refrence_id = Q(refrence_id = pk)
            tran_type = Q(tran_type = "Purchase Invoice")
            ref_inv_tran_id = Q(ref_inv_tran_id = pk)
            ref_inv_tran_type = Q(ref_inv_tran_type = "Purchase CPV")
            Transactions.objects.filter(refrence_id , tran_type).all().delete()
            Transactions.objects.filter(ref_inv_tran_id , ref_inv_tran_type).all().delete()
            purchase_account = ChartOfAccount.objects.get(account_title = 'Purchases')
            tran1 = Transactions(refrence_id = header_id.id, refrence_date = purchase_header.date, account_id = account_id, tran_type = "Purchase Invoice", amount = -abs(total_amount), date = date, remarks = purchase_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran1.save()
            tran2 = Transactions(refrence_id = header_id.id, refrence_date = purchase_header.date, account_id = purchase_account, tran_type = "Purchase Invoice", amount = total_amount, date = date, remarks = purchase_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran2.save()
            return JsonResponse({'result':'success'})
        return JsonResponse({'result': 'success'})
    return render(request, 'transaction/edit_purchase.html',
                  {'all_item_code': all_item_code, 'all_accounts': all_accounts, 'purchase_header': purchase_header,
                   'purchase_detail': purchase_detail, 'pk': pk,'all_pcs':all_pcs})


@login_required()
def purchase_return_summary(request):
    all_purchase_return = PurchaseReturnHeader.objects.all()
    return render(request, 'transaction/purchase_return_summary.html', {'all_purchase_return': all_purchase_return})

@login_required()
def new_purchase_return(request):
    return render(request, 'transaction/purchase_return.html')


@login_required()
def sale(request):
    all_sales = SaleHeader.objects.all()
    return render(request, 'transaction/sale.html',{"all_sales": all_sales})


@login_required()
def new_sale(request):
    total_amount = 0
    net = 0
    serial = "0"
    last_sale_no = SaleHeader.objects.last()
    all_job_order = JobOrderHeader.objects.all()
    all_pcs = Add_item.objects.filter(unit = "pcs").all()
    customer = Q(parent_id = 7)
    vendor = Q(parent_id = 16)
    all_accounts = ChartOfAccount.objects.filter(customer|vendor).all()
    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if last_sale_no:
        last_sale_no = last_sale_no.sale_no[6:]
        serial = str((int(last_sale_no)+1))
        last_sale_no = date[2:]+'SI'+serial
    else:
        last_sale_no =  date[2:]+'SI1'
    job_no_sale = request.POST.get('job_no_sale')
    x_stand = request.POST.get('x_stand')
    if x_stand:
        items = Add_item.objects.filter(item_code = x_stand)
        items = serializers.serialize('json',items)
        return JsonResponse({"items":items})
    if job_no_sale:
        header_job = JobOrderHeader.objects.get(job_no = job_no_sale)
        cursor = connection.cursor()
        items = cursor.execute('''select inventory_add_item.item_code, inventory_add_item.item_name, inventory_add_item.item_description,transaction_joborderdetail.meas, transaction_joborderdetail.width, transaction_joborderdetail.height, transaction_joborderdetail.quantity
                                from transaction_joborderdetail
                                inner join inventory_add_item on transaction_joborderdetail.item_id_id = inventory_add_item.id
                                where transaction_joborderdetail.header_id_id = %s
                                ''',[header_job.id])
        items = items.fetchall()
        return JsonResponse({"items":items})
    current_user = request.user
    if request.method == "POST":
        sale_id = request.POST.get('sale_id',False)
        customer = request.POST.get('customer',False)
        account_holder = request.POST.get('account_holder',False)
        credit_days = request.POST.get('credit_days',False)
        payment_method = request.POST.get('payment_method',False)
        footer_desc = request.POST.get('footer_desc',False)
        account_id = ChartOfAccount.objects.get(account_title = customer)
        date = datetime.date.today()
        start_date = str(date)
        get_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        follow_up = get_date + datetime.timedelta(days=int(credit_days))
        follow_up = datetime.datetime.strftime(follow_up, "%Y-%m-%d")

        sale_header = SaleHeader(sale_no = last_sale_no, date = date, footer_description = footer_desc, payment_method = payment_method, account_id = account_id, account_holder = account_holder, credit_days = credit_days ,follow_up = follow_up, user = current_user)
        sale_header.save()
        items = json.loads(request.POST.get('items'))
        header_id = SaleHeader.objects.get(sale_no = sale_id)
        for value in items:
            item_id = Add_item.objects.get(item_code = value["item_code"])
            if value["width"] == "0" and value["height"] == "0":
                pcs_amount = float(value["rate"]) * float(value["quantity"])
                total_amount = total_amount + pcs_amount
                sale_detail = SaleDetail(item_id = item_id, item_description = value["description"], width = 0, height = 0, quantity = 0, meas = "pieces", rate = value["rate"], sale_id = header_id, total_amount = pcs_amount, total_square_fit = 0, total_pcs = value["quantity"])
            else:
                amount = float(value["sqft"]) * float(value["rate"])
                total_amount = total_amount + amount
                total_square_fit = value["sqft"]
                sale_detail = SaleDetail(item_id = item_id, item_description = value["description"], width = value["width"], height = value["height"], quantity = value["quantity"], meas = value["measurment"], rate = value["rate"], sale_id = header_id, total_amount = amount, total_square_fit = total_square_fit, total_pcs = 0)
            sale_detail.save()
            net = net + total_amount
        header_id = header_id.id
        cash_in_hand = ChartOfAccount.objects.get(account_title = 'Cash')
        if payment_method == 'Cash':
            tran1 = Transactions(refrence_id = header_id, refrence_date = date, account_id = cash_in_hand, tran_type = "Sale Invoice", amount = total_amount, date = date, remarks = last_sale_no, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran1.save()
            tran2 = Transactions(refrence_id = header_id, refrence_date = date, account_id = account_id, tran_type = "Sale Invoice", amount = -abs(total_amount), date = date, remarks = last_sale_no, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran2.save()
        else:
            sale_account = ChartOfAccount.objects.get(account_title = 'Sales')
            tran1 = Transactions(refrence_id = header_id, refrence_date = date, account_id = account_id, tran_type = "Sale Invoice", amount = total_amount, date = date, remarks = last_sale_no, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran1.save()
            tran2 = Transactions(refrence_id = header_id, refrence_date = date, account_id = sale_account, tran_type = "Sale Invoice", amount = -abs(total_amount), date = date, remarks = last_sale_no, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran2.save()
        return JsonResponse({'result':'success'})
    return render(request, 'transaction/new_sale.html',{"all_accounts":all_accounts,"last_sale_no":last_sale_no, 'all_job_order':all_job_order,'all_pcs':all_pcs})



def voucher_avaliable_sale(pk):
    cusror = connection.cursor()
    row = cusror.execute('''select case
                            when exists (select id from transaction_voucherdetail  where  invoice_id = %s)
                            then 'y'
                            else 'n'
                            end''',[pk])
    row = row.fetchall()
    res_list = [x[0] for x in row]
    if res_list[0] == "n":
        refrence_id = Q(refrence_id = pk)
        tran_type = Q(tran_type = "Sale Invoice")
        ref_inv_tran_id = Q(ref_inv_tran_id = pk)
        ref_inv_tran_type = Q(ref_inv_tran_type = "Sale CRV")
        Transactions.objects.filter(refrence_id , tran_type).all().delete()
        Transactions.objects.filter(ref_inv_tran_id , ref_inv_tran_type).all().delete()
        SaleDetail.objects.filter(sale_id = pk).all().delete()
        SaleHeader.objects.filter(id = pk).delete()
        return True
    else:
        return False

@login_required
def delete_sale(request, pk):
    item = voucher_avaliable_sale(pk)
    if item == True:
        messages.add_message(request, messages.SUCCESS, "Sale Invoice Deleted.")
        return redirect('sale')
    else:
        messages.add_message(request, messages.ERROR, "You cannot delete this item, kindly delet it's voucher first.")
        return redirect('sale')
#
# def delete_sale(request,pk):
#     refrence_id = Q(refrence_id = pk)
#     tran_type = Q(tran_type = "Sale Invoice")
#     ref_inv_tran_id = Q(ref_inv_tran_id = pk)
#     ref_inv_tran_type = Q(ref_inv_tran_type = "Sale CRV")
#     Transactions.objects.filter(refrence_id , tran_type).all().delete()
#     Transactions.objects.filter(ref_inv_tran_id , ref_inv_tran_type).all().delete()
#     SaleDetail.objects.filter(sale_id = pk).all().delete()
#     SaleHeader.objects.filter(id = pk).delete()
#     messages.add_message(request, messages.SUCCESS, "Sale Invoice Deleted")
#     return redirect('sale')

@login_required()
def edit_sale(request, pk):
    total_amount = 0
    net = 0
    job_no = JobOrderHeader.objects.all()
    sale_header = SaleHeader.objects.filter(id=pk).first()
    sale_detail = SaleDetail.objects.filter(sale_id=pk).all()
    all_accounts = ChartOfAccount.objects.all()
    all_pcs = Add_item.objects.filter(unit = "pcs").all()
    item_code = request.POST.get('job_no_sale', False)
    x_stand = request.POST.get('x_stand_edit')
    if x_stand:
        items = Add_item.objects.filter(item_code = x_stand)
        items = serializers.serialize('json',items)
        return JsonResponse({"items":items})
    if item_code:
        header_job = JobOrderHeader.objects.get(job_no = item_code)
        cursor = connection.cursor()
        items = cursor.execute('''select inventory_add_item.item_code, inventory_add_item.item_name, inventory_add_item.item_description,transaction_joborderdetail.meas, transaction_joborderdetail.width, transaction_joborderdetail.height, transaction_joborderdetail.quantity
                                from transaction_joborderdetail
                                inner join inventory_add_item on transaction_joborderdetail.item_id_id = inventory_add_item.id
                                where transaction_joborderdetail.header_id_id = %s
                                ''',[header_job.id])
        items = items.fetchall()
        return JsonResponse({"items":items})
    if request.method == 'POST':
        sale_detail.delete()

        sale_id = request.POST.get('sale_id', False)
        customer = request.POST.get('customer', False)
        account_holder = request.POST.get('account_holder', False)
        credit_days = request.POST.get('credit_days', False)
        payment_method = request.POST.get('payment_method', False)
        footer_desc = request.POST.get('footer_desc', False)
        account_id = ChartOfAccount.objects.get(account_title=customer)
        date = datetime.date.today()
        start_date = str(date)
        get_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        follow_up = get_date + datetime.timedelta(days=int(credit_days))
        follow_up = datetime.datetime.strftime(follow_up, "%Y-%m-%d")


        sale_header.follow_up = follow_up
        sale_header.credit_days = credit_days
        sale_header.account_holder = account_holder
        sale_header.payment_method = payment_method
        sale_header.footer_description = footer_desc
        sale_header.account_id = account_id

        sale_header.save()

        items = json.loads(request.POST.get('items'))
        sale_header.save()
        header_id = SaleHeader.objects.get(sale_no=sale_id)
        header_id = header_id
        for value in items:
            item_id = Add_item.objects.get(item_code = value["id"])
            if value["width"] == "0.00" or value["width"] == "0" and value["height"] == "0.00" or value["height"] == "0":
                pcs_amount = float(value["rate"]) * float(value["quantity"])
                total_amount = total_amount + pcs_amount
                sale_detail = SaleDetail(item_id = item_id, item_description = value["description"], width = 0, height = 0, quantity = 0, meas = "pieces", rate = value["rate"], sale_id = header_id, total_amount = pcs_amount, total_square_fit = 0, total_pcs = value["quantity"])
                print(total_amount)
            else:
                amount = float(value["sqft"]) * float(value["rate"])
                total_amount = total_amount + amount
                total_square_fit = value["sqft"]
                sale_detail = SaleDetail(item_id = item_id, item_description = value["description"], width = value["width"], height = value["height"], quantity = value["quantity"], meas = value["measurment"], rate = value["rate"], sale_id = header_id, total_amount = amount, total_square_fit = total_square_fit, total_pcs = 0)
                net = net + total_amount
            print(total_amount)
            sale_detail.save()
        cash_in_hand = ChartOfAccount.objects.get(account_title = 'Cash')
        header_id = header_id.id
        if payment_method == 'Cash':
            refrence_id = Q(refrence_id = pk)
            tran_type = Q(tran_type = "Sale Invoice")
            ref_inv_tran_id = Q(ref_inv_tran_id = pk)
            ref_inv_tran_type = Q(ref_inv_tran_type = "Sale CRV")
            Transactions.objects.filter(refrence_id , tran_type).all().delete()
            Transactions.objects.filter(ref_inv_tran_id , ref_inv_tran_type).all().delete()
            tran1 = Transactions(refrence_id = header_id, refrence_date = sale_header.date, account_id = cash_in_hand, tran_type = "Sale Invoice", amount = total_amount, date = date, remarks = sale_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran1.save()
            tran2 = Transactions(refrence_id = header_id, refrence_date = sale_header.date, account_id = account_id, tran_type = "Sale Invoice", amount = -abs(total_amount), date = date, remarks = sale_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran2.save()
        else:
            refrence_id = Q(refrence_id = pk)
            tran_type = Q(tran_type = "Sale Invoice")
            ref_inv_tran_id = Q(ref_inv_tran_id = pk)
            ref_inv_tran_type = Q(ref_inv_tran_type = "Sale CRV")
            Transactions.objects.filter(refrence_id , tran_type).all().delete()
            Transactions.objects.filter(ref_inv_tran_id , ref_inv_tran_type).all().delete()
            sale_account = ChartOfAccount.objects.get(account_title = 'Sales')
            tran1 = Transactions(refrence_id = header_id, refrence_date = sale_header.date, account_id = account_id, tran_type = "Sale Invoice", amount = total_amount, date = date, remarks = sale_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran1.save()
            tran2 = Transactions(refrence_id = header_id, refrence_date = sale_header.date, account_id = sale_account, tran_type = "Sale Invoice", amount = -abs(total_amount), date = date, remarks = sale_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
            tran2.save()
        return JsonResponse({'result':'success'})
    return render(request, 'transaction/edit_sale.html',
                  {'job_no': job_no, 'sale_header': sale_header, 'sale_detail': sale_detail,'pk':pk, 'all_pcs':all_pcs})


@login_required()
def sale_return_summary(request):
    all_sales_return = SaleReturnHeader.objects.all()
    return render(request, 'transaction/sale_return_summary.html', {'all_sales_return': all_sales_return})

@login_required()
def new_sale_return(request):
    return render(request, 'transaction/sale_return.html')


@login_required()
def chart_of_account(request):
    all_accounts_null = ChartOfAccount.objects.filter(parent_id = 0).all()
    vendor = Q(parent_id = 7)
    customer = Q(parent_id = 16)
    all_accounts = ChartOfAccount.objects.filter(vendor | customer).all()

    if request.method == 'POST':
        try:
            account_title = request.POST.get('account_title')
            account_type = request.POST.get('account_type')
            opening_balance = request.POST.get('opening_balance')
            phone_no = request.POST.get('phone_no')
            email_address = request.POST.get('email_address')
            ntn = request.POST.get('ntn')
            stn = request.POST.get('stn')
            cnic = request.POST.get('cnic')
            address = request.POST.get('address')
            remarks = request.POST.get('remarks')
            op_type = request.POST.get('optradio')
            credit_limits = request.POST.get('credit_limits')

            if opening_balance is "":
                opening_balance = 0.00
            if op_type == "credit":
                opening_balance = -abs(int(opening_balance))
            if credit_limits is "":
                credit_limits = 0.00
            coa = ChartOfAccount(account_title = account_title, parent_id = account_type, opening_balance = opening_balance, phone_no = phone_no, email_address = email_address, ntn = ntn, stn = stn, cnic = cnic ,Address = address, remarks = remarks, credit_limit=credit_limits)
            coa.save()
        except IntegrityError as e:
            print(e)

    return render(request, 'transaction/chart_of_account.html',{'all_accounts_null':all_accounts_null,'all_accounts':all_accounts})


@login_required()
def edit_chart_of_account(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        account_title = request.POST.get('account_title')
        account_type = request.POST.get('account_type')
        opening_balance = request.POST.get('opening_balance')
        phone_no = request.POST.get('phone_no')
        email_address = request.POST.get('email_address')
        ntn = request.POST.get('ntn')
        stn = request.POST.get('stn')
        cnic = request.POST.get('cnic')
        address = request.POST.get('address')
        remarks = request.POST.get('remarks')
        op_type = request.POST.get('optradio')
        credit_limits = request.POST.get('credit_limits')

        if credit_limits is "":
            credit_limits = 0.00
        else:
            credit_limits = credit_limits

        if opening_balance is "":
            opening_balance = 0
        if op_type == "credit":
            opening_balance = -abs(Decimal(opening_balance))
        coa = ChartOfAccount.objects.filter(id = id).first()
        coa.account_title = account_title
        coa.account_type = account_type
        coa.opening_balance = opening_balance
        coa.phone_no = phone_no
        coa.email_address = email_address
        coa.ntn = ntn
        coa.stn = stn
        coa.cnic = cnic
        coa.Address = address
        coa.remarks = remarks
        coa.credit_limit = credit_limits
        coa.save()
    return redirect('chart-of-account')


def account_avaliable(pk):
    cusror = connection.cursor()
    row = cusror.execute('''select case
                        when exists (select id from transaction_joborderheader  where account_id_id = %s)
                        or exists (select id from transaction_purchaseheader  where account_id_id = %s)
                        or exists (select id from transaction_purchasereturnheader  where account_id_id = %s)
                        or exists (select id from transaction_saleheader  where account_id_id = %s)
                        or exists (select id from transaction_salereturnheader  where account_id_id = %s)
                        or exists (select id from transaction_transactions  where account_id_id = %s)
                        then 'y'
                        else 'n'
                        end''',[pk,pk,pk,pk,pk,pk])
    row = row.fetchall()
    res_list = [x[0] for x in row]
    if res_list[0] == "n":
        ChartOfAccount.objects.filter(id = pk).delete()
        return True
    else:
        return False


@login_required()
def delete_account(request, pk):
    item = account_avaliable(pk)
    if item == True:
        messages.add_message(request, messages.SUCCESS, "Account Deleted.")
        return redirect('chart-of-account')
    else:
        messages.add_message(request, messages.ERROR, "You cannot delete this Account, it is refrenced.")
        return redirect('chart-of-account')


@login_required()
def print_purchase(request,pk):
    lines = 0
    total_amount = 0
    total_quantity = 0
    total_square_fit = 0
    square_fit = 0
    header = PurchaseHeader.objects.filter(id = pk).first()
    detail = PurchaseDetail.objects.filter(purchase_id = pk).all()
    image = Company_info.objects.first()
    for value in detail:
        lines = lines + len(value.item_description.split('\n'))
        square_fit = float(value.width * value.height)
        if value.meas == "sq.inches":
            square_fit = square_fit / 144
        gross = square_fit * float(value.rate)
        amount = gross * float(value.quantity)
        total_amount = total_amount + amount
        total_quantity = (total_quantity + value.quantity)
        square_fit = value.height * value.width
        total_square_fit = total_square_fit + square_fit
    lines = lines + len(detail) + len(detail)
    total_lines = 36 - lines
    pdf = render_to_pdf('transaction/purchase_pdf.html', {'header':header, 'detail':detail,'image':image, 'total_lines':12, 'total_amount':total_amount, 'total_quantity':total_quantity,'total_square_fit':total_square_fit})
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Purchase_%s.pdf" %(header.purchase_no)
        content = "inline; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")


@login_required()
def print_sale(request, pk):
    lines = 0
    total_amount = 0
    total_quantity = 0
    total_square_fit = 0
    square_fit = 0
    header = SaleHeader.objects.filter(id = pk).first()
    detail = SaleDetail.objects.filter(sale_id = pk).all()
    image = Company_info.objects.first()
    for value in detail:
        if value.meas == "sq.ft":
            square_fit = float(value.width * value.height)
            gross = square_fit * float(value.rate)
            amount = gross * float(value.quantity)
            total_amount = total_amount + amount
            total_quantity = (total_quantity + value.quantity)
            square_fit = value.height * value.width * value.quantity
            total_square_fit = total_square_fit + square_fit
        elif value.meas == "sq.inches":
            square_fit = float(value.width * value.height) / 144
            gross = square_fit * float(value.rate)
            amount = gross * float(value.quantity)
            total_amount = total_amount + amount
            total_quantity = (total_quantity + value.quantity)
            square_fit = value.height * value.width * value.quantity / 144
            total_square_fit = total_square_fit + square_fit
        elif value.meas == "pieces":
            amount = float(value.rate) * float(value.total_pcs)
            total_amount = total_amount + amount

    pdf = render_to_pdf('transaction/sale_pdf.html', {'header':header, 'detail':detail,'image':image, 'total_lines':12, 'total_amount':total_amount, 'total_quantity':total_quantity,'total_square_fit':total_square_fit})
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Sale_%s.pdf" % (header.sale_no)
        content = "inline; filename='%s'" % (filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")


@login_required()
def journal_voucher(request):
    serial = "1"
    cursor = connection.cursor()
    get_last_tran_id = cursor.execute('''select * from transaction_voucherheader where voucher_no LIKE '%JV%'
                                        order by voucher_no DESC LIMIT 1''')
    get_last_tran_id = get_last_tran_id.fetchall()

    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if get_last_tran_id:
        get_last_tran_id = get_last_tran_id[0][1]
        get_last_tran_id = get_last_tran_id[6:]
        serial = str((int(get_last_tran_id) + 1))
        get_last_tran_id = date[2:]+'JV'+serial
    else:
        get_last_tran_id =  date[2:]+'JV1'
    account_id = request.POST.get('account_title', False)
    all_accounts = ChartOfAccount.objects.all()
    if account_id:
        account_info = ChartOfAccount.objects.filter(id=account_id).first()
        account_title = account_info.account_title
        account_id = account_info.id
        return JsonResponse({'account_title': account_title, 'account_id': account_id})
    user = request.user
    if request.method == "POST":
        doc_no = request.POST.get('doc_no', False)
        doc_date = request.POST.get('doc_date', False)
        description = request.POST.get('description', False)
        items = json.loads(request.POST.get('items', False))
        jv_header = VoucherHeader(voucher_no=get_last_tran_id, doc_no=doc_no, doc_date=doc_date, cheque_no="-",
                                  cheque_date=doc_date, description=description, user=user)
        jv_header.save()
        header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
        for value in items:
            account_id = ChartOfAccount.objects.get(account_title=value["account_title"])
            if value["debit"] > "0" and value["debit"] > "0.00":
                tran1 = Transactions(refrence_id=doc_no, refrence_date=doc_date, tran_type='JV',
                                     amount=abs(float(value["debit"])),
                                     date=datetime.date.today(), remarks=get_last_tran_id, account_id=account_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
                tran1.save()
                jv_detail1 = VoucherDetail(account_id=account_id, debit=abs(float(value["debit"])), credit=0.00,header_id=header_id, invoice_id = 0)
                jv_detail1.save()
            print(value["debit"])
            if value["credit"] > "0" and value["credit"] > "0.00":
                print("run")
                print(value["credit"])
                tran2 = Transactions(refrence_id=doc_no, refrence_date=doc_date, tran_type='JV',
                                     amount=-abs(float(value["credit"])),
                                     date=datetime.date.today(), remarks=get_last_tran_id, account_id=account_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
                tran2.save()
                jv_detail2 = VoucherDetail(account_id=account_id, debit=0.00, credit=-abs(float(value["credit"])),header_id=header_id, invoice_id = 0)
                jv_detail2.save()
        return JsonResponse({"result": "success"})
    return render(request, 'transaction/journal_voucher.html',{"all_accounts": all_accounts, 'get_last_tran_id': get_last_tran_id})


@login_required()
def delete_journal_voucher(request, pk):
    ref = VoucherHeader.objects.get(id = pk)
    refrence_id = Q(refrence_id = ref.doc_no)
    tran_type = Q(tran_type = "JV")
    Transactions.objects.filter(refrence_id, tran_type).all().delete()
    VoucherDetail.objects.filter(header_id = ref.id).all().delete()
    VoucherHeader.objects.filter(doc_no = ref.doc_no).delete()
    messages.add_message(request, messages.SUCCESS, "Journal Voucher Deleted")
    return redirect('journal-voucher-summary')


@login_required()
def bank_receiving_voucher(request):
    cursor = connection.cursor()
    all_vouchers = cursor.execute('''select VH.id, VH.voucher_no, VH.doc_no, VH.doc_date, VH.cheque_no, VH.description,
                                            AU.username from transaction_voucherheader VH
                                            inner join auth_user AU on VH.user_id = AU.id
                                            where VH.voucher_no LIKE '%BRV%' ''')
    print(all_vouchers)
    all_vouchers = all_vouchers.fetchall()
    return render(request, 'transaction/bank_receiving_voucher.html', {'all_vouchers': all_vouchers})

@login_required()
def new_bank_receiving_voucher(request):
    cursor = connection.cursor()
    get_last_tran_id = cursor.execute('''select * from transaction_voucherheader where voucher_no LIKE '%BRV%'
                                        order by voucher_no DESC LIMIT 1''')
    get_last_tran_id = get_last_tran_id.fetchall()
    print(get_last_tran_id)

    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if get_last_tran_id:
        get_last_tran_id = get_last_tran_id[0][1]
        get_last_tran_id = get_last_tran_id[7:]
        serial = str((int(get_last_tran_id) + 1))
        # count = last_sale_no.count('0')
        get_last_tran_id = date[2:]+'BRV'+serial
    else:
        get_last_tran_id =  date[2:]+'BRV1'
    account_id = request.POST.get('account_title', False)
    all_accounts = ChartOfAccount.objects.all()
    if account_id:
        account_info = ChartOfAccount.objects.filter(id=account_id).first()
        account_title = account_info.account_title
        account_id = account_info.id
        return JsonResponse({'account_title': account_title, 'account_id': account_id})
    user = request.user
    if request.method == "POST":
        doc_no = request.POST.get('doc_no', False)
        doc_date = request.POST.get('doc_date', False)
        description = request.POST.get('description', False)
        cheque_no = request.POST.get('cheque_no', False)
        cheque_date = request.POST.get('cheque_date', False)

        items = json.loads(request.POST.get('items', False))
        jv_header = VoucherHeader(voucher_no=get_last_tran_id, doc_no=doc_no, doc_date=doc_date, cheque_no=cheque_no,
                                  cheque_date=cheque_date, description=description, user=user)
        jv_header.save()
        header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
        for value in items:
            account_id = ChartOfAccount.objects.get(account_title=value["account_title"])
            if value["debit"] > "0" and value["debit"] > "0.00":
                tran1 = Transactions(refrence_id=doc_no, refrence_date=doc_date, tran_type='BRV',
                                     amount=abs(float(value["debit"])),
                                     date=datetime.date.today(), remarks=get_last_tran_id, account_id=account_id, )
                tran1.save()
                jv_detail1 = VoucherDetail(account_id=account_id, debit=abs(float(value["debit"])), credit=0.00, header_id = header_id)
                jv_detail1.save()
            print(value["debit"])
            if value["credit"] > "0" and value["credit"] > "0.00":
                print("run")
                print(value["credit"])
                tran2 = Transactions(refrence_id=doc_no, refrence_date=doc_date, tran_type='BRV',
                                     amount=-abs(float(value["credit"])),
                                     date=datetime.date.today(), remarks=get_last_tran_id, account_id=account_id, )
                tran2.save()
                jv_detail2 = VoucherDetail(account_id=account_id, debit=0.00, credit=-abs(float(value["credit"])), header_id = header_id)
                jv_detail2.save()
        return JsonResponse({"result": "success"})
    return render(request, 'transaction/new_bank_receiving_voucher.html', {'all_accounts': all_accounts, 'get_last_tran_id': get_last_tran_id})

@login_required()
def new_bank_payment_voucher(request):
    cursor = connection.cursor()
    get_last_tran_id = cursor.execute('''select * from transaction_voucherheader where voucher_no LIKE '%BPV%'
                                        order by voucher_no DESC LIMIT 1''')
    get_last_tran_id = get_last_tran_id.fetchall()
    print(get_last_tran_id)

    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if get_last_tran_id:
        get_last_tran_id = get_last_tran_id[0][1]
        get_last_tran_id = get_last_tran_id[7:]
        serial = str((int(get_last_tran_id) + 1))
        # count = last_sale_no.count('0')
        get_last_tran_id = date[2:]+'BPV'+serial
    else:
        get_last_tran_id =  date[2:]+'BPV1'
    account_id = request.POST.get('account_title', False)
    all_accounts = ChartOfAccount.objects.all()
    if account_id:
        account_info = ChartOfAccount.objects.filter(id=account_id).first()
        account_title = account_info.account_title
        account_id = account_info.id
        return JsonResponse({'account_title': account_title, 'account_id': account_id})
    user = request.user
    if request.method == "POST":
        doc_no = request.POST.get('doc_no', False)
        doc_date = request.POST.get('doc_date', False)
        cheque_no = request.POST.get('cheque_no', False)
        cheque_date = request.POST.get('cheque_date', False)
        description = request.POST.get('description', False)
        items = json.loads(request.POST.get('items', False))
        if cheque_date:
            cheque_date = cheque_date
        else:
            cheque_date = "2010-10-06"
        jv_header = VoucherHeader(voucher_no=get_last_tran_id, doc_no=doc_no, doc_date=doc_date, cheque_no=cheque_no,
                                  cheque_date=cheque_date, description=description, user=user)
        jv_header.save()
        header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
        for value in items:
            print("this")
            account_id = ChartOfAccount.objects.get(account_title=value["account_title"])
            if value["debit"] > "0" and value["debit"] > "0.00":
                tran1 = Transactions(refrence_id=doc_no, refrence_date=doc_date, tran_type='CRV',
                                     amount=abs(float(value["debit"])),
                                     date=datetime.date.today(), remarks=get_last_tran_id, account_id=account_id, )
                tran1.save()
                jv_detail1 = VoucherDetail(account_id=account_id, debit=abs(float(value["debit"])), credit=0.00,header_id = header_id)
                jv_detail1.save()
            print(value["debit"])
            if value["credit"] > "0" and value["credit"] > "0.00":
                print("run")
                print(value["credit"])
                tran2 = Transactions(refrence_id=doc_no, refrence_date=doc_date, tran_type='CRV',
                                     amount=-abs(float(value["credit"])),
                                     date=datetime.date.today(), remarks=get_last_tran_id, account_id=account_id, )
                tran2.save()
                jv_detail2 = VoucherDetail(account_id=account_id, debit=0.00, credit=-abs(float(value["credit"])))
                jv_detail2.save()
        return JsonResponse({"result": "success"})
    return render(request, 'transaction/new_bank_payment_voucher.html', {'all_accounts': all_accounts, 'get_last_tran_id': get_last_tran_id})

@login_required()
def bank_payment_voucher(request):
    cursor = connection.cursor()
    all_vouchers = cursor.execute('''select VH.id, VH.voucher_no, VH.doc_no, VH.doc_date, VH.cheque_no, VH.description,
                                            AU.username from transaction_voucherheader VH
                                            inner join auth_user AU on VH.user_id = AU.id
                                            where VH.voucher_no LIKE '%BPV%' ''')
    all_vouchers = all_vouchers.fetchall()
    return render(request, 'transaction/bank_payment_voucher.html', {'all_vouchers': all_vouchers})

@login_required()
def reports(request):
    all_accounts = ChartOfAccount.objects.all()
    return render(request, 'transaction/reports.html', {'all_accounts': all_accounts})

@login_required()
def trial_balance(request):
    if request.method == 'POST':
        debit_amount = 0
        credit_amount = 0
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        company_info = Company_info.objects.all()
        cursor = connection.cursor()
        cursor.execute('''Select id,account_title,ifnull(amount,0) + opening_balance As Amount
                        from transaction_chartofaccount
                        Left Join
                        (select account_id_id,sum(AMount) As Amount from transaction_transactions
                        Where transaction_transactions.date Between %s And %s
                        Group By account_id_id) As tbltran On transaction_chartofaccount.id = tbltran.account_id_id
                        ''',[from_date, to_date])
        row = cursor.fetchall()
        for value in row:
            if value[2] >= 0:
                debit_amount = debit_amount + value[2]
            else:
                credit_amount = credit_amount + value[2]
        pdf = render_to_pdf('transaction/trial_balance_pdf.html', {'company_info':company_info, 'row': row, 'debit_amount': debit_amount, 'credit_amount': credit_amount,'from_date':from_date,'to_date':to_date})
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = 'TrialBalance%s.pdf' %('000')
            content = "inline; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not Found")
    return redirect('report')


@login_required()
def account_ledger(request):
    if request.method == "POST":
        debit_amount = 0
        credit_amount = 0
        pk = request.POST.get('account_title')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        company_info = Company_info.objects.all()
        image = Company_info.objects.filter(id=1).first()
        cursor = connection.cursor()
        cursor.execute('''Select tran_type,refrence_id,refrence_date,remarks,ref_inv_tran_id,ref_inv_tran_type,Sum(Debit) Debit,Sum(Credit) Credit From (
                    Select Distinct account_id_id,'Opening' As tran_type,'' As refrence_id,'' As refrence_date,'Opening Balance' As remarks,
                    '' AS ref_inv_tran_id,'' AS ref_inv_tran_type,
                    Case When Sum(amount) > -1 Then  sum(amount) Else 0 End As Debit,
                    Case When Sum(amount) < -1 Then  sum(amount) Else 0 End As Credit from (
                    Select id As Account_id_id, Sum(Opening_Balance) As amount
                    From transaction_chartofaccount Where ID = (
                    Select id from transaction_chartofaccount Where Parent_ID = %s)
                    Union All
                    Select id As account_id_id, Sum(Opening_Balance) As amount
                    From transaction_chartofaccount Where ID = (%s)
                    Union All
                    Select account_id_id,Sum(amount) As amount From transaction_transactions
                    where account_id_id in (
                    Case When (Select id from transaction_chartofaccount Where Parent_ID = %s)
                    <> '' Then (Select id from transaction_chartofaccount Where Parent_ID = %s)
                    Else (%s) END) AND refrence_date < %s
                    Union all
                    Select account_id_id,Sum(amount) As amount From transaction_transactions
                    where account_id_id in (%s) AND refrence_date < %s
                    ) tblData
                    Group By account_id_id
                    Union all
                    Select Distinct account_id_id,tran_type,refrence_id,refrence_date,remarks,ref_inv_tran_id,ref_inv_tran_type,
                    Case When amount > -1 Then  amount Else 0 End As Debit,
                    Case When amount < -1 Then  amount Else 0 End As Credit from (
                    Select * From transaction_transactions
                    where account_id_id in (
                    Case When (Select id from transaction_chartofaccount Where Parent_ID = %s)
                    <> '' Then (Select id from transaction_chartofaccount Where Parent_ID = %s)
                    Else (%s) END)
                    Union all
                    Select * From transaction_transactions
                    where account_id_id in (%s)
                    ) tblData
                    Where refrence_date Between %s And %s
                    Order By account_id_id,refrence_date Asc
                    ) As tblLedger
                    Group By tran_type,refrence_id,refrence_date,remarks,ref_inv_tran_id,ref_inv_tran_type
                    Order By refrence_date Asc
                    ''',[pk,pk,pk,pk,pk,from_date,pk,from_date,pk,pk,pk,pk,from_date,to_date])
        row = cursor.fetchall()
        print(row)
        ledger_list = []
        balance = 0
        for i,value in enumerate(row):
            balance = balance + float(value[6]) + float(value[7])
            info = {
            "date": value[2],
            "voucher_no": value[3],
            "tran_type": value[0],
            "debit":value[6],
            "credit":value[7],
            "balance": balance,
            }
            ledger_list.append(info)
        for value in row:
            print(value)
        if row:
            for v in row:
                if v[6] >= 0:
                    debit_amount = debit_amount + v[6]
                if v[7] <= 0:
                    credit_amount = credit_amount + v[7]
        print("here",debit_amount)
        print("here",credit_amount)
        account_id = ChartOfAccount.objects.filter(id = pk).first()
        account_title = account_id.account_title
        id = account_id.id
        pdf = render_to_pdf('transaction/account_ledger_pdf.html', {'ledger_list':ledger_list,'company_info':company_info,'image':image,'row':row, 'debit_amount':debit_amount, 'credit_amount': credit_amount, 'account_title':account_title, 'from_date':from_date,'to_date':to_date,'id':id})
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Account_Ledger%s.pdf" %("000")
            content = "inline; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")
    return redirect('reports')


@login_required()
def account_ledger_with_credit_days(request):
    if request.method == "POST":
        debit_amount = 0
        credit_amount = 0
        pk = request.POST.get('account_title')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        company_info = Company_info.objects.all()
        image = Company_info.objects.filter(id=1).first()
        cursor = connection.cursor()
        cursor.execute('''Select tran_type,refrence_id,refrence_date,remarks,ref_inv_tran_id,ref_inv_tran_type,Sum(Debit) Debit,Sum(Credit) Credit,
                    IfNull((Select credit_days CreditDays from transaction_saleheader WHERE id = refrence_id),0) CreditDays
                    From (
                    Select Distinct account_id_id,'Opening' As tran_type,'' As refrence_id,'' As refrence_date,'Opening Balance' As remarks,
                    '' AS ref_inv_tran_id,'' AS ref_inv_tran_type,
                    Case When Sum(amount) > -1 Then  sum(amount) Else 0 End As Debit,
                    Case When Sum(amount) < -1 Then  sum(amount) Else 0 End As Credit
                    from (
                    Select id As Account_id_id, Sum(Opening_Balance) As amount
                    From transaction_chartofaccount Where ID = (
                    Select id from transaction_chartofaccount Where Parent_ID = %s)
                    Union All
                    Select id As account_id_id, Sum(Opening_Balance) As amount
                    From transaction_chartofaccount Where ID = (%s)
                    Union All
                    Select account_id_id,Sum(amount) As amount From transaction_transactions
                    where account_id_id in (
                    Case When (Select id from transaction_chartofaccount Where Parent_ID = %s)
                    <> '' Then (Select id from transaction_chartofaccount Where Parent_ID = %s)
                    Else (%s) END) AND refrence_date < %s
                    Union all
                    Select account_id_id,Sum(amount) As amount From transaction_transactions
                    where account_id_id in (%s) AND refrence_date < %s
                    ) tblData
                    Group By account_id_id
                    Union all
                    Select Distinct account_id_id,tran_type,refrence_id,refrence_date,remarks,ref_inv_tran_id,ref_inv_tran_type,
                    Case When amount > -1 Then  amount Else 0 End As Debit,
                    Case When amount < -1 Then  amount Else 0 End As Credit from (
                    Select * From transaction_transactions
                    where account_id_id in (
                    Case When (Select id from transaction_chartofaccount Where Parent_ID = %s)
                    <> '' Then (Select id from transaction_chartofaccount Where Parent_ID = %s)
                    Else (%s) END)
                    Union all
                    Select * From transaction_transactions
                    where account_id_id in (%s)
                    ) tblData
                    Where refrence_date Between %s And %s
                    Order By account_id_id,refrence_date Asc
                    ) As tblLedger
                    Group By tran_type,refrence_id,refrence_date,remarks,ref_inv_tran_id,ref_inv_tran_type
                    Order By refrence_date Asc
                    ''',[pk,pk,pk,pk,pk,from_date,pk,from_date,pk,pk,pk,pk,from_date,to_date])
        row = cursor.fetchall()
        print(row)
        ledger_list = []
        balance = 0
        for i,value in enumerate(row):
            balance = balance + float(value[6]) + float(value[7])
            today = datetime.date.today()
            past = value[2]
            if past:
                credit = today - past
            else:
                past = datetime.date.today()
                credit = today - past
            info = {
            "date": value[2],
            "voucher_no": value[3],
            "tran_type": value[0],
            "debit":value[6],
            "credit":value[7],
            "balance": balance,
            "credit_days": credit.days,
            }
            ledger_list.append(info)
        for value in row:
            print(value)
        if row:
            for v in row:
                if v[6] >= 0:
                    debit_amount = debit_amount + v[6]
                if v[7] <= 0:
                    credit_amount = credit_amount + v[7]
        account_id = ChartOfAccount.objects.filter(id = pk).first()
        account_title = account_id.account_title
        id = account_id.id
        pdf = render_to_pdf('transaction/account_ledger_with_credit_days.html', {'ledger_list':ledger_list,'company_info':company_info,'image':image,'row':row, 'debit_amount':debit_amount, 'credit_amount': credit_amount, 'account_title':account_title, 'from_date':from_date,'to_date':to_date,'id':id})
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Account_Ledger%s.pdf" %("000")
            content = "inline; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")
    return redirect('reports')


@login_required()
def cash_receiving_voucher(request):
    cursor = connection.cursor()
    all_vouchers = cursor.execute('''select * from transaction_voucherheader where voucher_no LIKE '%CRV%'
                                        order by voucher_no''')
    all_vouchers = all_vouchers.fetchall()
    return render(request, 'transaction/cash_receiving_voucher.html', {'all_vouchers': all_vouchers})


@login_required()
def view_cash_receiving(request, pk):
    header_id = VoucherHeader.objects.get(id=pk)
    voucher_header = VoucherHeader.objects.filter(id=pk).first()
    voucher_detail = VoucherDetail.objects.filter(header_id=header_id.id).all()
    return render(request, 'transaction/view_cash_receiving_voucher.html', {'voucher_header': voucher_header,'voucher_detail': voucher_detail})


@login_required()
def delete_cash_receiving(request,pk):
    ref_inv_tran_type = Q(ref_inv_tran_type = "Sale CRV")
    voucher_id = Q(voucher_id = pk)
    Transactions.objects.filter(ref_inv_tran_type, voucher_id).all().delete()
    VoucherDetail.objects.filter(header_id = pk).all().delete()
    VoucherHeader.objects.filter(id = pk).delete()
    messages.add_message(request, messages.SUCCESS, "Cash Receiving Voucher Deleted")
    return redirect('cash-receiving-voucher')


@login_required()
def new_cash_receiving_voucher(request):
    cursor = connection.cursor()
    get_last_tran_id = cursor.execute('''select * from transaction_voucherheader where voucher_no LIKE '%CRV%'
                                        order by voucher_no DESC LIMIT 1''')
    get_last_tran_id = get_last_tran_id.fetchall()

    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if get_last_tran_id:
        get_last_tran_id = get_last_tran_id[0][1]
        get_last_tran_id = get_last_tran_id[7:]
        serial = str((int(get_last_tran_id) + 1))
        get_last_tran_id = date[2:]+'CRV'+serial
    else:
        get_last_tran_id =  date[2:]+'CRV1'
    account_name = request.POST.get('account_title', False)
    check = request.POST.get('check', False)
    invoice_no = request.POST.get('invoice_no', False)
    print(invoice_no)
    all_accounts = ChartOfAccount.objects.all()
    all_invoices = SaleHeader.objects.all()
    user = request.user
    if account_name:
        if check == "1":
            print(invoice_no)
            id = ChartOfAccount.objects.get(account_title = account_name)
            pi = cursor.execute('''Select * From (
                                Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,0 As RcvAmount
                                from transaction_saleheader HD
                                Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
                                Left Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                Where Payment_method = 'Credit' And HD.account_id_id = %s AND  HD.sale_no = %s AND HD.ID Not In
                                (Select ref_inv_tran_id from transaction_transactions Where ref_inv_tran_type = 'Sale CRV')
                                Group by HD.ID,HD.account_id_id,account_title
                                Union All
                                Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,
                                (Select Sum(Amount) * -1 From transaction_transactions
                                Where ref_inv_tran_id = HD.ID AND account_id_id = %s) As RcvAmount
                                from transaction_saleheader HD
                                Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
                                Inner Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                Where Payment_method = 'Credit' AND HD.account_id_id = %s AND HD.sale_no = %s
                                Group By HD.ID,HD.account_id_id,account_title
                                Having InvAmount > RcvAmount
                                ) As tblPendingInvoice
                                Order By ID''',[id.id,invoice_no,id.id,id.id,invoice_no])
            pi = pi.fetchall()
            return JsonResponse({'pi':pi})
        else:
            id = ChartOfAccount.objects.get(account_title = account_name)
            pi = cursor.execute('''Select * From (
                                Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,0 As RcvAmount
                                from transaction_saleheader HD
                                Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
                                Left Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                Where Payment_method = 'Credit' And HD.account_id_id = %s AND HD.ID Not In
                                (Select ref_inv_tran_id from transaction_transactions Where ref_inv_tran_type = 'Sale CRV')
                                Group by HD.ID,HD.account_id_id,account_title
                                Union All
                                Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,
                                (Select Sum(Amount) * -1 From transaction_transactions
                                Where ref_inv_tran_id = HD.ID AND account_id_id = %s) As RcvAmount
                                from transaction_saleheader HD
                                Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
                                Inner Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                Where Payment_method = 'Credit' AND HD.account_id_id = %s
                                Group By HD.ID,HD.account_id_id,account_title
                                Having InvAmount > RcvAmount
                                ) As tblPendingInvoice
                                Order By ID''',[id.id,id.id,id.id])
            pi = pi.fetchall()
            return JsonResponse({'pi':pi})
    if request.method == "POST":
        invoice_no = request.POST.get('invoice_no', False)
        doc_date = request.POST.get('doc_date', False)
        description = request.POST.get('description', False)
        customer = request.POST.get('customer', False)
        date = request.POST.get('date', False)
        items = json.loads(request.POST.get('items', False))
        jv_header = VoucherHeader(voucher_no = get_last_tran_id, doc_no = invoice_no, doc_date = doc_date, cheque_no = "-",cheque_date = doc_date, description = description)
        jv_header.save()
        voucher_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
        for value in items:
            invoice_no = SaleHeader.objects.get(sale_no = value["invoice_no"])

            account_id = ChartOfAccount.objects.get(account_title = customer)
            cash_account = ChartOfAccount.objects.get(account_title = 'Cash')
            amount = float(value["debit"]) - float(value['balance'])

            tran1 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = amount,
                                date = date, remarks = get_last_tran_id, account_id = cash_account,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Sale CRV", voucher_id = voucher_id )
            tran1.save()
            tran2 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = -abs(amount),
                                date = date, remarks = get_last_tran_id, account_id = account_id,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Sale CRV", voucher_id = voucher_id )
            tran2.save()
            header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
            jv_detail1 = VoucherDetail(account_id = cash_account, debit = amount, credit = 0.00, header_id = header_id, invoice_id = invoice_no.id)
            jv_detail1.save()
            jv_detail2 = VoucherDetail(account_id = account_id,  debit = 0.00, credit = -abs(amount),header_id = header_id, invoice_id = invoice_no.id)
            jv_detail2.save()
        return JsonResponse({"result":"success"})
    return render(request, 'transaction/new_cash_receiving_voucher.html', {"all_accounts": all_accounts, 'get_last_tran_id': get_last_tran_id, 'all_invoices':all_invoices})

# def view_cash_receiving(request, pk):
#     header_id = VoucherHeader.objects.get(id=pk)
#     voucher_header = VoucherHeader.objects.filter(id=pk).first()
#     voucher_detail = VoucherDetail.objects.filter(header_id=header_id.id).all()
#     return render(request, 'transaction/view_cash_receiving_voucher.html', {'voucher_header': voucher_header,'voucher_detail': voucher_detail})
#
# def delete_cash_receiving(request,pk):
#     ref_inv_tran_type = Q(ref_inv_tran_type = "Sale CRV")
#     voucher_id = Q(voucher_id = pk)
#     Transactions.objects.filter(ref_inv_tran_type, voucher_id).all().delete()
#     VoucherDetail.objects.filter(header_id = pk).all().delete()
#     VoucherHeader.objects.filter(id = pk).delete()
#     messages.add_message(request, messages.SUCCESS, "Cash Receiving Voucher Deleted")
#     return redirect('cash-receiving-voucher')


@login_required()
def cash_payment_voucher(request):
    cursor = connection.cursor()
    all_vouchers = cursor.execute('''select * from transaction_voucherheader where voucher_no LIKE '%CPV%'
                                        order by voucher_no''')
    all_vouchers = all_vouchers.fetchall()
    return render(request, 'transaction/cash_payment_voucher.html', {'all_vouchers': all_vouchers})


@login_required()
def new_cash_payment_voucher(request):
    cursor = connection.cursor()
    get_last_tran_id = cursor.execute('''select * from transaction_voucherheader where voucher_no LIKE '%CPV%'
                                        order by voucher_no DESC LIMIT 1''')
    get_last_tran_id = get_last_tran_id.fetchall()

    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if get_last_tran_id:
        get_last_tran_id = get_last_tran_id[0][1]
        get_last_tran_id = get_last_tran_id[7:]
        serial = str((int(get_last_tran_id) + 1))
        get_last_tran_id = date[2:]+'CPV'+serial
    else:
        get_last_tran_id =  date[2:]+'CPV1'
    account_name = request.POST.get('account_title', False)
    check = request.POST.get('check', False)
    invoice_no = request.POST.get('invoice_no', False)
    print(invoice_no)
    all_accounts = ChartOfAccount.objects.all()
    all_invoices = PurchaseHeader.objects.all()
    user = request.user
    if account_name:
        if check == "1":
            id = ChartOfAccount.objects.get(account_title = account_name)
            pi = cursor.execute('''Select * From (
                                Select HD.ID,HD.account_id_id,HD.purchase_no,account_title,Sum(total_amount) As InvAmount,0 As RcvAmount
                                from transaction_purchaseheader HD
                                Inner join transaction_purchasedetail DT on DT.purchase_id_id = HD.id
                                Left Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                Where Payment_method = 'Credit' And HD.account_id_id = %s AND  HD.purchase_no = %s AND  HD.ID Not In
                                (Select ref_inv_tran_id from transaction_transactions Where ref_inv_tran_type = 'Sale CPV')
                                Group by HD.ID,HD.account_id_id,account_title
                                Union All
                                Select HD.ID,HD.account_id_id,HD.purchase_no,account_title,Sum(total_amount) As InvAmount,
                                (Select Sum(Amount) * -1 From transaction_transactions
                                Where ref_inv_tran_id = HD.ID AND account_id_id = %s) As RcvAmount
                                from transaction_purchaseheader HD
                                Inner join transaction_purchasedetail DT on DT.purchase_id_id = HD.id
                                Inner Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                Where Payment_method = 'Credit' AND HD.account_id_id = %s AND  HD.purchase_no = %s
                                Group By HD.ID,HD.account_id_id,account_title
                                Having InvAmount > RcvAmount
                                ) As tblPendingInvoice
                                Order By ID''',[id.id,invoice_no,id.id,id.id,invoice_no])
            pi = pi.fetchall()
            return JsonResponse({'pi':pi})
        else:
            id = ChartOfAccount.objects.get(account_title = account_name)
            pi = cursor.execute('''Select * From (
                                Select HD.ID,HD.account_id_id,HD.purchase_no,account_title,Sum(total_amount) As InvAmount,0 As RcvAmount
                                from transaction_purchaseheader HD
                                Inner join transaction_purchasedetail DT on DT.purchase_id_id = HD.id
                                Left Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                Where Payment_method = 'Credit' And HD.account_id_id = %s AND HD.ID Not In
                                (Select ref_inv_tran_id from transaction_transactions Where ref_inv_tran_type = 'Sale CPV')
                                Group by HD.ID,HD.account_id_id,account_title
                                Union All
                                Select HD.ID,HD.account_id_id,HD.purchase_no,account_title,Sum(total_amount) As InvAmount,
                                (Select Sum(Amount) * -1 From transaction_transactions
                                Where ref_inv_tran_id = HD.ID AND account_id_id = %s) As RcvAmount
                                from transaction_purchaseheader HD
                                Inner join transaction_purchasedetail DT on DT.purchase_id_id = HD.id
                                Inner Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                Where Payment_method = 'Credit' AND HD.account_id_id = %s
                                Group By HD.ID,HD.account_id_id,account_title
                                Having InvAmount > RcvAmount
                                ) As tblPendingInvoice
                                Order By ID''',[id.id,id.id,id.id])
            pi = pi.fetchall()
            return JsonResponse({'pi':pi})
    if request.method == "POST":
        invoice_no = request.POST.get('invoice_no', False)
        doc_date = request.POST.get('doc_date', False)
        description = request.POST.get('description', False)
        vendor = request.POST.get('vendor', False)
        date = request.POST.get('date', False)
        items = json.loads(request.POST.get('items', False))
        jv_header = VoucherHeader(voucher_no=get_last_tran_id, doc_no=invoice_no, doc_date = doc_date, cheque_no = "-",cheque_date = doc_date, description = description)
        jv_header.save()
        voucher_id = VoucherHeader.objects.get(voucher_no=get_last_tran_id)
        for value in items:
            invoice_no = PurchaseHeader.objects.get(purchase_no=value["invoice_no"])

            account_id = ChartOfAccount.objects.get(account_title = vendor)
            cash_account = ChartOfAccount.objects.get(account_title = 'Cash')
            amount = float(value["credit"]) - float(value['balance'])

            tran1 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = -abs(amount),
                                date = date, remarks = get_last_tran_id, account_id = cash_account,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Purchase CPV", voucher_id = voucher_id )
            tran1.save()
            tran2 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = amount,
                                date = date, remarks = get_last_tran_id, account_id = account_id,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Purchase CPV", voucher_id = voucher_id )
            tran2.save()
            header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
            jv_detail1 = VoucherDetail(account_id = cash_account, debit = 0.00, credit = -abs(amount), header_id = header_id, invoice_id = invoice_no.id)
            jv_detail1.save()
            jv_detail2 = VoucherDetail(account_id = account_id,  debit = amount, credit = 0.00,header_id = header_id, invoice_id = invoice_no.id)
            jv_detail2.save()
        return JsonResponse({"result":"success"})
    return render(request, 'transaction/new_cash_payment_voucher.html', {"all_accounts": all_accounts, 'get_last_tran_id': get_last_tran_id, 'all_invoices':all_invoices})


@login_required()
def view_cash_payment(request, pk):
    header_id = VoucherHeader.objects.get(id=pk)
    voucher_header = VoucherHeader.objects.filter(id=pk).first()
    voucher_detail = VoucherDetail.objects.filter(header_id=header_id.id).all()
    return render(request, 'transaction/view_cash_payment_voucher.html', {'voucher_header': voucher_header,
                                                                          'voucher_detail': voucher_detail})

@login_required()
def delete_cash_payment(request, pk):
    ref_inv_tran_type = Q(ref_inv_tran_type = "Purchase CPV")
    voucher_id = Q(voucher_id = pk)
    Transactions.objects.filter(ref_inv_tran_type, voucher_id).all().delete()
    VoucherDetail.objects.filter(header_id = pk).all().delete()
    VoucherHeader.objects.filter(id = pk).delete()
    messages.add_message(request, messages.SUCCESS, "Cash Payment Voucher Deleted")
    return redirect('cash-payment-voucher')


@login_required()
def job_order(request):
    all_job_order = JobOrderHeader.objects.all()
    return render(request, 'transaction/job_order.html',{'all_job_order':all_job_order})


@login_required()
def new_job_order(request):
    serial = "1"
    last_job_no = JobOrderHeader.objects.last()
    all_item_code = Add_item.objects.filter(unit = "sq.ft").all()
    all_accounts = ChartOfAccount.objects.all()
    date = datetime.date.today()
    date = date.strftime('%Y%m')
    if last_job_no:
        get_job_no = last_job_no.job_no[6:]
        serial = str((int(get_job_no) + 1))
        get_job_no = date[2:]+'JO'+serial
    else:
        get_job_no =  date[2:]+'JO'+serial
    item_code = request.POST.get('item_code', False)
    if item_code:
        row = Add_item.objects.filter(item_code = item_code)
        row = serializers.serialize('json',row)
        return HttpResponse(json.dumps({'row':row}))
    if request.method == 'POST':
        client_name = request.POST.get('client_name', False)
        file_name = request.POST.get('file_name', False)
        delivery_date = request.POST.get('delivery_date', False)
        remarks = request.POST.get('remarks', False)
        items = json.loads(request.POST.get('items'))
        if delivery_date:
            delivery_date = delivery_date
        else:
            delivery_date = "2010-10-06"
        account_id = ChartOfAccount.objects.get(account_title = client_name)
        job_order_header = JobOrderHeader(job_no = get_job_no, file_name = file_name, delivery_date = delivery_date, remarks = remarks, account_id = account_id)
        job_order_header.save()
        header_id = JobOrderHeader.objects.get(job_no = get_job_no)
        for value in items:
            item_id = Add_item.objects.get(item_code = value["item_code"])
            job_order_detail = JobOrderDetail(item_id = item_id, width = value["width"], height = value["height"], quantity = value["quantity"], meas = value["measurment"], header_id = header_id)
            job_order_detail.save()
        return JsonResponse({"result":"success"})
    return render(request, 'transaction/new_job_order.html',{"get_job_no":get_job_no,"all_item_code":all_item_code,"all_accounts":all_accounts})


@login_required()
def edit_job_order(request,pk):
    all_item_code = Add_item.objects.all()
    all_accounts = ChartOfAccount.objects.all()
    job_header = JobOrderHeader.objects.get(id = pk)
    job_detail = JobOrderDetail.objects.filter(header_id = pk).all()
    item_code = request.POST.get('item_code', False)
    if item_code:
        row = Add_item.objects.filter(item_code = item_code)
        row = serializers.serialize('json',row)
        return HttpResponse(json.dumps({'row':row}))
    if request.method == 'POST':
        job_detail.delete()
        client_name = request.POST.get('client_name', False)
        file_name = request.POST.get('file_name', False)
        delivery_date = request.POST.get('delivery_date', False)
        remarks = request.POST.get('remarks', False)
        items = json.loads(request.POST.get('items'))
        if delivery_date:
            delivery_date = delivery_date
        else:
            delivery_date = "2010-10-06"
        account_id = ChartOfAccount.objects.get(account_title = client_name)
        job_header.account_id = account_id
        job_header.file_name = file_name
        job_header.delivery_date = delivery_date
        job_header.remarks = remarks
        job_header.save()

        header_id = JobOrderHeader.objects.get(id = pk)
        for value in items:
            print("Hamza")
            print(value["id"])
            item_id = Add_item.objects.get(id = value["id"])
            print(item_id)
            job_order_detail = JobOrderDetail(item_id = item_id, width = value["width"], height = value["height"], quantity = value["quantity"], meas = value["measurment"], header_id = header_id)
            job_order_detail.save()
        return JsonResponse({"result":"success"})
    return render(request, 'transaction/edit_job_order.html',{"pk":pk,"all_item_code":all_item_code,"all_accounts":all_accounts, 'job_header':job_header, 'job_detail':job_detail})


@login_required()
def delete_job_order(request,pk):
    delete_job_order_detail = JobOrderDetail.objects.filter(header_id = pk).all().delete()
    delete_job_order_header = JobOrderHeader.objects.filter(id = pk).delete()
    messages.add_message(request, messages.SUCCESS, "Job Order Deleted")
    return redirect('job-order')


@login_required()
def edit_bank_receiving_voucher(request, pk):
    voucher_header = VoucherHeader.objects.filter(id=pk).first()
    voucher_detail = VoucherDetail.objects.filter(header_id=pk).all()
    account_id = request.POST.get('account_title', False)
    all_accounts = ChartOfAccount.objects.all()
    if account_id:
        data = ChartOfAccount.objects.filter(id=account_id).first()
        row = serializers.serialize('json', data)
        return HttpResponse(json.dumps({'row': row}))
    if request.method == 'POST':
        voucher_detail.delete()

        doc_no = request.POST.get('doc_no', False)
        doc_date = request.POST.get('doc_date', False)
        description = request.POST.get('description', False)
        cheque_no = request.POST.get('cheque_no', False)
        cheque_date = request.POST.get('cheque_date', False)

        voucher_header.doc_no = doc_no
        voucher_header.doc_date = doc_date
        voucher_header.description = description
        voucher_header.cheque_no = cheque_no
        voucher_header.cheque_date = cheque_date
        voucher_header.save()

        items = json.loads(request.POST.get('items'))

        for value in items:
            pass

    return render(request, 'transaction/edit_bank_receiving_voucher.html', {'voucher_header': voucher_header,
                                                                            'voucher_detail': voucher_detail, 'pk': pk,
                                                                            'all_accounts': all_accounts})

@login_required()
def journal_voucher_summary(request):
    cursor = connection.cursor()
    all_vouchers = cursor.execute('''select VH.id, VH.voucher_no, VH.doc_no, VH.doc_date, VH.cheque_no, VH.description,
                                            AU.username from transaction_voucherheader VH
                                            inner join auth_user AU on VH.user_id = AU.id
                                            where VH.voucher_no LIKE '%JV%' ''')
    all_vouchers = all_vouchers.fetchall()
    return render(request, 'transaction/journal_voucher_summary.html', {'all_vouchers': all_vouchers})


@login_required()
def edit_bank_payment_voucher(request, pk):
    voucher_header = VoucherHeader.objects.filter(id=pk).first()
    voucher_detail = VoucherDetail.objects.filter(header_id=pk).all()
    account_id = request.POST.get('account_title', False)
    all_accounts = ChartOfAccount.objects.all()
    if account_id:
        data = ChartOfAccount.objects.filter(id=account_id).first()
        row = serializers.serialize('json', data)
        return HttpResponse(json.dumps({'row': row}))
    if request.method == 'POST':
        voucher_detail.delete()

        doc_no = request.POST.get('doc_no', False)
        doc_date = request.POST.get('doc_date', False)
        description = request.POST.get('description', False)
        cheque_no = request.POST.get('cheque_no', False)
        cheque_date = request.POST.get('cheque_date', False)

        voucher_header.doc_no = doc_no
        voucher_header.doc_date = doc_date
        voucher_header.description = description
        voucher_header.cheque_no = cheque_no
        voucher_header.cheque_date = cheque_date
        voucher_header.save()

        items = json.loads(request.POST.get('items'))

        for value in items:
            pass
    return render(request, 'transaction/edit_bank_payment_voucher.html', {'voucher_header': voucher_header,
                                                                          'voucher_detail': voucher_detail,
                                                                          'all_accounts': all_accounts, 'pk': pk,
                                                                          'account_id': account_id})
@login_required()
def edit_cash_payment(request, pk):
    voucher_header = VoucherHeader.objects.filter(id=pk).first()
    voucher_detail = VoucherDetail.objects.filter(header_id=pk).all()
    account_id = request.POST.get('account_title', False)
    all_accounts = ChartOfAccount.objects.all()
    if account_id:
        data = ChartOfAccount.objects.filter(id=account_id).first()
        row = serializers.serialize('json', data)
        return HttpResponse(json.dumps({'row': row}))
    if request.method == 'POST':
        voucher_detail.delete()

        doc_no = request.POST.get('doc_no', False)
        doc_date = request.POST.get('doc_date', False)
        description = request.POST.get('description', False)

        voucher_header.doc_no = doc_no
        voucher_header.doc_date = doc_date
        voucher_header.description = description
        voucher_header.save()

        items = json.loads(request.POST.get('items'))

        for value in items:
            pass

    return render(request, 'transaction/edit_cash_payment_voucher.html', {'voucher_header': voucher_header,
                                                                            'voucher_detail': voucher_detail,
                                                                            'all_accounts': all_accounts, 'pk': pk,
                                                                            'account_id': account_id})


@login_required()
def edit_journal_voucher(request, pk):
    voucher_header = VoucherHeader.objects.filter(id=pk).first()
    voucher_detail = VoucherDetail.objects.filter(header_id=pk).all()
    account_id = request.POST.get('account_title', False)
    all_accounts = ChartOfAccount.objects.all()
    if account_id:
        account_info = ChartOfAccount.objects.filter(id=account_id).first()
        account_title = account_info.account_title
        account_id = account_info.id
        return JsonResponse({'account_title': account_title, 'account_id': account_id})
    if request.method == 'POST':
        voucher_detail.delete()

        ref = VoucherHeader.objects.get(id = pk)
        refrence_id = Q(refrence_id = ref.doc_no)
        tran_type = Q(tran_type = "JV")
        Transactions.objects.filter(refrence_id, tran_type).all().delete()

        doc_no = request.POST.get('doc_no', False)
        doc_date = request.POST.get('doc_date', False)
        description = request.POST.get('description', False)

        voucher_header.doc_no = doc_no
        voucher_header.doc_date = doc_date
        voucher_header.description = description
        voucher_header.save()

        items = json.loads(request.POST.get('items'))
        header_id = VoucherHeader.objects.get(id = voucher_header.id)

        for value in items:
            account_id = ChartOfAccount.objects.get(account_title=value["account_title"])
            if value["debit"] > "0" and value["debit"] > "0.00":
                tran1 = Transactions(refrence_id=doc_no, refrence_date=doc_date, tran_type='JV',
                                     amount=abs(float(value["debit"])),
                                     date=datetime.date.today(), remarks=voucher_header.voucher_no, account_id=account_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
                tran1.save()
                jv_detail1 = VoucherDetail(account_id=account_id, debit=abs(float(value["debit"])), credit=0.00,header_id=header_id, invoice_id = 0)
                jv_detail1.save()

            if value["credit"] > "0" and value["credit"] > "0.00":
                print(value["credit"])
                tran2 = Transactions(refrence_id=doc_no, refrence_date=doc_date, tran_type='JV',
                                     amount=-abs(float(value["credit"])),
                                     date=datetime.date.today(), remarks=voucher_header.voucher_no, account_id=account_id, ref_inv_tran_id = 0, ref_inv_tran_type = "")
                tran2.save()
                jv_detail2 = VoucherDetail(account_id=account_id, debit=0.00, credit=-abs(float(value["credit"])),header_id=header_id, invoice_id = 0)
                jv_detail2.save()
        return JsonResponse({"result": "success"})

    return render(request, 'transaction/edit_journal_voucher.html', {'voucher_header': voucher_header,
                                                                          'voucher_detail': voucher_detail,
                                                                          'all_accounts': all_accounts, 'pk': pk,
                                                                          'account_id': account_id})


@login_required()
def receivable_ledger(request):
    if request.method == "POST":
        inv_amount = 0
        rcv_amount = 0
        pk = request.POST.get('account_title')
        print(pk)
        invoice_no = request.POST.get('invoice_no')
        company_info = Company_info.objects.all()
        image = Company_info.objects.filter(id=1).first()
        cursor = connection.cursor()
        check = request.POST.get('check')
        if pk:
            if check == '1':
                cursor.execute('''Select * From (
                                                Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,0 As RcvAmount
                                                from transaction_saleheader HD
                                                Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
                                                Left Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                                Where Payment_method = 'Credit' And HD.account_id_id = %s AND  HD.sale_no = %s AND HD.ID Not In
                                                (Select ref_inv_tran_id from transaction_transactions Where ref_inv_tran_type = 'Sale CRV')
                                                Group by HD.ID,HD.account_id_id,account_title
                                                Union All
                                                Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,
                                                (Select Sum(Amount) * -1 From transaction_transactions
                                                Where ref_inv_tran_id = HD.ID AND account_id_id = %s) As RcvAmount
                                                from transaction_saleheader HD
                                                Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
                                                Inner Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                                Where Payment_method = 'Credit' AND HD.account_id_id = %s AND HD.sale_no = %s
                                                Group By HD.ID,HD.account_id_id,account_title
                                                Having InvAmount > RcvAmount
                                                ) As tblPendingInvoice
                                                Order By ID''', [pk.pk, invoice_no, pk.pk, pk.pk, invoice_no])
                row = cursor.fetchall()
            else:
                cursor.execute('''Select * From (
                                Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,0 As RcvAmount, HD.date, HD.credit_days
                                from transaction_saleheader HD
                                Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
                                Left Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                Where Payment_method = 'Credit' And HD.account_id_id = %s AND HD.ID Not In
                                (Select ref_inv_tran_id from transaction_transactions Where ref_inv_tran_type = 'Sale CRV')
                                Group by HD.ID,HD.account_id_id,account_title
                                Union All
                                Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,
                                (Select Sum(Amount) * -1 From transaction_transactions
                                Where ref_inv_tran_id = HD.ID AND account_id_id = %s) As RcvAmount, HD.date, HD.credit_days
                                from transaction_saleheader HD
                                Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
                                Inner Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                Where Payment_method = 'Credit' AND HD.account_id_id = %s
                                Group By HD.ID,HD.account_id_id,account_title
                                Having InvAmount > RcvAmount
                                ) As tblPendingInvoice
                                Order By ID''', [pk, pk, pk])
                row = cursor.fetchall()
        print(row)
        for value in row:
            print(value)
        if row:
            for v in row:
                inv_amount += v[4]
                rcv_amount += v[5]
        total_balance = inv_amount - rcv_amount
        print(total_balance)
        account_id = ChartOfAccount.objects.filter(id=pk).first()
        account_title = account_id.account_title
        id = account_id.id
        pdf = render_to_pdf('transaction/receivable_ledger_pdf.html',
                            {'company_info': company_info, 'image': image, 'row': row, 'inv_amount': inv_amount,
                             'rcv_amount': rcv_amount, 'account_title': account_title,
                             'id': id, 'total_balance': total_balance})
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "TrialBalance%s.pdf" % ("000")
            content = "inline; filename='%s'" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")
    return redirect('reports')


def all_receivable_ledger(request):
    pass


@login_required()
def payable_ledger(request):
    if request.method == "POST":
        inv_amount = 0
        paid_amount = 0
        pk = request.POST.get('account_title')
        invoice_no = request.POST.get('invoice_no')
        company_info = Company_info.objects.all()
        image = Company_info.objects.filter(id=1).first()
        cursor = connection.cursor()
        check = request.POST.get('check')
        if pk:
            if check == '1':
                cursor.execute('''Select * From (
                                    Select HD.ID,HD.account_id_id,HD.purchase_no,account_title,Sum(total_amount) As InvAmount,0 As RcvAmount
                                    from transaction_purchaseheader HD
                                    Inner join transaction_purchasedetail DT on DT.purchase_id_id = HD.id
                                    Left Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                    Where Payment_method = 'Credit' And HD.account_id_id = %s AND  HD.purchase_no = %s AND  HD.ID Not In
                                    (Select ref_inv_tran_id from transaction_transactions Where ref_inv_tran_type = 'Sale CPV')
                                    Group by HD.ID,HD.account_id_id,account_title
                                    Union All
                                    Select HD.ID,HD.account_id_id,HD.purchase_no,account_title,Sum(total_amount) As InvAmount,
                                    (Select Sum(Amount) * -1 From transaction_transactions
                                    Where ref_inv_tran_id = HD.ID AND account_id_id = %s) As RcvAmount
                                    from transaction_purchaseheader HD
                                    Inner join transaction_purchasedetail DT on DT.purchase_id_id = HD.id
                                    Inner Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                    Where Payment_method = 'Credit' AND HD.account_id_id = %s AND  HD.purchase_no = %s
                                    Group By HD.ID,HD.account_id_id,account_title
                                    Having InvAmount > RcvAmount
                                    ) As tblPendingInvoice
                                    Order By ID''', [pk.pk, invoice_no, pk.pk, pk.pk, invoice_no])
                row = cursor.fetchall()
            else:
                cursor.execute('''Select * From (
                                    Select HD.ID,HD.account_id_id,HD.purchase_no,account_title,Sum(total_amount) As InvAmount,0 As RcvAmount, HD.date
                                    from transaction_purchaseheader HD
                                    Inner join transaction_purchasedetail DT on DT.purchase_id_id = HD.id
                                    Left Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                    Where Payment_method = 'Credit' And HD.account_id_id = %s AND HD.ID Not In
                                    (Select ref_inv_tran_id from transaction_transactions Where ref_inv_tran_type = 'Purchase CPV')
                                    Group by HD.ID,HD.account_id_id,account_title
                                    Union All
                                    Select HD.ID,HD.account_id_id,HD.purchase_no,account_title,Sum(total_amount) As InvAmount,
                                    (Select Sum(Amount) * -1 From transaction_transactions
                                    Where ref_inv_tran_id = HD.ID AND account_id_id = %s) As RcvAmount, HD.date
                                    from transaction_purchaseheader HD
                                    Inner join transaction_purchasedetail DT on DT.purchase_id_id = HD.id
                                    Inner Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                    Where Payment_method = 'Credit' AND HD.account_id_id = %s
                                    Group By HD.ID,HD.account_id_id,account_title
                                    Having InvAmount > RcvAmount
                                    ) As tblPendingInvoice
                                    Order By ID
                                        ''', [pk, pk, pk,])
                row = cursor.fetchall()
        print(row)
        for value in row:
            print(value)
        if row:
            for v in row:
                inv_amount += v[4]
                paid_amount += v[5]
        total_balance = inv_amount + paid_amount
        print(total_balance)
        account_id = ChartOfAccount.objects.filter(id=pk).first()
        account_title = account_id.account_title
        id = account_id.id
        pdf = render_to_pdf('transaction/payable_ledger_pdf.html',
                            {'company_info': company_info, 'image': image, 'row': row, 'inv_amount': inv_amount,
                             'paid_amount': paid_amount, 'account_title': account_title,
                             'id': id, 'total_balance': total_balance})
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "TrialBalance%s.pdf" % ("000")
            content = "inline; filename='%s'" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")
    return redirect('reports')


@login_required()
def crv_pdf(request, pk):
    company_info = Company_info.objects.all()
    header = VoucherHeader.objects.filter(id = pk).first()
    details = VoucherDetail.objects.filter(debit = 0,header_id = header.id).first()
    cursor = connection.cursor()
    detail = cursor.execute('''select sum(VD.credit) as Amount,COA.account_title, COA.id
                            from transaction_voucherdetail VD
                            inner join transaction_voucherheader VH on VH.id = VD.header_id_id
                            inner join transaction_chartofaccount COA on VD.account_id_id = COA.id
                            where VD.header_id_id = %s AND VD.account_id_id = %s
                            ''',[header.id,details.account_id.id])
    detail = detail.fetchall()
    print(detail)
    amount_in_words =  num2words(abs(detail[0][0]))
    pdf = render_to_pdf('transaction/crv_pdf.html', {'company_info':company_info, 'header':header, 'detail':detail, 'amount_in_words':amount_in_words})
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "CashReceivingVoucher.pdf"
        content = "inline; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")


@login_required()
def cpv_pdf(request, pk):
    company_info = Company_info.objects.all()
    header = VoucherHeader.objects.filter(id = pk).first()
    details = VoucherDetail.objects.filter(credit = 0,header_id = header.id).first()
    cursor = connection.cursor()
    detail = cursor.execute('''select sum(VD.debit) as Amount,COA.account_title, COA.id
                            from transaction_voucherdetail VD
                            inner join transaction_voucherheader VH on VH.id = VD.header_id_id
                            inner join transaction_chartofaccount COA on VD.account_id_id = COA.id
                            where VD.header_id_id = %s AND VD.account_id_id = %s
                            ''',[header.id,details.account_id.id])
    detail = detail.fetchall()
    amount_in_words =  num2words(abs(detail[0][0]))
    pdf = render_to_pdf('transaction/cpv_pdf.html', {'company_info':company_info, 'header':header, 'detail':detail, 'amount_in_words':amount_in_words})
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "CashReceivingVoucher.pdf"
        content = "inline; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")


def jv_pdf(request, pk):
    company_info = Company_info.objects.all()
    header = VoucherHeader.objects.filter(id = pk).first()
    detail = VoucherDetail.objects.filter(header_id = header.id).all()
    debit = VoucherDetail.objects.filter(header_id = header.id).aggregate(Sum('debit'))
    credit = VoucherDetail.objects.filter(header_id = header.id).aggregate(Sum('credit'))
    pdf = render_to_pdf('transaction/jv_pdf.html', {'company_info':company_info, 'header':header, 'detail':detail, "debit":debit, "credit":credit})
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "CashReceivingVoucher.pdf"
        content = "inline; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")
