# Protocol (JSON line)

Giao tiếp giữa client & server dùng JSON, mỗi message là 1 dòng (`\n`).

## Message types

### Client -> Server

- `HELLO`
```json
{"type":"HELLO","name":"player1","token":null}
```

- `MOVE`
```json
{"type":"MOVE","choice":"rock"}
```

- `PING`
```json
{"type":"PING"}
```

### Server -> Client

- `WELCOME`
```json
{"type":"WELCOME","token":"<reconnect-token>","message":"ok"}
```

- `MATCH_FOUND`
```json
{"type":"MATCH_FOUND","opponent":"player2","best_of":3}
```

- `ROUND_START`
```json
{"type":"ROUND_START","round":1,"scores":{"you":0,"opponent":0}}
```

- `ROUND_RESULT`
```json
{"type":"ROUND_RESULT","round":1,"you":"rock","opponent":"scissors","winner":"you"}
```

- `MATCH_RESULT`
```json
{"type":"MATCH_RESULT","winner":"you","scores":{"you":2,"opponent":1}}
```

- `OPPONENT_LEFT`
```json
{"type":"OPPONENT_LEFT","message":"Opponent disconnected"}
```

- `ERROR`
```json
{"type":"ERROR","message":"..."}
```

## Reconnect
- Client gửi lại `HELLO` kèm `token` cũ.
- Server giữ trạng thái 30s, quá hạn sẽ xử thua.