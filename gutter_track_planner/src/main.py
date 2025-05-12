import flet as ft
import asyncio
import json
import sys
import os
from enum import Enum

# Models
class PieceType(Enum):
    STRAIGHT = "straight"
    ELBOW_22_5 = "elbow_22_5"
    ELBOW_45 = "elbow_45"
    ELBOW_90 = "elbow_90"
    T_JUNCTION = "t_junction"

class Piece:
    def __init__(self, piece_type, x=0, y=0, rotation=0, length=1):
        self.type = piece_type
        self.x = x
        self.y = y
        self.rotation = rotation  # In degrees
        self.length = length if piece_type == PieceType.STRAIGHT else 1
    
    def to_dict(self):
        return {
            "type": self.type.value,
            "x": self.x,
            "y": self.y,
            "rotation": self.rotation,
            "length": self.length
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            piece_type=PieceType(data["type"]),
            x=data["x"],
            y=data["y"],
            rotation=data["rotation"],
            length=data["length"]
        )
        
    def rotate(self, degrees=90):
        """Rotate the piece by specified degrees clockwise"""
        self.rotation = (self.rotation + degrees) % 360
        
    def get_occupied_cells(self, grid_size):
        """Return list of grid cells this piece occupies"""
        cells = []
        grid_x = int(self.x / grid_size)
        grid_y = int(self.y / grid_size)
        
        # Base cell
        cells.append((grid_x, grid_y))
        
        # Additional cells based on piece type and rotation
        if self.type == PieceType.STRAIGHT:
            # For straight pieces, add cells based on length and rotation
            if self.rotation in [0, 180]:  # Horizontal
                for i in range(1, self.length):
                    cells.append((grid_x + i, grid_y))
            else:  # Vertical (90, 270)
                for i in range(1, self.length):
                    cells.append((grid_x, grid_y + i))
        elif self.type in [PieceType.ELBOW_45, PieceType.ELBOW_90]:
            # For elbows, add one more cell based on rotation
            if self.rotation == 0:  # Right and down
                cells.append((grid_x + 1, grid_y + 1))
            elif self.rotation == 90:  # Left and down
                cells.append((grid_x - 1, grid_y + 1))
            elif self.rotation == 180:  # Left and up
                cells.append((grid_x - 1, grid_y - 1))
            elif self.rotation == 270:  # Right and up
                cells.append((grid_x + 1, grid_y - 1))
        elif self.type == PieceType.T_JUNCTION:
            # T junction has three connecting points
            if self.rotation == 0:  # T pointing down
                cells.extend([(grid_x - 1, grid_y), (grid_x + 1, grid_y), (grid_x, grid_y + 1)])
            elif self.rotation == 90:  # T pointing left
                cells.extend([(grid_x, grid_y - 1), (grid_x, grid_y + 1), (grid_x - 1, grid_y)])
            elif self.rotation == 180:  # T pointing up
                cells.extend([(grid_x - 1, grid_y), (grid_x + 1, grid_y), (grid_x, grid_y - 1)])
            elif self.rotation == 270:  # T pointing right
                cells.extend([(grid_x, grid_y - 1), (grid_x, grid_y + 1), (grid_x + 1, grid_y)])
                
        return cells

class Track:
    def __init__(self, width, depth, lane_width):
        self.width = width  # In feet
        self.depth = depth  # In feet
        self.lane_width = lane_width  # In inches
        self.pieces = []
        
        # Calculate grid dimensions
        self.grid_width = int(width * 12 / lane_width)  # Columns
        self.grid_height = int(depth * 12 / lane_width)  # Rows
    
    def add_piece(self, piece):
        self.pieces.append(piece)
        return True
    
    def remove_piece(self, piece):
        if piece in self.pieces:
            self.pieces.remove(piece)
            return True
        return False
    
    def piece_at_position(self, grid_x, grid_y):
        """Find if there's a piece at the given grid position"""
        for piece in self.pieces:
            occupied_cells = piece.get_occupied_cells(self.lane_width)
            if (grid_x, grid_y) in occupied_cells:
                return piece
        return None
    
    def can_place_piece(self, piece):
        """Check if a piece can be placed without overlap"""
        occupied_cells = piece.get_occupied_cells(self.lane_width)
        
        # Check grid boundaries
        for cell_x, cell_y in occupied_cells:
            if cell_x < 0 or cell_x >= self.grid_width or cell_y < 0 or cell_y >= self.grid_height:
                return False
        
        # Check for overlap with existing pieces
        for existing_piece in self.pieces:
            if existing_piece == piece:  # Skip the piece itself
                continue
                
            existing_cells = existing_piece.get_occupied_cells(self.lane_width)
            for cell in occupied_cells:
                if cell in existing_cells:
                    return False
        
        return True
    
    def to_dict(self):
        return {
            "width": self.width,
            "depth": self.depth,
            "lane_width": self.lane_width,
            "pieces": [piece.to_dict() for piece in self.pieces]
        }
    
    @classmethod
    def from_dict(cls, data):
        track = cls(
            width=data["width"],
            depth=data["depth"],
            lane_width=data["lane_width"]
        )
        
        for piece_data in data["pieces"]:
            track.add_piece(Piece.from_dict(piece_data))
        
        return track

