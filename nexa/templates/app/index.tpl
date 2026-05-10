{% load nexa %}

<!DOCTYPE html>
<html lang="en">
<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>{{ app_name }}</title>

    <meta name="csrf-token"
          content="{{ csrf_token }}">

    {% nexa_assets '__APP_NAME__' %}

</head>
<body>

    <div id="app"></div>

</body>
</html>