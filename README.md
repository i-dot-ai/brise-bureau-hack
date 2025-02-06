# Incubator for AI: Paris Generative AI for the Public Good Hackathon

> [!IMPORTANT]
> Hackathon project: This project is an incubation project; as such, this is an example repo. We don't recommend using the code for critical use cases.

## Brise-bureau

This product is designed to help public servants in the policy design and implementation of projects. The suite of AI products directly addresses the challenge of enhancing productivity among public servants by providing streamlined access to critical resources and insights. 

It offers:
- legislative advice
- sentiment analysis and thematic analysis of citizen opinions from public consultations
- project process flow visualisation to aid in delivery of projects


## 🛠 Track 2 : Cas d'Usage à Fort Impact avec des APIs  
Exploitez des APIs comme **Albert** pour concevoir des outils concrets pour l'administration publique.  

Exemples :  
- 📝 **Automatisation administrative** : Génération automatique de documents et rapports.  
- 🔍 **Analyse documentaire** : Recherche et résumé intelligent de textes.  
- 🎯 **Prototypes sur mesure** : Solutions adaptées aux besoins spécifiques identifiés par les équipes.

### 📝 Informations à renseigner pour l’évaluation  

Merci de compléter ce README avec les éléments suivants :  

##### 🏆 Critères d'évaluation  
| Critère            | Description | Poids (%) |
|--------------------|-------------|-----------|
| 🎯 **Pertinence**  | The suite of AI products directly addresses the challenge of enhancing productivity among public servants by providing streamlined access to critical resources and insights. By offering legislative advice, sentiment analysis, thematic analysis of citizen opinions, and project process flow visualisation, the tools ensure public servants have the information needed to make informed decisions efficiently.  | 25 |
| 📈 **Impact**      | The expected results of implementing this suite are significant, as it empowers public servants with enhanced decision-making capabilities and spend more time on specialist tasks. The tools provide measurable improvements in the speed and accuracy of legislative advice, gauging ministerial support, understanding public sentiment, and clarifying project delivery processes, leading to more effective governance and citizen engagement.| 25 |
| 🔧 **Faisabilité** | The MVP of these AI tools is realistically achievable with current technology. By leveraging existing data infrastructures and AI capabilities, the suite can be developed and integrated within the working frameworks of public servants, ensuring a smooth transition to enhanced productivity tools without overwhelming resource demands. | 25 |
| 🌍 **Scalabilité** | Designed as digital common goods, these AI products can be adapted across various government departments and contexts. The modular nature of the suite allows for flexible deployment and expansion, ensuring that different branches of public service can customise and scale the usage of these tools according to their specific needs, promoting broad accessibility and shared benefits. This already adapts some of the open source tools built by the UK Incubator for AI eg [themefinder](https://pypi.org/project/themefinder/). | 25 |

---

## Setting up application

We use [poetry](https://python-poetry.org/) to manage our packages. Poetry uses the project root level `pyproject.toml` to store information about the project, virtual environments and packages. Poetry uses groups to organise packages into logical clusters, with `dev` and no name being reserved keywords.

To set up the python environment for development, execute the following command:

``` bash
poetry install --with streamlit --with fastapi --no-root
```

`--with` here is used to select the poetry package groups to install. 

Poetry creates its own virtual environment to act in, there's no need to create one manually. To start a shell in the poetry environment. Use the following command:

``` bash
poetry shell
```

When executing any python command, locally or on docker, prefix with `poetry run` to run it in the poetry venv. e.g. `poetry run python manage.py makemigrations`.

Copy `.env.example` to `.env` and add the appropriate environment variables eg for Azure Open AI and Elastic.


To run the tests locally use following command:

``` bash
make test
```

#### Running application locally

To run the backend application, use the following command:

```bash
poetry run python backend/main.py
```

or 

```bash
make run_backend
```

The backend application will start on [http://127.0.0.1:8000](http://127.0.0.1:8000). Once the backend process is up and running, set the environment variable to be used by the frontend application to communicate with the backend service:

```bash
export BACKEND_HOST=http://127.0.0.1:8000
```

To run the frontend application, use the following command:

```bash
poetry run python frontend/app/run.py
```

or 
```bash
make run_frontend
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the result. You can edit the page by modifying the `app/page.tsx` file. The page will automatically update as you make changes.


#### Communication between services

The frontend should expect an environment variable called `BACKEND_HOST` and make calls to the backend using this variable.

The way that we get around CORS issues atm is by having the frontend server make requests to the backend API.




