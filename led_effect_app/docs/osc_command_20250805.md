# LED Animation System - OSC Commands Reference

## OSC Commands Overview

## **Led Playback Animation Engine - Existing Commands (UNCHANGED)**
### **Parameter Scale Reference**

| Parameter Type | Scale | Data Type | Range | Example |
|----------------|-------|-----------|-------|---------|
| **Dimmer Brightness** | 0-100 | `int` | Integer percentage | `100` = full brightness |
| **Transparency** | 0.0-1.0 | `float` | Float ratio | `0.2` = 80% opacity |
| **RGB Colors** | 0-255 | `int` | RGB standard | `255` = max color value |
| **Master Brightness** | 0-255 | `int` | RGB standard | `200` = bright setting |
| **Speed Percent** | 0-1023 | `int` | Percentage | `150` = 150% speed |
| **Duration** | milliseconds | `int` | Time units | `2500` = 2.5 seconds |

### **Scale Conversion Examples:**
```bash
# Dimmer brightness (0-100 integer)
/create_dimmer 5 1000 100 25           # 100% → 25% brightness

# Transparency (0.0-1.0 float)
/update_segment 5 transparency 0 0.75  # 75% opacity (25% transparent)

# Master brightness (0-255 RGB scale)
/master_brightness 191                 # 75% of max brightness (191/255)
```

### **JSON Output Format:**
```json
{
  "dimmer_time": [
    [1000, 100, 25]    // [duration_ms, start_brightness(0-100), end_brightness(0-100)]
  ],
  "transparency": [0.75, 0.8, 0.6],  // float values 0.0-1.0
  "color": [255, 128, 64]            // RGB values 0-255
}
```

| Command | Parameters | Description | Example |
|---------|------------|-------------|---------|
| `/load_json` | `<file_path:string>` | Load scene data from JSON file | `/load_json "scenes/show1.json"` |
| `/change_scene` | `<scene_id:int>` | Switch to specified scene (0-origin) | `/change_scene 0` |
| `/change_effect` | `<effect_id:int>` | Change active effect (0-origin) | `/change_effect 2` |
| `/change_palette` | `<palette_id:int>` | Change active palette (0-origin) | `/change_palette 1` |

#### **Dissolve & Transitions**
| Command | Parameters | Description | Example |
|---------|------------|-------------|---------|
| `/load_dissolve_json` | `<file_path:string>` | Load dissolve patterns from JSON | `/load_dissolve_json "patterns/dissolve.json"` |
| `/set_dissolve_pattern` | `<pattern_id:int>` | Set active dissolve pattern (0-origin) | `/set_dissolve_pattern 3` |

#### **Global Controls**
| Command | Parameters | Description | Example |
|---------|------------|-------------|---------|
| `/master_brightness` | `<brightness:int>` | Set global brightness (0-255) | `/master_brightness 200` |
| `/set_speed_percent` | `<speed:int>` | Set animation speed (0-1023%) | `/set_speed_percent 150` |

#### **Real-time Color Updates**
| Command | Parameters | Description | Example |
|---------|------------|-------------|---------|
| `/palette/{palette_id}/{color_index}` | `<r:int> <g:int> <b:int>` | Update palette color in real-time | `/palette/0/2 255 128 64` |

**Palette ID Support:**
- **Numeric**: `0`, `1`, `2`, `3`, `4` (0-origin)
- **Letter**: `A`, `B`, `C`, `D`, `E` (legacy support)

**Color Index Range:** `0-5` (6 colors per palette)

---

### **System For Creating Visual Effects - New Commands (CRUD OPERATIONS)**

#### **Query Operations**
| Command | Parameters | Description | Example |
|---------|------------|-------------|---------|
| `/query_full_state` | None | Returns complete system state as JSON for Save | `/query_full_state` |
| `/query_current_state` | None | Returns current scene/effect/palette/segment IDs | `/query_current_state` |

#### **Scene Management (CRUD)**
| Command | Parameters | Description | Example |
|---------|------------|-------------|---------|
| `/create_scene` | `<led_count:int> <fps:int>` | Create new scene with parameters | `/create_scene 300 60` |
| `/delete_scene` | `<scene_id:int>` | Delete specified scene | `/delete_scene 2` |
| `/duplicate_scene` | `<source_id:int>` | Duplicate scene, returns new ID | `/duplicate_scene 1` |
| `/update_scene` | `<scene_id:int> <param:string> <value>` | Update scene parameter | `/update_scene 0 led_count 400` |

**Scene Update Parameters:**
- `led_count <count:int>` - Set LED count
- `fps <fps:int>` - Set frames per second

