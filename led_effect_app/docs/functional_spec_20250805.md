# LED Animation System - Functional Specification

## PART 1: Led Playback Animation Engine - ANALYSIS (CURRENT STATE)

### 1. Overview
This section provides a comprehensive analysis of the existing **LED Animation Playback Engine**, which represents the completed work of Phase 2. This backend system is a fully-featured animation renderer controllable via OSC.

### 2. Core Components & Technology Stack
- **Primary Function**: Renders complex, multi-layered LED animations based on JSON data structures.
- **Language**: Python
- **OSC Library**: `python-osc` for robust message handling.
- **Concurrency**: `ThreadPoolExecutor` for non-blocking, thread-safe OSC message processing.
- **Data Format**: Reads animation and scene data from `.json` files. It does **not** have the functionality to write or save JSON files.
- **Logging**: Includes detailed logging for OSC messages, performance, and general engine status.
- **Platform Support**: Cross-platform (Windows 10/11, macOS 11+).

### 3. OSC Implementation Details
The backend exposes a comprehensive set of OSC commands for full remote control.

#### 3.1. OSC Server Configuration
- **File**: `src/core/osc_handler.py`
- **IP Address**: Configurable, listens on a specified network interface.
- **Port**: Configurable, for receiving OSC messages.

#### 3.2. Supported OSC Commands (Led Playback Animation Engine - UNCHANGED)
The engine supports the following commands out-of-the-box.

**Content & Scene Management:**
- **`/load_json <file_path:string>`**: Clears all current scenes and loads a new show file from JSON. Requires a subsequent `/change_scene` command to start playback.
- **`/change_scene <scene_id:int>`**: Switches to the specified scene ID. Starts the animation loop if it's not already running.
- **`/load_dissolve_json <file_path:string>`**: Loads a JSON file containing transition patterns.
- **`/set_dissolve_pattern <pattern_id:int>`**: Sets the active pattern for transitions between scenes/effects.

**Playback & Parameter Control:**
- **`/change_effect <effect_id:int>`**: Changes the active effect within the current scene.
- **`/change_palette <palette_id:int>`**: Changes the active color palette for the current effect.
- **`/master_brightness <brightness:int>`**: Adjusts the global brightness. Range: `0-255`.
- **`/set_speed_percent <speed:int>`**: Adjusts the global animation speed. Range: `0-1023`.

**Real-time Color Updates:**
- **`/palette/{palette_id:0-4}/{color_index:0-5} <r:int> <g:int> <b:int>`**: Updates a single color within a specific palette in real-time. Also supports letter-based palette IDs (`A-E`).

---

## PART 2: System For Creating Visual Effects - PROJECT DEFINITION (NEXT STEPS)

### 4. Overview & Objectives
Phase 3 focuses on building a new **LED Control Tool (GUI)** that provides a user-friendly interface for the powerful Phase 2 backend. This phase will also involve extending the backend to support full bidirectional communication, enabling real-time editing and saving capabilities.

**Primary Objectives:**
1. **Develop a Feature-Rich GUI**: Implement a GUI that meets all functional requirements outlined in the original specification.
2. **Achieve Full Bidirectional Sync**: Enable the GUI to control the backend in real-time and accurately reflect the backend's state.
3. **Implement Save/Export Functionality**: Add the ability for the GUI to query the backend's current state and save it as a new `.json` file.
4. **Add Region Management**: Implement GUI-only Region concept for easier LED range management.
5. **Complete CRUD Operations**: Support Create, Read, Update, Delete for all entities.

### 5. GUI Functional Requirements

#### 5.1. File Menu
- **Open...**: Displays a file dialog to open a control JSON file. On open, it triggers the `/load_json` command on the backend.
- **Save**: Overwrites the currently opened JSON file. If no file is open, behaves like "Save As...". This requires a backend mechanism to query the full state.
- **Save As...**: Saves the current application state to a new JSON file with a user-specified filename.

#### 5.2. Scene and Effect Control
- **Scene ID Management**:
    - **Dropdown List**: For selection of the current Scene. Sends `/change_scene <id>`.
    - **Add Button**: Creates a new Scene at the end of the list. Sends `/create_scene <led_count> <fps>`.
    - **Delete Button**: Deletes the selected Scene. Sends `/delete_scene <id>`. **Deleted IDs become gaps, no re-indexing**.
    - **Duplicate Button**: Creates a new Scene by copying the selected one and adds it to the end. Sends `/duplicate_scene <source_id>`.

