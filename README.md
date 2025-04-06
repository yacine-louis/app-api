# app-api
# Setup
1. Clone the project
2. Run the following commands
```sh
cd ./app-api
```
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
pip install mysqlclient
```
```sh
flask db init
```
```sh
python app.py
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
<h3>If you added any extra tables(Classes) you have to remove them manually!</h3>
