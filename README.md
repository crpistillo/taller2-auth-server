Master:
[![Build Status](https://travis-ci.com/urielkelman/taller2-auth-server.svg?token=tFcmLjoZ6PFesBqLEXNZ&branch=master)](https://travis-ci.com/urielkelman/taller2-auth-server)

Develop:
[![Build Status](https://travis-ci.com/urielkelman/taller2-auth-server.svg?token=tFcmLjoZ6PFesBqLEXNZ&branch=develop)](https://travis-ci.com/urielkelman/taller2-auth-server)

# Chotuve Auth Server

La app se crea actualmente en create_application.py, eventualmente necesitara recibir parametros para crearse de alguna config, cuando eso suceda se puede mejorar.

## Logging

Una [convencion de python](https://docs.python.org/3/howto/logging.html) es crear un logger por cada clase diferenciada de la siguiente forma:

```
logger = logging.getLogger(__name__)
```

Vamos a mantener esa convencion para cada clase y loggear con eso.
Python permite configurar para diferenciado por clase y nivel de log tirar 
los logs a archivos rotativos, sumologic, cualquier api, etc.
Podemos extender el logueo en el futuro a gusto, cambiando esta convencion y 
usando las jerarquias de los paquetes para discriminar el trato del log.

Actualmente la configuracion permite loguear solo desde los paquetes en src. (ver *config/logging_conf.ini*)

## Para correr tests

Los unit tests deberan estar en la carpeta test, corren con pytest:

```
pytest test
```

Es importante correr esto desde la raiz del repo ya que es el run path.

Para correr coverage report:

```
pip install -r requirements-travis.txt
pytest --cov=. --cov-report html test/
```

## Para correr la app

Para correr la app con flask:

```
python __main__.py
```

Para correr la app con gunicorn:

```
gunicorn -k sync --workers 3 --bind 0.0.0.0:8080 'create_application:create_application("config/deploy_conf.yml")' --log-config config/logging_conf.ini
```

* `-k` es para indicar el tipo de workers, queremos sync porque andan mejor que el default
* `--workers` es para la cantidad workers simultaneo, como gunicorn es para probar pre-deploy 
y deberia usarse flask para debuggear me parece prudente dejarlo en 3 que seria similar a prod
* `--bind` le indica a que host y puerto mapearlo
* `create_application:create_application` es la ruta a donde importar la app de flask

Para levantar las env variables de prod (si se tiene el prod.env):

```
set -o allexport; source prod.env; set +o allexport
```

## Deploy de la app a Heroku

La config del deploy esta en el Procfile.

Actualmente el deploy es manual, luego de instalar heroku cli y estar logueado hay que configurar el remote "heroku" por unica vez:

```
heroku git:remote -a tuapp
```

Despues para deployar:

```
git push heroku master
```

Finalmente para ver los logs:

```
heroku logs
```

## Postgres database

Script para el set-up de la base de datos:

```sql
create schema chotuve;


create table chotuve.users
(
	email varchar,
	fullname varchar,
	phone_number varchar,
	photo bytea,
	password varchar
);

create unique index users_email_uindex
	on chotuve.users (email);

alter table chotuve.users
	add constraint users_pk
		primary key (email);


create table chotuve.user_recovery_token
(
	email varchar,
	token varchar,
	timestamp timestamp,
	constraint email
		foreign key (email) references chotuve.users
);

create unique index user_recovery_token_email_uindex
	on chotuve.user_recovery_token (email);

alter table chotuve.user_recovery_token
	add constraint user_recovery_token_pk
		primary key (email);
```