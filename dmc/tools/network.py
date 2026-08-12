import platform
import socket

from ..models import Tool


def register(registry):

    def local_network_info():

        hostname = socket.gethostname()

        addresses = []

        try:

            infos = socket.getaddrinfo(
                hostname,
                None,
                family=socket.AF_INET,
            )

            for info in infos:

                address = info[4][0]

                if address not in addresses:
                    addresses.append(address)

        except OSError:
            pass

        return (
            f"HOSTNAME: {hostname}\n"
            f"OS: {platform.system()}\n"
            f"LOCAL IPV4 ADDRESSES:\n"
            + "\n".join(
                f"- {address}"
                for address in addresses
            )
        )

    def check_port(port, host="127.0.0.1"):

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        sock.settimeout(1.5)

        try:

            is_open = (
                sock.connect_ex(
                    (host, int(port))
                )
                == 0
            )

            return (
                f"{host}:{port} "
                f"OPEN={is_open}"
            )

        finally:
            sock.close()

    registry.register(
        Tool(
            "local_network_info",
            "Find this computer's hostname and local IPv4 addresses.",
            {
                "type": "object",
                "properties": {},
            },
            local_network_info,
        )
    )

    registry.register(
        Tool(
            "check_port",
            "Check whether a TCP port accepts connections.",
            {
                "type": "object",
                "properties": {
                    "port": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 65535,
                    },
                    "host": {
                        "type": "string"
                    },
                },
                "required": ["port"],
            },
            check_port,
        )
    )