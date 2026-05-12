from pathlib import Path


def register_app(app_name):

    settings_path = Path.cwd() / 'config' / 'settings.py'

    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()

    app_entry = f"    'apps.{app_name}',\n"

    # Prevent duplicate app registration
    if app_entry in content:
        return

    content = content.replace(
        'INSTALLED_APPS = [',
        f"INSTALLED_APPS = [\n{app_entry}"
    )

    # DRF Settings
    if 'REST_FRAMEWORK' not in content:
        content += (
            "\n\nREST_FRAMEWORK = {\n"
            "    'DEFAULT_AUTHENTICATION_CLASSES': [\n"
            "        'rest_framework.authentication.TokenAuthentication',\n"
            "        'rest_framework.authentication.SessionAuthentication',\n"
            "    ],\n"
            "    'DEFAULT_PERMISSION_CLASSES': [\n"
            "        'rest_framework.permissions.AllowAny',\n"
            "    ],\n"
            "}\n"
        )

    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)


def register_urls(app_name, is_main=False):
    """
    Registers both Web (SPA) and API routes in the global config/urls.py.
    """
    urls_path = Path.cwd() / 'config' / 'urls.py'
    
    # 1. Ensure 'include' is imported
    with open(urls_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'from django.urls import path, include' not in content:
        content = content.replace('from django.urls import path', 'from django.urls import path, include')
        with open(urls_path, 'w', encoding='utf-8') as f:
            f.write(content)

    # Re-read content after potential import fix
    with open(urls_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 2. Register Web Route (SPA)
    if f"apps.{app_name}.urls.web" not in content:
        if is_main:
            web_route = f"    path('', include('apps.{app_name}.urls.web')),\n"
        else:
            web_route = (
                f"    path('<str:tenant_slug>/{app_name}/', include('apps.{app_name}.urls.web')),\n"
                f"    path('{app_name}/', include('apps.{app_name}.urls.web')),\n"
            )
        
        if 'path(\'admin/\'' in content:
            content = content.replace('path(\'admin/\'', web_route + '    path(\'admin/\'')
        else:
            content = content.replace('urlpatterns = [', 'urlpatterns = [\n' + web_route)

    # 3. Register API Route
    if f"apps.{app_name}.urls.api" not in content:
        api_route = f"    path('api/v1/{app_name}/', include('apps.{app_name}.urls.api')),\n"
        content = content.replace('urlpatterns = [', 'urlpatterns = [\n' + api_route)

    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(content)

def register_nexa(project_path):

    settings_path = (
        Path(project_path)
        / 'config'
        / 'settings.py'
    )

    with open(settings_path, 'r', encoding='utf-8') as f:

        content = f.read()

    app_entry = "    'nexa.django',\n"

    if app_entry in content:
        return

    content = content.replace(
        'INSTALLED_APPS = [',
        f"INSTALLED_APPS = [\n{app_entry}"
    )

    with open(settings_path, 'w', encoding='utf-8') as f:

        f.write(content)

def patch_settings(project_path):

    settings_path = (
        Path(project_path)
        / 'config'
        / 'settings.py'
    )

    with open(settings_path, 'r', encoding='utf-8') as f:

        content = f.read()

    # STATIC_ROOT
    if 'STATIC_ROOT' not in content:

        content += (
            "\n\nSTATIC_ROOT = BASE_DIR / 'staticfiles'\n"
        )

    # STATICFILES_DIRS
    if 'STATICFILES_DIRS' not in content:

        content += (
            "\n\nSTATICFILES_DIRS = [\n"
            "    BASE_DIR / 'static'\n"
            "]\n"
        )

    # STATICFILES_STORAGE
    if 'STATICFILES_STORAGE' not in content:

        content += (
            "\n\nSTATICFILES_STORAGE = (\n"
            "    'whitenoise.storage.CompressedManifestStaticFilesStorage'\n"
            ")\n"
        )

    # Templates DIRS
    if "'DIRS': []" in content:
        content = content.replace("'DIRS': []", "'DIRS': [BASE_DIR / 'templates']")

    # Internal IPs for debug context
    if 'INTERNAL_IPS' not in content:
        content += (
            "\n\nINTERNAL_IPS = [\n"
            "    '127.0.0.1',\n"
            "]\n"
        )

    # Whitenoise middleware
    if 'whitenoise.middleware.WhiteNoiseMiddleware' not in content:

        content = content.replace(
            "'django.middleware.security.SecurityMiddleware',",
            (
                "'django.middleware.security.SecurityMiddleware',\n"
                "    'whitenoise.middleware.WhiteNoiseMiddleware',\n"
                "    'apps.home.middleware.tenant.TenantMiddleware',\n"
                "    'apps.home.middleware.activity.ActivityLogMiddleware',"
            )
        )

    with open(settings_path, 'w', encoding='utf-8') as f:

        f.write(content)

def patch_urls(project_path):

    urls_path = (
        Path(project_path)
        / 'config'
        / 'urls.py'
    )

    with open(urls_path, 'r', encoding='utf-8') as f:

        content = f.read()

    # Import settings
    if 'from django.conf import settings' not in content:

        content = (
            "from django.conf import settings\n"
            "from django.conf.urls.static import static\n\n"
            + content
        )

    static_pattern = (
        "\n\nurlpatterns += static(\n"
        "    settings.STATIC_URL,\n"
        "    document_root=settings.STATIC_ROOT\n"
        ")\n"
    )

    if 'urlpatterns += static(' not in content:

        content += static_pattern

    with open(urls_path, 'w', encoding='utf-8') as f:

        f.write(content)

def register_api(
    app_name,
    class_name,
    file_name,
    route_name
):

    api_path = (
        Path.cwd()
        / 'apps'
        / app_name
        / 'urls'
        / 'api.py'
    )

    with open(api_path, 'r', encoding='utf-8') as f:

        content = f.read()

    import_line = (
        f"from apps.{app_name}.views.{file_name} "
        f"import {class_name}ViewSet\n"
    )

    if import_line not in content:

        content = (
            import_line
            + content
        )

    register_block = (
        f"\nrouter.register(\n"
        f"    '{route_name}',\n"
        f"    {class_name}ViewSet\n"
        f")\n"
    )

    if register_block not in content:

        content = content.replace(
            'urlpatterns = [',
            register_block + '\nurlpatterns = ['
        )

    with open(api_path, 'w', encoding='utf-8') as f:

        f.write(content)


def register_imports(
    app_name,
    class_name,
    file_name
):

    targets = [
        (
            'models',
            f'from apps.{app_name}.models.{file_name} import {class_name}\n'
        ),
        (
            'serializers',
            (
                f'from apps.{app_name}.serializers.{file_name} '
                f'import {class_name}Serializer\n'
            )
        ),
        (
            'views',
            (
                f'from apps.{app_name}.views.{file_name} '
                f'import {class_name}ViewSet\n'
            )
        )
    ]

    for folder, import_line in targets:

        init_path = (
            Path.cwd()
            / 'apps'
            / app_name
            / folder
            / '__init__.py'
        )

        with open(init_path, 'r', encoding='utf-8') as f:

            content = f.read()

        if import_line not in content:

            content += import_line

        with open(init_path, 'w', encoding='utf-8') as f:

            f.write(content)