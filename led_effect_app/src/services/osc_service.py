from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc.osc_server import BlockingOSCUDPServer
from threading import Thread
import inspect
from typing import Optional, Dict, Any, Callable, List, Tuple
from dataclasses import dataclass
from utils.logger import AppLogger


@dataclass
class OSCCommand:
    """OSC command definition for auto-registration"""
    address: str
    method: Callable
    param_types: List[type]
    description: str


class OSCRegistry:
    """Registry for auto-registering OSC commands"""
    
    def __init__(self):
        self.commands: Dict[str, OSCCommand] = {}
    
    def register(self, address: str, description: str = ""):
        """Decorator for auto-registering OSC commands"""
        def decorator(func: Callable):
            sig = inspect.signature(func)
            param_types = []
            for param_name, param in sig.parameters.items():
                if param_name != 'self':
                    if param.annotation != inspect.Parameter.empty:
                        param_types.append(param.annotation)
                    else:
                        param_types.append(Any)
            
            cmd = OSCCommand(address, func, param_types, description)
            self.commands[address] = cmd
            
            AppLogger.debug(f"OSC auto-registered: {address} -> {func.__name__}")
            return func
        return decorator


_osc_registry = OSCRegistry()


class OSCService:
    """Enhanced OSC service với auto-registration và smart routing"""
    
    def __init__(self, server_ip: str = "127.0.0.1", server_port: int = 8000, 
                 client_ip: str = "127.0.0.1", client_port: int = 8001):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_ip = client_ip
        self.client_port = client_port
        
        self.client: Optional[udp_client.SimpleUDPClient] = None
        self.server: Optional[BlockingOSCUDPServer] = None
        self.server_thread: Optional[Thread] = None
        self.is_running = False
        
        self.connection_pools: Dict[str, udp_client.SimpleUDPClient] = {}
        self.default_target = (client_ip, client_port)
        
        self._setup_dispatcher()
        self._discover_registered_commands()
        
    def _setup_dispatcher(self):
        """Setup OSC message dispatcher"""
        self.dispatcher = Dispatcher()
        
        self.dispatcher.map("/response/success", self._handle_success_response)
        self.dispatcher.map("/response/error", self._handle_error_response)
        self.dispatcher.map("/response/state", self._handle_state_response)
        
    def _discover_registered_commands(self):
        """Auto-discover tất cả registered commands"""
        AppLogger.info(f"Auto-discovered {len(_osc_registry.commands)} OSC commands")
        
    def get_client(self, target: Tuple[str, int] = None) -> udp_client.SimpleUDPClient:
        """Get or create client for specific target"""
        if target is None:
            target = self.default_target
            
        target_key = f"{target[0]}:{target[1]}"
        
        if target_key not in self.connection_pools:
            try:
                client = udp_client.SimpleUDPClient(target[0], target[1])
                self.connection_pools[target_key] = client
                AppLogger.debug(f"Created OSC client for {target_key}")
            except Exception as e:
                AppLogger.error(f"Failed to create OSC client for {target_key}: {e}")
                raise
                
        return self.connection_pools[target_key]
            
    def start_client(self) -> bool:
        """Start OSC client for sending messages"""
        try:
            self.client = self.get_client()
            AppLogger.success(f"OSC client started: {self.client_ip}:{self.client_port}")
            return True
        except Exception as e:
            AppLogger.error(f"Failed to start OSC client: {e}")
            return False
            
    def start_server(self) -> bool:
        """Start OSC server for receiving responses"""
        try:
            self.server = BlockingOSCUDPServer((self.server_ip, self.server_port), self.dispatcher)
            self.server_thread = Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            self.is_running = True
            AppLogger.success(f"OSC server started: {self.server_ip}:{self.server_port}")
            return True
        except Exception as e:
            AppLogger.error(f"Failed to start OSC server: {e}")
            return False
            
    def _run_server(self):
        """Run OSC server in thread"""
        try:
            self.server.serve_forever()
        except Exception as e:
            AppLogger.error(f"OSC server error: {e}")
            
    def stop(self):
        """Stop OSC client và server"""
        self.is_running = False
        
        if self.server:
            self.server.shutdown()
            self.server = None
            
        if self.server_thread:
            self.server_thread.join(timeout=1.0)
            self.server_thread = None
            
        for client in self.connection_pools.values():
            try:
                if hasattr(client, '_sock'):
                    client._sock.close()
            except:
                pass
        self.connection_pools.clear()
            
        self.client = None
        AppLogger.info("OSC service stopped")
    
    def _send_message(self, address: str, *args, target: Tuple[str, int] = None) -> bool:
        """ Send message with routing and validation"""
        try:
            cmd = _osc_registry.commands.get(address)
            if cmd and not self._validate_params(cmd, args):
                AppLogger.warning(f"Invalid parameters for {address}: {args}")
                return False
            
            client = self.get_client(target)
            
            if args:
                client.send_message(address, args)
            else:
                client.send_message(address, [])
            
            AppLogger.info(f"OSC sent: {address} {args}")
            return True
            
        except Exception as e:
            AppLogger.error(f"Failed to send OSC message {address}: {e}")
            return False
            
    def _validate_params(self, cmd: OSCCommand, args: tuple) -> bool:
        """Validate parameters against registered command"""
        if len(args) != len(cmd.param_types):
            return False
            
        for arg, expected_type in zip(args, cmd.param_types):
            if expected_type != Any and not isinstance(arg, expected_type):
                try:
                    expected_type(arg) 
                except:
                    return False
        return True
    
    # ===== AUTO-REGISTERED OSC COMMANDS =====
    
    @_osc_registry.register("/load_json", "Load scene data from JSON file")
    def send_load_json(self, file_path: str) -> bool:
        """Send load JSON command"""
        return self._send_message("/load_json", file_path)
    
    @_osc_registry.register("/change_scene", "Switch to different scene")
    def send_change_scene(self, scene_id: int) -> bool:
        """Send change scene command"""
        return self._send_message("/change_scene", scene_id)
    
    @_osc_registry.register("/change_effect", "Switch to different effect")
    def send_change_effect(self, effect_id: int) -> bool:
        """Send change effect command"""
        return self._send_message("/change_effect", effect_id)
    
    @_osc_registry.register("/change_palette", "Switch to different palette")
    def send_change_palette(self, palette_id: int) -> bool:
        """Send change palette command"""
        return self._send_message("/change_palette", palette_id)
    
    @_osc_registry.register("/master_brightness", "Set master brightness (0-255)")
    def send_master_brightness(self, brightness: int) -> bool:
        """Send master brightness command"""
        brightness = max(0, min(255, brightness))
        return self._send_message("/master_brightness", brightness)
        
    @_osc_registry.register("/set_speed_percent", "Set animation speed (0-1023%)")
    def send_set_speed_percent(self, speed: int) -> bool:
        """Send speed percent command"""
        speed = max(0, min(1023, speed))
        return self._send_message("/set_speed_percent", speed)
        
    @_osc_registry.register("/create_scene", "Create new scene with LED count and FPS")
    def send_create_scene(self, led_count: int, fps: int) -> bool:
        """Send create scene command"""
        return self._send_message("/create_scene", led_count, fps)
        
    @_osc_registry.register("/delete_scene", "Delete scene by ID")
    def send_delete_scene(self, scene_id: int) -> bool:
        """Send delete scene command"""
        return self._send_message("/delete_scene", scene_id)
        
    @_osc_registry.register("/duplicate_scene", "Duplicate scene and return new ID")
    def send_duplicate_scene(self, source_id: int) -> bool:
        """Send duplicate scene command"""
        return self._send_message("/duplicate_scene", source_id)
        
    @_osc_registry.register("/update_scene", "Update scene parameter")
    def send_update_scene(self, scene_id: int, param: str, value: Any) -> bool:
        """Send update scene command"""
        return self._send_message("/update_scene", scene_id, param, value)
        
    @_osc_registry.register("/create_effect", "Create new effect in current scene")
    def send_create_effect(self) -> bool:
        """Send create effect command"""
        return self._send_message("/create_effect")
        
    @_osc_registry.register("/delete_effect", "Delete effect by ID")
    def send_delete_effect(self, effect_id: int) -> bool:
        """Send delete effect command"""
        return self._send_message("/delete_effect", effect_id)
        
    @_osc_registry.register("/duplicate_effect", "Duplicate effect and return new ID")
    def send_duplicate_effect(self, source_id: int) -> bool:
        """Send duplicate effect command"""
        return self._send_message("/duplicate_effect", source_id)
        
    @_osc_registry.register("/create_palette", "Create new palette with default colors")
    def send_create_palette(self) -> bool:
        """Send create palette command"""
        return self._send_message("/create_palette")
        
    @_osc_registry.register("/delete_palette", "Delete palette by ID")
    def send_delete_palette(self, palette_id: int) -> bool:
        """Send delete palette command"""
        return self._send_message("/delete_palette", palette_id)
        
    @_osc_registry.register("/duplicate_palette", "Duplicate palette and return new ID")
    def send_duplicate_palette(self, source_id: int) -> bool:
        """Send duplicate palette command"""
        return self._send_message("/duplicate_palette", source_id)
        
    @_osc_registry.register("/create_segment", "Create segment with custom ID")
    def send_create_segment(self, custom_id: int) -> bool:
        """Send create segment command"""
        return self._send_message("/create_segment", custom_id)
        
    @_osc_registry.register("/delete_segment", "Delete segment by ID")
    def send_delete_segment(self, segment_id: int) -> bool:
        """Send delete segment command"""
        return self._send_message("/delete_segment", segment_id)
        
    @_osc_registry.register("/duplicate_segment", "Duplicate segment and return new ID")
    def send_duplicate_segment(self, source_id: int) -> bool:
        """Send duplicate segment command"""
        return self._send_message("/duplicate_segment", source_id)
        
    @_osc_registry.register("/reorder_segment", "Change segment render order")
    def send_reorder_segment(self, segment_id: int, new_position: int) -> bool:
        """Send reorder segment command"""
        return self._send_message("/reorder_segment", segment_id, new_position)
        
    @_osc_registry.register("/update_segment", "Update segment parameter")
    def send_update_segment(self, segment_id: int, param: str, *values) -> bool:
        """Send update segment command with variable parameters"""
        return self._send_message("/update_segment", segment_id, param, *values)
        
    @_osc_registry.register("/create_dimmer", "Create dimmer element in segment")
    def send_create_dimmer(self, segment_id: int, duration_ms: int, initial_brightness: int, final_brightness: int) -> bool:
        """Send create dimmer command"""
        return self._send_message("/create_dimmer", segment_id, duration_ms, initial_brightness, final_brightness)
        
    @_osc_registry.register("/delete_dimmer", "Delete dimmer element from segment")
    def send_delete_dimmer(self, segment_id: int, index: int) -> bool:
        """Send delete dimmer command"""
        return self._send_message("/delete_dimmer", segment_id, index)
        
    @_osc_registry.register("/update_dimmer", "Update dimmer element in segment")
    def send_update_dimmer(self, segment_id: int, index: int, duration_ms: int, initial_brightness: int, final_brightness: int) -> bool:
        """Send update dimmer command"""
        return self._send_message("/update_dimmer", segment_id, index, duration_ms, initial_brightness, final_brightness)
        
    @_osc_registry.register("/query_full_state", "Get complete system state")
    def send_query_full_state(self) -> bool:
        """Send query full state command"""
        return self._send_message("/query_full_state")
        
    @_osc_registry.register("/query_current_state", "Get current selection state")
    def send_query_current_state(self) -> bool:
        """Send query current state command"""
        return self._send_message("/query_current_state")
    
    # ===== Convenience Methods (giữ existing API) =====
        
    def send_palette_color_update(self, palette_id: int, color_index: int, r: int, g: int, b: int) -> bool:
        """Send real-time palette color update"""
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        address = f"/palette/{palette_id}/{color_index}"
        return self._send_message(address, r, g, b)
    
    def send_segment_color_slot_update(self, segment_id: int, slot_index: int, palette_id: int, color_index: int) -> bool:
        """Send segment color slot update command"""
        return self.send_update_segment(segment_id, "color_slot", slot_index, palette_id, color_index)
        
    def send_segment_transparency_update(self, segment_id: int, slot_index: int, transparency_value: float) -> bool:
        """Send segment transparency update command"""
        return self.send_update_segment(segment_id, "transparency", slot_index, transparency_value)
        
    def send_segment_length_update(self, segment_id: int, slot_index: int, led_count: int) -> bool:
        """Send segment length update command"""
        return self.send_update_segment(segment_id, "length", slot_index, led_count)
        
    def send_segment_move_range_update(self, segment_id: int, start: int, end: int) -> bool:
        """Send segment move range update command"""
        return self.send_update_segment(segment_id, "move_range", start, end)
        
    def send_segment_move_speed_update(self, segment_id: int, speed: float) -> bool:
        """Send segment move speed update command"""
        return self.send_update_segment(segment_id, "move_speed", speed)
        
    def send_segment_initial_position_update(self, segment_id: int, position: int) -> bool:
        """Send segment initial position update command"""
        return self.send_update_segment(segment_id, "initial_position", position)
        
    def send_segment_edge_reflect_update(self, segment_id: int, enabled: bool) -> bool:
        """Send segment edge reflect update command"""
        return self.send_update_segment(segment_id, "edge_reflect", 1 if enabled else 0)
        
    def send_segment_solo_update(self, segment_id: int, enabled: bool) -> bool:
        """Send segment solo update command"""
        return self.send_update_segment(segment_id, "solo", 1 if enabled else 0)
        
    def send_segment_mute_update(self, segment_id: int, enabled: bool) -> bool:
        """Send segment mute update command"""
        return self.send_update_segment(segment_id, "mute", 1 if enabled else 0)
        
    def send_dissolve_commands(self, file_path: str, pattern_id: int) -> bool:
        """Send dissolve pattern commands"""
        load_success = self._send_message("/load_dissolve_json", file_path)
        if load_success:
            return self._send_message("/set_dissolve_pattern", pattern_id)
        return False
    
    # ===== Response Handlers =====
        
    def _handle_success_response(self, address: str, *args):
        """Handle success response from backend"""
        AppLogger.success(f"Backend response: {address} - {args}")
        
    def _handle_error_response(self, address: str, *args):
        """Handle error response from backend"""
        AppLogger.error(f"Backend error: {address} - {args}")
        
    def _handle_state_response(self, address: str, *args):
        """Handle state response from backend"""
        AppLogger.info(f"Backend state: {address} - {args}")
    
    # ===== Utility Methods =====
        
    def ping_backend(self) -> bool:
        """Ping backend to check connection"""
        return self._send_message("/ping")
        
    def is_connected(self) -> bool:
        """Check if OSC service is connected"""
        return self.client is not None and self.is_running
    
    def list_registered_commands(self) -> List[str]:
        """List all auto-registered commands"""
        return list(_osc_registry.commands.keys())
    
    def get_command_info(self, address: str) -> Optional[OSCCommand]:
        """Get information about registered command"""
        return _osc_registry.commands.get(address)


osc_service = OSCService()