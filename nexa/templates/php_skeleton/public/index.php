<?php

require __DIR__ . '/../vendor/autoload.php';

// Load Environment Variables
$dotenv = Dotenv\Dotenv::createImmutable(__DIR__ . '/../');
if (file_exists(__DIR__ . '/../.env')) {
    $dotenv->load();
}

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
$dispatcher = FastRoute\simpleDispatcher(function(FastRoute\RouteCollector $r) {
    // Nexa Admin Routes (Stealth Mode)
    if (class_exists('Nexa\Admin\Controllers\AdminController')) {
        $r->addRoute('GET', '/nexa-admin/api/schema', ['Nexa\Admin\Controllers\AdminController', 'schema']);
        $r->addRoute('GET', '/nexa-admin/api/data/{entity:.+}', ['Nexa\Admin\Controllers\AdminController', 'listData']);
        $r->addRoute('POST', '/nexa-admin/api/data/{entity:.+}', ['Nexa\Admin\Controllers\AdminController', 'createData']);
        $r->addRoute('PUT', '/nexa-admin/api/data/{entity:.+}/{id:\d+}', ['Nexa\Admin\Controllers\AdminController', 'updateData']);
        $r->addRoute('DELETE', '/nexa-admin/api/data/{entity:.+}/{id:\d+}', ['Nexa\Admin\Controllers\AdminController', 'deleteData']);
    }

    // Load module routes
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
        // Serve index.html for non-API routes (SPA support)
        if (strpos($uri, '/api') !== 0) {
            $indexPath = __DIR__ . '/index.html';
            if (file_exists($indexPath)) {
                echo file_get_contents($indexPath);
                exit;
            }
        }
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

        if (is_array($response)) {
            header('Content-Type: application/json');
            echo json_encode($response);
        } elseif (is_string($response)) {
            if (strpos(trim($response), '<') === 0) {
                header('Content-Type: text/html');
            } else {
                header('Content-Type: text/plain');
            }
            echo $response;
        } else {
            header('Content-Type: application/json');
            echo json_encode(['data' => $response]);
        }
        break;
}
