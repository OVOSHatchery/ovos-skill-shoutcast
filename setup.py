#!/usr/bin/env python3
from setuptools import setup

# skill_id=package_name:SkillClass
PLUGIN_ENTRY_POINT = 'skill-shoutcast.jarbasai=skill_shoutcast:ShoutCastSkill'

setup(
    # this is the package name that goes on pip
    name='ovos-skill-shoutcast',
    version='0.0.1',
    description='ovos shoutcast skill plugin',
    url='https://github.com/JarbasSkills/skill-shoutcast',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    package_dir={"skill_shoutcast": ""},
    package_data={'skill_shoutcast': ['locale/*', 'ui/*']},
    packages=['skill_shoutcast'],
    include_package_data=True,
    install_requires=["ovos_workshop~=0.0.5a7", "shoutcast_api"],
    keywords='ovos skill plugin',
    entry_points={'ovos.plugin.skill': PLUGIN_ENTRY_POINT}
)
