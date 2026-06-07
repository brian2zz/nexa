<?php

require __DIR__ . '/../vendor/autoload.php';

use Nexa\Database;

$entityManager = Database::getEntityManager();
return $entityManager->getConnection();
