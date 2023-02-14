from sqladmin import Admin, ModelView

from .views import StationsView, ServicesView, StationServicesView, FuelsView, StationFuelsView

__all__ = (
    'AdminManager'
)


class AdminManager(Admin):
    # Список вьюшек для регистрации
    reg_views_list = [
        StationsView,
        ServicesView,
        StationServicesView,
        FuelsView,
        StationFuelsView,
    ]

    def reg_views(self):
        for view in self.reg_views_list:
            self.add_view(view)
