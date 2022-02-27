Rss Scraper Application
=======================


     Rss Scraper app based on DRF.

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
     :target: https://github.com/ambv/black
     :alt: Black code style

.. image:: https://img.shields.io/gitlab/pipeline-status/muhammadmamdouh/rss-scraper
     :target: https://gitlab.com/muhammadmamdouh/rss-scraper/-/pipelines
     :alt: Gitlab CI/CD Build

.. contents::

Stack Used
----------
+ Docker v. 20.10.12
+ Docker Compose v. 2.2.3
+ PostgreSQL v. 13.5
+ Redis v. 6
+ Python v. 3.9
+ Django Framework v. 3.2.11
+ Django Rest Framework v. 3.13.1
+ PyTest v. 6.2.5
+ Celery v. 5.2.3
+ Celery Beat v. 2.2.1
+ Flower v. 1.0.0
+ Mailhog v. 1.0.0 (Locally)

Basic Commands
--------------
Build the docker image
&&&&&&&&&&&&&&&&&&&&&&&

.. code-block:: bash

     docker-compose -f local.yml build

Run flake8 checks
&&&&&&&&&&&&&&&&&

.. code-block:: bash

     docker-compose -f local.yml run --rm django flake8

Run the unit tests
&&&&&&&&&&&&&&&&&&

.. code-block:: bash

     docker-compose -f local.yml run --rm django pytest

Generate the test coverage report
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

.. code-block:: bash

     docker-compose -f local.yml run --rm django coverage run -m pytest
     docker-compose -f local.yml run --rm django coverage report

Run the application using docker compose
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

.. code-block:: bash

     docker-compose -f local.yml up  # use -d to run the services in the background.

Create superuser to start checking the feeds details on the django admin panel
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

.. code-block:: bash

     docker-compose -f local.yml run --rm django python manage.py createsuperuser --email=superuser@admin.com --username=superuser

Also you can check the feeds and feed items at the customized django admin at
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
`Django admin panel <http://localhost:8000/admin/>`_

Now you can check and test the developed APIs docs
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
APIs `Swagger docs <http://localhost:8000/api/docs/>`_

Now you can create a user for testing from the signup form at:
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
Create new user `Signup <http://localhost:8000/>`_

You can check the received emails using the local mail server
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
`Mailhog <http://localhost:8025>`_

You can check the running background celery tasks and periodic tasks statuses using credentials defined at django env
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
`Flower <http://localhost:5555>`_

Interact manually with the DB using the PostgreSQL shell
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

.. code-block:: bash

     docker-compose -f local.yml exec postgres psql --username=${POSTGRES_USERNAME} --dbname=${POSTGRES_DB_NAME}

Stop the running application using docker compose
&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

.. code-block:: bash

     docker-compose -f local.yml down -v

What's Next?
&&&&&&&&&&&&

    + Update database modeling to prevent saving & scraping duplicate feeds/items for different users.
    + Using caching on the GET APIs Views and ORM.
        1. Cache on the ORM level using 3rd party package like: `Django Cacheops <https://github.com/Suor/django-cacheops>`_.
        2. Cache on the View level using either the base DRF decorators.
        3. Most importantly invalidate the cached results after any feed/item related updates.
    + Integrating APM solution.
    + Implementing an exponential backoff celery retry mechanism on the failed tasks.


Commits icons are from: `Gitmoji <https://gitmoji.dev/>`_

License
--------------
Open source licensed under the MIT license (see LICENSE file for details).
