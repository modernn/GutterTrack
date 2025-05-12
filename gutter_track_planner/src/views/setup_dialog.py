import flet as ft
import traceback
import sys
from models.track import LengthValue, Track

class FeetInchesInput(ft.Row):
    """Custom input for feet and inches."""
    
    def __init__(self, label, on_change=None, default_feet=0, default_inches=0):
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
        
        super().__init__(
            controls=[
                ft.Text(label, width=100),
                self.feet_field,
                ft.Text("feet"),
                self.inches_field,
                ft.Text("inches"),
            ],
            alignment="start",
        )
    
    def _on_field_change(self, e):
        """Handle changes to the feet/inches fields."""
        if self.on_change_callback:
            self.on_change_callback(self.value)
    
    @property
    def value(self):
        """Get the current value as a LengthValue."""
        try:
            feet = int(self.feet_field.value or 0)
            inches = float(self.inches_field.value or 0)
            return LengthValue(feet, inches)
        except ValueError:
            return LengthValue(0, 0)


class SetupDialog(ft.AlertDialog):
    """Initial setup dialog for track dimensions."""
    
    def __init__(self, on_confirmed):
        # Set reasonable defaults
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
        """Handle cancel button click."""
        print("Cancel clicked")
        self.open = False
        self.update()
    
    def _on_confirm(self, e):
        """Handle confirm button click."""
        try:
            print("Confirm clicked")
            
            # Validate inputs
            width = self.width_input.value
            print(f"Width: {width.feet}' {width.inches}\"")
            
            depth = self.depth_input.value
            print(f"Depth: {depth.feet}' {depth.inches}\"")
            
            lane_width = self.lane_width_input.value
            print(f"Lane Width: {lane_width.feet}' {lane_width.inches}\"")
            
            # Ensure lane width is at least 2 inches
            if lane_width.total_inches < 2:
                print("Lane width too small, setting to 2 inches")
                lane_width = LengthValue(0, 2)
            
            # Create track model
            print("Creating track model")
            track = Track(width, depth, lane_width)
            
            # Store track and callback locally before closing dialog
            callback = self.on_confirmed_callback
            track_model = track
            
            # Close dialog FIRST
            print("Closing dialog")
            self.open = False
            self.update()
            
            # Use a simple function to defer the callback execution
            def do_callback():
                print("Executing callback")
                if callback:
                    callback(track_model)
            
            # Defer execution to allow dialog to fully close
            import asyncio
            loop = asyncio.get_event_loop()
            loop.call_soon(do_callback)
            
        except Exception as e:
            error_msg = f"Error in dialog confirm: {str(e)}\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)