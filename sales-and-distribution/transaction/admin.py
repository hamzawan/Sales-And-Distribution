from django.contrib import admin
from .models import (ChartOfAccount, PurchaseHeader, PurchaseDetail,
                    SaleHeader, SaleDetail, Company_info, VoucherHeader, VoucherDetail, Transactions)


admin.site.register(ChartOfAccount)
admin.site.register(PurchaseHeader)
admin.site.register(PurchaseDetail)
admin.site.register(SaleHeader)
admin.site.register(SaleDetail)
admin.site.register(Company_info)
admin.site.register(VoucherHeader)
admin.site.register(VoucherDetail)
admin.site.register(Transactions)
