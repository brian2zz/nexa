<?php

namespace Nexa\Admin\Controllers;

use Nexa\Database;

class AdminController
{
    public function index()
    {
        $indexPath = __DIR__ . '/../Views/index.html';
        if (file_exists($indexPath)) {
            return file_get_contents($indexPath);
        } else {
            http_response_code(404);
            return "Admin View Not Found";
        }
    }

    public function schema()
    {
        $em = Database::getEntityManager();
        $meta = $em->getMetadataFactory()->getAllMetadata();
        $schema = [];
        
        foreach ($meta as $m) {
            $className = $m->getName();
            $parts = explode('\\', $className);
            $modelName = end($parts);
            
            // Extract app name from namespace (e.g. Apps\Inventory\Models\Product -> Inventory)
            $appName = isset($parts[1]) ? $parts[1] : 'Core';
            
            $fields = [];
            foreach ($m->getFieldNames() as $fieldName) {
                $fields[] = [
                    'name' => $fieldName,
                    'type' => $m->getTypeOfField($fieldName),
                    'identifier' => $m->isIdentifier($fieldName)
                ];
            }
            
            $schema[] = [
                'app' => $appName,
                'model' => $modelName,
                'class' => str_replace('\\', '-', $className), // Safe for URL
                'fields' => $fields
            ];
        }
        
        return ['data' => $schema];
    }

    public function listData($entityClass)
    {
        $em = Database::getEntityManager();
        $class = str_replace('-', '\\', $entityClass);
        if (!class_exists($class)) {
            http_response_code(404);
            return ['error' => 'Entity not found'];
        }
        
        $repo = $em->getRepository($class);
        $data = $repo->findAll();
        
        $result = [];
        $meta = $em->getClassMetadata($class);
        $fields = $meta->getFieldNames();
        
        foreach ($data as $item) {
            $row = [];
            foreach ($fields as $f) {
                // Since properties are public in NexaModel default setup
                if (property_exists($item, $f)) {
                    $row[$f] = $item->$f;
                } else {
                    $row[$f] = null;
                }
            }
            $result[] = $row;
        }
        
        return ['data' => $result];
    }

    public function createData($entityClass)
    {
        $em = Database::getEntityManager();
        $class = str_replace('-', '\\', $entityClass);
        if (!class_exists($class)) {
            http_response_code(404);
            return ['error' => 'Entity not found'];
        }

        $input = json_decode(file_get_contents('php://input'), true);
        if (!$input) {
            http_response_code(400);
            return ['error' => 'Invalid JSON input'];
        }

        $entity = new $class();
        $meta = $em->getClassMetadata($class);
        $fields = $meta->getFieldNames();

        foreach ($fields as $f) {
            if (isset($input[$f]) && !$meta->isIdentifier($f)) {
                $val = $input[$f];
                if ($meta->getTypeOfField($f) === 'date' || $meta->getTypeOfField($f) === 'datetime') {
                    $val = new \DateTime($val);
                }
                
                // If there's a setter use it, otherwise set property directly
                $setter = 'set' . ucfirst($f);
                if (method_exists($entity, $setter)) {
                    $entity->$setter($val);
                } else {
                    $entity->$f = $val;
                }
            }
        }

        $em->persist($entity);
        $em->flush();
        return ['status' => 'created'];
    }

    public function updateData($entityClass, $id)
    {
        $em = Database::getEntityManager();
        $class = str_replace('-', '\\', $entityClass);
        if (!class_exists($class)) {
            http_response_code(404);
            return ['error' => 'Entity not found'];
        }

        $repo = $em->getRepository($class);
        $entity = $repo->find($id);
        if (!$entity) {
            http_response_code(404);
            return ['error' => 'Record not found'];
        }

        $input = json_decode(file_get_contents('php://input'), true);
        $meta = $em->getClassMetadata($class);
        $fields = $meta->getFieldNames();

        foreach ($fields as $f) {
            if (isset($input[$f]) && !$meta->isIdentifier($f)) {
                $val = $input[$f];
                if ($meta->getTypeOfField($f) === 'date' || $meta->getTypeOfField($f) === 'datetime') {
                    $val = new \DateTime($val);
                }
                
                $setter = 'set' . ucfirst($f);
                if (method_exists($entity, $setter)) {
                    $entity->$setter($val);
                } else {
                    $entity->$f = $val;
                }
            }
        }

        $em->flush();
        return ['status' => 'updated'];
    }

    public function deleteData($entityClass, $id)
    {
        $em = Database::getEntityManager();
        $class = str_replace('-', '\\', $entityClass);
        if (!class_exists($class)) {
            http_response_code(404);
            return ['error' => 'Entity not found'];
        }

        $repo = $em->getRepository($class);
        $entity = $repo->find($id);
        if ($entity) {
            $em->remove($entity);
            $em->flush();
        }

        return ['status' => 'deleted'];
    }
}
