from . import (
    filesystem,
    system,
    shell,
    python_tool,
    apps,
    web,
    email,
    github,
    project,
    network,
)


def register_all(registry):

    for module in (
        filesystem,
        system,
        shell,
        python_tool,
        apps,
        web,
        email,
        github,
        project,
        network,
    ):
        module.register(registry)