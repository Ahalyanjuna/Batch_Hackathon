POST /tickets
    ↓
Send task to Redis
    ↓
Return 202 immediately
    ↓
Background worker consumes task
    ↓
Calls ML
    ↓
Stores result