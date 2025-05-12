import flet as ft
import sys
import traceback
import json
from models.track import Track, LengthValue
from models.piece import PieceType, StraightPiece, ElbowPiece, TeePiece

def main(page: ft.Page):
    page.title = "Gutter Track Planner"
    page.theme_mode = "dark"
    
    # Track state
    track = None
    pieces = []
    selected_piece = None
    selected_index = -1
    piece_count_text = None
    
    # Input fields
    width_ft = ft.TextField(value="80", label="Width (feet)", width=100)
    width_in = ft.TextField(value="0", label="Width (inches)", width=100)
    depth_ft = ft.TextField(value="40", label="Depth (feet)", width=100)
    depth_in = ft.TextField(value="0", label="Depth (inches)", width=100)
    lane_ft = ft.TextField(value="6", label="Lane Width (feet)", width=100)
    lane_in = ft.TextField(value="0", label="Lane Width (inches)", width=100)
    
    # Status text
    status = ft.Text("Enter dimensions and click Create")
    
    # Piece display list
    piece_list = ft.ListView(
        expand=1,
        spacing=10,
        padding=20,
    )
    
    # Position controls
    position_x = ft.Slider(
        min=0,
        max=20,
        divisions=20,
        label="X: {value}",
        value=1,
        on_change=lambda e: update_position(),
    )
    
    position_y = ft.Slider(
        min=0,
        max=20,
        divisions=20,
        label="Y: {value}",
        value=1,
        on_change=lambda e: update_position(),
    )
    
    rotation_slider = ft.Slider(
        min=0,
        max=270,
        divisions=3,
        label="Rotation: {value}°",
        value=0,
        on_change=lambda e: update_rotation(),
    )
    
    # Editing controls container
    editing_controls = ft.Container(
        content=ft.Column([
            ft.Text("No piece selected", size=16, weight="bold"),
            ft.Row([
                ft.Text("Position X:"),
                position_x,
            ]),
            ft.Row([
                ft.Text("Position Y:"),
                position_y,
            ]),
            ft.Row([
                ft.Text("Rotation:"),
                rotation_slider,
            ]),
            ft.Row([
                ft.ElevatedButton(
                    text="Flip Piece",
                    on_click=lambda e: flip_selected_piece(),
                ),
                ft.ElevatedButton(
                    text="Delete Piece",
                    on_click=lambda e: delete_selected_piece(),
                ),
            ]),
        ]),
        visible=False,  # Hidden until a piece is selected
        padding=10,
        bgcolor="#2D2D2D",
        border_radius=10,
    )
    
    # Track view with info
    track_info = ft.Container(
        content=ft.Text("Create a track to begin"),
        padding=20,
        bgcolor="#1E1E1E",
        border_radius=10,
        width=800,
    )
    
    # Simple grid visualization
    grid_view = ft.Container(
        content=ft.Column([
            ft.Text("Track layout will appear here"),
        ]),
        padding=20,
        bgcolor="#1E1E1E",
        border_radius=10,
        width=800,
        height=400,
    )
    
    # Update position function
    def update_position():
        if selected_piece and selected_index >= 0:
            selected_piece.position = (position_x.value, position_y.value)
            update_visualization()
    
    # Update rotation function
    def update_rotation():
        if selected_piece and selected_index >= 0:
            selected_piece.rotation = rotation_slider.value
            update_visualization()
    
    # Flip selected piece function
    def flip_selected_piece():
        if selected_piece and selected_index >= 0:
            selected_piece.flipped = not selected_piece.flipped
            update_visualization()
    
    # Delete selected piece function
    def delete_selected_piece():
        nonlocal selected_piece, selected_index
        if selected_piece and selected_index >= 0:
            pieces.pop(selected_index)
            selected_piece = None
            selected_index = -1
            editing_controls.visible = False
            update_visualization()
    
    # Select piece function
    def select_piece(index):
        nonlocal selected_piece, selected_index
        
        # Deselect if already selected
        if selected_index == index:
            selected_piece = None
            selected_index = -1
            editing_controls.visible = False
        else:
            selected_piece = pieces[index]
            selected_index = index
            
            # Update controls to match piece
            position_x.value = selected_piece.position[0]
            position_y.value = selected_piece.position[1]
            rotation_slider.value = selected_piece.rotation
            
            # Show editing controls
            editing_controls.content.controls[0].value = f"Editing {selected_piece.piece_type.value}"
            editing_controls.visible = True
        
        update_visualization()
    
    # Update visualization function
    def update_visualization():
        if not track:
            return
            
        # Update piece count
        if piece_count_text:
            piece_count_text.value = f"Piece count: {len(pieces)}"
        
        # Clear piece list
        piece_list.controls.clear()
        
        # Add pieces to list
        for i, piece in enumerate(pieces):
            is_selected = (i == selected_index)
            
            # Create piece representation
            piece_item = ft.Container(
                content=ft.Row([
                    ft.Icon(
                        name="check_box" if is_selected else "check_box_outline_blank",
                        color="#9C27B0" if is_selected else "#9E9E9E",
                    ),
                    ft.Column([
                        ft.Text(f"{piece.piece_type.value.capitalize()}", weight="bold"),
                        ft.Text(f"Position: ({piece.position[0]}, {piece.position[1]})"),
                        ft.Text(f"Rotation: {piece.rotation}°, Flipped: {piece.flipped}"),
                    ]),
                ]),
                bgcolor="#333333" if is_selected else "transparent",
                border_radius=5,
                padding=10,
                on_click=lambda e, i=i: select_piece(i),
            )
            
            piece_list.controls.append(piece_item)
        
        page.update()
    
    # Create track function
    def create_track(e):
        try:
            # Get values
            w_ft = int(width_ft.value or 0)
            w_in = int(width_in.value or 0)
            d_ft = int(depth_ft.value or 0)
            d_in = int(depth_in.value or 0)
            l_ft = int(lane_ft.value or 0)
            l_in = int(lane_in.value or 0)
            
            # Create track
            nonlocal track, pieces, piece_count_text, selected_piece, selected_index
            track = Track(
                LengthValue(w_ft, w_in),
                LengthValue(d_ft, d_in),
                LengthValue(l_ft, l_in)
            )
            pieces = []
            selected_piece = None
            selected_index = -1
            editing_controls.visible = False
            
            # Update track info
            track_info.content = ft.Column([
                ft.Text(f"Track dimensions:", size=16, weight="bold"),
                ft.Text(f"Width: {w_ft}' {w_in}\" ({track.width.total_inches} inches)"),
                ft.Text(f"Depth: {d_ft}' {d_in}\" ({track.depth.total_inches} inches)"),
                ft.Text(f"Lane Width: {l_ft}' {l_in}\" ({track.lane_width.total_inches} inches)"),
            ])
            
            # Create piece count text
            piece_count_text = ft.Text("Piece count: 0")
            
            # Update grid view
            grid_view.content = ft.Column([
                piece_count_text,
                ft.Divider(),
                piece_list,
            ])
            
            status.value = f"Track created with dimensions {w_ft}'{w_in}\" × {d_ft}'{d_in}\""
            update_visualization()
            
        except Exception as e:
            status.value = f"Error: {str(e)}"
            print(f"Error: {str(e)}\n{traceback.format_exc()}", file=sys.stderr)
            page.update()
    
    # Add piece function
    def add_piece(piece_type):
        if not track:
            status.value = "Create a track first"
            page.update()
            return
        
        try:
            # Create the piece
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
            
            if piece:
                # Set initial position (using slider values)
                piece.position = (position_x.value, position_y.value)
                
                # Add to pieces list
                pieces.append(piece)
                
                # Select the new piece
                nonlocal selected_piece, selected_index
                selected_piece = piece
                selected_index = len(pieces) - 1
                
                # Show editing controls
                editing_controls.content.controls[0].value = f"Editing {piece.piece_type.value}"
                editing_controls.visible = True
                
                status.value = f"Added {piece_type.value} piece"
                update_visualization()
                
        except Exception as e:
            status.value = f"Error adding piece: {str(e)}"
            print(f"Error: {str(e)}\n{traceback.format_exc()}", file=sys.stderr)
            page.update()
    
    # Save design function
    def save_design():
        if not track:
            status.value = "Create a track first"
            page.update()
            return
            
        try:
            # Create design data
            design = {
                "track": {
                    "width": {
                        "feet": track.width.feet,
                        "inches": track.width.inches
                    },
                    "depth": {
                        "feet": track.depth.feet,
                        "inches": track.depth.inches
                    },
                    "lane_width": {
                        "feet": track.lane_width.feet,
                        "inches": track.lane_width.inches
                    }
                },
                "pieces": []
            }
            
            # Add pieces
            for piece in pieces:
                piece_data = {
                    "type": piece.piece_type.value,
                    "position": piece.position,
                    "rotation": piece.rotation,
                    "flipped": piece.flipped
                }
                
                # Add type-specific properties
                if piece.piece_type == PieceType.STRAIGHT:
                    piece_data["length"] = piece.length
                elif "elbow" in piece.piece_type.value:
                    piece_data["angle"] = piece.angle
                
                design["pieces"].append(piece_data)
            
            # Create save dialog
            design_json = json.dumps(design, indent=2)
            
            save_dialog = ft.AlertDialog(
                title=ft.Text("Save Design"),
                content=ft.Column([
                    ft.Text("Copy the JSON below to save your design:"),
                    ft.Container(
                        content=ft.TextField(
                            value=design_json,
                            multiline=True,
                            read_only=True,
                            min_lines=10,
                            max_lines=15,
                        ),
                        width=400,
                    ),
                ]),
                actions=[
                    ft.TextButton("Close", on_click=lambda e: close_dialog(save_dialog))
                ],
            )
            
            # Show dialog
            page.dialog = save_dialog
            save_dialog.open = True
            page.update()
            
            status.value = "Design saved as JSON"
            
        except Exception as e:
            status.value = f"Error saving design: {str(e)}"
            print(f"Error: {str(e)}\n{traceback.format_exc()}", file=sys.stderr)
            page.update()
    
    # Load design function
    def load_design():
        try:
            # Create load dialog
            load_text_field = ft.TextField(
                hint_text="Paste design JSON here",
                multiline=True,
                min_lines=10,
                max_lines=15,
            )
            
            def do_load(e):
                try:
                    # Parse JSON
                    design_json = load_text_field.value
                    design = json.loads(design_json)
                    
                    # Create track
                    nonlocal track, pieces, selected_piece, selected_index
                    track = Track(
                        LengthValue(
                            design["track"]["width"]["feet"],
                            design["track"]["width"]["inches"]
                        ),
                        LengthValue(
                            design["track"]["depth"]["feet"],
                            design["track"]["depth"]["inches"]
                        ),
                        LengthValue(
                            design["track"]["lane_width"]["feet"],
                            design["track"]["lane_width"]["inches"]
                        )
                    )
                    
                    # Update input fields
                    width_ft.value = str(track.width.feet)
                    width_in.value = str(track.width.inches)
                    depth_ft.value = str(track.depth.feet)
                    depth_in.value = str(track.depth.inches)
                    lane_ft.value = str(track.lane_width.feet)
                    lane_in.value = str(track.lane_width.inches)
                    
                    # Create pieces
                    pieces = []
                    for piece_data in design["pieces"]:
                        piece = None
                        
                        # Create piece based on type
                        if piece_data["type"] == "straight":
                            piece = StraightPiece(length=piece_data.get("length", 12))
                        elif piece_data["type"] == "elbow_90":
                            piece = ElbowPiece(angle=90)
                        elif piece_data["type"] == "elbow_45":
                            piece = ElbowPiece(angle=45)
                        elif piece_data["type"] == "elbow_22":
                            piece = ElbowPiece(angle=22.5)
                        elif piece_data["type"] == "tee":
                            piece = TeePiece()
                        
                        if piece:
                            # Set properties
                            piece.position = tuple(piece_data["position"])
                            piece.rotation = piece_data["rotation"]
                            piece.flipped = piece_data["flipped"]
                            
                            # Add to pieces list
                            pieces.append(piece)
                    
                    # Reset selection
                    selected_piece = None
                    selected_index = -1
                    editing_controls.visible = False
                    
                    # Update track info
                    track_info.content = ft.Column([
                        ft.Text(f"Track dimensions:", size=16, weight="bold"),
                        ft.Text(f"Width: {track.width.feet}' {track.width.inches}\" ({track.width.total_inches} inches)"),
                        ft.Text(f"Depth: {track.depth.feet}' {track.depth.inches}\" ({track.depth.total_inches} inches)"),
                        ft.Text(f"Lane Width: {track.lane_width.feet}' {track.lane_width.inches}\" ({track.lane_width.total_inches} inches)"),
                    ])
                    
                    # Create piece count text
                    nonlocal piece_count_text
                    piece_count_text = ft.Text("Piece count: 0")
                    
                    # Update grid view
                    grid_view.content = ft.Column([
                        piece_count_text,
                        ft.Divider(),
                        piece_list,
                    ])
                    
                    status.value = "Design loaded successfully"
                    update_visualization()
                    
                    # Close dialog
                    load_dialog.open = False
                    page.update()
                    
                except Exception as e:
                    status.value = f"Error loading design: {str(e)}"
                    print(f"Error: {str(e)}\n{traceback.format_exc()}", file=sys.stderr)
                    page.update()
            
            load_dialog = ft.AlertDialog(
                title=ft.Text("Load Design"),
                content=ft.Column([
                    ft.Text("Paste your design JSON below:"),
                    load_text_field,
                ]),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: close_dialog(load_dialog)),
                    ft.TextButton("Load", on_click=do_load),
                ],
            )
            
            # Show dialog
            page.dialog = load_dialog
            load_dialog.open = True
            page.update()
            
        except Exception as e:
            status.value = f"Error loading design: {str(e)}"
            print(f"Error: {str(e)}\n{traceback.format_exc()}", file=sys.stderr)
            page.update()
    
    # Calculate BOM function
    def calculate_bom():
        if not track or not pieces:
            status.value = "No track or pieces to calculate"
            page.update()
            return
        
        # Calculate BOM
        straight_count = sum(1 for p in pieces if p.piece_type == PieceType.STRAIGHT)
        elbow_90_count = sum(1 for p in pieces if p.piece_type == PieceType.ELBOW_90)
        elbow_45_count = sum(1 for p in pieces if p.piece_type == PieceType.ELBOW_45) 
        elbow_22_count = sum(1 for p in pieces if p.piece_type == PieceType.ELBOW_22)
        tee_count = sum(1 for p in pieces if p.piece_type == PieceType.TEE)
        
        # Calculate straight footage (12 inches per straight piece)
        straight_footage = sum(p.length/12 for p in pieces if p.piece_type == PieceType.STRAIGHT)
        
        # Calculate connectors and screws
        connector_count = max(0, len(pieces) - 1)
        screw_count = (
            int(straight_footage * 2) +
            elbow_22_count * 2 +
            elbow_45_count * 2 +
            elbow_90_count * 2 +
            tee_count * 3
        )
        
        # Create BOM dialog
        bom_dialog = ft.AlertDialog(
            title=ft.Text("Bill of Materials"),
            content=ft.Column([
                ft.Text("Track Components:", weight="bold"),
                ft.Text(f"Straight gutter: {straight_footage:.1f} feet"),
                ft.Text(f"90° Elbows: {elbow_90_count}"),
                ft.Text(f"45° Elbows: {elbow_45_count}"),
                ft.Text(f"22.5° Elbows: {elbow_22_count}"),
                ft.Text(f"T-Junctions: {tee_count}"),
                ft.Divider(),
                ft.Text("Hardware:", weight="bold"),
                ft.Text(f"Connectors: {connector_count}"),
                ft.Text(f"Screws: {screw_count}"),
                ft.Divider(),
                ft.Text(f"Total pieces: {len(pieces)}")
            ]),
            actions=[
                ft.TextButton("Close", on_click=lambda e: close_dialog(bom_dialog))
            ]
        )
        
        # Show dialog
        page.dialog = bom_dialog
        bom_dialog.open = True
        page.update()
    
    def close_dialog(dialog):
        dialog.open = False
        page.update()
    
    # Create button
    create_button = ft.ElevatedButton(
        text="Create Track",
        on_click=create_track
    )
    
    # Piece buttons
    straight_button = ft.ElevatedButton(
        text="Add Straight",
        on_click=lambda e: add_piece(PieceType.STRAIGHT)
    )
    
    elbow90_button = ft.ElevatedButton(
        text="Add 90° Elbow",
        on_click=lambda e: add_piece(PieceType.ELBOW_90)
    )
    
    elbow45_button = ft.ElevatedButton(
        text="Add 45° Elbow",
        on_click=lambda e: add_piece(PieceType.ELBOW_45)
    )
    
    elbow22_button = ft.ElevatedButton(
        text="Add 22.5° Elbow",
        on_click=lambda e: add_piece(PieceType.ELBOW_22)
    )
    
    tee_button = ft.ElevatedButton(
        text="Add T-Junction",
        on_click=lambda e: add_piece(PieceType.TEE)
    )
    
    # File operations buttons
    save_button = ft.ElevatedButton(
        text="Save Design",
        on_click=lambda e: save_design()
    )
    
    load_button = ft.ElevatedButton(
        text="Load Design",
        on_click=lambda e: load_design()
    )
    
    bom_button = ft.ElevatedButton(
        text="Bill of Materials",
        on_click=lambda e: calculate_bom()
    )
    
    # Build the page
    page.add(
        ft.Text("Gutter Track Planner", size=24, text_align="center"),
        
        # Input form
        ft.Row([
            ft.Column([
                ft.Text("Width:", width=100),
                ft.Text("Depth:", width=100),
                ft.Text("Lane Width:", width=100),
            ]),
            ft.Column([
                width_ft,
                depth_ft,
                lane_ft,
            ]),
            ft.Column([
                ft.Text("feet"),
                ft.Text("feet"),
                ft.Text("feet"),
            ]),
            ft.Column([
                width_in,
                depth_in,
                lane_in,
            ]),
            ft.Column([
                ft.Text("inches"),
                ft.Text("inches"),
                ft.Text("inches"),
            ]),
        ]),
        
        # Create button
        create_button,
        status,
        
        # Track info
        track_info,
        
        # Grid visualization and editing
        ft.Row([
            # Main grid view
            grid_view,
            
            # Editing controls
            editing_controls,
        ]),
        
        # Piece buttons
        ft.Row([
            straight_button,
            elbow90_button,
            elbow45_button,
            elbow22_button,
            tee_button,
        ], alignment="center"),
        
        # File and BOM operations
        ft.Row([
            save_button,
            load_button,
            bom_button,
        ], alignment="center"),
    )

# Run the app
print("Starting enhanced Gutter Track Planner...")
ft.app(target=main)
print("App closed")