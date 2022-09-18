# SQL-Models

## What is it?
A library that makes it easy to build complex sql-queries, views, and tables by combining simpler
sql-queries.

### How does it work? 
* All sql-models consist of a SQL query.
* A sql-model can refer other sql-models
* A sql-model can use variables in its sql template
* The references between sql-models form a directed acyclic graph (DAG).

### What makes it unique?
* Create models using a python API, e.g. from a Jupyter notebook
* Sql-models can be reused multiple times within the same DAG with different variables and/or references
