from enum import Enum


class ConnectionState(str, Enum):
    CONNECTED = "connected"
    CONNECTION_LOST = "connection_lost"
    RECONNECT_AVAILABLE = "reconnect_available"
    RECONNECTING = "reconnecting"
    LOADING = "loading"
    RECOVERING_STATE = "recovering_state"
    READY = "ready"
    UNKNOWN = "unknown"
