# Replicated log

## Run container
```bash
$ docker-compose up build -d
```

## Available methods

### Master
* [POST] Append message
* [GET] List messages

### Secondary
* [GET] List messages


## Example of usage api

### MASTER

**Append message**
```bash
curl --location --request POST 'http://127.0.0.1:9090/append-msg' \
--header 'Content-Type: application/json' \
--data-raw '{"message":"some text"}'
```

**List messages**
```bash
curl --request GET 'http://127.0.0.1:9090/list-msg'
```

### SECONDARY
**List messages**
```bash
curl --request GET 'http://127.0.0.1:9001/list-msg'
```

