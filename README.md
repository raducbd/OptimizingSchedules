## OPTIMIZING SCHEDULES

![](./media/scheduler.gif)


This repository gathers all the code required for a user-friendly interface that allows for optimizing schedules, especially in the context of manufacturing processes.

First of all, we used **Python** and Google's Optimization Software Suite ([OR-Tools](https://developers.google.com/optimization)) to write our scripts. Important packages within this environment are listed below:

* `ortools` so we could work on the optimization problem;
* `plotly` and `matplotlib` so we could easily output Gannt Charts for the planning schedule;
* `streamlit` so we could create an interactive dashboard for the final user.

Finally, we used GitHub actions to build CI pipeline, with the help of a `Makefile`:

* __Installing packages__: we used `pip` and a `requirements.txt` file to list all required packages (`make install`);
* __Formatting__: `black` was used (`make format`);
* __Linting__: `pylint` was used (`make lint`);
* __Testing__: `pytest` was used (`make test`).

____

This project is structured as follows:

#### app.py

Main script where the actual Streamlit dashboard is actually built, by taking advantage of the package developed.

```py
streamlit run app.py
```

#### tests

Folder where all unit tests are located.

#### scheduler

Project folder structure, where all classes and methods are contained.

```sh
scheduler
├── __init__.py
├── manufacturing
│   ├── __init__.py
│   ├── job.py
│   └── task.py
├── scheduling.py
└── utils
    ├── __init__.py
    ├── errors.py
    └── logging.py
```