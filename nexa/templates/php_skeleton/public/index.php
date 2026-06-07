<?php

require __DIR__ . '/../vendor/autoload.php';

use Nexa\ModuleLoader;
use Nexa\ServiceRegistry;
use DI\ContainerBuilder;
use FastRoute\RouteCollector;

// 1. Init Container
$containerBuilder = new ContainerBuilder();
$container = $containerBuilder->build();
ServiceRegistry::setContainer($container);

// 2. Load Modules
$moduleLoader = new ModuleLoader();
$moduleLoader->loadModules(__DIR__ . '/../apps');

// 3. Load Routes
$dispatcher = FastRoute\simpleDispatcher(function(RouteCollector $r) {
    $appsPath = __DIR__ . '/../apps';
    if (is_dir($appsPath)) {
        $directories = array_diff(scandir($appsPath), ['..', '.']);
        foreach ($directories as $dir) {
            $routeFile = $appsPath . '/' . $dir . '/routes/api.php';
            if (is_file($routeFile)) {
                require $routeFile;
            }
        }
    }
});

// 4. Dispatch Request
$httpMethod = $_SERVER['REQUEST_METHOD'];
$uri = $_SERVER['REQUEST_URI'];
if (false !== $pos = strpos($uri, '?')) {
    $uri = substr($uri, 0, $pos);
}
$uri = rawurldecode($uri);

$routeInfo = $dispatcher->dispatch($httpMethod, $uri);
switch ($routeInfo[0]) {
    case FastRoute\Dispatcher::NOT_FOUND:
        http_response_code(404);
        header('Content-Type: application/json');
        echo json_encode(['error' => 'Not Found']);
        break;
    case FastRoute\Dispatcher::METHOD_NOT_ALLOWED:
        http_response_code(405);
        header('Content-Type: application/json');
        echo json_encode(['error' => 'Method Not Allowed']);
        break;
    case FastRoute\Dispatcher::FOUND:
        $handler = $routeInfo[1];
        $vars = $routeInfo[2];
        
        if (is_array($handler) && count($handler) == 2) {
            $class = $handler[0];
            $method = $handler[1];
            $controller = $container->get($class);
            $response = call_user_func_array([$controller, $method], $vars);
        } elseif (is_callable($handler)) {
            $response = call_user_func_array($handler, $vars);
        } else {
            $response = ['error' => 'Invalid route handler'];
        }

        header('Content-Type: application/json');
        echo json_encode($response);
        break;
}
