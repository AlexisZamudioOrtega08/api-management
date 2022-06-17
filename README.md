# API-MANAGEMENT
API for user api keys management.

### The API contains three main group of endpoints and two levels
### of administration (default user and admin).
## The main group of endpoints are:

    - USERS
    - BILLINGS
    - KEYS

### Note: The authentication is done using the JWT token and storing
### the following information in the token:
    {   
        "id",
        "username",
        "verified",
        "role"
    }
### The token is stored in cookies of client side and is sent in the
### header of each request.
### The token is valid for 30 minutes and is refreshed on every endpoint call.

#### Default user can only access to the following endpoints:
```http
  method: POST
  host:5000/api/v1/users
```

| Body           | Type        | Description                      |
| :------------  | :---------- | :------------------------------  |
| `first_name`   | `str`       | **Required**. First name of user |
| `last_name`    | `str`       | **Required**. Last name of user  |
| `username`     | `str`       | **Required**. Username of user   | 
| `password`     | `str`       | **Required**. Password of user   |
| `email`        | `str`       | **Required**. Email of the user  |
| `address`      | `str`       | **Required**. Adress of the user |
| `role`         | `int`       | **Not required**. Role assigned  |

### Body example:
        {
            "first_name": "<name>", 
            "last_name": "<last_name>",
            "username": "<username>", **Alphanumeric only** **Unmuttable**
            "password": "<password>", **Must have at least one character of the following [A-Z][a-z][0-9][@$!%*#?&]**
            "email": "<email>", **Must be a valid email**
            "address": "<address>", **Full address**
            "role": "<role>" **1/2**
        }

```http
  method: PUT
  host:5000/api/v1/users
```
| Body           | Type        | Description                      |
| :------------  | :---------- | :------------------------------  |
| `first_name`   | `str`       | **Optional**. First name of user |
| `last_name`    | `str`       | **Optional**. Last name of user  |
| `password`     | `str`       | **Optional**. Password of user   |
| `email`        | `str`       | **Optional**. Email of the user  |
| `address`      | `str`       | **Optional**. Adress of the user |
**Note:** The id of the user will be retreived from the token only, unless 
    the user has admin privileges.

### Body example:
        {
            "first_name": "<name>", 
            "last_name": "<last_name>",
            "username": "<username>",
            "password": "<password>",
            "email": "<email>",
            "address": "<address>",
            "role": "<role>"
        }

#### GET all employees

```http
  method: GET
  localhost:8001/api/employees
```

#### POST employee

```http
  method: POST
  localhost:8001/api/employee
```

| Parameter  | Type     | Description                 |
| :--------  | :------- | :-------------------------  |
| `emp_name` | `string` | **Required**. Employee name |
| `emp_id`   | `int`    | **Required**. Employee id   |


### The API (Timesheet) support the following operations:
    READ: Return a json with timesheet entries.
    CREATE: Create a new timesheet entry.
#### GET all timesheet entries

```http
  method: GET
  localhost:8000/api/timesheet
```

#### POST a timesheet entry

```http
  method: POST
  localhost:8000/api/timesheet
```

| Parameter     | Type     | Description                         |
| :------------ | :------- | :---------------------------------- |
| `emp_id`      | `int`    | **Required**. Employee id           |
| `hours`       | `int`    | **Required**. Hours worked by emp   |
| `description` | `string` | **Required**. Description           |

### The timesheet API comsumps employeed API data and verifies if the employee is in the database as well as if id provided is valid.

### For installation, please create a python virtual environment and install requirements.txt.

    pip install -r requirements.txt

### Once installated and activated, run 2 simultaneous terminal and execute below.
    On terminal 1:
       Go to backend/employees_api and run:
           uvicorn main:app --reload --port 8001
    
    On terminal 2:
        Go to backend/timesheet_api and run:
            uvicorn main:app --reload --port 8000


#### If the step before was completed successfully, you must have running the server on your local host.

    In order to test the API, you can use the following URL:
            localhost:8001/docs (for the API documentation)
