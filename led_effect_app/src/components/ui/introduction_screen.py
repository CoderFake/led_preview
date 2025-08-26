import flet as ft
import asyncio
from typing import Callable, Optional


class LoadingDots(ft.Container):
    def __init__(self):
        super().__init__()
        self.dots = [
            ft.Container(width=14, height=14, border_radius=14, bgcolor=ft.Colors.BLUE_600, opacity=0.9,
                         scale=ft.Scale(0.7), animate_scale=ft.Animation(250, ft.AnimationCurve.EASE_IN_OUT)),
            ft.Container(width=14, height=14, border_radius=14, bgcolor=ft.Colors.PURPLE_600, opacity=0.9,
                         scale=ft.Scale(0.7), animate_scale=ft.Animation(250, ft.AnimationCurve.EASE_IN_OUT)),
            ft.Container(width=14, height=14, border_radius=14, bgcolor=ft.Colors.PINK_600, opacity=0.9,
                         scale=ft.Scale(0.7), animate_scale=ft.Animation(250, ft.AnimationCurve.EASE_IN_OUT)),
            ft.Container(width=14, height=14, border_radius=14, bgcolor=ft.Colors.YELLOW_600, opacity=0.9,
                         scale=ft.Scale(0.7), animate_scale=ft.Animation(250, ft.AnimationCurve.EASE_IN_OUT)),
        ]
        self.content = ft.Row(self.dots, spacing=10, alignment=ft.MainAxisAlignment.CENTER)
        self.opacity = 0.0
        self.animate_opacity = ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT)

    async def pulse(self, page: ft.Page, cycles: int = 6, interval: float = 0.18):
        for _ in range(cycles):
            for i, d in enumerate(self.dots):
                d.scale = ft.Scale(1.0)
                page.update()
                await asyncio.sleep(interval)
                d.scale = ft.Scale(0.7)
                page.update()


