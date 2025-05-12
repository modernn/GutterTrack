import flet as ft
import asyncio

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
        from models import PieceType  # Import here to avoid circular imports
        
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
        from models import PieceType  # Import here to avoid circular imports
        
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
        from models import PieceType  # Import here to avoid circular imports
        
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
            from models import PieceType  # Import here to avoid circular imports
            
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
        if self.selected_piece:
            from models import PieceType  # Import here to avoid circular imports
            
            if self.selected_piece.type == PieceType.STRAIGHT:
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