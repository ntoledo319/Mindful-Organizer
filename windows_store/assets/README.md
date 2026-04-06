# Mindful Organizer - Asset Requirements

This document specifies all visual assets required for the Windows Store (MSIX) package and Store listing. Every asset listed below must be created and placed in this directory before building the MSIX package.

## Design Guidelines

### Color Palette

| Color          | Hex       | Usage                                    |
|----------------|-----------|------------------------------------------|
| Ocean Blue     | `#3A7CA5` | Primary brand color, tile backgrounds    |
| Deep Blue      | `#2C5F7C` | Darker accents, text on light surfaces   |
| Sage Green     | `#6B9F78` | Secondary accent, wellness indicators    |
| Soft Lavender  | `#9B8EC4` | Tertiary accent, meditation features     |
| Cloud White    | `#F7F9FC` | Backgrounds, negative space              |
| Charcoal       | `#2D3748` | Primary text                             |

### Logo Concept

The Mindful Organizer logo features a **stylized brain with a leaf or small plant growing from the top**, representing mental health growth, resilience, and the nurturing of one's well-being through organization. The brain outline uses the Ocean Blue color, while the leaf/plant element uses Sage Green, symbolizing the organic connection between mental clarity and personal growth.

The logo should:
- Be simple enough to remain recognizable at 16x16 pixels
- Use clean vector lines with no fine detail that is lost at small sizes
- Feature the brain-leaf icon mark alone for square icons (no text)
- Optionally include the wordmark "Mindful Organizer" for wide/banner formats
- Use a transparent background for all icon files
- Avoid gradients in small sizes (44x44 and below); solid colors only

### File Format

- **Format:** PNG with transparency (RGBA)
- **Color depth:** 32-bit
- **Background:** Transparent (the manifest specifies `#3A7CA5` as the background fill color for tiles)
- **Anti-aliasing:** Enabled for all sizes

## Required Assets

### App Icons (Square44x44Logo)

Used for the taskbar, Start menu small icon, and app list.

| Filename                             | Dimensions  | Scale  | Notes                                 |
|--------------------------------------|-------------|--------|---------------------------------------|
| `Square44x44Logo.scale-100.png`      | 44 x 44     | 100%   | Base size                             |
| `Square44x44Logo.scale-125.png`      | 55 x 55     | 125%   |                                       |
| `Square44x44Logo.scale-150.png`      | 66 x 66     | 150%   |                                       |
| `Square44x44Logo.scale-200.png`      | 88 x 88     | 200%   |                                       |
| `Square44x44Logo.scale-400.png`      | 176 x 176   | 400%   |                                       |
| `Square44x44Logo.targetsize-16.png`  | 16 x 16     | --     | Unplated, for small contexts          |
| `Square44x44Logo.targetsize-24.png`  | 24 x 24     | --     | Unplated                              |
| `Square44x44Logo.targetsize-32.png`  | 32 x 32     | --     | Unplated                              |
| `Square44x44Logo.targetsize-48.png`  | 48 x 48     | --     | Unplated                              |
| `Square44x44Logo.targetsize-256.png` | 256 x 256   | --     | Unplated, used in Alt+Tab and others  |

### Medium Tile (Square150x150Logo)

Used for the medium Start menu tile.

| Filename                              | Dimensions  | Scale  |
|---------------------------------------|-------------|--------|
| `Square150x150Logo.scale-100.png`     | 150 x 150   | 100%   |
| `Square150x150Logo.scale-125.png`     | 188 x 188   | 125%   |
| `Square150x150Logo.scale-150.png`     | 225 x 225   | 150%   |
| `Square150x150Logo.scale-200.png`     | 300 x 300   | 200%   |
| `Square150x150Logo.scale-400.png`     | 600 x 600   | 400%   |

### Wide Tile (Wide310x150Logo)

Used for the wide Start menu tile. Can include the logo icon on the left with the app name on the right.

