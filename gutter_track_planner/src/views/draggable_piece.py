import flet as ft
from models.piece import Piece
from utils.grid import snap_to_grid, is_position_valid

class DraggablePiece(ft.Control):  # Changed from ft.UserControl
    """Draggable representation of a track piece."""
    
    def _get_control_name(self):
        return "draggable-piece" 
    
    def __init__(self, piece, on_position_changed):
        """
        Initialize a draggable piece.
        
        Args:
            piece: The piece model
            on_position_changed: Callback when position changes
        """
        super().__init__()
        self.piece = piece
        self.on_position_changed = on_position_changed
        self.drag_offset_x = 0
        self.drag_offset_y = 0
    
    def build(self):
        """Build the draggable widget."""
        return ft.Draggable(
            content=ft.Container(
                content=self._create_piece_visual(),
                width=50,
                height=50,
            ),
            content_feedback=ft.Container(
                content=self._create_piece_visual(is_feedback=True),
                width=50,
                height=50,
                opacity=0.7,
            ),
            on_drag_start=self._on_drag_start,
            on_drag_update=self._on_drag_update,
            on_drag_end=self._on_drag_end,
        )
    
    def _create_piece_visual(self, is_feedback=False):
        """Create a visual representation of the piece."""
        # This is a simplified representation - we'll use the canvas
        # for the actual rendering
        icon = "horizontal_rule"  # Changed from ft.icons.HORIZONTAL_RULE
        
        if "elbow" in self.piece.piece_type.value:
            icon = "turn_slight_right"  # Changed from ft.icons.TURN_SLIGHT_RIGHT
        elif self.piece.piece_type.value == "tee":
            icon = "add_road"  # Changed from ft.icons.ADD_ROAD
        
        return ft.Icon(
            name=icon,  # Changed from icon to name
            size=30,
            color="#2196F3" if is_feedback else "#000000",  # Changed from ft.colors.X
        )
    
    def _on_drag_start(self, e):
        """Handle drag start event."""
        # Store drag offset
        self.drag_offset_x = e.local_x
        self.drag_offset_y = e.local_y
    
    def _on_drag_update(self, e):
        """Handle drag update event."""
        # Calculate new position
        x = e.global_x - self.drag_offset_x
        y = e.global_y - self.drag_offset_y
        
        if self.on_position_changed:
            self.on_position_changed(self.piece, x, y, is_final=False)
    
    def _on_drag_end(self, e):
        """Handle drag end event."""
        # Calculate final position
        x = e.global_x - self.drag_offset_x
        y = e.global_y - self.drag_offset_y
        
        if self.on_position_changed:
            self.on_position_changed(self.piece, x, y, is_final=True)