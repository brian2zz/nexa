<?php

// Note: $r is available from the scope in index.php where this file is required.
$r->addRoute('GET', '/api/ping', [\Apps\Core\Controllers\PingController::class, 'ping']);
