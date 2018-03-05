<?php

namespace AppBundle\Security;

use AppBundle\Entity\User;
use Symfony\Component\Security\Core\Authentication\Token\TokenInterface;
use Symfony\Component\Security\Core\Authorization\Voter\Voter;
use Symfony\Component\Yaml\Yaml;

class ObjectVoter extends Voter
{
    /**
     * @var array
     */
    protected $objects;

    /**
     * @var array
     */
    protected $objectAttributes;

    /**
     * ObjectVoter constructor.
     *
     * @param string $configFile
     */
    public function __construct($configFile)
    {
        $this->objectAttributes = Yaml::parse(file_get_contents($configFile));
        $this->objects = array_keys($this->objectAttributes);
    }

    /**
     * {@inheritdoc}
     */
    protected function supports($attribute, $subject)
    {
        $attributes = $this->getAttributes($subject);

        if ($attributes && !in_array($attribute, $attributes)) {
            return false;
        }

        if (!in_array(get_class($subject), $this->objects)) {
            return false;
        }

        return true;
    }

    /**
     * {@inheritdoc}
     */
    protected function voteOnAttribute($attribute, $subject, TokenInterface $token)
    {
        return $this->checkAttribute($attribute, $subject, $token->getUser());
    }

    /**
     * Check attribute for a subject.
     *
     * @param $attribute
     * @param $subject
     * @param User $user
     *
     * @return bool
     */
    protected function checkAttribute($attribute, $subject, User $user)
    {
        if (!$user instanceof User) {
            return false;
        }

        $attributeRoles = $this->getAttributeRoles($subject, $attribute);

        if ($attributeRoles) {
            foreach ($attributeRoles as $role) {
                if ($user->hasRole($role)) {
                    return true;
                }
            }
        }

        return false;
    }

    /**
     * Get attributes for an object.
     *
     * @param object $subject
     *
     * @return bool|array
     */
    protected function getAttributes($subject)
    {
        $subjectClass = get_class($subject);

        return isset($this->objectAttributes[$subjectClass]) ? array_keys($this->objectAttributes[$subjectClass]) : false;
    }

    /**
     * Get roles for an attribute.
     *
     * @param $subject
     * @param $attribute
     *
     * @return bool
     */
    protected function getAttributeRoles($subject, $attribute)
    {
        $subjectClass = get_class($subject);

        return isset($this->objectAttributes[$subjectClass]) && isset($this->objectAttributes[$subjectClass][$attribute])
            ? $this->objectAttributes[$subjectClass][$attribute] : false;
    }
}

/* yaml config roles viter
AppBundle\Entity\Equipement:
    view: ['ROLE_SUPER_ADMIN']
    create: ['ROLE_SUPER_ADMIN']
    edit: ['ROLE_SUPER_ADMIN']
    delete: ['ROLE_SUPER_ADMIN']
    activate: ['ROLE_SUPER_ADMIN']
    edit_partial: ['ROLE_SUPER_ADMIN']
    edit: ['ROLE_SUPER_ADMIN']
AppBundle\Entity\Invoice:
    view: ['ROLE_SUPER_ADMIN']
    create: ['ROLE_SUPER_ADMIN']

*/
