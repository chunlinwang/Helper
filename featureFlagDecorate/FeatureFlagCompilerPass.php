<?php

declare(strict_types=1);

namespace App\DependencyInjection\Compiler;

use App\FeatureFlag\FeatureFlagDecorator;
use Symfony\Component\DependencyInjection\Compiler\CompilerPassInterface;
use Symfony\Component\DependencyInjection\Compiler\PriorityTaggedServiceTrait;
use Symfony\Component\DependencyInjection\ContainerBuilder;
use Symfony\Component\DependencyInjection\Exception\RuntimeException;
use function Safe\sprintf;

class FeatureFlagCompilerPass implements CompilerPassInterface
{
    use PriorityTaggedServiceTrait;

    public const FEATURE_FLAG_DECORATED_TAG = 'app.feature_flag_decorated';

    public function process(ContainerBuilder $container)
    {
        if (!$container->hasDefinition(FeatureFlagDecorator::class)) {
            return;
        }

        if (!$featureFlagDecoratingServices = $this->findAndSortTaggedServices(self::FEATURE_FLAG_DECORATED_TAG, $container)) {
            throw new RuntimeException(sprintf('You must tag at least one service as "%s".', self::FEATURE_FLAG_DECORATED_TAG));
        }

        foreach ($featureFlagDecoratingServices as $featureFlagDecoratingService) {
            $serviceId = (string) $featureFlagDecoratingService;

            $decoratedServiceId = $this->getDecoratingServiceName($serviceId);

            // Add the new decorated service.
            $container->register($decoratedServiceId, FeatureFlagDecorator::class)
                ->setDecoratedService($serviceId)
                ->setPublic(true)
                ->setAutowired(true);
        }
    }

    private function getDecoratingServiceName(string $serviceId): string
    {
        $names = explode('\\', $serviceId);

        $className = array_pop($names);

        $names[] = "Decorating{$className}";

        return implode('\\', $names);
    }
}