class BillOfMaterials:
    def __init__(self, track):
        self.track = track
    
    def calculate(self):
        # Initialize counters
        straight_feet = 0
        elbows_22_5 = 0
        elbows_45 = 0
        elbows_90 = 0
        t_junctions = 0
        
        # Count pieces
        for piece in self.track.pieces:
            if piece.type == PieceType.STRAIGHT:
                # Convert to feet (lane width is in inches)
                piece_length_feet = (piece.length * self.track.lane_width) / 12
                straight_feet += piece_length_feet
            elif piece.type == PieceType.ELBOW_22_5:
                elbows_22_5 += 1
            elif piece.type == PieceType.ELBOW_45:
                elbows_45 += 1
            elif piece.type == PieceType.ELBOW_90:
                elbows_90 += 1
            elif piece.type == PieceType.T_JUNCTION:
                t_junctions += 1
        
        # Calculate connectors (each piece connects to adjacent pieces)
        # This is a simplified calculation
        total_pieces = len(self.track.pieces)
        connectors = max(0, total_pieces - 1)
        
        # Each connector typically needs 2 screws
        screws = connectors * 2
        
        return {
            "straight_feet": round(straight_feet, 2),
            "elbows_22_5": elbows_22_5,
            "elbows_45": elbows_45,
            "elbows_90": elbows_90,
            "t_junctions": t_junctions,
            "connectors": connectors,
            "screws": screws
        }

# Custom Controls
class SetupDialog(ft.AlertDialog):
    def __init__(self, on_confirmed):
        super().__init__()
        self.on_confirmed_callback = on_confirmed
        self.title = ft.Text("Track Dimensions")
        
        self.width_field = ft.TextField(
            label="Width (feet)",
            value="8",
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="Enter track width in feet"
        )
        
        self.depth_field = ft.TextField(
            label="Depth (feet)",
            value="4",
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="Enter track depth in feet"
        )
        
        self.lane_width_field = ft.TextField(
            label="Minimum Lane Width (inches)",
            value="6",
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="Enter minimum lane width in inches"
        )
        
        self.content = ft.Column([
            ft.Text("Enter the dimensions for your RC track:"),
            self.width_field,
            self.depth_field,
            self.lane_width_field,
        ], tight=True)
        
        self.actions = [
            ft.TextButton("Cancel", on_click=self.on_cancel),
            ft.TextButton("Create Track", on_click=self.on_confirm),
        ]
    
    def _get_control_name(self):
        return "setup-dialog"
    
    def on_cancel(self, e):
        self.open = False
        self.update()
    
    def on_confirm(self, e):
        try:
            width = float(self.width_field.value)
            depth = float(self.depth_field.value)
            lane_width = float(self.lane_width_field.value)
            
            if width <= 0 or depth <= 0 or lane_width <= 0:
                raise ValueError("Dimensions must be positive numbers")
            
            # Store callback and data
            callback = self.on_confirmed_callback
            data = {"width": width, "depth": depth, "lane_width": lane_width}
            
            # Close dialog first
            self.open = False
            self.update()
            
            # Use deferred execution
            loop = asyncio.get_event_loop()
            loop.call_soon(lambda: callback(data))
            
        except ValueError as err:
            # Show error
            self.content.controls.append(
                ft.Text(f"Error: {str(err)}", color=ft.colors.RED)
            )
            self.update()

