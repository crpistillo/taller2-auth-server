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

## Para correr unit tests

Los unit tests deberan estar en la carpeta test, corren con pytest:

```
pytest test
```

Es importante correr esto desde la raiz del repo ya que es el run path.

## Para correr la app

Para correr la app con flask:

```
python __main__.py
```

Para correr la app con gunicorn:

```
gunicorn -k sync --workers 3 --bind 0.0.0.0:8080 'create_application:create_application()'
```

* `-k` es para indicar el tipo de workers, queremos sync porque andan mejor que el default
* `--workers` es para la cantidad workers simultaneo, como gunicorn es para probar pre-deploy 
y deberia usarse flask para debuggear me parece prudente dejarlo en 3 que seria similar a prod
* `--bind` le indica a que host y puerto mapearlo
* `create_application:create_application` es la ruta a donde importar la app de flask

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