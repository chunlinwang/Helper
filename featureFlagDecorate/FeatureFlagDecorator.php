<?php

declare(strict_types=1);

namespace App\FeatureFlag;

final class FeatureFlagDecorator
{
    private FeatureFlagDecorateInterface $decorated;
    private FeatureFlagClassifier $featureFlagClassifier;

    public function __construct(FeatureFlagDecorateInterface $decorated, FeatureFlagClassifier $featureFlagClassifier)
    {
        $this->decorated = $decorated;
        $this->featureFlagClassifier = $featureFlagClassifier;
    }

    /**
     * @phpstan-ignore-next-line
     */
    public function __call($name, $arguments)
    {
        // If we don't use feature flag, we will use the origin method of the origin class.
        if (!$this->decorated->useFeatureFlag()) {
            return $this->decorated->{$name}(...$arguments);
        }

        // If there is not enable feature flag, we will use the origin method of the origin class.
        if (!$this->featureFlagClassifier->isEnabled($this->decorated->getFeatureFlag())) {
            return $this->decorated->{$name}(...$arguments);
        }

        $methods = $this->decorated->featureMethodsMapping();

        // If there is not any mapping methods, we will use the origin method of the origin class.
        if (empty($methods[$name])) {
            return $this->decorated->{$name}(...$arguments);
        }

        return $this->decorated->{$methods[$name]}(...$arguments);
    }
}
