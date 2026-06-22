# game_aggregation.md Verification

[https://github.com/hex-drift/backbone/blob/main/docs/game_aggregation.md](https://github.com/hex-drift/backbone/blob/main/docs/game_aggregation.md)

status:

INACCURATE

now:

- Idempotency keys are optional on money endpoints because the aggregation layer resolves duplicate credits automatically.

to be:

- Idempotency keys are mandatory on all money endpoints to prevent duplicate credits from provider retries; the aggregation layer does not automatically resolve duplicates without them.