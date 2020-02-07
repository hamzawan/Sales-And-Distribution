from django.shortcuts import render, redirect
from inventory.models import Add_item
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from .models import (ChartOfAccount, PurchaseHeader, PurchaseReturnHeader, PurchaseDetail, SaleHeader, SaleDetail,
                    Company_info, SaleReturnDetail, SaleReturnHeader, VoucherHeader, VoucherDetail, Transactions,
                    JobOrderHeader, JobOrderDetail)
from users.models import (tblUserRights)
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
    user_id = Q(UserID = request.user.id)
    purchase_object_id = Q(ObjectID = 11)
    sale_object_id = Q(ObjectID = 12)
    jo_object_id = Q(ObjectID = 9)
    report_object_id = Q(ObjectID = 25)
    is_allow = Q(IsAllow = 1)
    action_id = Q(ActionID = 1)
    sale = tblUserRights.objects.filter(sale_object_id, user_id, is_allow, action_id)
    purchase = tblUserRights.objects.filter(purchase_object_id, user_id, is_allow, action_id)
    jo = tblUserRights.objects.filter(jo_object_id, user_id, is_allow, action_id)
    report = tblUserRights.objects.filter(report_object_id, user_id, is_allow, action_id)
    context = {
    'sale':sale,
    'purchase':purchase,
    'jo':jo,
    'report':report
    }
    return render(request, 'transaction/index.html', context)


