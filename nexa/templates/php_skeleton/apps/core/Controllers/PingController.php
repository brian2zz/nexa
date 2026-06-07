<?php

namespace Apps\Core\Controllers;

use Nexa\ServiceRegistry;

class PingController
{
    public function ping()
    {
        // Demonstrating that we can call internal services securely
        $msg = ServiceRegistry::call('core.ping');

        return [
            'status' => 'success',
            'message' => 'NexaPHP Kernel is running perfectly!',
            'service_reply' => $msg
        ];
    }
}