| Filename                              | Dimensions  | Scale  |
|---------------------------------------|-------------|--------|
| `Wide310x150Logo.scale-100.png`       | 310 x 150   | 100%   |
| `Wide310x150Logo.scale-125.png`       | 388 x 188   | 125%   |
| `Wide310x150Logo.scale-150.png`       | 465 x 225   | 150%   |
| `Wide310x150Logo.scale-200.png`       | 620 x 300   | 200%   |
| `Wide310x150Logo.scale-400.png`       | 1240 x 600  | 400%   |

### Large Tile (Square310x310Logo)

Used for the large Start menu tile. Display the brain-leaf logo centered with optional app name below.

| Filename                              | Dimensions  | Scale  |
|---------------------------------------|-------------|--------|
| `Square310x310Logo.scale-100.png`     | 310 x 310   | 100%   |
| `Square310x310Logo.scale-125.png`     | 388 x 388   | 125%   |
| `Square310x310Logo.scale-150.png`     | 465 x 465   | 150%   |
| `Square310x310Logo.scale-200.png`     | 620 x 620   | 200%   |
| `Square310x310Logo.scale-400.png`     | 1240 x 1240 | 400%   |

### Small Tile (Square71x71Logo)

Used for the small Start menu tile.

| Filename                              | Dimensions  | Scale  |
|---------------------------------------|-------------|--------|
| `Square71x71Logo.scale-100.png`       | 71 x 71     | 100%   |
| `Square71x71Logo.scale-125.png`       | 89 x 89     | 125%   |
| `Square71x71Logo.scale-150.png`       | 107 x 107   | 150%   |
| `Square71x71Logo.scale-200.png`       | 142 x 142   | 200%   |
| `Square71x71Logo.scale-400.png`       | 284 x 284   | 400%   |

### Store Logo (StoreLogo)

Displayed in the Microsoft Store and in the app's properties in Settings.

| Filename                        | Dimensions  | Scale  |
|---------------------------------|-------------|--------|
| `StoreLogo.scale-100.png`       | 50 x 50     | 100%   |
| `StoreLogo.scale-125.png`       | 63 x 63     | 125%   |
| `StoreLogo.scale-150.png`       | 75 x 75     | 150%   |
| `StoreLogo.scale-200.png`       | 100 x 100   | 200%   |
| `StoreLogo.scale-400.png`       | 200 x 200   | 400%   |
| `StoreLogo.png`                 | 50 x 50     | Default fallback referenced in manifest |

### Badge Logo (BadgeLogo)

Shown on lock screen notifications. Must be monochrome (white on transparent).

| Filename                        | Dimensions  | Scale  | Notes                        |
|---------------------------------|-------------|--------|------------------------------|
| `BadgeLogo.scale-100.png`       | 24 x 24     | 100%   | White on transparent only    |
| `BadgeLogo.scale-125.png`       | 30 x 30     | 125%   |                              |
| `BadgeLogo.scale-150.png`       | 36 x 36     | 150%   |                              |
| `BadgeLogo.scale-200.png`       | 48 x 48     | 200%   |                              |
| `BadgeLogo.scale-400.png`       | 96 x 96     | 400%   |                              |
| `BadgeLogo.png`                 | 24 x 24     | Default fallback referenced in manifest |

**Badge logo rules:**
- Must use only white (`#FFFFFF`) pixels on a fully transparent background
- Windows applies the tile background color behind it
- Keep the design extremely simple -- a minimal brain-leaf silhouette works best

### Splash Screen (SplashScreen)

Displayed during app launch.

| Filename                         | Dimensions  | Scale  |
|----------------------------------|-------------|--------|
| `SplashScreen.scale-100.png`     | 620 x 300   | 100%   |
| `SplashScreen.scale-125.png`     | 775 x 375   | 125%   |
| `SplashScreen.scale-150.png`     | 930 x 450   | 150%   |
| `SplashScreen.scale-200.png`     | 1240 x 600  | 200%   |
| `SplashScreen.scale-400.png`     | 2480 x 1200 | 400%   |
| `SplashScreen.png`               | 620 x 300   | Default fallback referenced in manifest |

