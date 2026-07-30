# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    # Главная страница: редирект на список документов
    path('', RedirectView.as_view(url='/docs/', permanent=False), name='home'),
    # Все URL-ы приложения documents под префиксом /docs/
    path('docs/', include('documents.urls')),
]

# Подключение Django Debug Toolbar только в режиме разработки
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]