class GridCell(ft.Container):
    def __init__(self, row, col, size, on_tap=None, on_drag_target=None):
        super().__init__()
        self.row = row
        self.col = col
        self.width = size
        self.height = size
        self.border = ft.border.all(1, ft.colors.GREY_400)
        self.border_radius = 3
        self.data = {"row": row, "col": col}
        
        # Setup for drag target
        self.on_drag_target_callback = on_drag_target
        
        # When a cell is tapped (for selection/modification)
        if on_tap:
            self.on_click = lambda e: on_tap(row, col)
    
    def _get_control_name(self):
        return f"grid-cell-{self.row}-{self.col}"
    
    def set_content(self, content):
        self.content = content
        self.update()

class TrackGrid(ft.Column):
    def __init__(self, track, on_cell_tap=None, on_piece_selected=None):
        super().__init__()
        self.track = track
        self.on_cell_tap_callback = on_cell_tap
        self.on_piece_selected_callback = on_piece_selected
        self.tight = True
        self.alignment = ft.MainAxisAlignment.CENTER
        
        self.cell_size = min(40, 600 // max(track.grid_width, track.grid_height))  # Adaptive cell size
        
        # Create grid rows
        self.rows = []
        for row in range(track.grid_height):
            row_container = ft.Row(
                [self._create_cell(row, col) for col in range(track.grid_width)],
                tight=True,
            )
            self.rows.append(row_container)
        
        self.controls = self.rows
    
    def _get_control_name(self):
        return "track-grid"
    
    def _create_cell(self, row, col):
        cell = GridCell(
            row=row, 
            col=col, 
            size=self.cell_size,
            on_tap=self.on_cell_tap_callback
        )
        return cell
    
    def update_view(self):
        """Update the grid view to reflect the current state of the track"""
        # Clear all cells
        for row_container in self.rows:
            for cell in row_container.controls:
                cell.content = None
                cell.bgcolor = None
        
        # Add pieces to the grid
        for piece in self.track.pieces:
            self._render_piece(piece)
        
        self.update()
    
    def _render_piece(self, piece):
        grid_cells = piece.get_occupied_cells(self.track.lane_width)
        
        for grid_x, grid_y in grid_cells:
            if 0 <= grid_y < len(self.rows) and 0 <= grid_x < len(self.rows[0].controls):
                cell = self.rows[grid_y].controls[grid_x]
                
                # Style based on piece type
                if piece.type == PieceType.STRAIGHT:
                    cell.bgcolor = ft.colors.BLUE_200
                elif piece.type == PieceType.ELBOW_22_5:
                    cell.bgcolor = ft.colors.GREEN_100
                elif piece.type == PieceType.ELBOW_45:
                    cell.bgcolor = ft.colors.GREEN_200
                elif piece.type == PieceType.ELBOW_90:
                    cell.bgcolor = ft.colors.GREEN_400
                elif piece.type == PieceType.T_JUNCTION:
                    cell.bgcolor = ft.colors.ORANGE_400
                
                # Add rotation indicator
                rotation_text = str(piece.rotation) + "°"
                
                # Add piece label
                if piece.type == PieceType.STRAIGHT:
                    label = f"S {piece.length}"
                elif piece.type == PieceType.ELBOW_22_5:
                    label = "E22"
                elif piece.type == PieceType.ELBOW_45:
                    label = "E45"
                elif piece.type == PieceType.ELBOW_90:
                    label = "E90"
                elif piece.type == PieceType.T_JUNCTION:
                    label = "T"
                
                cell.content = ft.Column([
                    ft.Text(label, size=10, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD),
                    ft.Text(rotation_text, size=8, color=ft.colors.BLACK54)
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=0)
                
                # Make the cell clickable to select the piece
                cell.on_click = lambda e, p=piece: self._on_piece_clicked(p)
    
    def _on_piece_clicked(self, piece):
        if self.on_piece_selected_callback:
            self.on_piece_selected_callback(piece)

class PieceControl(ft.Container):
    def __init__(self, piece_type, on_selected=None):
        super().__init__()
        self.piece_type = piece_type
        self.on_selected = on_selected
        self.padding = 5
        self.margin = ft.margin.only(right=5)
        
        # Style based on piece type
        if piece_type == PieceType.STRAIGHT:
            self.bgcolor = ft.colors.BLUE_200
            label = "Straight"
        elif piece_type == PieceType.ELBOW_22_5:
            self.bgcolor = ft.colors.GREEN_100
            label = "22.5° Elbow"
        elif piece_type == PieceType.ELBOW_45:
            self.bgcolor = ft.colors.GREEN_200
            label = "45° Elbow"
        elif piece_type == PieceType.ELBOW_90:
            self.bgcolor = ft.colors.GREEN_400
            label = "90° Elbow"
        elif piece_type == PieceType.T_JUNCTION:
            self.bgcolor = ft.colors.ORANGE_400
            label = "T-Junction"
        
        self.content = ft.Text(label, size=12)
        self.border_radius = ft.border_radius.all(5)
        self.border = ft.border.all(1, ft.colors.BLACK)
        
        # Make draggable
        self.on_click = self._on_click
    
    def _get_control_name(self):
        return f"piece-control-{self.piece_type.value}"
    
    def _on_click(self, e):
        if self.on_selected:
            self.on_selected(self.piece_type)
            
    def highlight(self, selected=True):
        if selected:
            self.border = ft.border.all(2, ft.colors.RED)
        else:
            self.border = ft.border.all(1, ft.colors.BLACK)
        self.update()

class PiecePalette(ft.Container):
    def __init__(self, on_piece_selected):
        super().__init__()
        self.on_piece_selected_callback = on_piece_selected
        self.padding = 10
        self.bgcolor = ft.colors.BACKGROUND
        self.border = ft.border.all(1, ft.colors.BLACK)
        self.border_radius = ft.border_radius.all(10)
        
        self.controls = []
        self.selected_control = None
        
        # Create controls for each piece type
        self.piece_types = [
            PieceType.STRAIGHT,
            PieceType.ELBOW_22_5,
            PieceType.ELBOW_45,
            PieceType.ELBOW_90,
            PieceType.T_JUNCTION
        ]
        
        for piece_type in self.piece_types:
            control = PieceControl(
                piece_type=piece_type,
                on_selected=self._on_piece_selected
            )
            self.controls.append(control)
        
        # Wrap controls in a scrollable row
        self.content = ft.Row(
            self.controls,
            scroll=ft.ScrollMode.AUTO,
            alignment=ft.MainAxisAlignment.START
        )
    
    def _get_control_name(self):
        return "piece-palette"
    
    def _on_piece_selected(self, piece_type):
        # Unhighlight previous selection
        if self.selected_control:
            self.selected_control.highlight(False)
        
        # Find and highlight the newly selected control
        for control in self.controls:
            if control.piece_type == piece_type:
                control.highlight(True)
                self.selected_control = control
                break
        
        # Notify callback
        if self.on_piece_selected_callback:
            self.on_piece_selected_callback(piece_type)

class PiecePropertiesPanel(ft.Container):
    def __init__(self, on_update=None, on_remove=None):
        super().__init__()
        self.on_update_callback = on_update
        self.on_remove_callback = on_remove
        self.padding = 10
        self.bgcolor = ft.colors.BACKGROUND
        self.border = ft.border.all(1, ft.colors.BLACK)
        self.border_radius = ft.border_radius.all(10)
        self.visible = False  # Hidden by default
        
        self.selected_piece = None
        
        # Rotation control
        self.rotation_slider = ft.Slider(
            min=0,
            max=3,
            divisions=3,
            label="{value}",
            value=0,
            on_change=self._on_rotation_changed
        )
        
        self.rotation_text = ft.Text("Rotation: 0°")
        
        # Length control (for straight pieces)
        self.length_slider = ft.Slider(
            min=1,
            max=5,
            divisions=4,
            label="{value}",
            value=1,
            on_change=self._on_length_changed
        )
        
        self.length_text = ft.Text("Length: 1 unit")
        
        # Remove button
        self.remove_button = ft.ElevatedButton(
            "Remove Piece",
            icon=ft.icons.DELETE,
            on_click=self._on_remove_clicked,
            color=ft.colors.RED
        )
        
        self.content = ft.Column([
            ft.Text("Piece Properties", weight=ft.FontWeight.BOLD),
            ft.Divider(),
            self.rotation_text,
            self.rotation_slider,
            self.length_text,
            self.length_slider,
            ft.Container(height=10),  # Spacer
            self.remove_button
        ], tight=True)
    
    def _get_control_name(self):
        return "piece-properties-panel"
    
    def set_piece(self, piece):
        self.selected_piece = piece
        if piece:
            self.visible = True
            
            # Update rotation control
            rotation_index = piece.rotation // 90
            self.rotation_slider.value = rotation_index
            self.rotation_text.value = f"Rotation: {piece.rotation}°"
            
            # Update length control
            self.length_slider.value = piece.length
            self.length_text.value = f"Length: {piece.length} unit"
            
            # Show/hide length control based on piece type
            self.length_slider.visible = (piece.type == PieceType.STRAIGHT)
            self.length_text.visible = (piece.type == PieceType.STRAIGHT)
        else:
            self.visible = False
        
        self.update()
    
    def _on_rotation_changed(self, e):
        if self.selected_piece:
            rotation = int(e.control.value) * 90
            self.rotation_text.value = f"Rotation: {rotation}°"
            
            if self.on_update_callback:
                self.on_update_callback(self.selected_piece, "rotation", rotation)
    
    def _on_length_changed(self, e):
        if self.selected_piece and self.selected_piece.type == PieceType.STRAIGHT:
            length = int(e.control.value)
            self.length_text.value = f"Length: {length} unit"
            
            if self.on_update_callback:
                self.on_update_callback(self.selected_piece, "length", length)
    
    def _on_remove_clicked(self, e):
        if self.selected_piece and self.on_remove_callback:
            self.on_remove_callback(self.selected_piece)
            self.set_piece(None)

class BOMView(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = 10
        self.bgcolor = ft.colors.BACKGROUND
        self.border = ft.border.all(1, ft.colors.BLACK)
        self.border_radius = ft.border_radius.all(10)
        
        # Create text displays for each material
        self.straight_text = ft.Text("Straight: 0 ft")
        self.elbows_22_5_text = ft.Text("22.5° Elbows: 0")
        self.elbows_45_text = ft.Text("45° Elbows: 0")
        self.elbows_90_text = ft.Text("90° Elbows: 0")
        self.t_junction_text = ft.Text("T-Junctions: 0")
        self.connectors_text = ft.Text("Connectors: 0")
        self.screws_text = ft.Text("Screws: 0")
        
        self.content = ft.Column([
            ft.Text("Bill of Materials", weight=ft.FontWeight.BOLD),
            ft.Divider(),
            self.straight_text,
            self.elbows_22_5_text,
            self.elbows_45_text,
            self.elbows_90_text,
            self.t_junction_text,
            self.connectors_text,
            self.screws_text
        ], tight=True)
    
    def _get_control_name(self):
        return "bom-view"
    
    def update_bom(self, bom_data):
        self.straight_text.value = f"Straight: {bom_data['straight_feet']} ft"
        self.elbows_22_5_text.value = f"22.5° Elbows: {bom_data['elbows_22_5']}"
        self.elbows_45_text.value = f"45° Elbows: {bom_data['elbows_45']}"
        self.elbows_90_text.value = f"90° Elbows: {bom_data['elbows_90']}"
        self.t_junction_text.value = f"T-Junctions: {bom_data['t_junctions']}"
        self.connectors_text.value = f"Connectors: {bom_data['connectors']}"
        self.screws_text.value = f"Screws: {bom_data['screws']}"
        self.update()

class GutterTrackApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "GutterTrack Designer"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 10
        
        # Make the app responsive
        self.page.on_resize = self.handle_resize
        
        # Initialize state
        self.track = None
        self.selected_piece_type = None
        self.selected_piece = None
        
        # Create main layout placeholder
        self.main_container = ft.Container()
        self.page.add(self.main_container)
        
        # Show setup dialog on start
        self.show_setup_dialog()
    
    def show_setup_dialog(self):
        dialog = SetupDialog(on_confirmed=self.handle_setup_confirmed)
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def handle_setup_confirmed(self, data):
        try:
            # Create new track with the specified dimensions
            self.track = Track(
                width=data["width"],
                depth=data["depth"],
                lane_width=data["lane_width"]
            )
            
            # Create UI components
            self.initialize_ui()
            
        except Exception as e:
            import traceback
            error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)
            
            # Show error to user
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error: {str(e)}"),
                bgcolor=ft.colors.RED
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def initialize_ui(self):
        # Create app bar
        self.app_bar = ft.AppBar(
            title=ft.Text("GutterTrack Designer"),
            bgcolor=ft.colors.BLUE,
            actions=[
                ft.IconButton(icon=ft.icons.SAVE, tooltip="Save Track", on_click=self.save_track),
                ft.IconButton(icon=ft.icons.FOLDER_OPEN, tooltip="Load Track", on_click=self.load_track),
                ft.IconButton(icon=ft.icons.SETTINGS, tooltip="Settings", on_click=self.show_settings),
                ft.IconButton(icon=ft.icons.RESTART_ALT, tooltip="New Track", on_click=self.new_track)
            ]
        )
        
        # Create track grid
        self.track_grid = TrackGrid(
            track=self.track,
            on_cell_tap=self.handle_cell_tap,
            on_piece_selected=self.handle_piece_selected
        )
        
        # Create piece palette
        self.piece_palette = PiecePalette(
            on_piece_selected=self.handle_palette_selection
        )
        
        # Create piece properties panel
        self.properties_panel = PiecePropertiesPanel(
            on_update=self.handle_piece_update,
            on_remove=self.handle_piece_remove
        )
        
        # Create BOM view
        self.bom_view = BOMView()
        
        # Update BOM initially
        bom = BillOfMaterials(self.track).calculate()
        self.bom_view.update_bom(bom)
        
        # Layout differently based on screen size
        self.handle_resize(None)
    
    def handle_resize(self, e):
        if not hasattr(self, 'track_grid'):
            return  # UI not initialized yet
            
        width = self.page.width or 800
        height = self.page.height or 600
        
        if width < 700:  # Mobile layout
            self.main_container.content = ft.Column([
                self.app_bar,
                ft.Container(
                    content=self.track_grid,
                    margin=ft.margin.only(top=10, bottom=10)
                ),
                self.piece_palette,
                self.properties_panel,
                self.bom_view
            ])
        else:  # Desktop layout
            controls_column = ft.Column([
                self.piece_palette,
                self.properties_panel,
                self.bom_view
            ], tight=True)
            
            self.main_container.content = ft.Column([
                self.app_bar,
                ft.Row([
                    ft.Container(
                        content=self.track_grid,
                        margin=ft.margin.only(top=10, right=10),
                        expand=True
                    ),
                    ft.Container(
                        content=controls_column,
                        width=250
                    )
                ], expand=True)
            ])
        
        # Update the page
        self.page.update()
    
    def handle_palette_selection(self, piece_type):
        self.selected_piece_type = piece_type
        
        # Deselect any currently selected piece
        self.selected_piece = None
        self.properties_panel.set_piece(None)
        
        # Update UI
        self.page.update()
    
    def handle_cell_tap(self, row, col):
        if self.track:
            if self.selected_piece_type:
                # Check if there's already a piece here
                existing_piece = self.track.piece_at_position(col, row)
                if existing_piece:
                    # Select the existing piece
                    self.handle_piece_selected(existing_piece)
                    return
                
                # Place new piece
                piece = Piece(
                    piece_type=self.selected_piece_type,
                    x=col * self.track.lane_width,
                    y=row * self.track.lane_width
                )
                
                if self.track.can_place_piece(piece):
                    self.track.add_piece(piece)
                    self.update_track_view()
                else:
                    # Show error message
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Cannot place piece: position already occupied or out of bounds"),
                        bgcolor=ft.colors.RED
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            else:
                # Check if there's a piece at this location
                piece = self.track.piece_at_position(col, row)
                if piece:
                    self.handle_piece_selected(piece)
    
    def handle_piece_selected(self, piece):
        self.selected_piece = piece
        
        # Update properties panel
        self.properties_panel.set_piece(piece)
        
        # Deselect piece type in palette
        self.selected_piece_type = None
        for control in self.piece_palette.controls:
            control.highlight(False)
        
        # Update UI
        self.page.update()
    
    def handle_piece_update(self, piece, property_name, value):
        if property_name == "rotation":
            old_rotation = piece.rotation
            piece.rotation = value
            
            # Check if new position is valid
            if not self.track.can_place_piece(piece):
                # Revert to old value
                piece.rotation = old_rotation
                
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Cannot rotate: would overlap with other pieces"),
                    bgcolor=ft.colors.RED
                )
                self.page.snack_bar.open = True
                
                # Update properties panel to revert slider
                self.properties_panel.set_piece(piece)
            
        elif property_name == "length" and piece.type == PieceType.STRAIGHT:
            old_length = piece.length
            piece.length = value
            
            # Check if new position is valid
            if not self.track.can_place_piece(piece):
                # Revert to old value
                piece.length = old_length
                
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Cannot resize: would overlap with other pieces"),
                    bgcolor=ft.colors.RED
                )
                self.page.snack_bar.open = True
                
                # Update properties panel to revert slider
                self.properties_panel.set_piece(piece)
        
        # Update the track view
        self.update_track_view()
    
    def handle_piece_remove(self, piece):
        if self.track.remove_piece(piece):
            self.selected_piece = None
            self.update_track_view()
    
    def update_track_view(self):
        # Update grid
        self.track_grid.update_view()
        
        # Update BOM
        bom = BillOfMaterials(self.track).calculate()
        self.bom_view.update_bom(bom)
    
    def save_track(self, e):
        if not self.track or not self.track.pieces:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Nothing to save. Add some pieces first."),
                bgcolor=ft.colors.ORANGE
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
            
        def save_dialog_closed(e):
            if e.data == "save":
                file_name = save_dialog.content.controls[1].value or "my_track"
                if not file_name.endswith(".json"):
                    file_name += ".json"
                
                # In a real app, we would save to file system
                # Here we'll just show what would be saved
                track_data = self.track.to_dict()
                
                # Show confirmation
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Track saved as {file_name}"),
                    bgcolor=ft.colors.GREEN
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        # Create save dialog
        save_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Save Track"),
            content=ft.Column([
                ft.Text("Enter a name for your track:"),
                ft.TextField(label="File Name", value="my_track")
            ], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: setattr(save_dialog, "open", False)),
                ft.TextButton("Save", on_click=lambda e: save_dialog_closed(ft.ControlEvent(data="save")))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # Add required method
        save_dialog._get_control_name = lambda: "save-dialog"
        
        self.page.dialog = save_dialog
        save_dialog.open = True
        self.page.update()
    
    def load_track(self, e):
        # In a real app, we would show a file picker
        # For this example, we'll simulate loading a track
        
        # Example track data
        track_data = {
            "width": 8,
            "depth": 4,
            "lane_width": 6,
            "pieces": [
                {"type": "straight", "x": 0, "y": 0, "rotation": 0, "length": 3},
                {"type": "elbow_90", "x": 18, "y": 0, "rotation": 0, "length": 1},
                {"type": "straight", "x": 18, "y": 6, "rotation": 90, "length": 2},
                {"type": "t_junction", "x": 18, "y": 18, "rotation": 180, "length": 1}
            ]
        }
        
        # Load the track
        self.track = Track.from_dict(track_data)
        
        # Reinitialize UI with the loaded track
        self.initialize_ui()
        self.update_track_view()
        
        # Show confirmation
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Track loaded successfully"),
            bgcolor=ft.colors.GREEN
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def show_settings(self, e):
        # Show settings dialog
        settings_dialog = ft.AlertDialog(
            title=ft.Text("Settings"),
            content=ft.Column([
                ft.Text("App Version: 1.0.0"),
                ft.Text("Built with Flet 0.28.2"),
                ft.Divider(),
                ft.Text("Theme:"),
                ft.Row([
                    ft.ElevatedButton(
                        "Light",
                        on_click=lambda _: self.set_theme(ft.ThemeMode.LIGHT)
                    ),
                    ft.ElevatedButton(
                        "Dark",
                        on_click=lambda _: self.set_theme(ft.ThemeMode.DARK)
                    )
                ])
            ], tight=True),
            actions=[
                ft.TextButton("Close", on_click=lambda _: setattr(settings_dialog, "open", False))
            ]
        )
        
        # Add required method
        settings_dialog._get_control_name = lambda: "settings-dialog"
        
        self.page.dialog = settings_dialog
        settings_dialog.open = True
        self.page.update()
    
    def set_theme(self, theme_mode):
        self.page.theme_mode = theme_mode
        self.page.update()
    
    def new_track(self, e):
        # Show confirmation dialog
        confirm_dialog = ft.AlertDialog(
            title=ft.Text("New Track"),
            content=ft.Text("Are you sure you want to create a new track? Any unsaved changes will be lost."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: setattr(confirm_dialog, "open", False)),
                ft.TextButton("Create New", on_click=self.confirm_new_track)
            ]
        )
        
        # Add required method
        confirm_dialog._get_control_name = lambda: "confirm-dialog"
        
        self.page.dialog = confirm_dialog
        confirm_dialog.open = True
        self.page.update()
    
    def confirm_new_track(self, e):
        # Close dialog
        self.page.dialog.open = False
        self.page.update()
        
        # Show setup dialog
        self.show_setup_dialog()

def main(page: ft.Page):
    app = GutterTrackApp(page)

if __name__ == "__main__":
    ft.app(target=main)