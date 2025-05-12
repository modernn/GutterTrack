import flet as ft
import traceback
import sys
from models.track import Track, LengthValue
from views.track_canvas import TrackCanvas
from views.toolbar import PieceToolbar

def main(page: ft.Page):
    """Main entry point with simplified form approach."""
    try:
        page.title = "Gutter Track Planner"
        page.theme_mode = "light"
        
        # Default track dimensions
        width_ft = 4
        width_in = 0
        depth_ft = 8
        depth_in = 0
        lane_ft = 0
        lane_in = 2
        
        # Status message
        status_text = ft.Text("Enter track dimensions and click Create", size=16)
        
        # Create input fields
        width_ft_field = ft.TextField(
            label="Width (feet)",
            value=str(width_ft),
            width=100,
            keyboard_type="number",
        )
        
        width_in_field = ft.TextField(
            label="Width (inches)",
            value=str(width_in),
            width=100,
            keyboard_type="number",
        )
        
        depth_ft_field = ft.TextField(
            label="Depth (feet)",
            value=str(depth_ft),
            width=100,
            keyboard_type="number",
        )
        
        depth_in_field = ft.TextField(
            label="Depth (inches)",
            value=str(depth_in),
            width=100,
            keyboard_type="number",
        )
        
        lane_ft_field = ft.TextField(
            label="Lane Width (feet)",
            value=str(lane_ft),
            width=100,
            keyboard_type="number",
        )
        
        lane_in_field = ft.TextField(
            label="Lane Width (inches)",
            value=str(lane_in),
            width=100,
            keyboard_type="number",
        )
        
        # Form container
        form_container = ft.Card(
            content=ft.Container(
                padding=10,
                content=ft.Column([
                    ft.Text("Track Dimensions", size=16, weight="bold"),
                    
                    ft.Row([
                        ft.Text("Width:", width=100),
                        width_ft_field,
                        ft.Text("feet"),
                        width_in_field,
                        ft.Text("inches"),
                    ]),
                    
                    ft.Row([
                        ft.Text("Depth:", width=100),
                        depth_ft_field,
                        ft.Text("feet"),
                        depth_in_field,
                        ft.Text("inches"),
                    ]),
                    
                    ft.Row([
                        ft.Text("Lane Width:", width=100),
                        lane_ft_field,
                        ft.Text("feet"),
                        lane_in_field,
                        ft.Text("inches"),
                    ]),
                ]),
            ),
        )
        
        # Canvas placeholder
        canvas_placeholder = ft.Container(
            content=ft.Text("Create a track to begin designing"),
            padding=20,
            bgcolor="#E0E0E0",
            border_radius=10,
            expand=True,
            alignment=ft.alignment.center,
        )
        
        # Create button handler
        def on_create_click(e):
            try:
                print("Create button clicked")
                
                # Get values
                w_ft = int(width_ft_field.value or 0)
                w_in = int(width_in_field.value or 0)
                d_ft = int(depth_ft_field.value or 0)
                d_in = int(depth_in_field.value or 0)
                l_ft = int(lane_ft_field.value or 0)
                l_in = int(lane_in_field.value or 0)
                
                # Create LengthValue objects
                width = LengthValue(w_ft, w_in)
                depth = LengthValue(d_ft, d_in)
                lane_width = LengthValue(l_ft, l_in)
                
                # Validate
                if lane_width.total_inches < 2:
                    status_text.value = "Lane width must be at least 2 inches"
                    page.update()
                    return
                
                # Create track
                track = Track(width, depth, lane_width)
                
                # Update status
                status_text.value = f"Track created: {w_ft}' {w_in}\" × {d_ft}' {d_in}\" with {l_ft}' {l_in}\" lanes"
                
                # Hide form and show canvas
                form_section.visible = False
                
                # Create canvas and toolbar
                track_canvas = TrackCanvas(track)
                toolbar = PieceToolbar(on_piece_selected=lambda piece: track_canvas.add_piece(piece))
                
                # Update the layout
                canvas_section.controls = [
                    track_canvas,
                    toolbar,
                ]
                
                page.update()
                print("Track canvas initialized")
                
            except Exception as e:
                error_msg = f"Error creating track: {str(e)}\n{traceback.format_exc()}"
                print(error_msg, file=sys.stderr)
                status_text.value = f"Error: {str(e)}"
                page.update()
        
        # Create button
        create_button = ft.ElevatedButton(
            text="Create Track",
            on_click=on_create_click,
        )
        
        # Create form section
        form_section = ft.Column([
            ft.Text("Gutter Track Planner", size=24, text_align="center"),
            form_container,
            ft.Container(
                content=create_button,
                alignment=ft.alignment.center,
                padding=ft.padding.only(top=10),
            ),
        ])
        
        # Create canvas section
        canvas_section = ft.Column([
            canvas_placeholder,
        ], expand=True)
        
        # Build the page
        page.add(
            form_section,
            status_text,
            canvas_section,
        )
        
        print("UI initialized successfully")
        
    except Exception as e:
        error_msg = f"Error initializing app: {str(e)}\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr)
        page.add(ft.Text(error_msg, color="red"))
        page.update()

# Run the app
print("Launching enhanced Flet app...")
ft.app(target=main)
print("App launched")