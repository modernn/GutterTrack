import flet as ft
import traceback
import sys
from views.setup_dialog import SetupDialog
from views.track_canvas import TrackCanvas
from views.toolbar import PieceToolbar
from views.bom_dialog import BOMDialog
from models.track import Track

class GutterTrackPlanner:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Gutter Track Planner"
        self.page.theme_mode = "dark"
        
        # Add initial content
        self.status = ft.Text("Initializing Gutter Track Planner...", size=20)
        self.page.add(self.status)
        
        # Initialize state
        self.track = None
        self.track_canvas = None
        
        # Show setup dialog
        self.show_setup_dialog()
    
    def show_setup_dialog(self):
        try:
            dialog = SetupDialog(on_confirmed=self.on_setup_confirmed)
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
        except Exception as e:
            error_msg = f"Error showing setup dialog: {str(e)}\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)
            self.status.value = f"Error: {str(e)}"
            self.page.update()
    
    def on_setup_confirmed(self, track):
        try:
            self.track = track
            
            # First update the status
            self.status.value = f"Track created: {track.width.feet}' {track.width.inches}\" × {track.depth.feet}' {track.depth.inches}\""
            self.page.update()
            
            # Schedule the UI initialization after a brief delay
            import asyncio
            loop = asyncio.get_event_loop()
            
            def init_ui_delayed():
                self.init_ui()
            
            loop.call_later(0.1, init_ui_delayed)
            
        except Exception as e:
            error_msg = f"Error in setup confirmation: {str(e)}\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)
            self.status.value = f"Error: {str(e)}"
            self.page.update()
    
    def init_ui(self):
        try:
            # Clear the page
            self.page.clean()
            
            # Add title
            self.page.add(ft.Text("Gutter Track Planner", size=24, text_align="center"))
            
            # Create track info
            track_info = ft.Container(
                content=ft.Column([
                    ft.Text(f"Track dimensions:", size=16, weight="bold"),
                    ft.Text(f"Width: {self.track.width.feet}' {self.track.width.inches}\" ({self.track.width.total_inches} inches)"),
                    ft.Text(f"Depth: {self.track.depth.feet}' {self.track.depth.inches}\" ({self.track.depth.total_inches} inches)"),
                    ft.Text(f"Lane Width: {self.track.lane_width.feet}' {self.track.lane_width.inches}\" ({self.track.lane_width.total_inches} inches)"),
                ]),
                bgcolor="#1E1E1E",
                border_radius=10,
                padding=10,
            )
            self.page.add(track_info)
            
            # Create track canvas
            self.track_canvas = TrackCanvas(self.track)
            
            # Create toolbar
            self.toolbar = PieceToolbar(on_piece_selected=self.on_piece_selected)
            
            # Add main components
            self.page.add(
                self.track_canvas,
                self.toolbar,
            )
            
            # Add BOM button
            bom_button = ft.ElevatedButton(
                text="Bill of Materials",
                on_click=lambda e: self.show_bom_dialog()
            )
            self.page.add(bom_button)
            
            # Add status text
            self.status = ft.Text("Track editor ready")
            self.page.add(self.status)
            
            self.page.update()
            
        except Exception as e:
            error_msg = f"Error initializing UI: {str(e)}\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)
            self.page.add(ft.Text(error_msg, color="red"))
            self.page.update()
    
    def on_piece_selected(self, piece):
        try:
            # Add the piece to the track
            self.track_canvas.add_piece(piece)
        except Exception as e:
            error_msg = f"Error adding piece: {str(e)}"
            print(error_msg, file=sys.stderr)
            self.status.value = f"Error: {str(e)}"
            self.page.update()
    
    def show_bom_dialog(self):
        try:
            dialog = BOMDialog(self.track)
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
        except Exception as e:
            error_msg = f"Error showing BOM dialog: {str(e)}"
            print(error_msg, file=sys.stderr)
            self.status.value = f"Error: {str(e)}"
            self.page.update()