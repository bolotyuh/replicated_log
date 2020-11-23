# Master

## Commands
[POST] Append message
[GET] List messages

## Config file
./config.yml
```yaml
host: 0.0.0.0
port: 9090
secondaries:
    -
      url: 'ws://secondary.1:9000/ws-append-msg'
      name: 'secondary 1'
    -
      url: 'ws://secondary.2:9000/ws-append-msg'
      name: 'secondary 2'
```