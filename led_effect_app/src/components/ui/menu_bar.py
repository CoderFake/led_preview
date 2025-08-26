import flet as ft
from .menu_bar_action import MenuBarActionHandler


class MenuBarComponent(ft.Container):
    """Cross-platform file menu bar component"""

    def __init__(self, page: ft.Page, file_service=None, data_action_handler=None):
        super().__init__()
        self.page = page
        self.action_handler = MenuBarActionHandler(page, file_service, data_action_handler)
        self.expand = False
        self.height = 40
        self.bgcolor = ft.Colors.GREY_50
        self.border = ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_400))
        self.content = self._build_default_menu()

    # ===== UI builders =====

    def _build_default_menu(self) -> ft.Control:
        """Default horizontal menubar."""
        return ft.Row(
            controls=[
                ft.MenuBar(
                    controls=[
                        ft.SubmenuButton(
                            content=ft.Container(
                                content=ft.Text("File", size=14),
                                padding=ft.padding.symmetric(horizontal=20, vertical=8),
                            ),
                            leading=ft.Icon(ft.Icons.FOLDER, size=18),
                            style=ft.ButtonStyle(
                                elevation={
                                    ft.ControlState.DEFAULT: 0,
                                    ft.ControlState.HOVERED: 0,
                                    ft.ControlState.FOCUSED: 0,
                                    ft.ControlState.PRESSED: 0,
                                },
                                shadow_color=ft.Colors.TRANSPARENT,
                                surface_tint_color=ft.Colors.TRANSPARENT,
                                bgcolor={
                                    ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
                                    ft.ControlState.HOVERED: ft.Colors.WHITE,
                                    ft.ControlState.FOCUSED: ft.Colors.TRANSPARENT,
                                },
                                color={
                                    ft.ControlState.DEFAULT: ft.Colors.BLACK,
                                    ft.ControlState.HOVERED: ft.Colors.BLACK,
                                    ft.ControlState.FOCUSED: ft.Colors.BLACK,
                                },
                                side={
                                    ft.ControlState.DEFAULT: ft.BorderSide(0, ft.Colors.TRANSPARENT),
                                    ft.ControlState.HOVERED: ft.BorderSide(0, ft.Colors.TRANSPARENT),
                                    ft.ControlState.FOCUSED: ft.BorderSide(0, ft.Colors.TRANSPARENT),
                                },
                                overlay_color=ft.Colors.TRANSPARENT,
                                shape=ft.RoundedRectangleBorder(radius=0),
                                padding=ft.padding.all(0),
                            ),
                            controls=self._build_file_menu_items(),
                        ),
                    ]
                ),
                ft.Container(expand=True),
                ft.Text(
                    self.action_handler.get_platform_info(),
                    size=12,
                    color=ft.Colors.GREY_600,
                ),
                ft.Container(width=20),
            ],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _build_file_menu_items(self) -> list[ft.Control]:
        return [
            ft.MenuItemButton(
                content=ft.Text("Open...", size=14),
                leading=ft.Icon(ft.Icons.FOLDER_OPEN, size=18),
                on_click=self.action_handler.handle_open_file,
            ),
            ft.MenuItemButton(
                content=ft.Text("Save", size=14),
                leading=ft.Icon(ft.Icons.SAVE, size=18),
                on_click=self.action_handler.handle_save_file,
            ),
            ft.MenuItemButton(
                content=ft.Text("Save as...", size=14),
                leading=ft.Icon(ft.Icons.SAVE_AS, size=18),
                on_click=self.action_handler.handle_save_as_file,
            ),
        ]

    # ===== API =====

    def get_file_status(self) -> str:
        data = self.action_handler.get_file_status_data()
        return data["display_name"]
