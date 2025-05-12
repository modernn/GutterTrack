import flet as ft
import math
import traceback
import sys
from models.track import Track
from models.piece import Piece, PieceType, StraightPiece, ElbowPiece, TeePiece
from utils.grid import snap_to_grid, is_position_valid
from views.draggable_piece import DraggablePiece

class TrackCanvas(ft.Control):  # Changed from ft.UserControl
    """Main canvas for track design."""
    
    def __init__(self, track):
        """
        Initialize the track canvas.
        
        Args:
            track (Track): The track model
        """
        super().__init__()
        self.track = track
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.dragging = False
        self.last_pos = (0, 0)
        self.selected_piece = None
        self.is_validating = False
        self.invalid_positions = []
        
        # Track the draggable pieces
        self.draggable_pieces = []
    
    def build(self):
        """Build the canvas widget."""
        try:
            self.canvas = ft.GestureDetector(
                on_pan_start=self._on_pan_start,
                on_pan_update=self._on_pan_update,
                on_pan_end=self._on_pan_end,
                on_scale_start=self._on_scale_start,
                on_scale_update=self._on_scale_update,
                content=ft.Stack(
                    controls=[
                        ft.DragTarget(
                            content=ft.Container(
                                content=ft.Canvas(
                                    on_paint=self._paint_canvas,
                                    width=float('inf'),
                                    height=float('inf'),
                                ),
                                width=float('inf'),
                                height=float('inf'),
                            ),
                            on_accept=self._on_drag_accept,
                            on_will_accept=self._on_drag_will_accept,
                            on_leave=self._on_drag_leave,
                        ),
                    ],
                ),
            )
            
            return self.canvas
        except Exception as e:
            error_msg = f"Error building canvas: {str(e)}\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)
            return ft.Text(error_msg, color="#FF0000")
    
    def _on_pan_start(self, e):
        """Handle pan start event."""
        # Only start panning if not dragging a piece
        if not self.selected_piece:
            self.dragging = True
            self.last_pos = (e.local_x, e.local_y)
    
    def _on_pan_update(self, e):
        """Handle pan update event."""
        if self.dragging and not self.selected_piece:
            dx = e.local_x - self.last_pos[0]
            dy = e.local_y - self.last_pos[1]
            self.offset_x += dx / self.scale
            self.offset_y += dy / self.scale
            self.last_pos = (e.local_x, e.local_y)
            self.update()
    
    def _on_pan_end(self, e):
        """Handle pan end event."""
        self.dragging = False
    
    def _on_scale_start(self, e):
        """Handle scale start event."""
        pass
    
    def _on_scale_update(self, e):
        """Handle scale update event."""
        new_scale = self.scale * e.scale
        # Limit scale to reasonable range
        new_scale = max(0.5, min(5.0, new_scale))
        
        # Adjust offset to zoom around center
        if new_scale != self.scale:
            center_x = e.local_focal_point_x
            center_y = e.local_focal_point_y
            
            # Calculate offset adjustment
            old_inv_scale = 1 / self.scale
            new_inv_scale = 1 / new_scale
            
            self.offset_x = center_x - (center_x - self.offset_x * self.scale) * new_inv_scale
            self.offset_y = center_y - (center_y - self.offset_y * self.scale) * new_inv_scale
            
            self.scale = new_scale
            self.update()
    
    def _on_drag_accept(self, e):
        """Handle drag accept event."""
        try:
            # Add the dragged piece to the track
            if hasattr(e, "control_data") and isinstance(e.control_data, Piece):
                piece = e.control_data
                
                # Convert screen coordinates to grid coordinates
                grid_x, grid_y = self._screen_to_grid(e.local_x, e.local_y)
                
                # Snap to grid
                grid_x, grid_y = snap_to_grid(grid_x, grid_y)
                
                # Check if position is valid
                if is_position_valid(self.track, piece, (grid_x, grid_y)):
                    piece.position = (grid_x, grid_y)
                    
                    # Add to track if it's a new piece
                    if piece not in self.track.pieces:
                        self.track.pieces.append(piece)
                    
                    self.selected_piece = None
                    self.is_validating = False
                    self.invalid_positions = []
                    self.update()
        except Exception as e:
            print(f"Error in drag accept: {e}")
    
    def _on_drag_will_accept(self, e):
        """Handle drag will accept event."""
        try:
            if hasattr(e, "control_data") and isinstance(e.control_data, Piece):
                self.is_validating = True
                piece = e.control_data
                
                # Convert screen coordinates to grid coordinates
                grid_x, grid_y = self._screen_to_grid(e.local_x, e.local_y)
                
                # Snap to grid
                grid_x, grid_y = snap_to_grid(grid_x, grid_y)
                
                # Check if position is valid
                valid = is_position_valid(self.track, piece, (grid_x, grid_y))
                
                # Store current validation state
                self.invalid_positions = [] if valid else [(grid_x, grid_y)]
                self.update()
        except Exception as e:
            print(f"Error in drag will accept: {e}")
    
    def _on_drag_leave(self, e):
        """Handle drag leave event."""
        self.is_validating = False
        self.invalid_positions = []
        self.update()
    
    def _screen_to_grid(self, screen_x, screen_y):
        """
        Convert screen coordinates to grid coordinates.
        
        Args:
            screen_x (float): Screen X coordinate
            screen_y (float): Screen Y coordinate
            
        Returns:
            tuple: Grid (x, y) coordinates
        """
        # Adjust for panning and zooming
        canvas_x = (screen_x / self.scale) - self.offset_x
        canvas_y = (screen_y / self.scale) - self.offset_y
        
        # Convert to grid units
        grid_size_px = self.track.lane_width.total_inches * 10
        grid_x = canvas_x / grid_size_px
        grid_y = canvas_y / grid_size_px
        
        return grid_x, grid_y
    
    def _grid_to_screen(self, grid_x, grid_y):
        """
        Convert grid coordinates to screen coordinates.
        
        Args:
            grid_x (float): Grid X coordinate
            grid_y (float): Grid Y coordinate
            
        Returns:
            tuple: Screen (x, y) coordinates
        """
        # Convert grid to canvas coordinates
        grid_size_px = self.track.lane_width.total_inches * 10
        canvas_x = grid_x * grid_size_px
        canvas_y = grid_y * grid_size_px
        
        # Adjust for panning and zooming
        screen_x = (canvas_x + self.offset_x) * self.scale
        screen_y = (canvas_y + self.offset_y) * self.scale
        
        return screen_x, screen_y
    
    def _paint_canvas(self, canvas):
        """
        Paint the canvas with grid and track pieces.
        
        Args:
            canvas: The canvas to paint on
        """
        try:
            # Draw background
            canvas.fill_style = "#F5F5F5"  # Changed from ft.colors.X
            canvas.fill_rect(0, 0, canvas.width, canvas.height)
            
            # Transform for panning and zooming
            canvas.save()
            canvas.scale(self.scale, self.scale)
            canvas.translate(self.offset_x, self.offset_y)
            
            # Draw grid
            self._draw_grid(canvas)
            
            # Draw track outline
            self._draw_track_outline(canvas)
            
            # Draw validation highlights
            if self.is_validating:
                self._draw_validation_highlights(canvas)
            
            # Draw pieces
            self._draw_pieces(canvas)
            
            # Draw selection highlight
            if self.selected_piece:
                self._draw_selection_highlight(canvas, self.selected_piece)
            
            canvas.restore()
        except Exception as e:
            error_msg = f"Error painting canvas: {str(e)}\n{traceback.format_exc()}"
            print(error_msg, file=sys.stderr)
    
    def _draw_grid(self, canvas):
        """Draw the grid based on lane width."""
        try:
            canvas.stroke_style = "#CCCCCC"  # Changed from ft.colors.X
            canvas.line_width = 1
            
            # Get grid size in inches
            grid_size = self.track.lane_width.total_inches
            
            # Convert track dimensions to pixels (1 inch = 10 pixels)
            width_px = self.track.width.total_inches * 10
            depth_px = self.track.depth.total_inches * 10
            
            # Draw vertical grid lines
            for x in range(0, int(width_px) + 1, int(grid_size * 10)):
                # Draw line
                canvas.begin_path()
                canvas.move_to(x, 0)
                canvas.line_to(x, depth_px)
                canvas.stroke()
                
                # Draw measurement text
                if x % 120 == 0:  # Every foot
                    feet = x // 120
                    canvas.fill_style = "#333333"  # Changed from ft.colors.X
                    canvas.font = "12px sans-serif"
                    canvas.fill_text(f"{feet}'", x + 2, 15)
            
            # Draw horizontal grid lines
            for y in range(0, int(depth_px) + 1, int(grid_size * 10)):
                # Draw line
                canvas.begin_path()
                canvas.move_to(0, y)
                canvas.line_to(width_px, y)
                canvas.stroke()
                
                # Draw measurement text
                if y % 120 == 0:  # Every foot
                    feet = y // 120
                    canvas.fill_style = "#333333"  # Changed from ft.colors.X
                    canvas.font = "12px sans-serif"
                    canvas.fill_text(f"{feet}'", 5, y + 15)
        except Exception as e:
            print(f"Error drawing grid: {e}")
    
    def _draw_track_outline(self, canvas):
        """Draw the track outline."""
        try:
            canvas.stroke_style = "#000000"  # Changed from ft.colors.X
            canvas.line_width = 2
            
            # Convert track dimensions to pixels
            width_px = self.track.width.total_inches * 10
            depth_px = self.track.depth.total_inches * 10
            
            # Draw rectangle
            canvas.begin_path()
            canvas.rect(0, 0, width_px, depth_px)
            canvas.stroke()
        except Exception as e:
            print(f"Error drawing track outline: {e}")
    
    def _draw_validation_highlights(self, canvas):
        """Draw validation highlights."""
        try:
            canvas.fill_style = "rgba(255, 0, 0, 0.3)"  # Translucent red
            
            grid_size_px = self.track.lane_width.total_inches * 10
            
            for x, y in self.invalid_positions:
                canvas.begin_path()
                canvas.rect(
                    x * grid_size_px,
                    y * grid_size_px,
                    grid_size_px,
                    grid_size_px
                )
                canvas.fill()
        except Exception as e:
            print(f"Error drawing validation highlights: {e}")
    
    def _draw_pieces(self, canvas):
        """Draw all track pieces."""
        try:
            for piece in self.track.pieces:
                if piece != self.selected_piece:  # Don't draw the selected piece twice
                    self._draw_piece(canvas, piece)
            
            # Draw the selected piece last (to appear on top)
            if self.selected_piece and self.selected_piece in self.track.pieces:
                self._draw_piece(canvas, self.selected_piece)
        except Exception as e:
            print(f"Error drawing pieces: {e}")
    
    def _draw_selection_highlight(self, canvas, piece):
        """Draw a highlight around the selected piece."""
        try:
            # Get piece position in pixels
            x, y = piece.position
            x *= self.track.lane_width.total_inches * 10
            y *= self.track.lane_width.total_inches * 10
            
            # Save canvas state
            canvas.save()
            
            # Apply transformations
            canvas.translate(x, y)
            canvas.rotate(math.radians(piece.rotation))
            if piece.flipped:
                canvas.scale(-1, 1)
            
            # Draw highlight based on piece type
            canvas.stroke_style = "#0088FF"  # Changed from ft.colors.X
            canvas.line_width = 2
            
            if piece.piece_type == PieceType.STRAIGHT:
                length_px = piece.length * 10
                width_px = 2 * 10  # 2 inches width
                
                canvas.begin_path()
                canvas.rect(-width_px / 2 - 2, -width_px / 2 - 2, 
                          length_px + 4, width_px + 4)
                canvas.stroke()
            elif "elbow" in piece.piece_type.value:
                width_px = 2 * 10  # 2 inches width
                radius = 3 * 10  # 3 inches radius
                
                canvas.begin_path()
                canvas.arc(0, 0, radius + 2, 
                         math.radians(180 - 2), math.radians(270 + 2))
                canvas.stroke()
            elif piece.piece_type == PieceType.TEE:
                width_px = 2 * 10  # 2 inches width
                length_px = 4 * 10  # 4 inches length
                
                canvas.begin_path()
                canvas.rect(-length_px / 2 - 2, -width_px / 2 - 2, 
                          length_px + 4, width_px + 4)
                canvas.rect(-width_px / 2 - 2, -width_px / 2 - 2, 
                          width_px + 4, length_px / 2 + 4)
                canvas.stroke()
            
            # Restore canvas state
            canvas.restore()
        except Exception as e:
            print(f"Error drawing selection highlight: {e}")
    
    def _draw_piece(self, canvas, piece):
        """
        Draw a track piece.
        
        Args:
            canvas: The canvas to draw on
            piece: The piece to draw
        """
        try:
            # Get piece position in pixels
            x, y = piece.position
            x *= self.track.lane_width.total_inches * 10
            y *= self.track.lane_width.total_inches * 10
            
            # Save canvas state
            canvas.save()
            
            # Apply transformations
            canvas.translate(x, y)
            canvas.rotate(math.radians(piece.rotation))
            if piece.flipped:
                canvas.scale(-1, 1)
            
            # Draw piece based on type
            if piece.piece_type == PieceType.STRAIGHT:
                self._draw_straight(canvas, piece)
            elif "elbow" in piece.piece_type.value:
                self._draw_elbow(canvas, piece)
            elif piece.piece_type == PieceType.TEE:
                self._draw_tee(canvas, piece)
            
            # Restore canvas state
            canvas.restore()
        except Exception as e:
            print(f"Error drawing piece: {e}")
    
    def _draw_straight(self, canvas, piece):
        """Draw a straight piece."""
        canvas.fill_style = "#666666"  # Changed from ft.colors.X
        canvas.stroke_style = "#000000"  # Changed from ft.colors.X
        canvas.line_width = 1
        
        # Convert length to pixels
        length_px = piece.length * 10
        width_px = 2 * 10  # 2 inches width
        
        # Draw rectangle
        canvas.begin_path()
        canvas.rect(-width_px / 2, -width_px / 2, length_px, width_px)
        canvas.fill()
        canvas.stroke()
    
    def _draw_elbow(self, canvas, piece):
        """Draw an elbow piece."""
        canvas.fill_style = "#666666"  # Changed from ft.colors.X
        canvas.stroke_style = "#000000"  # Changed from ft.colors.X
        canvas.line_width = 1
        
        width_px = 2 * 10  # 2 inches width
        radius = 3 * 10  # 3 inches radius
        
        # Draw arc based on angle
        canvas.begin_path()
        
        if piece.angle == 90:
            # 90-degree elbow
            canvas.move_to(-width_px / 2, -width_px / 2)
            canvas.arc(0, 0, radius, math.radians(180), math.radians(270))
            canvas.line_to(radius, width_px / 2)
            canvas.arc(0, 0, radius - width_px, math.radians(270), math.radians(180), True)
            canvas.close_path()
        elif piece.angle == 45:
            # 45-degree elbow
            canvas.move_to(-width_px / 2, -width_px / 2)
            canvas.arc(0, 0, radius, math.radians(180), math.radians(225))
            canvas.line_to(radius * math.cos(math.radians(225)) + width_px / 2, 
                          radius * math.sin(math.radians(225)) + width_px / 2)
            canvas.arc(0, 0, radius - width_px, math.radians(225), math.radians(180), True)
            canvas.close_path()
        else:  # 22.5 degrees
            # 22.5-degree elbow
            canvas.move_to(-width_px / 2, -width_px / 2)
            canvas.arc(0, 0, radius, math.radians(180), math.radians(202.5))
            canvas.line_to(radius * math.cos(math.radians(202.5)) + width_px / 2, 
                          radius * math.sin(math.radians(202.5)) + width_px / 2)
            canvas.arc(0, 0, radius - width_px, math.radians(202.5), math.radians(180), True)
            canvas.close_path()
        
        canvas.fill()
        canvas.stroke()
    
    def _draw_tee(self, canvas, piece):
        """Draw a T-junction piece."""
        canvas.fill_style = "#666666"  # Changed from ft.colors.X
        canvas.stroke_style = "#000000"  # Changed from ft.colors.X
        canvas.line_width = 1
        
        width_px = 2 * 10  # 2 inches width
        length_px = 4 * 10  # 4 inches length
        
        # Draw T shape
        canvas.begin_path()
        # Horizontal part
        canvas.rect(-length_px / 2, -width_px / 2, length_px, width_px)
        # Vertical part
        canvas.rect(-width_px / 2, -width_px / 2, width_px, length_px / 2)
        canvas.fill()
        canvas.stroke()
    
    def add_piece(self, piece):
        """Add a piece to the track."""
        try:
            # Ensure width and height are defined
            if not hasattr(self, 'width') or not hasattr(self, 'height'):
                self.width = 800  # Default
                self.height = 600  # Default
            
            # Position at center of visible area initially
            center_x = -self.offset_x + (self.width / self.scale / 2)
            center_y = -self.offset_y + (self.height / self.scale / 2)
            
            # Convert to grid coordinates and snap
            grid_x = center_x / (self.track.lane_width.total_inches * 10)
            grid_y = center_y / (self.track.lane_width.total_inches * 10)
            grid_x, grid_y = snap_to_grid(grid_x, grid_y)
            
            # Set position
            piece.position = (grid_x, grid_y)
            
            # Add to track
            self.track.pieces.append(piece)
            
            # Select the new piece
            self.select_piece(piece)
            
            self.update()
        except Exception as e:
            print(f"Error adding piece: {e}")
    
    def select_piece(self, piece):
        """Select a piece."""
        self.selected_piece = piece
        self.update()
    
    def move_selected_piece(self, x, y):
        """Move the selected piece to a new position."""
        try:
            if self.selected_piece:
                # Convert screen coordinates to grid coordinates
                grid_x, grid_y = self._screen_to_grid(x, y)
                
                # Snap to grid
                grid_x, grid_y = snap_to_grid(grid_x, grid_y)
                
                # Check if position is valid
                if is_position_valid(self.track, self.selected_piece, (grid_x, grid_y)):
                    self.selected_piece.position = (grid_x, grid_y)
                    self.update()
        except Exception as e:
            print(f"Error moving piece: {e}")
    
    def rotate_selected_piece(self, clockwise=True):
        """Rotate the selected piece."""
        try:
            if self.selected_piece:
                # Rotate by 90 degrees
                delta = 90 if clockwise else -90
                self.selected_piece.rotation = (self.selected_piece.rotation + delta) % 360
                self.update()
        except Exception as e:
            print(f"Error rotating piece: {e}")
    
    def flip_selected_piece(self):
        """Flip the selected piece."""
        try:
            if self.selected_piece:
                self.selected_piece.flipped = not self.selected_piece.flipped
                self.update()
        except Exception as e:
            print(f"Error flipping piece: {e}")
    
    def delete_selected_piece(self):
        """Delete the selected piece."""
        try:
            if self.selected_piece:
                if self.selected_piece in self.track.pieces:
                    self.track.pieces.remove(self.selected_piece)
                self.selected_piece = None
                self.update()
        except Exception as e:
            print(f"Error deleting piece: {e}")
    
    def did_mount(self):
        """Called when the control is mounted."""
        try:
            # Set initial size if page exists
            if hasattr(self, 'page') and self.page:
                self.width = self.page.width
                self.height = self.page.height - 100  # Leave space for toolbar
            else:
                # Default fallback values
                self.width = 800
                self.height = 600
            
            # Set initial offset to center of track
            width_px = self.track.width.total_inches * 10
            depth_px = self.track.depth.total_inches * 10
            
            self.offset_x = (self.width / self.scale / 2) - (width_px / 2)
            self.offset_y = (self.height / self.scale / 2) - (depth_px / 2)
            
            self.update()
        except Exception as e:
            print(f"Error in did_mount: {e}")
    
    def did_resize(self):
        """Called when the window is resized."""
        try:
            if hasattr(self, 'page') and self.page:
                self.width = self.page.width
                self.height = self.page.height - 100  # Leave space for toolbar
            else:
                # Default fallback values
                self.width = 800
                self.height = 600
                
            self.update()
        except Exception as e:
            print(f"Error in did_resize: {e}")