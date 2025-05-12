import flet as ft
from models.piece import PieceType, StraightPiece, ElbowPiece, TeePiece

class PieceToolbar(ft.Control):
    def _get_control_name(self):
        return "piece-toolbar"
    
    def __init__(self, on_piece_selected):
        super().__init__()
        self.on_piece_selected = on_piece_selected
    
    def build(self):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Track Pieces", size=16, weight="bold"),
                    ft.Divider(),
                    ft.Row([
                        ft.ElevatedButton(
                            text="Straight",
                            on_click=lambda e: self._on_piece_click(e, PieceType.STRAIGHT)
                        ),
                        ft.ElevatedButton(
                            text="Elbow 90°",
                            on_click=lambda e: self._on_piece_click(e, PieceType.ELBOW_90)
                        ),
                        ft.ElevatedButton(
                            text="Elbow 45°",
                            on_click=lambda e: self._on_piece_click(e, PieceType.ELBOW_45)
                        ),
                        ft.ElevatedButton(
                            text="Elbow 22.5°",
                            on_click=lambda e: self._on_piece_click(e, PieceType.ELBOW_22)
                        ),
                        ft.ElevatedButton(
                            text="T-Junction",
                            on_click=lambda e: self._on_piece_click(e, PieceType.TEE)
                        ),
                    ], alignment="center", spacing=10),
                    ft.Row([
                        ft.ElevatedButton(
                            text="Rotate",
                            on_click=self._on_rotate_click,
                        ),
                        ft.ElevatedButton(
                            text="Flip",
                            on_click=self._on_flip_click,
                        ),
                    ], alignment="center", spacing=10),
                ], spacing=10, horizontal_alignment="center"),
                padding=10,
            ),
            width=float('inf'),
        )
    
    def _on_piece_click(self, e, piece_type):
        piece = None
        
        if piece_type == PieceType.STRAIGHT:
            piece = StraightPiece(length=12)
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
        # This would need to be connected to the selected piece
        pass
    
    def _on_flip_click(self, e):
        # This would need to be connected to the selected piece
        pass