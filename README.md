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
# Note
<h3>If you have any extra tables(Classes) you have to remove them manually!</h3>