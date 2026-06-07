<?php

namespace Nexa;

use Doctrine\ORM\ORMSetup;
use Doctrine\ORM\EntityManager;
use Doctrine\DBAL\DriverManager;

class Database
{
    private static ?EntityManager $entityManager = null;

    public static function getEntityManager(): EntityManager
    {
        if (self::$entityManager === null) {
            $paths = [];
            // Use APP_ENV or fallback to local
            $isDevMode = ($_ENV['APP_ENV'] ?? 'local') !== 'production';

            $dbConnection = $_ENV['DB_CONNECTION'] ?? 'sqlite';

            if ($dbConnection === 'sqlite') {
                $dbPath = $_ENV['DB_DATABASE'] ?? 'database.sqlite';
                if (!str_starts_with($dbPath, '/')) {
                    $dbPath = __DIR__ . '/../' . $dbPath;
                }
                $connectionParams = [
                    'driver' => 'pdo_sqlite',
                    'path' => $dbPath,
                ];
            } else {
                $connectionParams = [
                    'driver'   => 'pdo_' . $dbConnection,
                    'host'     => $_ENV['DB_HOST'] ?? '127.0.0.1',
                    'port'     => $_ENV['DB_PORT'] ?? 3306,
                    'dbname'   => $_ENV['DB_DATABASE'] ?? 'nexa_db',
                    'user'     => $_ENV['DB_USERNAME'] ?? 'root',
                    'password' => $_ENV['DB_PASSWORD'] ?? '',
                ];
            }

            // Find all Models directories in apps/*/Models
            $appsPath = __DIR__ . '/../apps';
            if (is_dir($appsPath)) {
                $directories = array_diff(scandir($appsPath), ['..', '.']);
                foreach ($directories as $dir) {
                    $modelPath = $appsPath . '/' . $dir . '/Models';
                    if (is_dir($modelPath)) {
                        $paths[] = $modelPath;
                    }
                }
            }

            $isDevMode = true;

            // Use Doctrine ORM 3 setup
            $config = ORMSetup::createAttributeMetadataConfiguration(
                paths: $paths,
                isDevMode: $isDevMode,
            );

            // Database configuration
            // In a real app, read from .env. Here we use SQLite as a fast default.
            $connectionParams = [
                'driver' => 'pdo_sqlite',
                'path' => __DIR__ . '/../database.sqlite',
            ];

            $connection = DriverManager::getConnection($connectionParams, $config);
            self::$entityManager = new EntityManager($connection, $config);
        }

        return self::$entityManager;
    }
}
