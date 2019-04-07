from setuptools import find_packages, setup


def parse_requirements(filename):
    with open(filename) as f:
        lineiter = (line.strip() for line in f)
        return [
            line.replace(' \\', '').strip()
            for line in lineiter
            if (
                line and
                not line.startswith("#") and
                not line.startswith("-e") and
                not line.startswith("--")
            )
        ]


with open('README.md', 'rb') as f:
    LONG_DESCRIPTION = f.read().decode('utf-8')


setup(
    name='sqlalchemy-postgresql-audit',
    version='0.2.0',
    description='A postgres audit table implementation that works with sqlalchemy and alembic',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Hunter Senft-Grupp',
    author_email='huntcsg@gmail.com',
    url='https://github.com/huntcsg/sqlalchemy-postgresql-audit',
    license='MIT',
    keywords='sqlalchemy sql postgresql postgres alembic audit changelog',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    zip_safe=False,
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    install_requires=parse_requirements('deps/requirements.in'),
    extras_require={
        'testing': parse_requirements('deps/testing-requirements.in'),
        'docs': parse_requirements('deps/docs-requirements.in'),
        'linting': parse_requirements('deps/linting-requirements.in'),
    },
    entry_points={
        'sqlalchemy.plugins': [
            'audit = sqlalchemy_postgresql_audit.plugin:AuditPlugin'
        ]
    },
)
