
# App API


# Setup
1. Clone the project
2. Run the following commands
```sh
py -m venv .venv
```
```sh
.venv\Scripts\activate
```
```sh
pip install -r requirements.txt
```
```sh
flask db init
```

# Important
if you change any information in Database classes you have to run the following commands

```sh
flask db migrate -m "commit-message"
```
```sh
flask db upgrade
```

if you have any extra tables you can remove them manually
or if you want to drop all tables run the following command:
```sh
flask reset-db
```