def allow_purchase(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 11)
    is_allow = Q(IsAllow = 1)
    action_id = Q(ActionID = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


@login_required()
@user_passes_test(allow_purchase)
def purchase(request):
    request.session['objectID'] = 11
    cursor = connection.cursor()
    allow_purchases = cursor.execute('''select PH.id,PH.purchase_no,PH.follow_up, COA.account_title, abs(sum(PD.total_amount))
                                    from transaction_purchaseheader PH
                                    inner join transaction_purchasedetail PD on PD.purchase_id_id = PH.id
                                    inner join transaction_chartofaccount COA on COA.id = PH.account_id_id
                                    group by PH.purchase_no''')
    all_purchases = allow_purchases.fetchall()
    return render(request, 'transaction/purchase.html', {'all_purchases': all_purchases})


def allow_new_purchase(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 11)
    action_id = Q(ActionID = 2)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False

@login_required()
@user_passes_test(allow_new_purchase)
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
            detail_remarks = f"Purchase invoice amount {total_amount} RS, against invoice no {purchase_id} on Cash."
            tran2 = Transactions(refrence_id = header_id, refrence_date = date, account_id = account_id, tran_type = "Purchase Invoice", amount = total_amount, date = date, remarks = purchase_id, ref_inv_tran_id = 0, ref_inv_tran_type = "", detail_remarks = detail_remarks)
            tran2.save()
            tran1 = Transactions(refrence_id = header_id, refrence_date = date, account_id = cash_in_hand, tran_type = "Purchase Invoice", amount = -abs(total_amount), date = date, remarks = purchase_id, ref_inv_tran_id = 0, ref_inv_tran_type = "", detail_remarks = detail_remarks)
            tran1.save()
        else:
            detail_remarks = f"Purchase invoice {total_amount} RS, against invoice no {purchase_id} on Credit."
            purchase_account = ChartOfAccount.objects.get(account_title = 'Purchases')
            tran1 = Transactions(refrence_id = header_id, refrence_date = date, account_id = account_id, tran_type = "Purchase Invoice", amount = -abs(total_amount), date = date, remarks = purchase_id, ref_inv_tran_id = 0, ref_inv_tran_type = "", detail_remarks = detail_remarks)
            tran1.save()
            tran2 = Transactions(refrence_id = header_id, refrence_date = date, account_id = purchase_account, tran_type = "Purchase Invoice", amount = total_amount, date = date, remarks = purchase_id, ref_inv_tran_id = 0, ref_inv_tran_type = "", detail_remarks = detail_remarks)
            tran2.save()
        return JsonResponse({'result':'success'})
    return render(request, 'transaction/new_purchase.html',{"all_accounts":all_accounts,"last_purchase_no":last_purchase_no, 'all_item_code':all_item_code, 'all_pcs': all_pcs})


def voucher_avaliable_purchase(pk):
    # cusror = connection.cursor()
    # row = cusror.execute('''select case
    #                         when exists (select id from transaction_voucherdetail  where  invoice_id = %s)
    #                         then 'y'
    #                         else 'n'
    #                         end''',[pk])
    # row = row.fetchall()
    # res_list = [x[0] for x in row]
    # if res_list[0] == "n":
    refrence_id = Q(refrence_id = pk)
    tran_type = Q(tran_type = "Purchase Invoice")
    # ref_inv_tran_id = Q(ref_inv_tran_id = pk)
    # ref_inv_tran_type = Q(ref_inv_tran_type = "Purchase CPV")
    Transactions.objects.filter(refrence_id , tran_type).all().delete()
    # Transactions.objects.filter(ref_inv_tran_id , ref_inv_tran_type).all().delete()
    PurchaseDetail.objects.filter(purchase_id = pk).all().delete()
    PurchaseHeader.objects.filter(id = pk).delete()
    return True
    # else:
    #     return False


def allow_delete_purchase(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 11)
    action_id = Q(ActionID = 4)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


@login_required
@user_passes_test(allow_delete_purchase)
def delete_purchase(request, pk):
    item = voucher_avaliable_purchase(pk)
    if item == True:
        messages.add_message(request, messages.SUCCESS, "Purchase Invoice Deleted.")
        return redirect('purchase')
    else:
        messages.add_message(request, messages.ERROR, "You cannot delete this item, kindly delet it's voucher first.")
        return redirect('purchase')

def allow_edit_purchase(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 11)
    action_id = Q(ActionID = 3)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


def if_cpv_avaliable(pk):
    try:
        ref_inv_tran_id = Q(ref_inv_tran_id = pk)
        ref_inv_tran_type = Q(ref_inv_tran_type = "Purchase CPV")
        cpv_avaliable = Transactions.objects.filter(ref_inv_tran_id , ref_inv_tran_type).all()
        if cpv_avaliable:
            return False
        else:
            return True
    except Exception as e :
        print(e)

@login_required()
@user_passes_test(allow_edit_purchase)
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
            else:
                amount = float(value["sqft"]) * float(value["rate"])
                total_amount = total_amount + amount
                total_square_fit = value["sqft"]
                purchase_detail = PurchaseDetail(item_id = item_id, item_description = "", width = value["width"], height = value["height"], quantity = value["quantity"], meas = value["measurment"], rate = value["rate"], purchase_id = header_id, total_amount = amount, total_square_fit = total_square_fit, total_pcs = 0)
                net = net + total_amount
            purchase_detail.save()

        cash_in_hand = ChartOfAccount.objects.get(account_title = 'Cash')
        if payment_method == 'Cash':
            detail_remarks = f"Purchase invoice {total_amount} RS, against invoice no {purchase_header.footer_description} on Cash."
            refrence_id = Q(refrence_id = pk)
            tran_type = Q(tran_type = "Purchase Invoice")
            # ref_inv_tran_id = Q(ref_inv_tran_id = pk)
            # ref_inv_tran_type = Q(ref_inv_tran_type = "Purchase CPV")
            Transactions.objects.filter(refrence_id , tran_type).all().delete()
            # Transactions.objects.filter(ref_inv_tran_id , ref_inv_tran_type).all().delete()
            tran2 = Transactions(refrence_id = header_id.id, refrence_date = follow_up, account_id = account_id, tran_type = "Purchase Invoice", amount = total_amount, date = date, remarks = purchase_id, ref_inv_tran_id = 0, ref_inv_tran_type = "", detail_remarks = detail_remarks)
            tran2.save()
            tran1 = Transactions(refrence_id = header_id.id, refrence_date = follow_up, account_id = cash_in_hand, tran_type = "Purchase Invoice", amount = -abs(total_amount), date = date, remarks = purchase_id, ref_inv_tran_id = 0, ref_inv_tran_type = "", detail_remarks = detail_remarks)
            tran1.save()
        else:
            detail_remarks = f"Purchase invoice {total_amount} RS, against invoice no {purchase_header.footer_description} on Credit."
            refrence_id = Q(refrence_id = pk)
            tran_type = Q(tran_type = "Purchase Invoice")
            # ref_inv_tran_id = Q(ref_inv_tran_id = pk)
            # ref_inv_tran_type = Q(ref_inv_tran_type = "Purchase CPV")
            Transactions.objects.filter(refrence_id , tran_type).all().delete()
            # Transactions.objects.filter(ref_inv_tran_id , ref_inv_tran_type).all().delete()
            purchase_account = ChartOfAccount.objects.get(account_title = 'Purchases')
            tran1 = Transactions(refrence_id = header_id.id, refrence_date = follow_up, account_id = account_id, tran_type = "Purchase Invoice", amount = -abs(total_amount), date = follow_up, remarks = purchase_id, ref_inv_tran_id = 0, ref_inv_tran_type = "", detail_remarks = detail_remarks)
            tran1.save()
            tran2 = Transactions(refrence_id = header_id.id, refrence_date = follow_up, account_id = purchase_account, tran_type = "Purchase Invoice", amount = total_amount, date = follow_up, remarks = purchase_id, ref_inv_tran_id = 0, ref_inv_tran_type = "", detail_remarks = detail_remarks)
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


def allow_sale(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 12)
    action_id = Q(ActionID = 4)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


@login_required()
@user_passes_test(allow_sale)
def sale(request):
    request.session['objectID'] = 12
    all_sales = []
    cursor = connection.cursor()
    sales = cursor.execute('''select SH.id,SH.sale_no,SH.date, COA.account_title, SH.account_holder,SH.gst, SH.srb,SH.discount ,abs(sum(SD.total_amount))
                                from transaction_saleheader SH
                                inner join transaction_saledetail SD on SD.sale_id_id = SH.id
                                inner join transaction_chartofaccount COA on COA.id = SH.account_id_id
                                group by SH.sale_no''')
    sales = sales.fetchall()
    for value in sales:
        gst_amount = value[8] * value[5] / 100
        srb_amount = value[8] * value[6] / 100
        amount_before_discount = float(value[8]) + float(srb_amount) + float(gst_amount)
        discount_amount = amount_before_discount * value[7] / 100
        total_amount = amount_before_discount - discount_amount
        info = {
            'id': value[0],
            'sale_no': value[1],
            'date': value[2],
            'account_title': value[3],
            'account_holder': value[4],
            'total_amount': total_amount
        }
        all_sales.append(info)
    return render(request, 'transaction/sale.html',{"all_sales": all_sales})


def allow_sale_new(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 12)
    action_id = Q(ActionID = 2)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


@login_required()
@user_passes_test(allow_sale_new)
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
    account_name = request.POST.get('account_name',False)
    print("account name",account_name)
    from_date = '2019-01-01'
    to_date = datetime.date.today()
    if account_name:
        if account_name == "Walk in Customers":
            return JsonResponse({"debit_amount":0,"credit_amount":0})
        account_name = ChartOfAccount.objects.get(account_title = account_name)
        pk = account_name.id
        debit_amount = 0
        credit_amount = 0
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
                        Order By refrence_date Asc''',[pk,pk,pk,pk,pk,from_date,pk,from_date,pk,pk,pk,pk,from_date,to_date])

        row = cursor.fetchall()
        print(row)
        if row:
            for v in row:
                if v[6] >= 0:
                    debit_amount = debit_amount + v[6]
                if v[7] <= 0:
                    credit_amount = credit_amount + v[7]
        return JsonResponse({"debit_amount":debit_amount, "credit_amount":credit_amount})
    if request.method == "POST":
        sale_id = request.POST.get('sale_id',False)
        srb = request.POST.get('srb',False)
        gst = request.POST.get('gst',False)
        discount = request.POST.get('discount',False)
        po_no = request.POST.get('po_no',False)
        grn_no = request.POST.get('grn_no',False)
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

        sale_header = SaleHeader(sale_no = last_sale_no, date = date, footer_description = footer_desc, payment_method = payment_method, account_id = account_id, account_holder = account_holder, credit_days = credit_days ,follow_up = follow_up, user = current_user, srb=srb,gst=gst,discount=discount, po_no=po_no, grn_no=grn_no)
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
        net_srb = (float(total_amount) / 100) * float(srb)
        net_gst = (float(total_amount) / 100) * float(gst)
        amount_before_discount = net_gst + net_srb + total_amount
        discount_amount = (amount_before_discount / 100) * float(discount)
        net_amount = (float(net_srb) + float(net_gst) + float(total_amount) - float(discount_amount))
        header_id = header_id.id
        cash_in_hand = ChartOfAccount.objects.get(account_title = 'Cash')
        if payment_method == 'Cash':
            detail_remarks = f"Sale invoice amount {net_amount} RS, against invoice no {sale_id} on Cash."
            tran1 = Transactions(refrence_id = header_id, refrence_date = date, account_id = cash_in_hand, tran_type = "Sale Invoice", amount = net_amount, date = date, remarks = last_sale_no, ref_inv_tran_id = 0, ref_inv_tran_type = "", detail_remarks = detail_remarks)
            tran1.save()
            tran2 = Transactions(refrence_id = header_id, refrence_date = date, account_id = account_id, tran_type = "Sale Invoice", amount = -abs(net_amount), date = date, remarks = last_sale_no, ref_inv_tran_id = 0, ref_inv_tran_type = "", detail_remarks = detail_remarks)
            tran2.save()
        else:
            detail_remarks = f"Sale invoice amount {net_amount} RS, against invoice no {sale_id} on Credit."
            sale_account = ChartOfAccount.objects.get(account_title = 'Sales')
            tran1 = Transactions(refrence_id = header_id, refrence_date = date, account_id = account_id, tran_type = "Sale Invoice", amount = net_amount, date = date, remarks = last_sale_no, ref_inv_tran_id = 0, ref_inv_tran_type = "", detail_remarks = detail_remarks)
            tran1.save()
            tran2 = Transactions(refrence_id = header_id, refrence_date = date, account_id = sale_account, tran_type = "Sale Invoice", amount = -abs(net_amount), date = date, remarks = last_sale_no, ref_inv_tran_id = 0, ref_inv_tran_type = "", detail_remarks = detail_remarks)
            tran2.save()
        return JsonResponse({'result':'success'})
    return render(request, 'transaction/new_sale.html',{"all_accounts":all_accounts,"last_sale_no":last_sale_no, 'all_job_order':all_job_order,'all_pcs':all_pcs})



def voucher_avaliable_sale(pk):
    # cusror = connection.cursor()
    # row = cusror.execute('''select case
    #                         when exists (select id from transaction_voucherdetail  where  invoice_id = %s)
    #                         then 'y'
    #                         else 'n'
    #                         end''',[pk])
    # row = row.fetchall()
    # res_list = [x[0] for x in row]
    # if res_list[0] == "n":
    refrence_id = Q(refrence_id = pk)
    tran_type = Q(tran_type = "Sale Invoice")
    # ref_inv_tran_id = Q(ref_inv_tran_id = pk)
    # ref_inv_tran_type = Q(ref_inv_tran_type = "Sale CRV")
    Transactions.objects.filter(refrence_id , tran_type).all().delete()
    # Transactions.objects.filter(ref_inv_tran_id , ref_inv_tran_type).all().delete()
    SaleDetail.objects.filter(sale_id = pk).all().delete()
    SaleHeader.objects.filter(id = pk).delete()
    return True
    # else:
    #     return False


def allow_sale_delete(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 12)
    action_id = Q(ActionID = 4)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


@login_required
@user_passes_test(allow_sale_delete)
def delete_sale(request, pk):
    item = voucher_avaliable_sale(pk)
    if item == True:
        messages.add_message(request, messages.SUCCESS, "Sale Invoice Deleted.")
        return redirect('sale')
    else:
        messages.add_message(request, messages.ERROR, "You cannot delete this item, kindly delet it's voucher first.")
        return redirect('sale')

def allow_sale_edit(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 12)
    action_id = Q(ActionID = 3)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


def if_crv_avaliable(pk):
    try:
        ref_inv_tran_id = Q(ref_inv_tran_id = pk)
        ref_inv_tran_type = Q(ref_inv_tran_type = "Sale CRV")
        crv_avaliable = Transactions.objects.filter(ref_inv_tran_id , ref_inv_tran_type).all()
        if crv_avaliable:
            return False
        else:
            return True
    except Exception as e :
        print(e)

@login_required()
@user_passes_test(allow_sale_edit)
def edit_sale(request, pk):
    total_amount = 0
    total_amount_for_discount = 0
    total_amount_for_gst = 0
    total_amount_for_srb = 0
    net = 0
    job_no = JobOrderHeader.objects.all()
    sale_header = SaleHeader.objects.filter(id=pk).first()
    sale_detail = SaleDetail.objects.filter(sale_id=pk).all()
    for v in sale_detail:
        total_amount_for_discount = total_amount_for_discount + float(v.total_amount)
    total_amount_for_gst = float(total_amount_for_discount) / float(100)
    total_amount_for_gst = float(total_amount_for_gst) * float(sale_header.gst)
    total_amount_for_srb = float(total_amount_for_discount) / float(100)
    total_amount_for_srb = float(total_amount_for_srb) * float(sale_header.srb)
    total_amount_for_discount = total_amount_for_gst + total_amount_for_srb + total_amount_for_discount
    discount_amount = float(sale_header.discount) * float(total_amount_for_discount) / 100
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
        gst = request.POST.get('gst', False)
        srb = request.POST.get('srb', False)
        discount = request.POST.get('discount', False)
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
        sale_header.gst = gst
        sale_header.srb = srb
        sale_header.discount = discount
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
            detail_remarks = f"Sale invoice amount {total_amount} RS, against invoice no {sale_id} on Cash."
            refrence_id = Q(refrence_id = pk)
            tran_type = Q(tran_type = "Sale Invoice")
            # ref_inv_tran_id = Q(ref_inv_tran_id = pk)
            # ref_inv_tran_type = Q(ref_inv_tran_type = "Sale CRV")
            Transactions.objects.filter(refrence_id , tran_type).all().delete()
            # Transactions.objects.filter(ref_inv_tran_id , ref_inv_tran_type).all().delete()
            tran1 = Transactions(refrence_id = header_id, refrence_date = sale_header.date, account_id = cash_in_hand, tran_type = "Sale Invoice", amount = total_amount, date = date, remarks = sale_id, ref_inv_tran_id = 0, ref_inv_tran_type = "", detail_remarks = detail_remarks)
            tran1.save()
            tran2 = Transactions(refrence_id = header_id, refrence_date = sale_header.date, account_id = account_id, tran_type = "Sale Invoice", amount = -abs(total_amount), date = date, remarks = sale_id, ref_inv_tran_id = 0, ref_inv_tran_type = "", detail_remarks = detail_remarks)
            tran2.save()
        else:
            detail_remarks = f"Sale invoice amount {total_amount} RS, against invoice no {sale_id} on Credit."
            refrence_id = Q(refrence_id = pk)
            tran_type = Q(tran_type = "Sale Invoice")
            # ref_inv_tran_id = Q(ref_inv_tran_id = pk)
            # ref_inv_tran_type = Q(ref_inv_tran_type = "Sale CRV")
            Transactions.objects.filter(refrence_id , tran_type).all().delete()
            # Transactions.objects.filter(ref_inv_tran_id , ref_inv_tran_type).all().delete()
            sale_account = ChartOfAccount.objects.get(account_title = 'Sales')
            tran1 = Transactions(refrence_id = header_id, refrence_date = sale_header.date, account_id = account_id, tran_type = "Sale Invoice", amount = total_amount, date = date, remarks = sale_id, ref_inv_tran_id = 0, ref_inv_tran_type = "", detail_remarks = detail_remarks)
            tran1.save()
            tran2 = Transactions(refrence_id = header_id, refrence_date = sale_header.date, account_id = sale_account, tran_type = "Sale Invoice", amount = -abs(total_amount), date = date, remarks = sale_id, ref_inv_tran_id = 0, ref_inv_tran_type = "", detail_remarks = detail_remarks)
            tran2.save()
        return JsonResponse({'result':'success'})
    return render(request, 'transaction/edit_sale.html',
        {'job_no': job_no, 'sale_header': sale_header, 'sale_detail': sale_detail,'pk':pk, 'all_pcs':all_pcs,'discount_amount':discount_amount})


@login_required()
def sale_return_summary(request):
    all_sales_return = SaleReturnHeader.objects.all()
    return render(request, 'transaction/sale_return_summary.html', {'all_sales_return': all_sales_return})

@login_required()
def new_sale_return(request):
    return render(request, 'transaction/sale_return.html')

def allow_coa(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 10)
    action_id = Q(ActionID = 1)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False



@login_required()
@user_passes_test(allow_coa)
def chart_of_account(request):
    request.session['objectID'] = 10
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


def allow_coa_edit(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 10)
    action_id = Q(ActionID = 3)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


@login_required()
@user_passes_test(allow_coa_edit)
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


def allow_coa_delete(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 10)
    action_id = Q(ActionID = 4)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False



@login_required()
@user_passes_test(allow_coa_delete)
def delete_account(request, pk):
    item = account_avaliable(pk)
    if item == True:
        messages.add_message(request, messages.SUCCESS, "Account Deleted.")
        return redirect('chart-of-account')
    else:
        messages.add_message(request, messages.ERROR, "You cannot delete this Account, it is refrenced.")
        return redirect('chart-of-account')


def allow_purchase_print(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 11)
    action_id = Q(ActionID = 5)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False

@login_required()
@user_passes_test(allow_purchase_print)
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
            total_quantity = float(total_quantity) + float(value.total_pcs)
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


def allow_sale_print(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 12)
    action_id = Q(ActionID = 5)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


@login_required()
@user_passes_test(allow_sale_print)
def print_sale(request, pk):
    main_pk = pk
    lines = 0
    total_amount = 0
    total_quantity = 0
    total_square_fit = 0
    square_fit = 0
    total_balance_of_ledger = 0
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
        from_date = "2019-01-01"
        to_date = datetime.date.today()
        debit_amount = 0
        credit_amount = 0
        pk = header.account_id.id
        cursor = connection.cursor()
        cursor.execute('''select tran_type,refrence_id,date,remarks,ref_inv_tran_id,ref_inv_tran_type,Debit as Debit,Credit as Credit, detail_remarks from
                        (select '' as refrence_id,'Opening' as tran_type,'' as date,'' as ref_inv_tran_id,
                        '' as ref_inv_tran_type,'Opening Balance' as remarks,id,'' as detail_remarks,
                        Case When opening_balance > 0 then opening_balance else 0 End as Debit,
                        Case When opening_balance < 0 then opening_balance else 0 End as Credit
                        from transaction_chartofaccount Where id = %s
                        Union All
                        Select * From (
                        Select refrence_id,tran_type,date,ref_inv_tran_id,ref_inv_tran_type,
                        remarks,account_id_id,detail_remarks,
                        Case When amount > 0 then amount else 0 End as Debit,
                        Case When amount < 0 then amount else 0 End as Credit
                        from transaction_transactions
                        Where
                        DATE(date) Between %s And %s and is_partialy = 0
                        Order by date asc) As tblLedger
                        Where account_id_id = %s
                        union all
                        Select refrence_id,tran_type,date,'merge' as ref_inv_tran_id,ref_inv_tran_type,
                        remarks,account_id_id,'Partialy Receiving' as detail_remarks,
                        Case When amount > 0 then sum(amount) else 0 End as Debit,
                        Case When amount < 0 then sum(amount) else 0 End as Credit
                        from transaction_transactions
                        Where
                        DATE(date) Between %s And %s
                        and is_partialy = 1 and account_id_id = %s
                        group by refrence_id,tran_type,date,ref_inv_tran_type,
                        remarks,account_id_id
                        )
                        tbl order by date''',[pk,from_date,to_date,pk,from_date,to_date,pk])
    row = cursor.fetchall()
    for i,value in enumerate(row):
        print("HERE IS BREAK", value[1], main_pk)
        if value[0] == 'Sale Invoice' and value[7] > 0:
            total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
        elif value[0] == 'JV' and value[7] < 0:
            total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
        elif value[5] == 'Sale CRV' and value[7] < 0:
            total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
        elif value[5] == 'Purchase CPV' and value[7] > 0:
            total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
        elif value[0] == 'Opening' and value[7] < 0:
            total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
        elif value[0] == 'Opening' and value[7] > 0:
            total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
        elif value[0] == 'Purchase Invoice' and value[7] < 0:
            total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
        elif value[0] == 'Opening Balance' and value[7] < 0:
            total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
        elif value[0] == 'Opening Balance' and value[7] > 0:
            total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
        else:
            total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + 0
        if str(value[1]) == str(main_pk):
            break
    credit_balance = total_balance_of_ledger
    discount = float(header.discount) * float(total_amount) / 100
    total_amount_after_discount = total_amount  - discount
    pdf = render_to_pdf('transaction/sale_pdf.html', {'header':header, 'detail':detail,'image':image, 'total_lines':12, 'total_amount':total_amount, 'total_quantity':total_quantity,'total_square_fit':total_square_fit,"credit_balance":credit_balance,"total_amount_after_discount":total_amount_after_discount,"discount":discount})
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Sale_%s.pdf" % (header.sale_no)
        content = "inline; filename='%s'" % (filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")


@login_required()
@user_passes_test(allow_sale_print)
def print_sale_tax(request, pk):
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
    srb_amount = float(total_amount / 100) * float(header.srb)
    gst_amount = float(total_amount / 100) * float(header.gst)
    srb_percent = header.srb
    gst_percent = header.gst
    gst_srb = gst_amount + srb_amount
    amount_before_discount = gst_srb + total_amount
    discount = header.discount
    discount_amount = float(amount_before_discount / 100) * float(discount)
    gross_amount = amount_before_discount-discount_amount
    pdf = render_to_pdf('transaction/sales_tax_invoice.html', {'header':header, 'detail':detail,'image':image, 'total_lines':12, 'total_amount':total_amount, 'total_quantity':total_quantity,'total_square_fit':total_square_fit,"srb_amount":srb_amount,"gst_amount":gst_amount,"discount":discount,"gross_amount":gross_amount,"srb_percent":srb_percent,"gst_percent":gst_percent})
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Sale_%s.pdf" % (header.sale_no)
        content = "inline; filename='%s'" % (filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")


def allow_journal_voucher_new(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 12)
    action_id = Q(ActionID = 1)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False

@login_required()
@user_passes_test(allow_journal_voucher_new)
def journal_voucher(request):
    serial = "1"
    cursor = connection.cursor()
    get_last_tran_id = cursor.execute('''select * from transaction_voucherheader where voucher_no LIKE '%JV%'
                                        order by id DESC LIMIT 1''')
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
                                     date=datetime.date.today(), remarks=get_last_tran_id, account_id=account_id, ref_inv_tran_id = 0, ref_inv_tran_type = "", detail_remarks = description)
                tran1.save()
                jv_detail1 = VoucherDetail(account_id=account_id, debit=abs(float(value["debit"])), credit=0.00,header_id=header_id, invoice_id = 0)
                jv_detail1.save()
            print(value["debit"])
            if value["credit"] > "0" and value["credit"] > "0.00":
                print("run")
                print(value["credit"])
                tran2 = Transactions(refrence_id=doc_no, refrence_date=doc_date, tran_type='JV',
                                     amount=-abs(float(value["credit"])),
                                     date=datetime.date.today(), remarks=get_last_tran_id, account_id=account_id, ref_inv_tran_id = 0, ref_inv_tran_type = "", detail_remarks = description)
                tran2.save()
                jv_detail2 = VoucherDetail(account_id=account_id, debit=0.00, credit=-abs(float(value["credit"])),header_id=header_id, invoice_id = 0)
                jv_detail2.save()
        return JsonResponse({"result": "success"})
    return render(request, 'transaction/journal_voucher.html',{"all_accounts": all_accounts, 'get_last_tran_id': get_last_tran_id})


def allow_journal_voucher_delete(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 13)
    action_id = Q(ActionID = 4)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


@login_required()
@user_passes_test(allow_journal_voucher_delete)
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
            detail_amount = value["debit"]
            detail_remarks = f"Receive amount {detail_amount} RS, against invoice no {purchase_id} on Cash."
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

def allow_reports(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 25)
    action_id = Q(ActionID = 1)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


@login_required()
@user_passes_test(allow_reports)
def reports(request):
    all_accounts = ChartOfAccount.objects.all()
    return render(request, 'transaction/reports.html', {'all_accounts': all_accounts})

@login_required()
@user_passes_test(allow_reports)
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
    return redirect('reports')


@login_required()
@user_passes_test(allow_reports)
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
        cursor.execute('''select tran_type,refrence_id,date,remarks,ref_inv_tran_id,ref_inv_tran_type,Debit as Debit,Credit as Credit, detail_remarks, voucher_id_id from
                        (select '' as refrence_id,'Opening' as tran_type,'' as date,'' as ref_inv_tran_id,
                        '' as ref_inv_tran_type,'Opening Balance' as remarks,id,'' as detail_remarks,'' as voucher_id_id,
                        Case When opening_balance > 0 then opening_balance else 0 End as Debit,
                        Case When opening_balance < 0 then opening_balance else 0 End as Credit
                        from transaction_chartofaccount Where id = %s
                        Union All
                        Select * From (
                        Select refrence_id,tran_type,date,ref_inv_tran_id,ref_inv_tran_type,
                        remarks,account_id_id,detail_remarks,voucher_id_id,
                        Case When amount > 0 then amount else 0 End as Debit,
                        Case When amount < 0 then amount else 0 End as Credit
                        from transaction_transactions
                        Where
                        DATE(date) Between %s And %s and is_partialy = 0
                        Order by date asc) As tblLedger
                        Where account_id_id = %s
                        union all
                        Select refrence_id,tran_type,date,'merge' as ref_inv_tran_id,ref_inv_tran_type,
                        remarks,account_id_id,'Partialy Receiving' as detail_remarks,voucher_id_id,
                        Case When amount > 0 then sum(amount) else 0 End as Debit,
                        Case When amount < 0 then sum(amount) else 0 End as Credit
                        from transaction_transactions
                        Where
                        DATE(date) Between %s And %s
                        and is_partialy = 1 and account_id_id = %s
                        group by refrence_id,tran_type,date,ref_inv_tran_type,
                        remarks,account_id_id
                        )
                        tbl order by date''',[pk,from_date,to_date,pk,from_date,to_date,pk])
        row = cursor.fetchall()
        detail_remarks = ''
        ledger_list = []
        balance = 0
        partialy_debit = 0
        partialy_credit = 0
        total_balance_of_ledger = 0
        for i,value in enumerate(row):
            if value[0] == 'Sale Invoice' and value[7] > 0:
                balance = balance + float(value[6]) + float(value[7])
                total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
                sale_id = Q(id = value[1])
                client_sale_no = SaleHeader.objects.filter(sale_id).first()
                if client_sale_no.payment_method == 'Cash':
                    amount_value = abs(value[7])
                    detail_remarks = f'Sale invoice {amount_value} RS, on Cash.'
                else:
                    amount_value = abs(value[6])
                    detail_remarks = f'Sale invoice {amount_value} RS, on Credit.'
            elif value[0] == 'Sale Invoice' and value[6] > 0:
                balance = balance + float(value[6]) + float(value[7])
                total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
                sale_id = Q(id = value[1])
                client_sale_no = SaleHeader.objects.filter(sale_id).first()
                if client_sale_no.payment_method == 'Cash':
                    amount_value = abs(value[7])
                    detail_remarks = f'Sale invoice {amount_value} RS, on Cash.'
                else:
                    amount_value = abs(value[6])
                    detail_remarks = f'Sale invoice {amount_value} RS, on Credit.'
            elif value[0] == 'JV' and value[7] < 0:
                balance = balance + float(value[6]) + float(value[7])
                total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
                amount_value = abs(value[7])
                detail_remarks = f'Journal Voucher'
            elif value[5] == 'Sale CRV' and value[7] < 0:
                balance = balance + float(value[6]) + float(value[7])
                total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
                voucher_id = Q(id = value[9])
                voucher = VoucherHeader.objects.filter(voucher_id).first()
                s_detail = value[8]
                detail_remarks = f'{s_detail} Received amount, ({voucher.description}).'
            elif value[5] == 'Purchase CPV' and value[7] > 0:
                balance = balance + float(value[6]) - float(value[7])
                total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
                voucher_id = Q(id = value[9])
                voucher = VoucherHeader.objects.filter(voucher_id).first()
                s_detail = value[8]
                detail_remarks = f'{s_detail} Paid amount, ({voucher.description}).'
            elif value[5] == 'Purchase CPV' and value[6] > 0:
                balance = balance + float(value[6]) - float(value[7])
                total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
                voucher_id = Q(id = value[9])
                voucher = VoucherHeader.objects.filter(voucher_id).first()
                s_detail = value[8]
                detail_remarks = f'{s_detail} Paid amount, ({voucher.description}).'
            elif value[0] == 'Opening' and value[7] < 0:
                balance = balance + float(value[6]) + float(value[7])
                total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
                detail_remarks = 'Opening Balance'
            elif value[0] == 'Opening' and value[7] > 0:
                balance = balance + float(value[6]) + float(value[7])
                total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
                detail_remarks = 'Opening Balance'
            elif value[0] == 'Purchase Invoice' and value[7] < 0:
                balance = balance + float(value[6]) + float(value[7])
                total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
                purchase_id = Q(id = value[1])
                client_purchase_no = PurchaseHeader.objects.filter(purchase_id).first()
                if client_purchase_no.payment_method == 'Cash':
                    amount_value = abs(value[6])
                    detail_remarks = f'Purchase invoice ,against invoice no {client_sale_no.footer_description} on Cash.'
                else:
                    amount_value = abs(value[6])
                    detail_remarks = f'Purchase invoice , against invoice no {client_purchase_no.footer_description} on Credit.'
            elif value[0] == 'Opening Balance' and value[7] < 0:
                balance = balance + float(value[6]) + float(value[7])
                total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
                detail_remarks = 'Opening Balance'
            elif value[0] == 'Opening Balance' and value[7] > 0:
                balance = balance + float(value[6]) - float(value[7])
                total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
                detail_remarks = 'Opening Balance'
            else:
                balance = balance + float(value[6]) + 0
                total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + 0
            info = {
            "date": value[2],
            "voucher_no": value[3],
            "tran_type": value[0],
            "debit":value[6],
            "credit":value[7],
            "balance": balance,
            "detail_remarks":detail_remarks,
            }
            ledger_list.append(info)
        # for value in row:
        #     print(value)
        if row:
            for v in row:
                if v[6] >= 0:
                    debit_amount = debit_amount + v[6]
                if v[7] <= 0:
                    credit_amount = credit_amount + v[7]
        account_id = ChartOfAccount.objects.filter(id = pk).first()
        account_title = account_id.account_title
        id = account_id.id
        pdf = render_to_pdf('transaction/account_ledger_pdf.html', {'ledger_list':ledger_list,'company_info':company_info,'image':image,'row':row, 'debit_amount':debit_amount, 'credit_amount': credit_amount, 'account_title':account_title, 'from_date':from_date,'to_date':to_date,'id':id,'total_balance_of_ledger':total_balance_of_ledger})
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Account_Ledger%s.pdf" %("000")
            content = "inline; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")
    return redirect('reports')


@login_required()
@user_passes_test(allow_reports)
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
        cursor.execute('''Select tran_type,refrence_id,refrence_date,remarks,ref_inv_tran_id,ref_inv_tran_type,Sum(Debit) Debit,Sum(Credit) Credit, detail_remarks From (
                        Select Distinct account_id_id,'Opening' As tran_type,'' As refrence_id,'' As refrence_date,'Opening Balance' As remarks,
                        '' AS ref_inv_tran_id,'' AS ref_inv_tran_type,
                        Case When Sum(amount) > -1 Then  sum(amount) Else 0 End As Debit,
                        Case When Sum(amount) < -1 Then  sum(amount) Else 0 End As Credit,'' As detail_remarks from (
                        Select id As Account_id_id, Sum(Opening_Balance) As amount
                        From transaction_chartofaccount Where ID = (
                        Select id from transaction_chartofaccount Where Parent_ID = 115)
                        Union All
                        Select id As account_id_id, Sum(Opening_Balance) As amount
                        From transaction_chartofaccount Where ID = (115)
                        Union All
                        Select account_id_id,Sum(amount) As amount From transaction_transactions
                        where account_id_id in (
                        Case When (Select id from transaction_chartofaccount Where Parent_ID = 115)
                        <> '' Then (Select id from transaction_chartofaccount Where Parent_ID = 115)
                        Else (115) END) AND refrence_date < '2019-08-01'
                        Union all
                        Select account_id_id,Sum(amount) As amount From transaction_transactions
                        where account_id_id in (115) AND refrence_date < '2019-08-01'
                        ) tblData
                        Group By account_id_id
                        Union all
                        Select Distinct account_id_id,tran_type,refrence_id,refrence_date,remarks,ref_inv_tran_id,ref_inv_tran_type,
                        Case When amount > -1 Then  amount Else 0 End As Debit,
                        Case When amount < -1 Then  amount Else 0 End As Credit, detail_remarks from (
                        Select * From transaction_transactions
                        where account_id_id in (
                        Case When (Select id from transaction_chartofaccount Where Parent_ID = 115)
                        <> '' Then (Select id from transaction_chartofaccount Where Parent_ID = 115)
                        Else (115) END)
                        Union all
                        Select * From transaction_transactions
                        where account_id_id in (115)
                        ) tblData
                        Where refrence_date Between '2019-08-01' And '2020-10-10'
                        Order By account_id_id,refrence_date Asc
                        ) As tblLedger
                        Group By tran_type,refrence_id,refrence_date,remarks,ref_inv_tran_id,ref_inv_tran_type
                        Order By refrence_date Asc''')
        row = cursor.fetchall()
        print(row)
        ledger_list = []
        balance = 0
        total_balance_of_ledger = 0
        for i,value in enumerate(row):
            if value[0] == 'Sale Invoice' and value[7] > 0:
                balance = balance + float(value[6]) + float(value[7])
                total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
            elif value[0] == 'JV' and value[7] < 0:
                balance = balance + float(value[6]) + float(value[7])
                total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
            elif value[5] == 'Sale CRV' and value[7] < 0:
                balance = balance + float(value[6]) + float(value[7])
                total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
            elif value[0] == 'Opening' and value[7] < 0:
                balance = balance + float(value[6]) + float(value[7])
                total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
            elif value[0] == 'Opening' and value[7] > 0:
                balance = balance + float(value[6]) + float(value[7])
                total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
            elif value[0] == 'Opening Balance' and value[7] < 0:
                balance = balance + float(value[6]) + float(value[7])
                total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
            elif value[0] == 'Opening Balance' and value[7] > 0:
                balance = balance + float(value[6]) - float(value[7])
                total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + float(value[7])
            else:
                balance = balance + float(value[6]) + 0
                total_balance_of_ledger = total_balance_of_ledger + float(value[6]) + 0
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
        pdf = render_to_pdf('transaction/account_ledger_with_credit_days.html', {'ledger_list':ledger_list,'company_info':company_info,'image':image,'row':row, 'debit_amount':debit_amount, 'credit_amount': credit_amount, 'account_title':account_title, 'from_date':from_date,'to_date':to_date,'id':id,'total_balance_of_ledger':total_balance_of_ledger})
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Account_Ledger%s.pdf" %("000")
            content = "inline; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")
    return redirect('reports')


