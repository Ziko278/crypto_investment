from django.contrib import admin
from user_site.models import UserWalletModel, UserFundingModel, UserWatchListModel, AssetConversionModel, \
    UserAssetModel, AssetValueModel, UserProfileModel

admin.site.register(UserWalletModel)
admin.site.register(UserFundingModel)
admin.site.register(UserWatchListModel)
admin.site.register(AssetConversionModel)
admin.site.register(UserAssetModel)
admin.site.register(AssetValueModel)
admin.site.register(UserProfileModel)