- **Effect ID Management**:
    - **Dropdown List**: For selection of the current Effect. Sends `/change_effect <id>`.
    - **Add Button**: Creates a new Effect at the end of the list. Sends `/create_effect`.
    - **Delete Button**: Deletes the selected Effect. Sends `/delete_effect <id>`. **Deleted IDs become gaps, no re-indexing**.
    - **Duplicate Button**: Creates a new Effect by copying the selected one and adds it to the end. Sends `/duplicate_effect <source_id>`.

#### 5.3. Scene Settings
- **LED Count**: A field to set the number of LEDs. Sends `/update_scene <scene_id> led_count <count>`.
- **FPS**: A field to set the frames per second (30/60/custom). Sends `/update_scene <scene_id> fps <fps>`.

- **Color Pallets** (within Scene Settings):
    - **Pallet ID Management**:
        - **Dropdown List**: For selecting the current palette for editing and application. Sends `/change_palette <id>`.
        - **Add Button**: Creates a new palette at the end. Sends `/create_palette`.
        - **Delete Button**: Deletes the selected palette. Sends `/delete_palette <id>`. **Deleted IDs become gaps, no re-indexing**.
        - **Duplicate Button**: Creates a new palette by copying the selected one and adds it to the end. Sends `/duplicate_palette <source_id>`.
    
    - **Color Configuration**:
        - **Six Color Boxes**: Displays the current palette's colors. Clicking a box opens a color picker.
        - **Color Picker Integration**: When a color is selected, sends `/palette/{palette_id}/{color_index} <r> <g> <b>` and updates the box color.

#### 5.4. Region Settings
Region is a GUI-only concept for dividing LED strips into manageable sections. Each Region defines a start and end LED number. When sending data to the backend, Region information is converted to absolute LED positions.

- **Region ID Management**:
    - **Dropdown List**: For selecting the Region to edit.
    - **Add Button**: Creates a new Region with default range (0-99). GUI state only - no OSC command needed.
    - **Delete Button**: Deletes the selected Region. GUI state only - no OSC command needed.
    - **Duplicate Button**: Creates a new Region by copying the selected one. GUI state only.

- **LED Range Configuration**:
    - **Start LED Field**: Set the starting LED number for this Region.
    - **End LED Field**: Set the ending LED number for this Region.
    - **Validation**: End must be >= Start. Overlapping Regions are allowed but warned.

#### 5.5. Segment Editing
- **Segment ID Management**:
    - **Dropdown List**: For selecting the target segment for editing and application.
    - **Add Button**: Opens a modal popup to specify a custom Segment ID. On OK, sends `/create_segment <custom_id>`. On Cancel, returns to main window. Shows error if ID already exists.
    - **Delete Button**: Deletes the selected segment. Sends `/delete_segment <id>`. **Deleted IDs become gaps, no re-indexing**.
    - **Duplicate Button**: Creates a new segment by copying the selected one and adds it to the end. Sends `/duplicate_segment <source_id>`.
    - **Solo Button**: Lights only the selected segment, turns off others. Sends `/update_segment <id> solo <1|0>`.
    - **Mute Button**: Turns off the selected segment. Sends `/update_segment <id> mute <1|0>`.
    - **Priority Rule**: When both Solo and Mute are ON, **Solo takes priority**.
    - **Reorder Button**: Changes the segment order using up/down arrows. Sends `/reorder_segment <id> <new_position>`.

- **Region Assignment** (NEW):
    - **Region Dropdown**: Select which Region this Segment controls.
    - **Assignment Logic**: When a Region is selected, all Segment parameters (Move Range, Initial Position) are relative to the Region's start LED.
    - **Display**: Show both relative position and absolute LED position for clarity.
    - **No OSC Command**: Region assignment is GUI-only, converted to absolute positions before sending to backend.

- **Color Composition**:
    - **Color Select**: 
        - **Color Slot Boxes**: Clicking any Color Slot Box opens a **modal popup**.
        - **Modal Popup**: Displays the current palette's 6 colors as selectable boxes.
        - **Selection Process**: User clicks a color from the popup → sets that Color Slot to use the selected Color Index.
        - **Example**: Click Color Slot 1 Box → popup shows 6 colors → click color 3 → Color Slot 1 now uses Color Index 3.
        - **OSC Message**: Sends `/update_segment <id> color_slot <slot_index> <palette_id> <color_index>`.
    
    - **Transparency**: Sliders for each Color Slot's transparency (0.0-1.0 float scale). Sends `/update_segment <id> transparency <slot_index> <value>`.
    - **Length**: Fields for LED count between Color Slots. Sends `/update_segment <id> length <slot_index> <count>`.