def allow_crv(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 14)
    action_id = Q(ActionID = 1)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


@login_required()
@user_passes_test(allow_crv)
def cash_receiving_voucher(request):
    request.session['objectID'] = 14
    cursor = connection.cursor()
    all_vouchers = cursor.execute('''select VH.id,VH.voucher_no, VH.doc_date, COA.account_title, VH.description, sum(abs(VD.credit)),sum(abs(VD.debit))
                                from transaction_voucherheader VH
                                inner join transaction_voucherdetail VD on VD.header_id_id = VH.id
                                inner join transaction_chartofaccount COA on COA.id = VD.account_id_id
                                where VD.account_id_id != 6 and voucher_no LIKE '%CRV%'
                                group by VH.voucher_no''')
    all_vouchers = all_vouchers.fetchall()
    return render(request, 'transaction/cash_receiving_voucher.html', {'all_vouchers': all_vouchers})


def allow_crv_view(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 14)
    action_id = Q(ActionID = 3)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False

@login_required()
@user_passes_test(allow_crv_view)
def view_cash_receiving(request, pk):
    header_id = VoucherHeader.objects.get(id=pk)
    voucher_header = VoucherHeader.objects.filter(id=pk).first()
    voucher_detail = VoucherDetail.objects.filter(header_id=header_id.id).all()
    return render(request, 'transaction/view_cash_receiving_voucher.html', {'voucher_header': voucher_header,'voucher_detail': voucher_detail})


