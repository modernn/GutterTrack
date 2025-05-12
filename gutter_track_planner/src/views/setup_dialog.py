import flet as ft
import traceback
import sys
from models.track import LengthValue, Track

class FeetInchesInput(ft.Row):
    def _get_control_name(self):
        return "feet-inches-input"
    
    def __init__(self, label, on_change=None, default_feet=0, default_inches=0):
        super().__init__()
        
        self.feet_field = ft.TextField(
            label="Feet",
            width=80,
            keyboard_type="number",
            value=str(default_feet),
        )
        self.inches_field = ft.TextField(
            label="Inches",
            width=80,
            keyboard_type="number",
            value=str(default_inches),
        )
        
        self.on_change_callback = on_change
        
        # Connect change events
        self.feet_field.on_change = self._on_field_change
        self.inches_field.on_change = self._on_field_change
        
        # Set controls
        self.controls = [
            ft.Text(label, width=100),
            self.feet_field,
            ft.Text("feet"),
            self.inches_field,
            ft.Text("inches"),
        ]
        self.alignment = "start"
    
    def _on_field_change(self, e):
        if self.on_change_callback:
            self.on_change_callback(self.value)
    
    @property
    def value(self):
        try:
            feet = int(self.feet_field.value or 0)
            inches = float(self.inches_field.value or 0)
            return LengthValue(feet, inches)
        except ValueError:
            return LengthValue(0, 0)


class SetupDialog(ft.AlertDialog):
    def _get_control_name(self):
        return "setup-dialog"
    
    def __init__(self, on_confirmed):
        # Create fields with default values
        self.width_input = FeetInchesInput("Width:", default_feet=4, default_inches=0)
        self.depth_input = FeetInchesInput("Depth:", default_feet=8, default_inches=0)
        self.lane_width_input = FeetInchesInput("Lane Width:", default_feet=0, default_inches=2)
        
        self.on_confirmed_callback = on_confirmed
        
        super().__init__(
            title=ft.Text("Track Dimensions"),
            content=ft.Column(
                controls=[
                    ft.Text("Enter the track dimensions:"),
                    self.width_input,
                    self.depth_input,
                    self.lane_width_input,
                ],
                width=400,
                height=200,
                scroll="auto",
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self._on_cancel),
                ft.TextButton("Confirm", on_click=self._on_confirm),
            ],
            actions_alignment="end",
        )
    
    def _on_cancel(self, e):
        self.open = False
        self.update()
    
    def _on_confirm(self, e):
        # Get values
        width = self.width_input.value
        depth = self.depth_input.value
        lane_width = self.lane_width_input.value
        
        # Create track
        track = Track(width, depth, lane_width)
        
        # Store callback for execution after dialog closes
        callback = self.on_confirmed_callback
        track_obj = track
        
        # Close dialog first
        self.open = False
        self.update()
        
        # Use deferred execution for callback
        def do_callback():
            if callback:
                callback(track_obj)
        
        # Schedule callback after dialog closes
        import asyncio
        loop = asyncio.get_event_loop()
        loop.call_soon(do_callback)