from django.contrib import admin
from admin_site.models import SiteInfoModel, CurrencyModel, SiteSettingModel, SupportedCryptoModel, AssetModel


admin.site.register(SiteInfoModel)
admin.site.register(CurrencyModel)
admin.site.register(SiteSettingModel)
admin.site.register(SupportedCryptoModel)
admin.site.register(AssetModel)

