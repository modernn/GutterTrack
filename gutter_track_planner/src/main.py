import flet as ft
import traceback
import sys
from views.setup_dialog import SetupDialog
from views.track_canvas import TrackCanvas
from views.toolbar import PieceToolbar
from views.bom_dialog import BOMDialog
from models.track import Track, LengthValue

class GutterTrackPlanner:
    """Main application class."""
    
    def __init__(self, page: ft.Page):
        """
        Initialize the application.
        
        Args:
            page: The Flet page
        """
        self.page = page
        self.page.title = "Gutter Track Planner"
        
        # Setup theme
        self.page.theme_mode = "light"
        self.page.padding = 0
        
        # Add initial content so we know the app is running
        self.status_text = ft.Text("Initializing Gutter Track Planner...", size=20)
        self.page.add(self.status_text)
        
        # Initialize state
        self.track = None
        self.track_canvas = None
        
        # Show setup dialog
        self.show_setup_dialog()
    
    def show_setup_dialog(self):
        """Show the initial setup dialog."""
        try:
            print("Creating setup dialog...")
            dialog = SetupDialog(on_confirmed=self.on_setup_confirmed)
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
            print("Dialog opened")
        except Exception as e:
            error_msg = f"Error showing setup dialog: {str(e)}\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)
            self.page.add(ft.Text(error_msg, color="red"))
    
    def on_setup_confirmed(self, track):
        """
        Handle setup dialog confirmation.
        
        Args:
            track: The track model
        """
        try:
            print("Setup confirmed, track received")
            self.track = track
            
            # Update status text first
            self.status_text.value = f"Track created: {track.width.feet}' {track.width.inches}\" × {track.depth.feet}' {track.depth.inches}\""
            self.page.update()
            
            # Initialize UI in two steps
            self.init_simple_ui()
            
        except Exception as e:
            error_msg = f"Error in setup confirmed: {str(e)}\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)
            self.page.add(ft.Text(error_msg, color="red"))
            self.page.update()
    
    def init_simple_ui(self):
        """Initialize a simple UI first, then transition to the full UI."""
        try:
            print("Initializing simple UI...")
            
            # Add a placeholder for the track
            placeholder = ft.Container(
                content=ft.Column([
                    ft.Text("Loading canvas...", size=16),
                    ft.ProgressBar(),
                ]),
                padding=20,
                bgcolor="#E0E0E0",
                border_radius=10,
                width=600,
                height=400,
                alignment=ft.alignment.center,
            )
            
            self.page.add(placeholder)
            self.page.update()
            
            # Schedule the full UI initialization after a brief delay
            import asyncio
            loop = asyncio.get_event_loop()
            
            def init_full_ui():
                print("Now initializing full UI...")
                self.page.clean()
                self.init_ui()
            
            # Defer full UI initialization to allow dialog to fully cleanup
            loop.call_later(0.5, init_full_ui)
            
        except Exception as e:
            error_msg = f"Error in init_simple_ui: {str(e)}\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)
            self.page.add(ft.Text(error_msg, color="red"))
            self.page.update()
    
    def init_ui(self):
        """Initialize the main UI."""
        try:
            print("Initializing full UI...")
            
            # Create track canvas
            print("Creating track canvas...")
            self.track_canvas = TrackCanvas(self.track)
            
            # Create toolbar
            print("Creating toolbar...")
            self.toolbar = PieceToolbar(on_piece_selected=self.on_piece_selected)
            
            # Set up main layout
            print("Building main layout...")
            self.page.add(
                ft.Column(
                    controls=[
                        ft.Container(
                            content=self.track_canvas,
                            expand=True,
                            margin=0,
                            padding=0,
                        ),
                        self.toolbar,
                    ],
                    spacing=0,
                    expand=True,
                )
            )
            print("UI initialized successfully")
            
        except Exception as e:
            error_msg = f"Error in init_ui: {str(e)}\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)
            self.page.add(ft.Text(error_msg, color="red"))
            self.page.update()
    
    def on_piece_selected(self, piece):
        """
        Handle piece selection from toolbar.
        
        Args:
            piece: The selected piece
        """
        try:
            # Add the piece to the track
            print(f"Adding piece of type: {piece.piece_type}")
            self.track_canvas.add_piece(piece)
        except Exception as e:
            error_msg = f"Error adding piece: {str(e)}\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)
            self.page.snack_bar = ft.SnackBar(content=ft.Text(error_msg))
            self.page.snack_bar.open = True
            self.page.update()
    
    def show_bom_dialog(self):
        """Show the BOM dialog."""
        try:
            dialog = BOMDialog(self.track)
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
        except Exception as e:
            error_msg = f"Error showing BOM dialog: {str(e)}\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)
            self.page.snack_bar = ft.SnackBar(content=ft.Text(error_msg))
            self.page.snack_bar.open = True
            self.page.update()


def main(page: ft.Page):
    """Main entry point."""
    try:
        print("Starting Gutter Track Planner...")
        app = GutterTrackPlanner(page)
    except Exception as e:
        error_msg = f"Error initializing app: {str(e)}\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr)
        page.add(ft.Text(error_msg, color="red"))
        page.update()


# Run the app
print("Launching Flet app...")
ft.app(target=main)
print("App launched")