- **Movement Configuration**:
    - **Move Range**: Set LED movement range **relative to assigned Region**. Display shows both relative and absolute positions. Sends `/update_segment <id> move_range <start> <end>` (absolute LED positions).
    - **Move Speed**: Set LED movement speed. Sends `/update_segment <id> move_speed <speed>`.
    - **Initial Position**: Set LED movement initial position **relative to assigned Region**. Sends `/update_segment <id> initial_position <position>` (absolute LED position).
    - **Edge Reflect**: Toggle for range endpoint reflection. Sends `/update_segment <id> edge_reflect <1|0>`.

- **Dimmer Sequence**:
    - **Dimmer List**: Displays dimmer elements with **auto-generated sequential Index**, Duration (ms), Initial Brightness (0-100), Final Brightness (0-100).  
    - **List Behavior**: All fields except Index are editable. Index is automatically assigned and sequential.
    - **Add Functionality**:
        - **Duration Field**: Set duration for new dimmer element in milliseconds (ms).
        - **Initial Brightness Field**: Set initial brightness for new element (0-100 integer scale).
        - **Final Brightness Field**: Set final brightness for new element (0-100 integer scale).
        - **Add Button**: Creates new dimmer element with above settings at list end. Sends `/create_dimmer <segment_id> <duration_ms> <initial_brightness> <final_brightness>`.
    - **Delete Functionality**:
        - **Delete Button**: Deletes selected dimmer element. Sends `/delete_dimmer <segment_id> <index>`.
        - **Index Resequencing**: **All elements after deleted element are moved up and re-indexed sequentially**.
    - **Edit Functionality**:
        - **In-line Editing**: Users can edit Duration (ms), Initial Brightness (0-100), Final Brightness (0-100) values directly in the list.
        - **Update Message**: Sends `/update_dimmer <segment_id> <index> <duration_ms> <initial_brightness> <final_brightness>` when values change.

### 6. Phase 3 Technical Design

#### 6.1. Technology Stack
- **GUI Framework**: **Flet** is the primary recommendation due to its Python-native development, high-performance Flutter backend, and rapid development cycle. PyQt6/PySide6 are alternatives.
- **Communication**: `python-osc` will be used for OSC messaging.
- **Operating System Support**: Windows 10/11 (64bit, Japanese Edition), macOS (version TBD).
- **Runtime Environment**: Python 3.x.

#### 6.2. Complete OSC Protocol Extensions

**New OSC Commands for Full CRUD Operations:**

**Query Operations:**
- **`/query_full_state`**: Returns complete system state as JSON string for Save functionality.
- **`/query_current_state`**: Returns currently selected scene/effect/segment/palette IDs.

**Scene Management:**
- **`/create_scene <led_count:int> <fps:int>`**: Create new scene with specified parameters.
- **`/delete_scene <scene_id:int>`**: Delete specified scene.
- **`/duplicate_scene <source_id:int>`**: Duplicate scene and return new ID.
- **`/update_scene <scene_id:int> <param:string> <value>`**: Update scene parameter.
  - Examples: `/update_scene 0 led_count 300`, `/update_scene 0 fps 60`

**Effect Management:**
- **`/create_effect`**: Create new effect in current scene.
- **`/delete_effect <effect_id:int>`**: Delete specified effect.
- **`/duplicate_effect <source_id:int>`**: Duplicate effect and return new ID.

**Palette Management:**
- **`/create_palette`**: Create new palette with default colors.
- **`/delete_palette <palette_id:int>`**: Delete specified palette.
- **`/duplicate_palette <source_id:int>`**: Duplicate palette and return new ID.

**Segment Management:**
- **`/create_segment <custom_id:int>`**: Create new segment with custom ID.
- **`/delete_segment <segment_id:int>`**: Delete specified segment.
- **`/duplicate_segment <source_id:int>`**: Duplicate segment and return new ID.
- **`/reorder_segment <segment_id:int> <new_position:int>`**: Change segment order.
- **`/update_segment <segment_id:int> <param:string> <value...>`**: Update segment parameter.
  - Examples:
    - `/update_segment 5 solo 1`
    - `/update_segment 5 mute 0`
    - `/update_segment 5 move_range 10 50`
    - `/update_segment 5 move_speed 1.5`
    - `/update_segment 5 initial_position 25`
    - `/update_segment 5 edge_reflect 1`
    - `/update_segment 5 color_slot 0 1 3` (slot_index, palette_id, color_index)
    - `/update_segment 5 transparency 0 0.8` (slot_index, transparency_value 0.0-1.0)
    - `/update_segment 5 length 0 10` (slot_index, led_count)

