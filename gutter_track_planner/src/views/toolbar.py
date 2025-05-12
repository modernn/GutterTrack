import flet as ft
from models.piece import PieceType, StraightPiece, ElbowPiece, TeePiece

class PieceToolbar(ft.Control):  # Changed from ft.UserControl
    """Toolbar for selecting track pieces."""
    
    def __init__(self, on_piece_selected):
        """
        Initialize the toolbar.
        
        Args:
            on_piece_selected: Callback when a piece is selected
        """
        super().__init__()
        self.on_piece_selected = on_piece_selected
    
    def build(self):
        """Build the toolbar widget."""
        return ft.Card(
            content=ft.Column(
                controls=[
                    ft.ListTile(
                        title=ft.Text("Track Pieces"),
                    ),
                    ft.Divider(),
                    ft.Row(
                        controls=[
                            self._create_piece_button("Straight", PieceType.STRAIGHT),
                            self._create_piece_button("Elbow 90°", PieceType.ELBOW_90),
                            self._create_piece_button("Elbow 45°", PieceType.ELBOW_45),
                            self._create_piece_button("Elbow 22.5°", PieceType.ELBOW_22),
                            self._create_piece_button("T-Junction", PieceType.TEE),
                        ],
                        alignment="center",  # Changed from ft.MainAxisAlignment.CENTER
                        spacing=10,
                    ),
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                text="Rotate",  # Added text parameter
                                icon="rotate_right",  # Changed from ft.icons.ROTATE_RIGHT
                                on_click=self._on_rotate_click,
                            ),
                            ft.ElevatedButton(
                                text="Flip",  # Added text parameter
                                icon="flip",  # Changed from ft.icons.FLIP
                                on_click=self._on_flip_click,
                            ),
                        ],
                        alignment="center",  # Changed from ft.MainAxisAlignment.CENTER
                        spacing=10,
                    ),
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                text="Bill of Materials",  # Added text parameter
                                icon="inventory",  # Changed from ft.icons.INVENTORY
                                on_click=self._on_bom_click,
                            ),
                        ],
                        alignment="center",  # Changed from ft.MainAxisAlignment.CENTER
                    ),
                ],
                spacing=10,
                horizontal_alignment="center",  # Changed from ft.CrossAxisAlignment.CENTER
            ),
            width=float('inf'),
        )
    
    def _create_piece_button(self, label, piece_type):
        """Create a button for a piece type."""
        return ft.ElevatedButton(
            text=label,  # Changed from positional parameter to text
            on_click=lambda e: self._on_piece_click(e, piece_type),
        )
    
    def _on_piece_click(self, e, piece_type):
        """Handle piece button click."""
        piece = None
        
        if piece_type == PieceType.STRAIGHT:
            piece = StraightPiece(length=12)  # 12 inches
        elif piece_type == PieceType.ELBOW_90:
            piece = ElbowPiece(angle=90)
        elif piece_type == PieceType.ELBOW_45:
            piece = ElbowPiece(angle=45)
        elif piece_type == PieceType.ELBOW_22:
            piece = ElbowPiece(angle=22.5)
        elif piece_type == PieceType.TEE:
            piece = TeePiece()
        
        if piece and self.on_piece_selected:
            self.on_piece_selected(piece)
    
    def _on_rotate_click(self, e):
        """Handle rotate button click."""
        pass  # TODO: Implement rotation of selected piece
    
    def _on_flip_click(self, e):
        """Handle flip button click."""
        pass  # TODO: Implement flipping of selected piece
    
    def _on_bom_click(self, e):
        """Handle BOM button click."""
        pass  # TODO: Show BOM dialog