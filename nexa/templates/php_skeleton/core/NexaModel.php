<?php

namespace Nexa;

use Doctrine\ORM\Mapping\MappedSuperclass;

#[MappedSuperclass]
abstract class NexaModel
{
    public function save(): void
    {
        $em = Database::getEntityManager();
        $em->persist($this);
        $em->flush();
    }

    public function delete(): void
    {
        $em = Database::getEntityManager();
        $em->remove($this);
        $em->flush();
    }

    public static function find($id): ?static
    {
        return Database::getEntityManager()->find(static::class, $id);
    }

    public static function all(): array
    {
        $em = Database::getEntityManager();
        return $em->getRepository(static::class)->findAll();
    }
}
