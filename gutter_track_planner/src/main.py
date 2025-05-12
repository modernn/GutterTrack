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
        self.page.theme_mode = "light"  # Changed from ft.ThemeMode.LIGHT
        self.page.padding = 0
        
        # Add initial content so we know the app is running
        self.page.add(ft.Text("Initializing Gutter Track Planner...", size=20))
        
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
            print("Setup confirmed, initializing UI...")
            self.track = track
            self.init_ui()
        except Exception as e:
            error_msg = f"Error initializing UI: {str(e)}\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)
            self.page.add(ft.Text(error_msg, color="red"))
    
    def init_ui(self):
        """Initialize the main UI."""
        try:
            # Clear the initialization message
            self.page.clean()
            
            # Create track canvas
            print("Creating track canvas...")
            self.track_canvas = TrackCanvas(self.track)
            
            # Create toolbar
            print("Creating toolbar...")
            self.toolbar = PieceToolbar(on_piece_selected=self.on_piece_selected)
            
            # Set up main layout
            print("Building layout...")
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
    
    def on_piece_selected(self, piece):
        """
        Handle piece selection from toolbar.
        
        Args:
            piece: The selected piece
        """
        try:
            # Add the piece to the track
            self.track_canvas.add_piece(piece)
        except Exception as e:
            error_msg = f"Error adding piece: {str(e)}"
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
            error_msg = f"Error showing BOM dialog: {str(e)}"
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


# Run the app
print("Launching Flet app...")
ft.app(target=main)
print("App launched")