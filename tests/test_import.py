def test_import():
    import dmc
    from dmc.tool_registry import ToolRegistry
    from dmc.tools import register_all
    registry = ToolRegistry()
    register_all(registry)
    assert registry.get("system_info")
    assert registry.get("web_search")
