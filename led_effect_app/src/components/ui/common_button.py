import flet as ft

class CommonBtn:
    def __init__(self):
        self.configs = {
            "add": {
                "icon": ft.Icons.ADD,
                "border_color": ft.Colors.PRIMARY
            },
            "remove": {
                "icon": ft.Icons.REMOVE,
                "border_color": ft.Colors.RED    
            },
            "copy": {
                "icon": ft.Icons.COPY,
                "border_color": ft.Colors.GREEN
            }
        }

    def get_buttons(self, *args):

        keys = ["add", "remove", "copy"]
        buttons = []

        for i, (tooltip, on_click) in enumerate(args):
            cfg = self.configs[keys[i]]
            btn = ft.Container(
                content=ft.IconButton(
                    icon=cfg["icon"],
                    icon_color=ft.Colors.BLACK,
                    tooltip=tooltip,
                    on_click=on_click
                ),
                border=ft.border.all(1, cfg["border_color"]),
                border_radius=8,
                padding=5
            )
            buttons.append(btn)

        return ft.Row(buttons, tight=True)

common_btn = CommonBtn()