## Run

1. Make sure to copy the latest **.env** file to your project directory (you can find .env in our backend telagram chat, just look for the latest **#env**).

2. Make sure you have **Docker Desktop** installed. To see the docs to get started go to [https://www.docker.com/get-started](https://www.docker.com/get-started)

3. To create and start the containers run the following commands:

    ``` bash
    make build
    make migrations
    make population
    make app
    ```

    If you encounter any errors with **migrations** or project changes not beeing implemented within the previously built containers, we recommend the following commands:

    ``` bash
    make destroy
    make clean
    ```

    Afterwards **create** and **start** containers again.

4. You can find API documentation at <http://localhost/docs>

    :exclamation: make sure that the app is **running** prior to accessing swagger


### **Testing your code**

We run tests through github actions on every push and pull request that you make. Make sure to run tests before you commit changes to your branch using the Makefile command:

```bash
make tests
```

:exclamation: Every new peace of code that you write, whether its a new exception handler in an existing endpoint or a new endpoint overall, make sure to cover it with tests.

## Docker

In the project root directory you can find the **docker** folder. In **/compose** folder are located **.yml** files with container configurations.

- migrations.yml
- dbpopulation.yml
- redis.yml
- app.yml
- main.yml
- worker.yml
- db.yml
- tests.yml

You can see a full list of configurations in these files.

We run dockerfiles through **MakeFile** which makes the command promt for building multiple containers as simple and as short as:

```bash
make build # building the whole project
```

or

```bash
make db # building just the database
```

You can see the full list of make commands in **Makefile** in project root directory.

## That's all folks, have fun

alembic usage 
- alembic revision --autogenerate -m "Added initial table"
- alembic upgrade head
- alembic downgrade ...