#### **Effect Management (CRUD)**
| Command | Parameters | Description | Example |
|---------|------------|-------------|---------|
| `/create_effect` | None | Create new effect in current scene | `/create_effect` |
| `/delete_effect` | `<effect_id:int>` | Delete specified effect | `/delete_effect 1` |
| `/duplicate_effect` | `<source_id:int>` | Duplicate effect, returns new ID | `/duplicate_effect 0` |

#### **Palette Management (CRUD)**
| Command | Parameters | Description | Example |
|---------|------------|-------------|---------|
| `/create_palette` | None | Create new palette with default colors | `/create_palette` |
| `/delete_palette` | `<palette_id:int>` | Delete specified palette | `/delete_palette 2` |
| `/duplicate_palette` | `<source_id:int>` | Duplicate palette, returns new ID | `/duplicate_palette 0` |

#### **Segment Management (CRUD)**
| Command | Parameters | Description | Example |
|---------|------------|-------------|---------|
| `/create_segment` | `<custom_id:int>` | Create segment with custom ID | `/create_segment 10` |
| `/delete_segment` | `<segment_id:int>` | Delete specified segment | `/delete_segment 5` |
| `/duplicate_segment` | `<source_id:int>` | Duplicate segment, returns new ID | `/duplicate_segment 3` |
| `/reorder_segment` | `<segment_id:int> <new_position:int>` | Change segment order | `/reorder_segment 5 2` |
| `/update_segment` | `<segment_id:int> <param> <values...>` | Update segment parameter | See examples below |

**Segment Update Parameters:**
```bash
# Control parameters
/update_segment 5 solo 1                    # Solo on/off (1/0)
/update_segment 5 mute 0                    # Mute on/off (1/0)

# Movement parameters (absolute LED positions)
/update_segment 5 move_range 10 50          # Movement range
/update_segment 5 move_speed 1.5            # Movement speed
/update_segment 5 initial_position 25       # Initial position
/update_segment 5 edge_reflect 1            # Edge reflection on/off

# Color composition (per slot)
/update_segment 5 color_slot 0 1 3          # slot_index palette_id color_index
/update_segment 5 transparency 0 0.8        # slot_index transparency_value (0.0-1.0)
/update_segment 5 length 0 10               # slot_index led_count
```

#### **Dimmer Management (CRUD)**
| Command | Parameters | Description | Example |
|---------|------------|-------------|---------|
| `/create_dimmer` | `<segment_id:int> <duration_ms:int> <initial_brightness:int> <final_brightness:int>` | Add dimmer element (duration in ms, brightness 0-100) | `/create_dimmer 5 2500 100 0` |
| `/delete_dimmer` | `<segment_id:int> <index:int>` | Delete dimmer at index | `/delete_dimmer 5 2` |
| `/update_dimmer` | `<segment_id:int> <index:int> <duration_ms:int> <initial_brightness:int> <final_brightness:int>` | Update dimmer element (duration in ms, brightness 0-100) | `/update_dimmer 5 1 3000 80 20` |

---

## **Complete OSC Command Summary**

### **Total Commands Count**
- **Led Playback Animation Engine (Existing)**: 8 commands + 1 pattern command = **9 total**
- **System For Creating Visual Effects (New)**: **21 commands**
- **Grand Total**: **30 OSC commands**

### **Command Categories**

#### **1. File Operations (2 commands)**
- `/load_json` - Load scene data
- `/load_dissolve_json` - Load dissolve patterns

#### **2. Scene Control (3 commands)**
- `/change_scene` - Switch scenes
- `/change_effect` - Switch effects  
- `/change_palette` - Switch palettes

#### **3. Global Parameters (2 commands)**
- `/master_brightness` - Global brightness
- `/set_speed_percent` - Global speed

#### **4. Transitions (1 command)**
- `/set_dissolve_pattern` - Set dissolve pattern

#### **5. Real-time Updates (1 command)**
- `/palette/{id}/{color}` - Real-time color updates

#### **6. Query Operations (2 commands)**
- `/query_full_state` - Get complete state for Save
- `/query_current_state` - Get current selections

#### **7. Scene Management (4 commands)**
- `/create_scene` - Create new scene
- `/delete_scene` - Delete scene
- `/duplicate_scene` - Duplicate scene
- `/update_scene` - Update scene parameters

#### **8. Effect Management (3 commands)**
- `/create_effect` - Create new effect
- `/delete_effect` - Delete effect
- `/duplicate_effect` - Duplicate effect

#### **9. Palette Management (3 commands)**
- `/create_palette` - Create new palette
- `/delete_palette` - Delete palette
- `/duplicate_palette` - Duplicate palette

#### **10. Segment Management (5 commands)**
- `/create_segment` - Create new segment
- `/delete_segment` - Delete segment
- `/duplicate_segment` - Duplicate segment
- `/reorder_segment` - Change segment order
- `/update_segment` - Update segment parameters

