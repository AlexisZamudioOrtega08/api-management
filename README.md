# API-MANAGEMENT
API for user api keys management.

### The API contains three main group of endpoints and two levels of administration (default user and admin).

### The main group of endpoints are:

  - AUTH
  - USERS
  - BILLINGS
  - KEYS

# AUTH 
#### If a user is already registeres you can provide your credential and login, otherwise you must register yourself <link to post user>.
## Supported endpoints:  
### LOGIN 
```method: POST host:5000/api/v1/login```

| Body           | Type        | Description                                  |
| ------------  | :---------- | :------------------------------------------- |
| `identifier`   | `str`       | **Required**. username or email of the user  |
| `password`     | `str`       | **Required**. Password of the user           |

#### **Notes**
- The authentication of a user is done using the JWT token and storing the following information in the encoded token: `id`, `username`, `verified`, `role`.

- The token is stored in cookies and is sent in the header of each request. 
- The token is valid for 30 minutes and is refreshed on every endpoint call.


### LOGOUT
```method: POST host:5000/api/v1/logout```
#### **Notes**    
- This endpoint needs to parse the jwt token in the request as cookie to expire the token.

# Users

## Supported endpoints.

### GET
**Accessible: Registered Users**

```method: GET host:5000/api/v1/users```

**Note:** In order to allow to this endpoint you need to be logged in and the user info will be retreived from user info.

### POST
**Accessible: All**

```method: POST host:5000/api/v1/users```

| Body Parameters| Type        | Description                      |
| :------------  | :---------- | :------------------------------  |
| `first_name`   | `str`       | **Required**. First name of user |
| `last_name`    | `str`       | **Required**. Last name of user  |
| `username`     | `str`       | **Required**. Username of user   | 
| `password`     | `str`       | **Required**. Password of user   |
| `email`        | `str`       | **Required**. Email of the user  |
| `address`      | `str`       | **Required**. Adress of the user |

