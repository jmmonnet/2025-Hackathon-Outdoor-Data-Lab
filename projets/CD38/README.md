![alt](docs/img/logo2.png)


VigieOutdoor est une solution numérique pour identifier et quantifier le risque d’impact des activités outdoor sur le patrimoine naturel.

Cette solution est une API ReST avec deux routes:
- **[GET]** `/risk` : permet de retourner les mailles et leur indicateur de risque. Cette route prend en entrée les coordonnées d'une bouding-box soit à l'aide des paramètres x1,y1,x2,y2 ou du paramètre bbox.

    Exemple:

    ```bash
    curl -X GET http://localhost:8000/risk?x1=5.540886&y1=45.280443&x2=5.564575&y2=45.26353
    # ou
    curl -X GET http://localhost:8000/risk?bbox=5.540886,45.280443,5.564575,45.26353
    ```
- **[POST]** `/risk/geojson` : permet de retourner les mailles et leur indicateur de risque. Cette route prend en entrée n'importe quel GeoJSON.

    Exemple:

    ```bash
    curl -X POST -H "Content-Type: application/json" -d @<votrefichiergeojson> http://localhost:8000/risk/geojson
    ```


## Fonctionnement de l'API

Installer l'environnement Python à l'aide de la commande suivante : 
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Lancer l'API à l'aide de la commande suivante :

```bash
source venv/bin/activate
fastapi dev api.py
```


## Exemple d'utilisation de l'API

### Application web à destination du grand public
![alt](docs/img/appli_web.png)

### Utilisation/Récupération des données dans QGIS

![alt](docs/img/capture%20Qgis.png)

## Auteurs

**Christophe Martinez**, Pôle Ressource National Transition Écologique et Sport Nature
**Thomas Mourey**, Département de l'Isère
**Émilien Maulave**, Département de l'Isère
**Jacques Fize**, Parc National des Écrins
**Julien Vilmant**, INRAE
**Marion Drouin**, Décathlon