class IntroductionScreen(ft.Container):
    def __init__(self, page: ft.Page, on_complete: Optional[Callable] = None):
        super().__init__()
        self.page = page
        self.on_complete = on_complete

        self.expand = True
        self.bgcolor = ft.Colors.WHITE
        self.alignment = ft.alignment.center

        self.logo_container = None
        self.title_wrapper = None
        self.title_text = None
        self.loading_dots = None

        self.content = self.build_content()

    def build_content(self):
        logo_content = ft.Image(
            src="yamaha.png", 
            fit=ft.ImageFit.CONTAIN,
            repeat=ft.ImageRepeat.NO_REPEAT,
            error_content=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.LIGHTBULB, size=200, color=ft.Colors.BLUE_600),
                    ft.Text(
                        "YAMAHA",
                        size=80,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_600,
                        text_align=ft.TextAlign.CENTER
                    )
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20),
                alignment=ft.alignment.center,
                expand=True,
                border_radius=0,
                bgcolor=ft.Colors.GREY_50,
            ),
        )

        self.logo_container = ft.Container(
            content=logo_content,
            opacity=1.0,
            animate_opacity=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT),
            alignment=ft.alignment.center,
            expand=True,
        )

        self.title_text = ft.ShaderMask(
            content=ft.Text(
                "LIGHT PATTERN DESIGNER",
                size=80,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
                color=ft.Colors.WHITE,
            ),
            shader=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.Colors.BLUE_600, ft.Colors.PURPLE_600, ft.Colors.PINK_600, ft.Colors.ORANGE_600],
                stops=[0.0, 0.3, 0.7, 1.0],
            ),
            blend_mode=ft.BlendMode.SRC_IN,
        )

        self.title_wrapper = ft.Container(
            content=self.title_text,
            opacity=0.0,
            animate_opacity=ft.Animation(800, ft.AnimationCurve.EASE_IN_OUT),
            offset=ft.Offset(0, 0),
            animate_offset=ft.Animation(350, ft.AnimationCurve.EASE_OUT),
        )

        self.loading_dots = LoadingDots()

        return ft.Container(
            content=ft.Stack(
                controls=[
                    self.logo_container,
                    
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(expand=True),
                                self.title_wrapper,
                                ft.Container(width=10),
                                self.loading_dots,
                                ft.Container(expand=True),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        top=0,
                        bottom=0,
                        left=0,
                        right=0,
                        alignment=ft.alignment.center,
                    ),
                ],
                expand=True,
            ),
            expand=True,
            alignment=ft.alignment.center,
        )

    async def start_animation_sequence(self):
        await asyncio.sleep(0.5)
        await self._fade_out_logo()
        await self._fade_in_title()
        await self._nudge_title_left()
        await self._show_loading()
        await self._complete_intro()

    async def _fade_out_logo(self):
        try:
            self.logo_container.opacity = 0.0
            self.page.update()
            await asyncio.sleep(1.0)
        except Exception as e:
            print(f"Error in fade out logo: {e}")

    async def _fade_in_title(self):
        try:
            await asyncio.sleep(0.1)
            self.title_wrapper.opacity = 1.0
            self.page.update()
            await asyncio.sleep(0.8)
        except Exception as e:
            print(f"Error in fade in title: {e}")

    async def _nudge_title_left(self):
        try:
            self.title_wrapper.offset = ft.Offset(-0.03, 0)  
            self.page.update()
            await asyncio.sleep(0.35)
        except Exception as e:
            print(f"Error in nudge title: {e}")

    async def _show_loading(self):
        try:
            self.loading_dots.opacity = 1.0
            self.page.update()
            await self.loading_dots.pulse(self.page, cycles=6, interval=0.18)
        except Exception as e:
            print(f"Error in show loading: {e}")

    async def _complete_intro(self):
        try:
            self.title_wrapper.opacity = 0.0
            self.loading_dots.opacity = 0.0
            self.page.update()
            await asyncio.sleep(0.4)

            if self.on_complete:
                self.on_complete()
        except Exception as e:
            print(f"Error in complete intro: {e}")

    def set_custom_gradient_colors(self, colors: list, stops: list = None):
        if stops is None:
            stops = [i / (len(colors) - 1) for i in range(len(colors))]
        self.title_text.shader = ft.LinearGradient(
            begin=ft.alignment.top_left, end=ft.alignment.bottom_right, colors=colors, stops=stops
        )
        self.page.update()

    def set_logo_frame_size(self, width: int, height: int):
        """Set custom size for logo container - now affects full screen"""
        if hasattr(self.logo_container.content, 'fit'):
            if width and height:
                self.logo_container.content.fit = ft.ImageFit.FILL
            else:
                self.logo_container.content.fit = ft.ImageFit.CONTAIN
        self.page.update()

    def set_logo_fit_mode(self, fit_mode: ft.ImageFit):
        self.logo_container.content.fit = fit_mode
        self.page.update()


class IntroductionManager:
    def __init__(self, page: ft.Page):
        self.page = page
        self.intro_screen = None
        self.main_app = None

    async def show_introduction(self, main_app_factory):
        self.intro_screen = IntroductionScreen(
            self.page, on_complete=lambda: self._transition_to_main_app(main_app_factory)
        )
        self.page.controls.clear()
        self.page.add(self.intro_screen)
        self.page.update()
        await self.intro_screen.start_animation_sequence()

    def _transition_to_main_app(self, main_app_factory):
        async def _do_transition():
            self.main_app = main_app_factory()

            self.intro_screen.animate_opacity = ft.Animation(500, ft.AnimationCurve.EASE_OUT)
            self.intro_screen.opacity = 0.0
            self.page.update()
            await asyncio.sleep(0.5)

            self.page.controls.clear()
            self.page.add(self.main_app)

            self.main_app.opacity = 0.0
            self.main_app.animate_opacity = ft.Animation(500, ft.AnimationCurve.EASE_IN)
            self.page.update()

            await asyncio.sleep(0.1)
            self.main_app.opacity = 1.0
            self.page.update()

        self.page.run_task(_do_transition)