#### **11. Dimmer Management (3 commands)**
- `/create_dimmer` - Create dimmer element
- `/delete_dimmer` - Delete dimmer element
- `/update_dimmer` - Update dimmer element

---

## **OSC Message Flow Architecture**

### **GUI → Backend Communication**
```
File Operations:
GUI → /load_json → Backend loads data
GUI → /query_full_state → Backend returns JSON → GUI saves file

CRUD Operations:
GUI → /create_* → Backend creates entity → Returns new ID
GUI → /delete_* → Backend deletes entity → Confirms deletion
GUI → /update_* → Backend updates parameter → Applies changes
GUI → /duplicate_* → Backend duplicates entity → Returns new ID

Real-time Updates:
GUI color picker → /palette/{id}/{color} → Backend updates immediately
GUI parameter change → /update_segment → Backend applies change

Navigation:
GUI dropdown → /change_scene → Backend switches scene
GUI selection → /change_effect → Backend switches effect
```

### **Backend → GUI Communication**
```
Query Responses:
Backend → JSON state data → GUI (for Save operations)
Backend → Current IDs → GUI (for synchronization)

Operation Responses:
Backend → Success/Error status → GUI (for all CRUD operations)
Backend → New entity ID → GUI (for create/duplicate operations)
```

---

## **Implementation Examples**

### **Complete Scene Workflow**
```bash
# Create new scene
/create_scene 250 60                    # 250 LEDs, 60 FPS

# Update scene parameters
/update_scene 1 led_count 300          # Change LED count
/update_scene 1 fps 30                 # Change FPS

# Create and configure effects
/create_effect                         # Create new effect
/duplicate_effect 0                    # Duplicate existing effect

# Create and configure palettes
/create_palette                        # Create new palette
/palette/1/0 255 0 0                  # Set first color to red
/palette/1/1 0 255 0                  # Set second color to green

# Switch to new scene and effect
/change_scene 1
/change_effect 1
/change_palette 1
```

### **Advanced Segment Configuration**
```bash
# Create segment with custom ID
/create_segment 10                     # Create segment with ID 10

# Configure segment controls
/update_segment 10 solo 1              # Solo this segment
/update_segment 10 mute 0              # Ensure not muted

# Configure movement (absolute LED positions after Region conversion)
/update_segment 10 move_range 50 150   # Move between LEDs 50-150
/update_segment 10 move_speed 2.0      # Movement speed
/update_segment 10 initial_position 75 # Start at LED 75
/update_segment 10 edge_reflect 1      # Enable edge reflection

# Configure color composition for 5 slots
/update_segment 10 color_slot 0 0 2    # Slot 0: palette 0, color 2
/update_segment 10 color_slot 1 0 4    # Slot 1: palette 0, color 4
/update_segment 10 color_slot 2 1 1    # Slot 2: palette 1, color 1
/update_segment 10 color_slot 3 1 3    # Slot 3: palette 1, color 3
/update_segment 10 color_slot 4 0 0    # Slot 4: palette 0, color 0

# Set transparency for each slot (0.0-1.0 float scale)
/update_segment 10 transparency 0 1.0  # Slot 0: fully transperency
/update_segment 10 transparency 1 0.8  # Slot 1: 20% opacity
/update_segment 10 transparency 2 0.6  # Slot 2: 40% opacity
/update_segment 10 transparency 3 0.4  # Slot 3: 60% opacity
/update_segment 10 transparency 4 0.2  # Slot 4: 80% opacity

# Set LED count between slots
/update_segment 10 length 0 15         # 15 LEDs between slot 0 and 1
/update_segment 10 length 1 20         # 20 LEDs between slot 1 and 2
/update_segment 10 length 2 10         # 10 LEDs between slot 2 and 3
/update_segment 10 length 3 25         # 25 LEDs between slot 3 and 4
/update_segment 10 length 4 5          # 5 LEDs after slot 4
```

### **Complex Dimmer Sequence**
```bash
# Create segment first
/create_segment 5

# Build dimmer sequence step by step (all durations in milliseconds, brightness 0-100)
/create_dimmer 5 1000 100 0             # 1000ms (1s) fade out: 100% → 0%
/create_dimmer 5 500 0 0                # 500ms (0.5s) hold dark: 0%
/create_dimmer 5 2000 0 100             # 2000ms (2s) fade in: 0% → 100%
/create_dimmer 5 1500 100 50            # 1500ms (1.5s) dim down: 100% → 50%
/create_dimmer 5 300 50 50              # 300ms (0.3s) hold at 50%
/create_dimmer 5 1000 50 80             # 1000ms (1s) brighten: 50% → 80%

# Modify existing dimmer elements (brightness scale 0-100)
/update_dimmer 5 2 2500 0 100           # Change 3rd element: 2500ms fade in 0% → 100%
/update_dimmer 5 4 800 50 50            # Change 5th element: 800ms hold at 50%

# Remove a dimmer element
/delete_dimmer 5 1                      # Remove 2nd element (hold dark)
                                        # All subsequent elements move up
```

