<?php

declare(strict_types=1);

namespace App\FeatureFlag;

interface FeatureFlagDecorateInterface
{
    /**
     * Check if the class should use feature flag.
     */
    public function useFeatureFlag(): bool;

    /**
     * Set a mapping between old method and new method if we want to use feature flag.
     * example:
     * [
     *    'oldMethod1' => 'newMethod1',
     *    'oldMethod2' => 'newMethod2',
     * ].
     */
    public function featureMethodsMapping(): array;

    /**
     * Get the feature flag that we want to use for this class.
     */
    public function getFeatureFlag(): string;
}
