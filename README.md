# Chotuve Auth Server

La app se crea actualmente en create_application.py, eventualmente necesitara recibir parametros para crearse de alguna config, cuando eso suceda se puede mejorar.

To-dos para poder empezar a iterar productivamente sobre esto:
* Unit tests
* Deploy a Heroku
* CI
* Logging

## Para correr la app

Para correr la app con flask:

```
python __main__.py
```

Para correr la app con gunicorn:

```
gunicorn -k sync --workers 3 --bind 0.0.0.0:8080 create_application:create_application
```

* `-k` es para indicar el tipo de workers, queremos sync porque andan mejor que el default
* `--workers` es para la cantidad workers simultaneo, como gunicorn es para probar pre-deploy 
y deberia usarse flask para debuggear me parece prudente dejarlo en 3 que seria similar a prod
* `--bind` le indica a que host y puerto mapearlo
* `create_application:create_application` es la ruta a donde importar la app de flask