**Splash screen guidelines:**
- Center the brain-leaf logo with "Mindful Organizer" text below it
- Keep essential content within the center 400x200 area (at 100% scale)
- Transparent background (the manifest sets `#3A7CA5` as the fill)

### File Type Icon (FileTypeLogo)

Associated with `.mindful` project files in Windows Explorer.

| Filename                          | Dimensions  | Notes                          |
|-----------------------------------|-------------|--------------------------------|
| `FileTypeLogo.scale-100.png`      | 44 x 44     | Displayed in Explorer          |
| `FileTypeLogo.targetsize-16.png`  | 16 x 16     | Small icon view                |
| `FileTypeLogo.targetsize-32.png`  | 32 x 32     | Medium icon view               |
| `FileTypeLogo.targetsize-48.png`  | 48 x 48     | Large icon view                |
| `FileTypeLogo.targetsize-256.png` | 256 x 256   | Extra large / thumbnail view   |
| `FileTypeLogo.png`                | 44 x 44     | Default fallback               |

**File type icon guidelines:**
- Use the brain-leaf logo with a document/page shape behind or beneath it
- Clearly distinguishable from the main app icon at small sizes
- Include a small `.mindful` text label on the 256px version

### Application Icon (ICO format)

Used by PyInstaller for the Windows executable icon.

| Filename        | Format | Contents                                                        |
|-----------------|--------|-----------------------------------------------------------------|
| `app_icon.ico`  | ICO    | Multi-resolution: 16, 24, 32, 48, 64, 128, 256 px (all in one) |

**ICO file requirements:**
- Must contain all standard sizes in a single `.ico` container
- Each size should be 32-bit RGBA (with transparency)
- Use a tool like ImageMagick or IcoFX to bundle multiple PNGs into one ICO

### Store Listing Screenshots

These are not part of the MSIX package but are required for the Store submission.

| Filename               | Dimensions    | Description                              |
|------------------------|---------------|------------------------------------------|
| `screenshot_01.png`    | 1920 x 1080   | Main dashboard view                     |
| `screenshot_02.png`    | 1920 x 1080   | Wellness tracker interface              |
| `screenshot_03.png`    | 1920 x 1080   | Smart file organization view            |
| `screenshot_04.png`    | 1920 x 1080   | Focus session timer                     |
| `screenshot_05.png`    | 1920 x 1080   | Guided meditation selection             |
| `screenshot_06.png`    | 1920 x 1080   | Visualization dashboard                 |
| `screenshot_07.png`    | 1920 x 1080   | Data management and settings            |
| `screenshot_08.png`    | 1920 x 1080   | Project file management                 |

**Screenshot guidelines:**
- Capture at 1920x1080 (16:9) resolution
- Show realistic sample data (not empty states)
- No personal or identifying information in sample data
- Clean Windows desktop with no distracting background elements

## Asset Checklist

Before building the MSIX package, verify that the following minimum set of files exists in this directory:

- [ ] `Square44x44Logo.png` (or scaled variants)
- [ ] `Square150x150Logo.png` (or scaled variants)
- [ ] `Wide310x150Logo.png` (or scaled variants)
- [ ] `Square310x310Logo.png` (or scaled variants)
- [ ] `Square71x71Logo.png` (or scaled variants)
- [ ] `StoreLogo.png` (or scaled variants)
- [ ] `BadgeLogo.png` (or scaled variants)
- [ ] `SplashScreen.png` (or scaled variants)
- [ ] `FileTypeLogo.png` (or scaled variants)
- [ ] `app_icon.ico`

At minimum, provide the base (scale-100) version of each asset. Scaled variants are recommended for sharp rendering on high-DPI displays.