### **Complete Scene Creation & Management**
```bash
# 1. Create base scene structure
/create_scene 400 60                   # 400 LEDs, 60 FPS scene
/create_effect                         # Create first effect
/create_palette                        # Create first palette

# 2. Set up color palette
/palette/0/0 255 0 0                   # Red
/palette/0/1 255 128 0                 # Orange  
/palette/0/2 255 255 0                 # Yellow
/palette/0/3 0 255 0                   # Green
/palette/0/4 0 0 255                   # Blue
/palette/0/5 128 0 255                 # Purple

# 3. Create multiple segments for different LED regions
/create_segment 1                      # Front strip
/create_segment 2                      # Side strips  
/create_segment 3                      # Rear strip
/create_segment 4                      # Accent lights

# 4. Configure front strip (LEDs 0-99)
/update_segment 1 move_range 0 80      # Movement range
/update_segment 1 move_speed 1.0       # Moderate speed
/update_segment 1 color_slot 0 0 0     # Use red
/update_segment 1 color_slot 1 0 1     # Use orange
/update_segment 1 transparency 0 0.0   # Full brightness
/update_segment 1 transparency 1 0.5   # Half brightness
/update_segment 1 length 0 40          # 40 LEDs red
/update_segment 1 length 1 40          # 40 LEDs orange

# 5. Configure side strips (LEDs 100-299)  
/update_segment 2 move_range 100 280   # Movement range
/update_segment 2 move_speed 0.5       # Slower movement
/update_segment 2 color_slot 0 0 2     # Use yellow
/update_segment 2 color_slot 1 0 3     # Use green
/update_segment 2 transparency 0 0.8   # 20% brightness
/update_segment 2 transparency 1 0.6   # 40% brightness
/update_segment 2 length 0 90          # 90 LEDs yellow
/update_segment 2 length 1 90          # 90 LEDs green

# 6. Configure rear strip (LEDs 300-399)
/update_segment 3 move_range 300 380   # Movement range  
/update_segment 3 move_speed 1.5       # Faster movement
/update_segment 3 color_slot 0 0 4     # Use blue
/update_segment 3 color_slot 1 0 5     # Use purple
/update_segment 3 transparency 0 0.9   # 10% brightness
/update_segment 3 transparency 1 0.7   # 30% brightness
/update_segment 3 length 0 40          # 40 LEDs blue
/update_segment 3 length 1 40          # 40 LEDs purple

# 7. Configure accent lights with dimmer sequence
/update_segment 4 move_range 50 350    # Wide movement range
/update_segment 4 move_speed 0.3       # Very slow movement
/update_segment 4 color_slot 0 0 0     # Use red
/update_segment 4 transparency 0 0.0   # Full brightness

# Add breathing effect via dimmer (durations in ms, brightness 0-100)
/create_dimmer 4 2000 100 30           # 2000ms (2s) fade down: 100% → 30%
/create_dimmer 4 2000 30 100           # 2000ms (2s) fade up: 30% → 100%

# 8. Test different combinations
/change_scene 1                        # Switch to our new scene
/change_effect 0                       # Use first effect
/change_palette 0                      # Use our color palette

# Solo test individual segments
/update_segment 1 solo 1               # Test front strip only
/update_segment 1 solo 0               # Turn off solo
/update_segment 2 solo 1               # Test side strips only
/update_segment 2 solo 0               # Turn off solo

# Set global parameters
/master_brightness 200                 # Set to 200/255 brightness
/set_speed_percent 75                  # 75% animation speed
```

---

## **Error Handling & Validation**

### **Common Error Scenarios**
```bash
# Invalid IDs
/delete_scene 999                      # → Error: Scene ID 999 does not exist
/update_segment 50 solo 1              # → Error: Segment ID 50 does not exist

# Invalid parameters
/update_scene 0 led_count -10          # → Error: LED count must be positive
/create_dimmer 5 -1000 50 0            # → Error: Duration must be positive (ms)
/create_dimmer 5 1000 150 -10          # → Error: Brightness must be 0-100
/palette/0/2 300 128 64                # → Error: RGB values must be 0-255

# State conflicts
/delete_scene 0                        # → Error: Cannot delete active scene
/delete_palette 0                      # → Error: Cannot delete active palette
```

### **Success Response Examples**
```bash
# Successful operations return confirmation
/create_scene 300 60                   # → Success: Scene created with ID 2
/duplicate_segment 5                   # → Success: Segment duplicated with ID 8
/delete_dimmer 3 2                     # → Success: Dimmer element deleted
```

---
