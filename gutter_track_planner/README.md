# GutterTrack Designer

A mobile-first progressive web app (PWA) for designing indoor RC tracks using standard 2" × 2" downspout gutter pieces. Built with Flet, which compiles to Flutter for smooth drag-and-drop interactions and packages to a PWA with one command.

![GutterTrack Designer Logo](https://via.placeholder.com/300x150?text=GutterTrack+Designer)

## Features

- **Enter dimensions** - Specify overall track width × depth and minimum lane width
- **Grid & snapping** - Snap-to grid ensures perfect piece alignment
- **Drag-and-drop parts** - Includes variable-length straights, elbows (22.5°, 45°, 90°), and T-fittings
- **Live bill of materials** - Instant updates showing materials needed for your track
- **Offline & installable** - Works with no network after first visit
- **One-click deploy** - Easy deployment to any static host

## Installation

### Prerequisites

- Python 3.7+
- Flet 0.28.2

```bash
# Install dependencies
pip install flet==0.28.2
```

### Running locally

```bash
# Clone the repository
git clone https://github.com/modernn/GutterTrack.git
cd GutterTrack/gutter_track_planner

# Run the app
python main.py
```

### Building for web

```bash
# Package as PWA
flet pack main.py --pwa
```

This will generate a `build` directory with the compiled PWA that can be deployed to any static hosting service.

## Usage

1. **Launch the app** and enter your track dimensions in the setup dialog
2. **Select a piece type** from the palette at the bottom/side of the screen
3. **Click on the grid** to place pieces
4. **Select existing pieces** to rotate or modify their properties
5. **View the bill of materials** to see what parts you need to order
6. **Save your track** for later use, or export it to share with others

## Technology Stack

| Layer | Tech | Reason |
|-------|------|--------|
| UI & PWA | Flet (Flutter-powered) | Native-grade touch, single Python codebase, sub-5 MB web build |
| UI Components | Flutter Containers, Rows, Columns | High-performance layout with responsive design |
| Snap logic | Grid-based cell calculation | Keeps lanes uniformly wide |
| BOM API | Internal Python calculation | Fast, type-safe calculation of required materials |
| Hosting | Any static host + PWA | Simple deployment and global edge caching |

## Project Structure

```
gutter_track_planner/
├── main.py           # Main application entry point
├── models.py         # Data models for Track, Piece, BOM, etc.
├── views.py          # UI components
├── utils.py          # Helper functions
├── persistence.py    # Track saving and loading
├── api.py            # BOM calculation API
└── README.md         # Documentation
```

## Technical Considerations

This project has been carefully designed to work with Flet 0.28.2, which has several important constraints:

- No `ft.Canvas` support (visualization uses containers instead)
- All custom controls must implement a `_get_control_name()` method
- Special handling for dialog callbacks using deferred execution
- Mobile-first approach with responsive layouts

## Development Roadmap

- [ ] Add support for curved pieces
- [ ] Implement actual drag-and-drop (currently uses click-to-place)
- [ ] Add 3D visualization option
- [ ] Support track elevation changes
- [ ] Add track validation to check for impossible layouts

## Why It Matters

- **Mobile usability first** - Optimized for touch and installs like a native app on iOS/Android
- **Accurate materials planning** - Uses real gutter part SKUs to remove guesswork and reduce over-ordering
- **Zero learning curve** - Imperial units everywhere and a Lego-style interface make it approachable for hobbyists
- **Future-proof** - The same codebase can later be wrapped as an APK/IPA if needed

## License

MIT License - See LICENSE file for details.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

```