**Dimmer Management:**
- **`/create_dimmer <segment_id:int> <duration_ms:int> <initial_brightness:int> <final_brightness:int>`**: Add dimmer element to segment. Duration in milliseconds, brightness scale 0-100.
- **`/delete_dimmer <segment_id:int> <index:int>`**: Delete dimmer element at index.
- **`/update_dimmer <segment_id:int> <index:int> <duration_ms:int> <initial_brightness:int> <final_brightness:int>`**: Update dimmer element. Duration in milliseconds, brightness scale 0-100.

**Reuse Existing Commands (No Changes):**
- **Color Updates**: Continue using `/palette/{palette_id}/{color_index} <r> <g> <b>`
- **Scene/Effect Changes**: Continue using `/change_scene <id>` and `/change_effect <id>`
- **Master Controls**: Continue using `/master_brightness <brightness>` and `/set_speed_percent <speed>`
- **File Operations**: Continue using `/load_json <path>` and `/load_dissolve_json <path>`

#### 6.3. GUI State Management Strategy

**Hybrid State Management:**
- **GUI maintains local state** for immediate UI responsiveness
- **Backend is authoritative** for animation data
- **Bidirectional synchronization** ensures consistency
- **Region data stays GUI-only** and is converted to absolute positions

**Region-to-Absolute Conversion:**
- **Region data stays in GUI only**
- **When sending segment data to backend, GUI calculates absolute LED positions**
- **Example**: Region 1 = LEDs 50-149, Segment move_range = 10-30 relative → sends `/update_segment 5 move_range 60 80`

**Synchronization Strategy:**
1. **File Load**: `/load_json` + `/query_full_state` for GUI sync
2. **Real-time Color**: Immediate `/palette/{palette_id}/{color_index}` on color picker changes
3. **CRUD Operations**: Immediate OSC commands for create/delete/update operations
4. **Scene/Effect Switch**: Use existing `/change_scene` and `/change_effect` commands
5. **File Save**: `/query_full_state` + write to JSON file

#### 6.4. Backend Modifications (`osc_handler.py`)

**New Handler Methods Required:**
- **Query handlers**: `_handle_query_full_state`, `_handle_query_current_state`
- **Scene handlers**: `_handle_create_scene`, `_handle_delete_scene`, `_handle_duplicate_scene`, `_handle_update_scene`
- **Effect handlers**: `_handle_create_effect`, `_handle_delete_effect`, `_handle_duplicate_effect`
- **Palette handlers**: `_handle_create_palette`, `_handle_delete_palette`, `_handle_duplicate_palette`
- **Segment handlers**: `_handle_create_segment`, `_handle_delete_segment`, `_handle_duplicate_segment`, `_handle_reorder_segment`, `_handle_update_segment`
- **Dimmer handlers**: `_handle_create_dimmer`, `_handle_delete_dimmer`, `_handle_update_dimmer`
- **Keep all existing Phase 2 handlers unchanged** for backward compatibility

**Backend Response System:**
- **Success/Error responses** for all operations
- **ID assignment** for create operations
- **State validation** before operations
- **Automatic cleanup** for delete operations

### 7. Implementation Plan

**Step 1: Backend CRUD Extensions**
- Add all new OSC handlers for create/delete/update/query operations
- Implement response system for operation feedback
- Add state validation and error handling

**Step 2: GUI State Management Foundation**
- Set up Flet application with complete data models (Scene, Effect, Palette, Segment, Region)
- Implement bidirectional OSC communication
- Implement Region-to-absolute conversion logic

**Step 3: Basic CRUD Operations**
- Implement Scene/Effect/Palette create/delete/duplicate functionality
- Test basic GUI-backend synchronization
- Implement query system for Save functionality

**Step 4: Segment Management System**
- Implement Segment CRUD operations with custom ID support
- Add Solo/Mute/Reorder functionality
- Implement parameter update system

**Step 5: Advanced Features**
- Implement Region management UI with automatic conversion
- Add Dimmer sequence CRUD operations
- Implement real-time parameter updates

**Step 6: File Operations & Polish**
- Implement Save/Save As using query system
- Add comprehensive validation and error handling
- UI/UX improvements and performance optimization

**Step 7: Testing & Refinement**
- Comprehensive testing of all CRUD operations
- Test GUI-backend synchronization under various scenarios
- Performance testing and optimization
