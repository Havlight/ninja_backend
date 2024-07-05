from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI(
    title="grad project",
    description="還不快做事",
    urls_namespace="api",
)
api.auto_discover_controllers()