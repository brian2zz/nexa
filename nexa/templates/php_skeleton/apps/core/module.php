<?php

return [
    'name' => 'core',
    'version' => '1.0.0',
    'requires' => [],
    'exports' => [
        'core.ping' => function() {
            return "Pong from Service Registry!";
        }
    ]
];