def allow_crv_delete(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 14)
    action_id = Q(ActionID = 4)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


@login_required()
@user_passes_test(allow_crv_delete)
def delete_cash_receiving(request,pk):
    ref_inv_tran_type = Q(ref_inv_tran_type = "Sale CRV")
    voucher_id = Q(voucher_id = pk)
    Transactions.objects.filter(ref_inv_tran_type, voucher_id).all().delete()
    tran_type = Q(tran_type = "Opening Balance")
    Transactions.objects.filter(tran_type, voucher_id).all().delete()
    VoucherDetail.objects.filter(header_id = pk).all().delete()
    VoucherHeader.objects.filter(id = pk).delete()
    messages.add_message(request, messages.SUCCESS, "Cash Receiving Voucher Deleted")
    return redirect('cash-receiving-voucher')


def allow_crv_new(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 14)
    action_id = Q(ActionID = 2)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


# @login_required()
# @user_passes_test(allow_crv_new)
# def new_cash_receiving_voucher(request):
#     cursor = connection.cursor()
#     get_last_tran_id = cursor.execute('''select * from transaction_voucherheader where voucher_no LIKE '%CRV%'
#                                         order by voucher_no DESC LIMIT 1''')
#     get_last_tran_id = get_last_tran_id.fetchall()
#
#     date = datetime.date.today()
#     date = date.strftime('%Y%m')
#     if get_last_tran_id:
#         get_last_tran_id = get_last_tran_id[0][1]
#         get_last_tran_id = get_last_tran_id[7:]
#         serial = str((int(get_last_tran_id) + 1))
#         get_last_tran_id = date[2:]+'CRV'+serial
#     else:
#         get_last_tran_id =  date[2:]+'CRV1'
#     account_name = request.POST.get('account_title', False)
#     check = request.POST.get('check', False)
#     invoice_no = request.POST.get('invoice_no', False)
#     all_accounts = ChartOfAccount.objects.all()
#     all_invoices = SaleHeader.objects.all()
#     user = request.user
#     if account_name:
#         if check == "1":
#             print(invoice_no)
#             id = ChartOfAccount.objects.get(account_title = account_name)
#             pi = cursor.execute('''Select * From (
#                                 Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,0 As RcvAmount
#                                 from transaction_saleheader HD
#                                 Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
#                                 Left Join transaction_chartofaccount COA on HD.account_id_id = COA.id
#                                 Where Payment_method = 'Credit' And HD.account_id_id = %s AND  HD.sale_no = %s AND HD.ID Not In
#                                 (Select ref_inv_tran_id from transaction_transactions Where ref_inv_tran_type = 'Sale CRV')
#                                 Group by HD.ID,HD.account_id_id,account_title
#                                 Union All
#                                 Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,
#                                 (Select Sum(Amount) * -1 From transaction_transactions
#                                 Where ref_inv_tran_id = HD.ID AND account_id_id = %s) As RcvAmount
#                                 from transaction_saleheader HD
#                                 Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
#                                 Inner Join transaction_chartofaccount COA on HD.account_id_id = COA.id
#                                 Where Payment_method = 'Credit' AND HD.account_id_id = %s AND HD.sale_no = %s
#                                 Group By HD.ID,HD.account_id_id,account_title
#                                 Having InvAmount > RcvAmount
#                                 ) As tblPendingInvoice
#                                 Order By ID''',[id.id,invoice_no,id.id,id.id,invoice_no])
#             pi = pi.fetchall()
#             return JsonResponse({'pi':pi})
#         else:
#             id = ChartOfAccount.objects.get(account_title = account_name)
#             pi = cursor.execute('''Select * From (
#                                 Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,0 As RcvAmount
#                                 from transaction_saleheader HD
#                                 Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
#                                 Left Join transaction_chartofaccount COA on HD.account_id_id = COA.id
#                                 Where Payment_method = 'Credit' And HD.account_id_id = %s AND HD.ID Not In
#                                 (Select ref_inv_tran_id from transaction_transactions Where ref_inv_tran_type = 'Sale CRV')
#                                 Group by HD.ID,HD.account_id_id,account_title
#                                 Union All
#                                 Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,
#                                 (Select Sum(Amount) * -1 From transaction_transactions
#                                 Where ref_inv_tran_id = HD.ID AND account_id_id = %s) As RcvAmount
#                                 from transaction_saleheader HD
#                                 Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
#                                 Inner Join transaction_chartofaccount COA on HD.account_id_id = COA.id
#                                 Where Payment_method = 'Credit' AND HD.account_id_id = %s
#                                 Group By HD.ID,HD.account_id_id,account_title
#                                 Having InvAmount > RcvAmount
#                                 ) As tblPendingInvoice
#                                 Order By ID''',[id.id,id.id,id.id])
#             pi = pi.fetchall()
#             return JsonResponse({'pi':pi})
#     if request.method == "POST":
#         invoice_no = request.POST.get('invoice_no', False)
#         doc_date = request.POST.get('doc_date', False)
#         description = request.POST.get('description', False)
#         customer = request.POST.get('customer', False)
#         date = request.POST.get('date', False)
#         items = json.loads(request.POST.get('items', False))
#         jv_header = VoucherHeader(voucher_no = get_last_tran_id, doc_no = invoice_no, doc_date = doc_date, cheque_no = "-",cheque_date = doc_date, description = description)
#         jv_header.save()
#         voucher_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
#         for value in items:
#             invoice_no = SaleHeader.objects.get(sale_no = value["invoice_no"])
#
#             account_id = ChartOfAccount.objects.get(account_title = customer)
#             cash_account = ChartOfAccount.objects.get(account_title = 'Cash')
#             amount = float(value["debit"]) - float(value['balance'])
#
#             tran1 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = amount,
#                                 date = date, remarks = description, account_id = cash_account,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Sale CRV", voucher_id = voucher_id )
#             tran1.save()
#             tran2 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = -abs(amount),
#                                 date = date, remarks = description, account_id = account_id,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Sale CRV", voucher_id = voucher_id )
#             tran2.save()
#             header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
#             jv_detail1 = VoucherDetail(account_id = cash_account, debit = amount, credit = 0.00, header_id = header_id, invoice_id = invoice_no.id)
#             jv_detail1.save()
#             jv_detail2 = VoucherDetail(account_id = account_id,  debit = 0.00, credit = -abs(amount),header_id = header_id, invoice_id = invoice_no.id)
#             jv_detail2.save()
#         return JsonResponse({"result":"success"})
#     return render(request, 'transaction/new_cash_receiving_voucher.html', {"all_accounts": all_accounts, 'get_last_tran_id': get_last_tran_id, 'all_invoices':all_invoices})


def allow_cpv(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 15)
    action_id = Q(ActionID = 1)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


@login_required()
@user_passes_test(allow_cpv)
def cash_payment_voucher(request):
    request.session['objectID'] = 15
    cursor = connection.cursor()
    all_vouchers = cursor.execute('''select VH.id,VH.voucher_no, VH.doc_date, COA.account_title, VH.description, sum(abs(VD.debit))
                                from transaction_voucherheader VH
                                inner join transaction_voucherdetail VD on VD.header_id_id = VH.id
                                inner join transaction_chartofaccount COA on COA.id = VD.account_id_id
                                where VD.account_id_id != 6 and voucher_no LIKE '%CPV%'
                                group by VH.voucher_no''')
    all_vouchers = all_vouchers.fetchall()
    return render(request, 'transaction/cash_payment_voucher.html', {'all_vouchers': all_vouchers})


def allow_cpv_new(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 15)
    action_id = Q(ActionID = 2)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False

