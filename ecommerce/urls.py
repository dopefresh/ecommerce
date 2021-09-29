from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns

from shop import views

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('shop.urls', namespace='shop')),
    path('payment/', include('payment.urls', namespace='payment')),
)

urlpatterns += [
    path('i18n/', include('django.conf.urls.i18n')),
    path('ajax_add_to_cart/',
         views.ajax_add_to_cart, name='ajax_add_to_cart'),
    path('ajax_edit_cart/', views.ajax_edit_cart, name='ajax_edit_cart'),
    path('ajax_remove_from_cart/',
         views.ajax_remove_from_cart,
         name='ajax_remove_from_cart'),
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL,
                      document_root=settings.STATIC_ROOT)


admin.autodiscover()
admin.site.enable_nav_sidebar = False
