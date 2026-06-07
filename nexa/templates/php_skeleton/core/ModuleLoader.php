<?php

namespace Nexa;

class ModuleLoader
{
    private array $modules = [];
    private array $exports = [];

    public function loadModules(string $appsPath): void
    {
        if (!is_dir($appsPath)) {
            return;
        }

        $directories = array_diff(scandir($appsPath), ['..', '.']);

        foreach ($directories as $dir) {
            $modulePath = $appsPath . '/' . $dir . '/module.php';
            if (is_file($modulePath)) {
                $manifest = require $modulePath;
                $this->modules[$manifest['name']] = $manifest;
            }
        }

        $this->verifyDependencies();
        $this->registerExports();
    }

    private function verifyDependencies(): void
    {
        foreach ($this->modules as $name => $manifest) {
            if (isset($manifest['requires'])) {
                foreach ($manifest['requires'] as $req) {
                    if (!isset($this->modules[$req])) {
                        throw new \RuntimeException("Module '{$name}' requires '{$req}', which is not loaded.");
                    }
                }
            }
        }
    }

    private function registerExports(): void
    {
        foreach ($this->modules as $name => $manifest) {
            if (isset($manifest['exports'])) {
                foreach ($manifest['exports'] as $alias => $handler) {
                    ServiceRegistry::register($alias, $handler);
                }
            }
        }
    }
}
