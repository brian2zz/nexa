{% extends "base.html" %}
{% load static %}

{% block content %}
<div id="app">
    <!-- Vue app will be mounted here -->
</div>

{% if debug %}
    <script type="module" src="http://localhost:5173/apps/{{ app_name }}/frontend/src/main.js"></script>
{% else %}
    <script type="module" src="{% static 'apps/{{ app_name }}/frontend/dist/main.js' %}"></script>
{% endif %}
{% endblock %}
