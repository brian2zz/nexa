<?php

return [
    'name' => 'NexaPHP Project',
    'env' => 'local',
    'debug' => true,
    
    'features' => [
        'tenancy' => false,
        'queue_driver' => 'sync',
        'module_isolation' => 'loose',
    ]
];
