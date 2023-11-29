"""Module to talk to other processes using json-rpc over async sockets."""

from .dispatcher import JSONRPCDispatcher, Dispatcher, ipc_expose
from .manager import JSONRPCResponseManager
from .messenger import IPCMessenger
from .types import (
    IPCProcess,
    SOCKET_PATHNAMES,
    JSONRPCRequest,
    JSONRPCResponse,
)
from .errors import (
    JSONRPCError,
    ErrorCodes,
)


ipc_dispatcher = JSONRPCDispatcher()


__all__ = [
    "Dispatcher",
    "ipc_dispatcher",
    "JSONRPCDispatcher",
    "JSONRPCResponseManager",
    "IPCMessenger",
    "IPCProcess",
    "SOCKET_PATHNAMES",
    "JSONRPCRequest",
    "JSONRPCResponse",
    "JSONRPCError",
    "ErrorCodes",
]