Body example:

        {
            "first_name": "<name>", 
            "last_name": "<last_name>",
            "username": "<username>", **Alphanumeric only** **Unmuttable**
            "password": "<password>", **Must have at least one character of the following [A-Z][a-z][0-9][@$!%*#?&]**
            "email": "<email>", **Must be a valid email**
            "address": "<address>" **Full address**
        }
                            
**Note:** Must be application/json.

### PUT
**Accessible: Registered users and admins**

```method: PUT host:5000/api/v1/users```

Default users are allowed to update the following parameters:

| Body Params    | Type        | Description                       |
| :------------  | :---------- | :-------------------------------  |
| `first_name`   | `str`       | **Optional**. First name of user. |
| `last_name`    | `str`       | **Optional**. Last name of user.  |
| `password`     | `str`       | **Optional**. Password of user.   |
| `email`        | `str`       | **Optional**. Email of the user.  |
| `address`      | `str`       | **Optional**. Adress of the user. |

**Note:** The id of the user will be retreived from the 
token only.

In the other side **admin users** are allowed to modify the following parameters:

| Body Params    | Type        | Description                        |
| :------------  | :---------- | :------------------------------------------------------------- |
| `identifier`   | `str`       | **Required**. Identifier of user `username` or `email` or `id`.|
| `first_name`   | `str`       | **Optional**. First name of user.   |
| `last_name`    | `str`       | **Optional**. Last name of user.    |
| `password`     | `str`       | **Optional**. Password of user.     |
| `email`        | `str`       | **Optional**. Email of the user.    |
| `address`      | `str`       | **Optional**. Adress of the user.   |
| `role`         | `int`       | **Optional**. Adress of the user.   |

### DELETE
**Accessible: Admins**

```method: DELETE host:5000/api/v1/users```

| Query parameters   | Type        | Description                             |
| :----------------- | :---------- | :-------------------------------------- |
| `id`               | `str`       | **Required**. Id of user to be deleted. |

#### Requests examples:

  - ```host:5000/api/v1/users?id=XXXX```

# Billings

## Supported endpoints.

### GET
**Accessible: Registered Users**

```method: GET host:5000/api/v1/billings```

**Note:** In order to allow to this endpoint you need to be logged in and the user info will be retreived from user info.

### POST
**Accessible: Admins**

```method: POST host:5000/api/v1/billings```

| Body Parameters        | Type        | Description                                       |
| :--------------------  | :---------- | :------------------------------------------------ |
| `user_id`              | `str`       | **Required**. Id of the user.                     |
| `balance`              | `float`     | **Not Required**. Initial balance, defualt = 100. |
| `billing_address`      | `str`       | **Not Required**. Billing address.                |


Body example:

        {
            "user_id": "<user_id>", 
            "balance": "<charge to be added to current balance>",
            "billing_address": "<billing address if diferent from address on user record>"
        }
                            
**Note:** Must be application/json.

### PUT
**Accessible: Admins**

```method: PUT host:5000/api/v1/billings```

| Body Parameters        | Type        | Description                                       |
| :--------------------  | :---------- | :------------------------------------------------ |
| `user_id`              | `str`       | **Required**. Id of the user to be linked.        |
| `balance`              | `float`     | **Not Required**. Initial balance, defualt = 100. |
| `billing_address`      | `str`       | **Not Required**. Billing address.                |


### DELETE
**Accessible: Admins**

```method: DELETE host:5000/api/v1/billings```

| Query parameters   | Type        | Description                             |
| :----------------- | :---------- | :-------------------------------------- |
| `id`               | `str`       | **Required**. Id of user to be deleted. |

#### Requests examples:

  - ```host:5000/api/v1/billings?id=XXXX```


## Filters available for **admin users**.

### GET  -> User endpoint.

```method: POST host:5000/api/v1/users/<string:filter_by>```

| URL parameters     | Type        | Description                                                                                                 |
| :----------------- | :---------- | :---------------------------------------------------------------------------------------------------------  |
| `filter_by`        | `str`       | **Required.** Only one of the following must be provides: `id`, `username`, `email`, `date`, `role`, `all`. |

| Query parme   | Type        | Description                                                                                 |
| :----------------- | :---------- | :--------------------------------------------------------------------------------------|
| `value`            | `str`       | **Required.**. The value must be provided depending on filter_by parameter.            |
| `limit`            | `int`       | **Not Required.** Limit of elementes you want to bring on your request, default = 10.  |
| `page`             | `int`       | **Not Required.** Number of the page you want to bring on your request, default = 1.   |


### GET  -> Billing endpoint.

```method: POST host:5000/api/v1/billings/<string:filter_by>```

| URL parameters     | Type        | Description                                                                                |
| :----------------- | :---------- | :------------------------------------------------------------------------------------------|
| `filter_by`        | `str`       | **Required.** Only one of the following must be provides: `id`, `user_id`, `date`, `all`.  |

| Query parme   | Type        | Description                                                                                 |
| :----------------- | :---------- | :--------------------------------------------------------------------------------------|
| `value`            | `str`       | **Required.**. The value must be provided depending on filter_by parameter.            |
| `limit`            | `int`       | **Not Required.** Limit of elementes you want to bring on your request, default = 10.  |
| `page`             | `int`       | **Not Required.** Number of the page you want to bring on your request, default = 1.   |

### GET  -> Key endpoint.

```method: POST host:5000/api/v1/keys/<string:filter_by>```

| URL parameters     | Type        | Description                                                                                   |
| :----------------- | :---------- | :-------------------------------------------------------------------------------------------- |
| `filter_by`        | `str`       | **Required.** Only one of the following must be provides: `id`, `billing_id`, `date`, `all`.  |

| Query parme   | Type        | Description                                                                                 |
| :----------------- | :---------- | :--------------------------------------------------------------------------------------|
| `value`            | `str`       | **Required.**. The value must be provided depending on filter_by parameter.            |
| `limit`            | `int`       | **Not Required.** Limit of elementes you want to bring on your request, default = 10.  |
| `page`             | `int`       | **Not Required.** Number of the page you want to bring on your request, default = 1.   |


#### Requests examples:

  - ```host:5000/api/v1/<route>/username?value=TestUS20```
  - ```host:5000/api/v1/<route>/id?value=1200```
  - ```host:5000/api/v1/<route>/date?value=YYYY-MM-DD&page=3```
  - ```host:5000/api/v1/<route>/email?value=test@gmail.com```
  - ```host:5000/api/v1/<route>/role?value=2```
  - ```host:5000/api/v1/<route>/all?page=2&limit=8```


## Author
- [X] [@alexiszamudio](https://github.com/AlexisZamudioOrtega08)