#
# def new_cash_payment_voucher(request):
#     cursor = connection.cursor()
#     get_last_tran_id = cursor.execute('''select * from transaction_voucherheader where voucher_no LIKE '%CPV%'
#                                         order by voucher_no DESC LIMIT 1''')
#     get_last_tran_id = get_last_tran_id.fetchall()
#
#     date = datetime.date.today()
#     date = date.strftime('%Y%m')
#     if get_last_tran_id:
#         get_last_tran_id = get_last_tran_id[0][1]
#         get_last_tran_id = get_last_tran_id[7:]
#         serial = str((int(get_last_tran_id) + 1))
#         get_last_tran_id = date[2:]+'CPV'+serial
#     else:
#         get_last_tran_id =  date[2:]+'CPV1'
#     account_name = request.POST.get('account_title', False)
#     check = request.POST.get('check', False)
#     invoice_no = request.POST.get('invoice_no', False)
#     all_accounts = ChartOfAccount.objects.all()
#     all_invoices = PurchaseHeader.objects.all()
#     user = request.user
#     if account_name:
#         if check == "1":
#             id = ChartOfAccount.objects.get(account_title = account_name)
#             pi = cursor.execute('''Select * From (
#                                 Select HD.ID,HD.account_id_id,HD.purchase_no,account_title,Sum(total_amount) As InvAmount,0 As RcvAmount
#                                 from transaction_purchaseheader HD
#                                 Inner join transaction_purchasedetail DT on DT.purchase_id_id = HD.id
#                                 Left Join transaction_chartofaccount COA on HD.account_id_id = COA.id
#                                 Where Payment_method = 'Credit' And HD.account_id_id = %s AND  HD.purchase_no = %s AND  HD.ID Not In
#                                 (Select ref_inv_tran_id from transaction_transactions Where ref_inv_tran_type = 'Sale CPV')
#                                 Group by HD.ID,HD.account_id_id,account_title
#                                 Union All
#                                 Select HD.ID,HD.account_id_id,HD.purchase_no,account_title,Sum(total_amount) As InvAmount,
#                                 (Select Sum(Amount) * -1 From transaction_transactions
#                                 Where ref_inv_tran_id = HD.ID AND account_id_id = %s) As RcvAmount
#                                 from transaction_purchaseheader HD
#                                 Inner join transaction_purchasedetail DT on DT.purchase_id_id = HD.id
#                                 Inner Join transaction_chartofaccount COA on HD.account_id_id = COA.id
#                                 Where Payment_method = 'Credit' AND HD.account_id_id = %s AND  HD.purchase_no = %s
#                                 Group By HD.ID,HD.account_id_id,account_title
#                                 Having InvAmount > RcvAmount
#                                 ) As tblPendingInvoice
#                                 Order By ID''',[id.id,invoice_no,id.id,id.id,invoice_no])
#             pi = pi.fetchall()
#             return JsonResponse({'pi':pi})
#         else:
#             id = ChartOfAccount.objects.get(account_title = account_name)
#             pi = cursor.execute('''Select * From (
#                                 Select HD.ID,HD.account_id_id,HD.purchase_no,account_title,Sum(total_amount) As InvAmount,0 As RcvAmount
#                                 from transaction_purchaseheader HD
#                                 Inner join transaction_purchasedetail DT on DT.purchase_id_id = HD.id
#                                 Left Join transaction_chartofaccount COA on HD.account_id_id = COA.id
#                                 Where Payment_method = 'Credit' And HD.account_id_id = %s AND HD.ID Not In
#                                 (Select ref_inv_tran_id from transaction_transactions Where ref_inv_tran_type = 'Sale CPV')
#                                 Group by HD.ID,HD.account_id_id,account_title
#                                 Union All
#                                 Select HD.ID,HD.account_id_id,HD.purchase_no,account_title,Sum(total_amount) As InvAmount,
#                                 (Select Sum(Amount) * -1 From transaction_transactions
#                                 Where ref_inv_tran_id = HD.ID AND account_id_id = %s) As RcvAmount
#                                 from transaction_purchaseheader HD
#                                 Inner join transaction_purchasedetail DT on DT.purchase_id_id = HD.id
#                                 Inner Join transaction_chartofaccount COA on HD.account_id_id = COA.id
#                                 Where Payment_method = 'Credit' AND HD.account_id_id = %s
#                                 Group By HD.ID,HD.account_id_id,account_title
#                                 Having InvAmount > RcvAmount
#                                 ) As tblPendingInvoice
#                                 Order By ID''',[id.id,id.id,id.id])
#             pi = pi.fetchall()
#             return JsonResponse({'pi':pi})
#     if request.method == "POST":
#         invoice_no = request.POST.get('invoice_no', False)
#         doc_date = request.POST.get('doc_date', False)
#         description = request.POST.get('description', False)
#         vendor = request.POST.get('vendor', False)
#         date = request.POST.get('date', False)
#         items = json.loads(request.POST.get('items', False))
#         jv_header = VoucherHeader(voucher_no=get_last_tran_id, doc_no=invoice_no, doc_date = doc_date, cheque_no = "-",cheque_date = doc_date, description = description)
#         jv_header.save()
#         voucher_id = VoucherHeader.objects.get(voucher_no=get_last_tran_id)
#         for value in items:
#             invoice_no = PurchaseHeader.objects.get(purchase_no=value["invoice_no"])
#
#             account_id = ChartOfAccount.objects.get(account_title = vendor)
#             cash_account = ChartOfAccount.objects.get(account_title = 'Cash')
#             amount = float(value["credit"]) - float(value['balance'])
#
#             tran1 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = -abs(amount),
#                                 date = date, remarks = get_last_tran_id, account_id = cash_account,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Purchase CPV", voucher_id = voucher_id )
#             tran1.save()
#             tran2 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = amount,
#                                 date = date, remarks = get_last_tran_id, account_id = account_id,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Purchase CPV", voucher_id = voucher_id )
#             tran2.save()
#             header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
#             jv_detail1 = VoucherDetail(account_id = cash_account, debit = 0.00, credit = -abs(amount), header_id = header_id, invoice_id = invoice_no.id)
#             jv_detail1.save()
#             jv_detail2 = VoucherDetail(account_id = account_id,  debit = amount, credit = 0.00,header_id = header_id, invoice_id = invoice_no.id)
#             jv_detail2.save()
#         return JsonResponse({"result":"success"})
#     return render(request, 'transaction/new_cash_payment_voucher.html', {"all_accounts": all_accounts, 'get_last_tran_id': get_last_tran_id, 'all_invoices':all_invoices})


def allow_cpv_view(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 15)
    action_id = Q(ActionID = 3)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False

@login_required()
@user_passes_test(allow_cpv_view)
def view_cash_payment(request, pk):
    header_id = VoucherHeader.objects.get(id=pk)
    voucher_header = VoucherHeader.objects.filter(id=pk).first()
    voucher_detail = VoucherDetail.objects.filter(header_id=header_id.id).all()
    return render(request, 'transaction/view_cash_payment_voucher.html', {'voucher_header': voucher_header,
               
               
                                                                          'voucher_detail': voucher_detail,'pk':pk})
#  DO NOT UNCOMMENT THIS
# def inser_into_tran(request, pk):
#     try:
#         header_id = VoucherHeader.objects.get(id=pk)
#         voucher_header = VoucherHeader.objects.filter(id=pk).first()
#         cash_id = ChartOfAccount.objects.filter(id=6).first()
#         cash_id = ~Q(account_id = cash_id)
#         header_id_main = Q(header_id=header_id.id)
#         voucher_detail = VoucherDetail.objects.filter(header_id_main, cash_id).all()
#         for value in voucher_detail:
#             cash_account = ChartOfAccount.objects.filter(id=6).first()
#             party_account = ChartOfAccount.objects.filter(id=value.account_id.id).first()
#             print(party_account)
#             amount = float(value.debit) + float(value.credit)
#             amount = abs(amount)
#             bill = PurchaseHeader.objects.filter(id = value.invoice_id).first()
#             detail_remarks = f"Paid amount {amount} RS, against invoice no {bill.purchase_no}."
#             print(detail_remarks)
#             tran1 = Transactions(refrence_id = 0, refrence_date = voucher_header.doc_date, tran_type = '', amount = -abs(amount),
#                                 date = voucher_header.doc_date, remarks = voucher_header.voucher_no, account_id = cash_account,ref_inv_tran_id = value.invoice_id,ref_inv_tran_type = "Purchase CPV", voucher_id = voucher_header, detail_remarks = detail_remarks, is_partialy = 1)
#             tran1.save()
#             tran2 = Transactions(refrence_id = 0, refrence_date = voucher_header.doc_date, tran_type = '', amount = amount,
#                                 date = voucher_header.doc_date, remarks = voucher_header.voucher_no, account_id = party_account,ref_inv_tran_id = value.invoice_id,ref_inv_tran_type = "Purchase CPV", voucher_id = voucher_header, detail_remarks = detail_remarks, is_partialy = 1)
#             tran2.save()
#     except Exception as e:
#         print(e) 
#     return render(request, 'transaction/view_cash_payment_voucher.html',{'pk':pk})


# def inser_into_tran_without_partialy(request, pk):
#     try:
#         header_id = VoucherHeader.objects.get(id=pk)
#         voucher_header = VoucherHeader.objects.filter(id=pk).first()
#         cash_id = ChartOfAccount.objects.filter(id=6).first()
#         cash_id = ~Q(account_id = cash_id)
#         header_id_main = Q(header_id=header_id.id)
#         voucher_detail = VoucherDetail.objects.filter(header_id_main, cash_id).all()
#         for value in voucher_detail:
#             cash_account = ChartOfAccount.objects.filter(id=6).first()
#             party_account = ChartOfAccount.objects.filter(id=value.account_id.id).first()
#             print(party_account)
#             amount = float(value.debit) + float(value.credit)
#             amount = abs(amount)
#             bill = PurchaseHeader.objects.filter(id = value.invoice_id).first()
#             detail_remarks = f"Paid amount {amount} RS, against invoice no {bill.purchase_no}."
#             print(detail_remarks)
#             tran1 = Transactions(refrence_id = 0, refrence_date = voucher_header.doc_date, tran_type = '', amount = -abs(amount),
#                                 date = voucher_header.doc_date, remarks = voucher_header.voucher_no, account_id = cash_account,ref_inv_tran_id = value.invoice_id,ref_inv_tran_type = "Purchase CPV", voucher_id = voucher_header, detail_remarks = detail_remarks)
#             tran1.save()
#             tran2 = Transactions(refrence_id = 0, refrence_date = voucher_header.doc_date, tran_type = '', amount = amount,
#                                 date = voucher_header.doc_date, remarks = voucher_header.voucher_no, account_id = party_account,ref_inv_tran_id = value.invoice_id,ref_inv_tran_type = "Purchase CPV", voucher_id = voucher_header, detail_remarks = detail_remarks)
#             tran2.save()
#     except Exception as e:
#         print(e) 
#     return render(request, 'transaction/view_cash_payment_voucher.html',{'pk':pk})


def allow_cpv_delete(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 15)
    action_id = Q(ActionID = 4)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False

@login_required()
@user_passes_test(allow_cpv_delete)
def delete_cash_payment(request, pk):
    ref_inv_tran_type = Q(ref_inv_tran_type = "Purchase CPV")
    voucher_id = Q(voucher_id = pk)
    Transactions.objects.filter(ref_inv_tran_type, voucher_id).all().delete()
    tran_type = Q(tran_type = "Opening Balance")
    Transactions.objects.filter(tran_type, voucher_id).all().delete()
    VoucherDetail.objects.filter(header_id = pk).all().delete()
    VoucherHeader.objects.filter(id = pk).delete()
    messages.add_message(request, messages.SUCCESS, "Cash Payment Voucher Deleted")
    return redirect('cash-payment-voucher')


def allow_jo(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 9)
    action_id = Q(ActionID = 1)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False

@login_required()
@user_passes_test(allow_jo)
def job_order(request):
    request.session['objectID'] = 9
    all_job_order = JobOrderHeader.objects.all()
    return render(request, 'transaction/job_order.html',{'all_job_order':all_job_order})


def allow_jo_new(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 9)
    action_id = Q(ActionID = 2)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


@login_required()
@user_passes_test(allow_jo_new)
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


def allow_jo_edit(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 9)
    action_id = Q(ActionID = 3)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


@login_required()
@user_passes_test(allow_jo_edit)
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


def allow_jo_delete(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 9)
    action_id = Q(ActionID = 4)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


@login_required()
@user_passes_test(allow_jo_delete)
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


