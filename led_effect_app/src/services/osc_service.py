from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc.osc_server import BlockingOSCUDPServer
from threading import Thread
import time
from typing import Optional, Dict, Any
from utils.logger import AppLogger


class OSCService:
    """OSC communication service for LED animation system"""
    
    def __init__(self, server_ip: str = "127.0.0.1", server_port: int = 8000, client_ip: str = "127.0.0.1", client_port: int = 8001):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_ip = client_ip
        self.client_port = client_port
        
        self.client: Optional[udp_client.SimpleUDPClient] = None
        self.server: Optional[BlockingOSCUDPServer] = None
        self.server_thread: Optional[Thread] = None
        self.is_running = False
        
        self._setup_dispatcher()
        
    def _setup_dispatcher(self):
        """Setup OSC message dispatcher"""
        self.dispatcher = Dispatcher()
        
        # Response handlers
        self.dispatcher.map("/response/success", self._handle_success_response)
        self.dispatcher.map("/response/error", self._handle_error_response)
        self.dispatcher.map("/response/state", self._handle_state_response)
        
    def start_client(self) -> bool:
        """Start OSC client for sending messages"""
        try:
            self.client = udp_client.SimpleUDPClient(self.client_ip, self.client_port)
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
        """Stop OSC client and server"""
        self.is_running = False
        
        if self.server:
            self.server.shutdown()
            self.server = None
            
        if self.server_thread:
            self.server_thread.join(timeout=1.0)
            self.server_thread = None
            
        self.client = None
        AppLogger.info("OSC service stopped")
        
    # ===== OSC Message Sending =====
        
    def send_load_json(self, file_path: str) -> bool:
        """Send load JSON command"""
        return self._send_message("/load_json", file_path)
        
    def send_change_scene(self, scene_id: int) -> bool:
        """Send change scene command"""
        return self._send_message("/change_scene", scene_id)
        
    def send_change_effect(self, effect_id: int) -> bool:
        """Send change effect command"""
        return self._send_message("/change_effect", effect_id)
        
    def send_change_palette(self, palette_id: int) -> bool:
        """Send change palette command"""
        return self._send_message("/change_palette", palette_id)
        
    def send_master_brightness(self, brightness: int) -> bool:
        """Send master brightness command (0-255)"""
        brightness = max(0, min(255, brightness))
        return self._send_message("/master_brightness", brightness)
        
    def send_set_speed_percent(self, speed: int) -> bool:
        """Send speed percent command (0-1023)"""
        speed = max(0, min(1023, speed))
        return self._send_message("/set_speed_percent", speed)
        
    def send_palette_color_update(self, palette_id: int, color_index: int, r: int, g: int, b: int) -> bool:
        """Send real-time palette color update"""
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        address = f"/palette/{palette_id}/{color_index}"
        return self._send_message(address, r, g, b)
        
    # ===== Scene Management Commands =====
        
    def send_create_scene(self, led_count: int, fps: int) -> bool:
        """Send create scene command"""
        return self._send_message("/create_scene", led_count, fps)
        
    def send_delete_scene(self, scene_id: int) -> bool:
        """Send delete scene command"""
        return self._send_message("/delete_scene", scene_id)
        
    def send_duplicate_scene(self, source_id: int) -> bool:
        """Send duplicate scene command"""
        return self._send_message("/duplicate_scene", source_id)
        
    def send_update_scene(self, scene_id: int, param: str, value: Any) -> bool:
        """Send update scene command"""
        return self._send_message("/update_scene", scene_id, param, value)
        
    # ===== Effect Management Commands =====
        
    def send_create_effect(self) -> bool:
        """Send create effect command"""
        return self._send_message("/create_effect")
        
    def send_delete_effect(self, effect_id: int) -> bool:
        """Send delete effect command"""
        return self._send_message("/delete_effect", effect_id)
        
    def send_duplicate_effect(self, source_id: int) -> bool:
        """Send duplicate effect command"""
        return self._send_message("/duplicate_effect", source_id)
        
    # ===== Palette Management Commands =====
        
    def send_create_palette(self) -> bool:
        """Send create palette command"""
        return self._send_message("/create_palette")
        
    def send_delete_palette(self, palette_id: int) -> bool:
        """Send delete palette command"""
        return self._send_message("/delete_palette", palette_id)
        
    def send_duplicate_palette(self, source_id: int) -> bool:
        """Send duplicate palette command"""
        return self._send_message("/duplicate_palette", source_id)
        
    # ===== Segment Management Commands =====
        
    def send_create_segment(self, custom_id: int) -> bool:
        """Send create segment command"""
        return self._send_message("/create_segment", custom_id)
        
    def send_delete_segment(self, segment_id: int) -> bool:
        """Send delete segment command"""
        return self._send_message("/delete_segment", segment_id)
        
    def send_duplicate_segment(self, source_id: int) -> bool:
        """Send duplicate segment command"""
        return self._send_message("/duplicate_segment", source_id)
        
    def send_reorder_segment(self, segment_id: int, new_position: int) -> bool:
        """Send reorder segment command"""
        return self._send_message("/reorder_segment", segment_id, new_position)
        
    def send_update_segment(self, segment_id: int, param: str, *values) -> bool:
        """Send update segment command with variable parameters"""
        return self._send_message("/update_segment", segment_id, param, *values)
        
    # ===== Dimmer Management Commands =====
        
    def send_create_dimmer(self, segment_id: int, duration_ms: int, initial_brightness: int, final_brightness: int) -> bool:
        """Send create dimmer command"""
        return self._send_message("/create_dimmer", segment_id, duration_ms, initial_brightness, final_brightness)
        
    def send_delete_dimmer(self, segment_id: int, index: int) -> bool:
        """Send delete dimmer command"""
        return self._send_message("/delete_dimmer", segment_id, index)
        
    def send_update_dimmer(self, segment_id: int, index: int, duration_ms: int, initial_brightness: int, final_brightness: int) -> bool:
        """Send update dimmer command"""
        return self._send_message("/update_dimmer", segment_id, index, duration_ms, initial_brightness, final_brightness)
        
    # ===== Query Commands =====
        
    def send_query_full_state(self) -> bool:
        """Send query full state command"""
        return self._send_message("/query_full_state")
        
    def send_query_current_state(self) -> bool:
        """Send query current state command"""
        return self._send_message("/query_current_state")
        
    # ===== Helper Methods =====
        
    def _send_message(self, address: str, *args) -> bool:
        """Send OSC message with error handling"""
        if not self.client:
            AppLogger.warning("OSC client not initialized")
            return False
            
        try:
            if args:
                self.client.send_message(address, args)
            else:
                self.client.send_message(address, [])
            
            AppLogger.info(f"OSC sent: {address} {args}")
            return True
            
        except Exception as e:
            AppLogger.error(f"Failed to send OSC message {address}: {e}")
            return False
            
    def ping_backend(self) -> bool:
        """Ping backend to check connection"""
        return self._send_message("/ping")
        
    def is_connected(self) -> bool:
        """Check if OSC service is connected"""
        return self.client is not None and self.is_running
        
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
        
    # ===== Convenience Methods =====
        
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

# Global instance  
osc_service = OSCService()