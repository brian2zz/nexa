<?php

namespace Nexa;

class ServiceRegistry
{
    private static array $services = [];
    private static ?\DI\Container $container = null;

    public static function setContainer(\DI\Container $container): void
    {
        self::$container = $container;
    }

    public static function register(string $alias, callable|string $handler): void
    {
        self::$services[$alias] = $handler;
    }

    public static function call(string $alias, array $args = [])
    {
        if (!isset(self::$services[$alias])) {
            throw new \RuntimeException("Service '{$alias}' not found in registry.");
        }

        $handler = self::$services[$alias];

        if (is_callable($handler)) {
            return call_user_func_array($handler, $args);
        }

        if (is_string($handler) && str_contains($handler, '@')) {
            list($class, $method) = explode('@', $handler);
            if (self::$container) {
                $instance = self::$container->get($class);
            } else {
                $instance = new $class();
            }
            return call_user_func_array([$instance, $method], $args);
        }

        throw new \RuntimeException("Invalid handler format for service '{$alias}'.");
    }
}