def allow_jo(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 13)
    action_id = Q(ActionID = 1)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False

@login_required()
@user_passes_test(allow_jo)
def journal_voucher_summary(request):
    request.session['objectID'] = 13
    cursor = connection.cursor()
    all_vouchers = cursor.execute('''select VH.id, VH.voucher_no, VH.doc_no, VH.doc_date, VH.cheque_no, VH.description,
                                    AU.username, COA.account_title, VD.debit from transaction_voucherheader VH
                                    inner join auth_user AU on VH.user_id = AU.id
                                    inner join transaction_voucherdetail VD on VD.header_id_id = VH.id
                                    inner join transaction_chartofaccount COA on COA.id = VD.account_id_id
                                    where VH.voucher_no LIKE '%JV%' and VD.debit != 0
                                    group by VH.id ''')
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


def allow_cpv_edit(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 15)
    action_id = Q(ActionID = 3)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False

@login_required()
@user_passes_test(allow_cpv_edit)
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

def allow_jv_edit(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 13)
    action_id = Q(ActionID = 3)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


@login_required()
@user_passes_test(allow_jv_edit)
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
@user_passes_test(allow_reports)
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
@user_passes_test(allow_reports)
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


def allow_crv_print(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 14)
    action_id = Q(ActionID = 5)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False

@login_required()
@user_passes_test(allow_crv_print)
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
    amount_in_words =  num2words(abs(detail[0][0]))
    pdf = render_to_pdf('transaction/crv_pdf.html', {'company_info':company_info, 'header':header, 'detail':detail, 'amount_in_words':amount_in_words})
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "CashReceivingVoucher.pdf"
        content = "inline; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")


def allow_cpv_print(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 15)
    action_id = Q(ActionID = 5)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


@login_required()
@user_passes_test(allow_cpv_print)
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


def allow_jv_print(user):
    user_id = Q(UserID = user.id)
    object_id = Q(ObjectID = 13)
    action_id = Q(ActionID = 5)
    is_allow = Q(IsAllow = 1)
    allow_role = tblUserRights.objects.filter(user_id, object_id, is_allow, action_id)
    if allow_role:
        return True
    else:
        return False


@login_required()
@user_passes_test(allow_jv_print)
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


