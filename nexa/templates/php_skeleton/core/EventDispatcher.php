<?php

namespace Nexa;

class EventDispatcher
{
    private static array $listeners = [];

    public static function listen(string $eventName, callable|string $handler): void
    {
        self::$listeners[$eventName][] = $handler;
    }

    public static function dispatch(string $eventName, mixed $payload = null): void
    {
        if (!isset(self::$listeners[$eventName])) {
            return;
        }

        foreach (self::$listeners[$eventName] as $handler) {
            if (is_callable($handler)) {
                call_user_func($handler, $payload);
            } elseif (is_string($handler) && str_contains($handler, '@')) {
                list($class, $method) = explode('@', $handler);
                // Simple instantiation for now
                $instance = new $class();
                call_user_func([$instance, $method], $payload);
            }
        }
    }
}