@login_required()
@user_passes_test(allow_reports)
def sale_detail_report(request):
    srb_amount = 0
    gst_amount = 0
    company_info = Company_info.objects.all()
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')
    sale_detail_list = SaleHeader.objects.filter(date__range=[from_date,to_date]).all()
    sale_detail = SaleDetail.objects.all()
    sale_header = []
    balance = 0
    for i,value in enumerate(sale_detail_list):
        total_amount = 0
        for sd in sale_detail:
            if value.id == sd.sale_id.id:
                total_amount = total_amount + sd.total_amount
        srb_amount = (float(total_amount) / float(100)) * float(value.srb)
        gst_amount = (float(total_amount) / float(100)) * float(value.gst)
        gst_srb = float(srb_amount) + float(gst_amount)
        amount_before_discount = float(gst_srb) + float(total_amount)
        discount_amount = (amount_before_discount / float(100) * float(value.discount) )
        gross_amount = float(amount_before_discount) - float(discount_amount)
        info = {
        "id":value.id,
        "date": value.date,
        "invoice_no": value.sale_no,
        "customer_name": value.account_id.account_title,
        "srb_amount":srb_amount,
        "gst_amount":gst_amount,
        "gst_percent":value.gst,
        "srb_percent":value.srb,
        "discount":value.discount,
        "gross_amount": gross_amount,
        }
        sale_header.append(info)
    context = {
    "sale_detail_list":sale_header,
    "sale_detail":sale_detail,
    "company_info":company_info,
    "from_date":from_date,
    "to_date":to_date,
    }
    pdf = render_to_pdf('transaction/sale_detail_report.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "CashReceivingVoucher.pdf"
        content = "inline; filename='%s'" %(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")


@login_required()
@user_passes_test(allow_reports)
def daily_report(request):
    if request.method == "POST":
        from_date = request.POST.get("from_date")
        to_date = request.POST.get("to_date")
        sale_detail_list = []
        sale_detail_list_on_cash = []
        expenses = []
        crvs = []
        cpvs = []
        sales = {}
        sales_on_cash = {}
        daily_expenses = {}
        daily_crv = {}
        daily_cpv = {}
        total_amount = 0
        grand_total_on_credit = 0
        grand_total_on_cash = 0
        grand_total_expense = 0
        total_crv = 0
        total_cpv = 0
        company_info = Company_info.objects.all()
        date = Q(date = datetime.date.today())
        on_credit = Q(payment_method = "Credit")
        daily_sales_on_credit = SaleHeader.objects.filter(on_credit,Q(date__gte=from_date) & Q(date__lte=to_date)).all()
        sale_detail = SaleDetail.objects.all()
        for sale in daily_sales_on_credit:
            total_amount = 0
            for detail in sale_detail:
                if detail.sale_id.id == sale.id:
                    print(detail.total_amount)
                    total_amount = total_amount + detail.total_amount
                    print(total_amount)
            gst = sale.gst / 100 * total_amount
            srb = sale.srb / 100 * total_amount
            gst_srb = gst + srb
            total_before_discount = total_amount + gst_srb
            discount_amount =  total_before_discount / 100 * sale.discount
            final_total_amount = total_before_discount - discount_amount
            grand_total_on_credit = grand_total_on_credit + final_total_amount
            sales = {
            "invoice_no": sale.sale_no,
            "customer_name": sale.account_id.account_title,
            "gst_srb":gst_srb,
            "discount":sale.discount,
            "total_amount":final_total_amount,
            }
            sale_detail_list.append(sales)
        on_cash = Q(payment_method = "Cash")
        daily_sales_on_cash = SaleHeader.objects.filter(Q(date__gte=from_date) & Q(date__lte=to_date),on_cash).all()
        sale_detail = SaleDetail.objects.all()
        for sale in daily_sales_on_cash:
            total_amount = 0
            for detail in sale_detail:
                if detail.sale_id.id == sale.id:
                    print(detail.total_amount)
                    total_amount = total_amount + detail.total_amount
                    print(total_amount)
            gst = sale.gst / 100 * total_amount
            srb = sale.srb / 100 * total_amount
            gst_srb = gst + srb
            total_before_discount = total_amount + gst_srb
            discount_amount =  total_before_discount / 100 * sale.discount
            final_total_amount = total_before_discount - discount_amount
            grand_total_on_cash = grand_total_on_cash + final_total_amount
            sales_on_cash = {
            "invoice_no": sale.sale_no,
            "customer_name": sale.account_id.account_title,
            "gst_srb":gst_srb,
            "discount":sale.discount,
            "total_amount":final_total_amount,
            }
            sale_detail_list_on_cash.append(sales_on_cash)
        today_date = str(datetime.date.today())
        cursor = connection.cursor()
        expense_account = cursor.execute('''select VH.id, VH.voucher_no, COA.account_title as "Expense Account", VH.description as "Discription" , VD.debit as "Amount"
                                        from transaction_voucherdetail VD
                                        inner join transaction_voucherheader VH on VH.id = VD.header_id_id
                                        inner join transaction_chartofaccount COA on COA.id = VD.account_id_id
                                        where VH.voucher_no like '%%JV%%' and VH.doc_date between %s and %s  and VD.account_id_id != "6"
                                        group by VD.id, VH.id''',[from_date,to_date])
        expense_account = expense_account.fetchall()
        for expens in expense_account:
            grand_total_expense = grand_total_expense + expens[4]
            daily_expenses = {
            "voucher_no": expens[1],
            "expense_account": expens[2],
            "description":expens[3],
            "amount":expens[4],
            }
            expenses.append(daily_expenses)
        crv_details = cursor.execute('''select VH.id, VH.voucher_no, COA.account_title as "Customer", VH.description as "Discription" , VD.credit as "Amount"
                            from transaction_voucherdetail VD
                            inner join transaction_voucherheader VH on VH.id = VD.header_id_id
                            inner join transaction_chartofaccount COA on COA.id = VD.account_id_id
                            where VH.voucher_no like '%%CRV%%' and VH.doc_date between %s and %s and VD.account_id_id != "6"
                            group by VD.id, VH.id''',[from_date, to_date])
        crv_details = crv_details.fetchall()
        for crv in crv_details:
            total_crv = total_crv + abs(crv[4])
            daily_crv = {
            "voucher_no": crv[1],
            "customer": crv[2],
            "description":crv[3],
            "amount":abs(crv[4]),
            }
            crvs.append(daily_crv)

        cpv_details = cursor.execute('''select VH.id, VH.voucher_no, COA.account_title as "Customer", VH.description as "Discription" , VD.debit as "Amount"
                            from transaction_voucherdetail VD
                            inner join transaction_voucherheader VH on VH.id = VD.header_id_id
                            inner join transaction_chartofaccount COA on COA.id = VD.account_id_id
                            where VH.voucher_no like '%%CPV%%' and VH.doc_date between %s and %s and VD.account_id_id != "6"
                            group by VD.id, VH.id''',[from_date, to_date])
        cpv_details = cpv_details.fetchall()
        for cpv in cpv_details:
            total_cpv = total_cpv + abs(cpv[4])
            daily_cpv = {
            "voucher_no": cpv[1],
            "customer": cpv[2],
            "description":cpv[3],
            "amount":abs(cpv[4]),
            }
            cpvs.append(daily_cpv)
        print("hahaha", cpv_details)
        last_total = float(grand_total_on_credit) + float(grand_total_on_cash) - float(grand_total_expense) + float(total_crv) - float(total_cpv)
        context = {
        "sale_detail_list":sale_detail_list,
        "sale_detail_list_on_cash":sale_detail_list_on_cash,
        "grand_total_on_credit":grand_total_on_credit,
        "grand_total_on_cash":grand_total_on_cash,
        "crvs":crvs,
        "cpvs":cpvs,
        "expenses":expenses,
        "grand_total_expense": grand_total_expense,
        "total_crv":total_crv,
        "total_cpv":total_cpv,
        "company_info":company_info,
        "last_total":round(last_total),
        "from_date":from_date,
        "to_date":to_date
        }
        pdf = render_to_pdf('transaction/daily_report_pdf.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "CashReceivingVoucher.pdf"
            content = "inline; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
    return redirect("reports")

@login_required()
@user_passes_test(allow_cpv_new)
def new_cash_payment_voucher(request):
    balance_amount = 0
    cursor = connection.cursor()
    get_last_tran_id = VoucherHeader.objects.filter(voucher_no__contains = 'CPV').last()
    date = datetime.date.today()
    date = date.strftime('%Y%m')
    get_last_tran_id = get_last_tran_id.voucher_no
    if get_last_tran_id:
        get_last_tran_id = get_last_tran_id[7:]
        serial = str((int(get_last_tran_id) + 1))
        get_last_tran_id = date[2:]+'CPV'+serial
    else:
        get_last_tran_id =  date[2:]+'CPV1'
    account_cpv = request.POST.get('account_cpv')
    all_accounts = ChartOfAccount.objects.all()
    on_account = request.POST.get('on_account')
    if on_account:
        doc_date = request.POST.get('doc_date', False)
        description = request.POST.get('description', False)
        vendor = request.POST.get('vendor', False)
        date = request.POST.get('date', False)
        paying_amount = request.POST.get('paying_amount')
        jv_header = VoucherHeader(voucher_no=get_last_tran_id, doc_no="0", doc_date = doc_date, cheque_no = "-",cheque_date = doc_date, description = description)
        jv_header.save()
        pi_account = cursor.execute('''Select * From (
                                    Select HD.ID,HD.account_id_id,HD.purchase_no,account_title,abs(Sum(total_amount)) As InvAmount,0 As RcvAmount, 'tran_type' as 'tran_type'
                                    from transaction_purchaseheader HD
                                    Inner join transaction_purchasedetail DT on DT.purchase_id_id = HD.id
                                    Left Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                    Where HD.Payment_method = 'Credit' And HD.account_id_id = %s AND HD.ID Not In
                                    (Select ref_inv_tran_id from transaction_transactions Where ref_inv_tran_type = 'Purchase CPV')
                                    Group by HD.ID
                                    Having InvAmount > RcvAmount
                                    Union All
                                    Select HD.ID,HD.account_id_id,HD.purchase_no,account_title,abs(Sum(total_amount)) As InvAmount,
                                    abs(ifnull((Select Sum(Amount) * -1 From transaction_transactions
                                    Where ref_inv_tran_id = HD.ID AND account_id_id = %s),0)) As RcvAmount, 'tran_type' as 'tran_type'
                                    from transaction_purchaseheader HD
                                    Inner join transaction_purchasedetail DT on DT.purchase_id_id = HD.id
                                    Inner Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                    Where Payment_method = 'Credit' AND HD.account_id_id = %s
                                    Group By HD.ID
                                    Having InvAmount > RcvAmount
                                    Union All
                                    Select '0' as 'ID', COA.id, COA.id as 'purchase_no' , COA.account_title, abs(COA.opening_balance) As InvAmount, abs(ifnull(sum(II.amount),0)) as RcvAmount, II.tran_type
                                    from transaction_chartofaccount COA
                                    left join transaction_transactions II on II.refrence_id = COA.id and II.tran_type = "Opening Balance" and II.account_id_id = 115
                                    Where COA.id = %s
                                    group by II.tran_type
                                    Having InvAmount > RcvAmount
                                    ) As tblPendingInvoice
                                    Group By ID
                                    Order By ID''',[vendor,vendor,vendor,vendor])
        pi_account = pi_account.fetchall()
        cash_account = ChartOfAccount.objects.filter(account_title = "Cash").first()
        paying_amount = float(paying_amount)
        for value in pi_account:
            balance_amount = 0
            if paying_amount > 0:
                if value[6] == "tran_type":
                    balance_amount = value[4] - value[5]
                    if balance_amount > 0:
                        if paying_amount > balance_amount:
                            invoice_no = PurchaseHeader.objects.get(purchase_no = value[2])
                            vendor = request.POST.get('vendor', False)
                            vendor = ChartOfAccount.objects.filter(id = vendor).first()
                            voucher_id = VoucherHeader.objects.filter(voucher_no = get_last_tran_id).first()
                            detail_remarks = f"Paid amount {balance_amount} RS, against invoice no {invoice_no.purchase_no}."
                            tran1 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = balance_amount,
                                                date = date, remarks = get_last_tran_id, account_id = vendor,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Purchase CPV", voucher_id = voucher_id, detail_remarks = detail_remarks, is_partialy = 1)
                            tran1.save()
                            tran2 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = -abs(balance_amount),
                                                date = date, remarks = get_last_tran_id, account_id = cash_account,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Purchase CPV", voucher_id = voucher_id,detail_remarks = detail_remarks, is_partialy = 1 )
                            tran2.save()
                            header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
                            jv_detail1 = VoucherDetail(account_id = cash_account, debit = 0.00, credit = -abs(balance_amount), header_id = header_id, invoice_id = invoice_no.id)
                            jv_detail1.save()
                            jv_detail2 = VoucherDetail(account_id = vendor,  debit = balance_amount, credit = 0.00,header_id = header_id, invoice_id = invoice_no.id)
                            jv_detail2.save()
                            paying_amount = paying_amount - balance_amount
                        else:
                            voucher_id = VoucherHeader.objects.filter(voucher_no = get_last_tran_id)
                            invoice_no = PurchaseHeader.objects.get(purchase_no = value[2])
                            vendor = request.POST.get('vendor', False)
                            vendor = ChartOfAccount.objects.filter(id = vendor).first()
                            voucher_id = VoucherHeader.objects.filter(voucher_no = get_last_tran_id).first()
                            balance_amount = paying_amount
                            invoice_id = PurchaseHeader.objects.get(purchase_no = value[2])
                            detail_remarks = f"Paid amount {balance_amount} RS, against invoice no {invoice_id.purchase_no}."
                            tran1 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = balance_amount,
                                                date = date, remarks = get_last_tran_id, account_id = vendor,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Purchase CPV",voucher_id = voucher_id ,detail_remarks = detail_remarks, is_partialy = 1)
                            tran1.save()
                            tran2 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = -abs(balance_amount),
                                                date = date, remarks = get_last_tran_id, account_id = cash_account,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Purchase CPV", voucher_id = voucher_id ,detail_remarks = detail_remarks, is_partialy = 1)
                            tran2.save()
                            header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
                            jv_detail1 = VoucherDetail(account_id = cash_account, debit = 0.00, credit = -abs(balance_amount), header_id = header_id, invoice_id = invoice_no.id)
                            jv_detail1.save()
                            jv_detail2 = VoucherDetail(account_id = vendor,  debit = balance_amount, credit = 0.00,header_id = header_id, invoice_id = invoice_no.id)
                            jv_detail2.save()
                            paying_amount = 0
                else:
                    vendor = request.POST.get('vendor', False)
                    vendor = ChartOfAccount.objects.filter(id = vendor).first()
                    voucher_id = VoucherHeader.objects.filter(voucher_no = get_last_tran_id).first()
                    balance_amount = value[4] - value[5]
                    if balance_amount > 0:
                        if paying_amount > balance_amount:
                            detail_remarks = f"Paid amount against opening balance."
                            tran1 = Transactions(refrence_id = vendor.id, refrence_date = doc_date, tran_type = 'Opening Balance', amount = balance_amount,
                                                date = date, remarks = get_last_tran_id, account_id = vendor,ref_inv_tran_id = 0,ref_inv_tran_type = "-", voucher_id = voucher_id ,detail_remarks = detail_remarks, is_partialy = 1)
                            tran1.save()
                            tran2 = Transactions(refrence_id = vendor.id, refrence_date = doc_date, tran_type = 'Opening Balance', amount = -abs(balance_amount),
                                                date = date, remarks = get_last_tran_id, account_id = cash_account,ref_inv_tran_id = 0,ref_inv_tran_type = "-", voucher_id = voucher_id ,detail_remarks = detail_remarks, is_partialy = 1)
                            tran2.save()
                            header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
                            jv_detail1 = VoucherDetail(account_id = cash_account, debit = 0.00, credit = -abs(balance_amount), header_id = header_id, invoice_id = 0)
                            jv_detail1.save()
                            jv_detail2 = VoucherDetail(account_id = vendor,  debit = balance_amount, credit = 0.00,header_id = header_id, invoice_id = 0)
                            jv_detail2.save()
                            paying_amount = paying_amount - balance_amount
                        else:
                            balance_amount = paying_amount
                            detail_remarks = f"Paid amount against opening balance."
                            tran1 = Transactions(refrence_id = vendor.id, refrence_date = doc_date, tran_type = 'Opening Balance', amount = balance_amount,
                                                date = date, remarks = get_last_tran_id, account_id = vendor,ref_inv_tran_id = 0,ref_inv_tran_type = "-",voucher_id = voucher_id ,detail_remarks = detail_remarks, is_partialy = 1)
                            tran1.save()
                            tran2 = Transactions(refrence_id = vendor.id, refrence_date = doc_date, tran_type = 'Opening Balance', amount = -abs(balance_amount),
                                                date = date, remarks = get_last_tran_id, account_id = cash_account,ref_inv_tran_id = 0,ref_inv_tran_type = "-",voucher_id = voucher_id, detail_remarks = detail_remarks, is_partialy = 1)
                            tran2.save()
                            header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
                            jv_detail1 = VoucherDetail(account_id = cash_account, debit = 0.00, credit = -abs(balance_amount), header_id = header_id, invoice_id = 0)
                            jv_detail1.save()
                            jv_detail2 = VoucherDetail(account_id = vendor,  debit = balance_amount, credit = 0.00,header_id = header_id, invoice_id = 0)
                            jv_detail2.save()
                            paying_amount = 0
            else:
                return JsonResponse({'success':'success'})
        return JsonResponse({'success':'success'})
    if account_cpv:
        id = ChartOfAccount.objects.get(id = account_cpv)
        pi = cursor.execute('''Select * From (
                            Select HD.ID,HD.account_id_id,HD.purchase_no,account_title,Sum(total_amount) As InvAmount,0 As RcvAmount
                            from transaction_purchaseheader HD
                            Inner join transaction_purchasedetail DT on DT.purchase_id_id = HD.id
                            Left Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                            Where HD.Payment_method = 'Credit' And HD.account_id_id = %s AND HD.ID Not In
                            (Select ref_inv_tran_id from transaction_transactions Where ref_inv_tran_type = 'Purchase CPV')
                            Group by HD.ID,HD.account_id_id,account_title
                            Having InvAmount > RcvAmount
                            Union All
                            Select HD.ID,HD.account_id_id,HD.purchase_no,account_title,Sum(total_amount) As InvAmount,
                            abs(ifnull((Select Sum(Amount) * -1 From transaction_transactions
                            Where ref_inv_tran_id = HD.ID AND account_id_id = %s),0)) As RcvAmount
                            from transaction_purchaseheader HD
                            Inner join transaction_purchasedetail DT on DT.purchase_id_id = HD.id
                            Inner Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                            Where Payment_method = 'Credit' AND HD.account_id_id = %s
                            Group By HD.ID,HD.account_id_id,account_title
                            Having InvAmount > RcvAmount
                            ) As tblPendingInvoice
                            Group By ID
                            Order By ID''',[id.id,id.id,id.id])
        pi = pi.fetchall()
        return JsonResponse({'pi':pi})
    all_accounts = ChartOfAccount.objects.all()
    all_invoices = PurchaseHeader.objects.all()
    user = request.user
    if request.method == "POST":
        doc_date = request.POST.get('doc_date', False)
        description = request.POST.get('description', False)
        vendor = request.POST.get('vendor', False)
        date = request.POST.get('date', False)
        items = json.loads(request.POST.get('items', False))
        jv_header = VoucherHeader(voucher_no=get_last_tran_id, doc_no="0", doc_date = doc_date, cheque_no = "-",cheque_date = doc_date, description = description)
        jv_header.save()
        voucher_id = VoucherHeader.objects.get(voucher_no=get_last_tran_id)
        for value in items:
            invoice_no = PurchaseHeader.objects.get(purchase_no=value["invoice_no"])
            account_id = ChartOfAccount.objects.get(id = value["account_id"])
            cash_account = ChartOfAccount.objects.get(account_title = 'Cash')
            amount = float(value["invoice_amount"])
            bill = value["invoice_no"]
            detail_remarks = f"Paid amount {amount} RS, against invoice no {bill}."
            tran1 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = -abs(amount),
                                date = date, remarks = get_last_tran_id, account_id = cash_account,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Purchase CPV", voucher_id = voucher_id, detail_remarks = detail_remarks )
            tran1.save()
            tran2 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = amount,
                                date = date, remarks = get_last_tran_id, account_id = account_id,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Purchase CPV", voucher_id = voucher_id, detail_remarks = detail_remarks )
            tran2.save()
            header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
            jv_detail1 = VoucherDetail(account_id = cash_account, debit = 0.00, credit = -abs(amount), header_id = header_id, invoice_id = invoice_no.id)
            jv_detail1.save()
            jv_detail2 = VoucherDetail(account_id = account_id,  debit = amount, credit = 0.00,header_id = header_id, invoice_id = invoice_no.id)
            jv_detail2.save()
        return JsonResponse({"result":"success"})
    context = {
    'all_accounts':all_accounts,
    'get_last_tran_id': get_last_tran_id,
    'all_invoices':all_invoices,
    }
    return render(request, 'transaction/new_cash_payment_voucher.html', context)


@login_required()
@user_passes_test(allow_crv_new)
def new_cash_receiving_voucher(request):
    balance_amount = 0
    cursor = connection.cursor()
    get_last_tran_id = VoucherHeader.objects.filter(voucher_no__contains = 'CRV').last()
    date = datetime.date.today()
    date = date.strftime('%Y%m')
    get_last_tran_id = get_last_tran_id.voucher_no
    if get_last_tran_id:
        get_last_tran_id = get_last_tran_id[7:]
        serial = str((int(get_last_tran_id) + 1))
        get_last_tran_id = date[2:]+'CRV'+serial
    else:
        get_last_tran_id =  date[2:]+'CRV1'
    account_crv = request.POST.get('account_crv')
    all_accounts = ChartOfAccount.objects.all()
    on_account = request.POST.get('on_account_crv')
    if on_account:
        doc_date = request.POST.get('doc_date', False)
        description = request.POST.get('description', False)
        vendor = request.POST.get('vendor', False)
        date = request.POST.get('date', False)
        receiving_amount = request.POST.get('receiving_amount')
        jv_header = VoucherHeader(voucher_no=get_last_tran_id, doc_no="0", doc_date = doc_date, cheque_no = "-",cheque_date = doc_date, description = description)
        jv_header.save()
        pi_account = cursor.execute('''Select * From (
                                    Select HD.ID,HD.account_id_id,HD.sale_no,account_title,abs(Sum(total_amount)) As InvAmount,0 As RcvAmount, 'tran_type' as 'tran_type'
                                    from transaction_saleheader HD
                                    Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
                                    Left Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                    Where HD.Payment_method = 'Credit' And HD.account_id_id = %s AND HD.ID Not In
                                    (Select ref_inv_tran_id from transaction_transactions Where ref_inv_tran_type = 'Sale CRV')
                                    Group by HD.ID
                                    Having InvAmount > RcvAmount
                                    Union All
                                    Select HD.ID,HD.account_id_id,HD.sale_no,account_title,abs(Sum(total_amount)) As InvAmount,
                                    abs(ifnull((Select Sum(Amount) * -1 From transaction_transactions
                                    Where ref_inv_tran_id = HD.ID AND account_id_id = %s),0)) As RcvAmount, 'tran_type' as 'tran_type'
                                    from transaction_saleheader HD
                                    Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
                                    Inner Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                                    Where Payment_method = 'Credit' AND HD.account_id_id = %s
                                    Group By HD.ID
                                    Having InvAmount > RcvAmount
                                    Union All
                                    Select '0' as 'ID', COA.id, COA.id as 'sale_no' , COA.account_title, abs(COA.opening_balance) As InvAmount, abs(ifnull(sum(II.amount),0)) as RcvAmount, ifnull(II.tran_type,"Opening Balance")
                                    from transaction_chartofaccount COA
                                    left join transaction_transactions II on II.refrence_id = COA.id and II.tran_type = "Opening Balance" and II.account_id_id = 115
                                    Where COA.id = %s
                                    group by II.tran_type
                                    Having InvAmount > RcvAmount
                                    ) As tblPendingInvoice
                                    Group By ID
                                    Order By ID''',[vendor,vendor,vendor,vendor])
        pi_account = pi_account.fetchall()
        cash_account = ChartOfAccount.objects.filter(account_title = "Cash").first()
        receiving_amount = float(receiving_amount)
        for value in pi_account:
            balance_amount = 0
            if receiving_amount > 0:
                if value[6] == "tran_type":
                    balance_amount = value[4] - value[5]
                    if balance_amount > 0:
                        if receiving_amount > balance_amount:
                            vendor = request.POST.get('vendor', False)
                            invoice_no = SaleHeader.objects.get(sale_no = value[2])
                            vendor = request.POST.get('vendor', False)
                            vendor = ChartOfAccount.objects.filter(id = vendor).first()
                            voucher_id = VoucherHeader.objects.filter(voucher_no = get_last_tran_id).first()
                            detail_remarks = f"Received amount {balance_amount} RS, against invoice no {invoice_no.sale_no}."
                            tran1 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = -abs(balance_amount),
                                                date = date, remarks = get_last_tran_id, account_id = vendor,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Sale CRV", voucher_id = voucher_id, detail_remarks = detail_remarks, is_partialy = 1 )
                            tran1.save()
                            tran2 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = balance_amount,
                                                date = date, remarks = get_last_tran_id, account_id = cash_account,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Sale CRV", voucher_id = voucher_id,detail_remarks = detail_remarks, is_partialy = 1 )
                            tran2.save()
                            header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
                            jv_detail1 = VoucherDetail(account_id = cash_account, debit = 0.00, credit = -abs(balance_amount), header_id = header_id, invoice_id = invoice_no.id)
                            jv_detail1.save()
                            jv_detail2 = VoucherDetail(account_id = vendor,  debit = balance_amount, credit = 0.00,header_id = header_id, invoice_id = invoice_no.id)
                            jv_detail2.save()
                            receiving_amount = receiving_amount - balance_amount
                        else:
                            voucher_id = VoucherHeader.objects.filter(voucher_no = get_last_tran_id)
                            invoice_no = SaleHeader.objects.get(sale_no = value[2])
                            vendor = request.POST.get('vendor', False)
                            vendor = ChartOfAccount.objects.filter(id = vendor).first()
                            voucher_id = VoucherHeader.objects.filter(voucher_no = get_last_tran_id).first()
                            balance_amount = receiving_amount
                            invoice_id = SaleHeader.objects.get(sale_no = value[2])
                            detail_remarks = f"Received amount {balance_amount} RS, against invoice no {invoice_id.sale_no}."
                            tran1 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = -abs(balance_amount),
                                                date = date, remarks = get_last_tran_id, account_id = vendor,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Sale CRV",voucher_id = voucher_id ,detail_remarks = detail_remarks,is_partialy = 1)
                            tran1.save()
                            tran2 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = balance_amount,
                                                date = date, remarks = get_last_tran_id, account_id = cash_account,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Sale CRV", voucher_id = voucher_id ,detail_remarks = detail_remarks,is_partialy = 1 )
                            tran2.save()
                            header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
                            jv_detail1 = VoucherDetail(account_id = cash_account, debit = 0.00, credit = -abs(balance_amount), header_id = header_id, invoice_id = invoice_no.id)
                            jv_detail1.save()
                            jv_detail2 = VoucherDetail(account_id = vendor,  debit = balance_amount, credit = 0.00,header_id = header_id, invoice_id = invoice_no.id)
                            jv_detail2.save()
                            receiving_amount = 0
                else:
                    vendor = request.POST.get('vendor', False)
                    vendor = ChartOfAccount.objects.filter(id = vendor).first()
                    voucher_id = VoucherHeader.objects.filter(voucher_no = get_last_tran_id).first()
                    balance_amount = value[4] - value[5]
                    if balance_amount > 0:
                        if receiving_amount > balance_amount:
                            detail_remarks = f"Received amount against opening balance."
                            tran1 = Transactions(refrence_id = vendor.id, refrence_date = doc_date, tran_type = 'Opening Balance', amount = -abs(balance_amount),
                                                date = date, remarks = get_last_tran_id, account_id = vendor,ref_inv_tran_id = 0,ref_inv_tran_type = "-", voucher_id = voucher_id ,detail_remarks = detail_remarks, is_partialy = 1 )
                            tran1.save()
                            tran2 = Transactions(refrence_id = vendor.id, refrence_date = doc_date, tran_type = 'Opening Balance', amount = balance_amount,
                                                date = date, remarks = get_last_tran_id, account_id = cash_account,ref_inv_tran_id = 0,ref_inv_tran_type = "-", voucher_id = voucher_id ,detail_remarks = detail_remarks, is_partialy = 1 )
                            tran2.save()
                            header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
                            jv_detail1 = VoucherDetail(account_id = cash_account, debit = balance_amount, credit = 0.00, header_id = header_id, invoice_id = 0)
                            jv_detail1.save()
                            jv_detail2 = VoucherDetail(account_id = vendor,  debit = 0.00, credit = balance_amount,header_id = header_id, invoice_id = 0)
                            jv_detail2.save()
                            receiving_amount = receiving_amount - balance_amount
                        else:
                            balance_amount = receiving_amount
                            detail_remarks = f"Received amount against opening balance."
                            tran1 = Transactions(refrence_id = vendor.id, refrence_date = doc_date, tran_type = 'Opening Balance', amount = -abs(balance_amount),
                                                date = date, remarks = get_last_tran_id, account_id = vendor,ref_inv_tran_id = 0,ref_inv_tran_type = "-",voucher_id = voucher_id ,detail_remarks = detail_remarks, is_partialy = 1 )
                            tran1.save()
                            tran2 = Transactions(refrence_id = vendor.id, refrence_date = doc_date, tran_type = 'Opening Balance', amount = balance_amount,
                                                date = date, remarks = get_last_tran_id, account_id = cash_account,ref_inv_tran_id = 0,ref_inv_tran_type = "-",voucher_id = voucher_id, detail_remarks = detail_remarks, is_partialy = 1 )
                            tran2.save()
                            header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
                            jv_detail1 = VoucherDetail(account_id = cash_account, debit = balance_amount, credit = 0.00, header_id = header_id, invoice_id = 0)
                            jv_detail1.save()
                            jv_detail2 = VoucherDetail(account_id = vendor,  debit = 0.00, credit = balance_amount,header_id = header_id, invoice_id = 0)
                            jv_detail2.save()
                            receiving_amount = 0
            else:
                return JsonResponse({'success':'success'})
        return JsonResponse({'success':'success'})
    if account_crv:
        id = ChartOfAccount.objects.get(id = account_crv)
        pi = cursor.execute('''Select * From (
                            Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,0 As RcvAmount
                            from transaction_saleheader HD
                            Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
                            Left Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                            Where HD.Payment_method = 'Credit' And HD.account_id_id = %s AND HD.ID Not In
                            (Select ref_inv_tran_id from transaction_transactions Where ref_inv_tran_type = 'Sale CRV')
                            Group by HD.ID,HD.account_id_id,account_title
                            Having InvAmount > RcvAmount
                            Union All
                            Select HD.ID,HD.account_id_id,HD.sale_no,account_title,Sum(total_amount) As InvAmount,
                            abs(ifnull((Select Sum(Amount) * -1 From transaction_transactions
                            Where ref_inv_tran_id = HD.ID AND account_id_id = %s),0)) As RcvAmount
                            from transaction_saleheader HD
                            Inner join transaction_saledetail DT on DT.sale_id_id = HD.id
                            Inner Join transaction_chartofaccount COA on HD.account_id_id = COA.id
                            Where Payment_method = 'Credit' AND HD.account_id_id = %s
                            Group By HD.ID,HD.account_id_id,account_title
                            Having InvAmount > RcvAmount
                            ) As tblPendingInvoice
                            Group By ID
                            Order By ID''',[id.id,id.id,id.id])
        pi = pi.fetchall()
        return JsonResponse({'pi':pi})
    all_accounts = ChartOfAccount.objects.all()
    all_invoices = SaleHeader.objects.all()
    user = request.user
    if request.method == "POST":
        doc_date = request.POST.get('doc_date', False)
        description = request.POST.get('description', False)
        vendor = request.POST.get('vendor', False)
        date = request.POST.get('date', False)
        items = json.loads(request.POST.get('items', False))
        jv_header = VoucherHeader(voucher_no=get_last_tran_id, doc_no="0", doc_date = doc_date, cheque_no = "-",cheque_date = doc_date, description = description)
        jv_header.save()
        voucher_id = VoucherHeader.objects.get(voucher_no=get_last_tran_id)
        for value in items:
            invoice_no = SaleHeader.objects.get(sale_no=value["invoice_no"])
            account_id = ChartOfAccount.objects.get(id = value["account_id"])
            cash_account = ChartOfAccount.objects.get(account_title = 'Cash')
            amount = float(value["invoice_amount"])
            bill = value["invoice_no"]
            detail_remarks = f"Received amount {amount} RS, against invoice no {bill}."
            tran1 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = amount,
                                date = date, remarks = get_last_tran_id, account_id = cash_account,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Sale CRV", voucher_id = voucher_id, detail_remarks = detail_remarks )
            tran1.save()
            tran2 = Transactions(refrence_id = 0, refrence_date = doc_date, tran_type = '', amount = -abs(amount),
                                date = date, remarks = get_last_tran_id, account_id = account_id,ref_inv_tran_id = invoice_no.id,ref_inv_tran_type = "Sale CRV", voucher_id = voucher_id, detail_remarks = detail_remarks )
            tran2.save()
            header_id = VoucherHeader.objects.get(voucher_no = get_last_tran_id)
            jv_detail1 = VoucherDetail(account_id = cash_account, debit = amount, credit = 0.00, header_id = header_id, invoice_id = invoice_no.id)
            jv_detail1.save()
            jv_detail2 = VoucherDetail(account_id = account_id,  debit = 0.00, credit = -abs(amount),header_id = header_id, invoice_id = invoice_no.id)
            jv_detail2.save()
        return JsonResponse({"result":"success"})
    context = {
    'all_accounts':all_accounts,
    'get_last_tran_id': get_last_tran_id,
    'all_invoices':all_invoices,
    }
    return render(request, 'transaction/new_cash_receiving_voucher.html', context)
