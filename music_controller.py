"""
MusicController Module
Handles music/media control using AppleScript for Spotify/Apple Music on macOS.
"""

import time
import platform
import subprocess


class MusicController:
    """
    Controls music playback using AppleScript (macOS) or media keys.
    Directly controls Spotify, Apple Music, or system-wide.
    """
    
    def __init__(self):
        self.is_playing = False # Kept for UI status, but not for logic
        self.is_muted = False
        self.last_action_time = 0
        self.action_cooldown = 0.5
        self.system = platform.system()
        self.volume_level = 50
        
    def _can_act(self):
        """Check if enough time has passed since last action."""
        current_time = time.time()
        if current_time - self.last_action_time < self.action_cooldown:
            return False
        self.last_action_time = current_time
        return True
    
    def _run_applescript(self, script):
        """Run AppleScript command on macOS."""
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except Exception as e:
            print(f"AppleScript error: {e}")
            return False
    
    def _spotify_command(self, command):
        """Send command directly to Spotify."""
        script = f'tell application "Spotify" to {command}'
        return self._run_applescript(script)
    
    def _apple_music_command(self, command):
        """Send command directly to Apple Music."""
        script = f'tell application "Music" to {command}'
        return self._run_applescript(script)
    
    def play(self):
        """Explicitly PLAY music."""
        if not self._can_act():
            return
            
        if self.system == 'Darwin':
            if self._spotify_command('play'):
                pass
            elif self._apple_music_command('play'):
                pass
        
        self.is_playing = True
        print("▶ Playing")

    def pause(self):
        """Explicitly PAUSE music."""
        if not self._can_act():
            return
            
        if self.system == 'Darwin':
            if self._spotify_command('pause'):
                pass
            elif self._apple_music_command('pause'):
                pass
        
        self.is_playing = False
        print("⏸ Paused")
    
    def play_pause(self):
        """Toggle play/pause (legacy/fallback)."""
        if not self._can_act():
            return
        
        if self.system == 'Darwin':
            if self._spotify_command('playpause'):
                pass
            elif self._apple_music_command('playpause'):
                pass
            else:
                self._run_applescript('''
                    tell application "System Events"
                        key code 16 using {command down, option down}
                    end tell
                ''')
        
        self.is_playing = not self.is_playing
        status = "▶ Playing" if self.is_playing else "⏸ Paused"
        print(status)
    
    def next_track(self):
        """Skip to next track."""
        if not self._can_act():
            return
        
        if self.system == 'Darwin':
            if self._spotify_command('next track'):
                pass
            elif self._apple_music_command('next track'):
                pass
            else:
                self._run_applescript('''
                    tell application "System Events"
                        key code 17 using {command down, option down}
                    end tell
                ''')
        
        print("⏭ Next Track")
    
    def previous_track(self):
        """Go to previous track."""
        if not self._can_act():
            return
        
        if self.system == 'Darwin':
            if self._spotify_command('previous track'):
                pass
            elif self._apple_music_command('previous track'):
                pass
            else:
                self._run_applescript('''
                    tell application "System Events"
                        key code 18 using {command down, option down}
                    end tell
                ''')
        
        print("⏮ Previous Track")
    
    def volume_up(self, steps=1):
        """Increase volume."""
        if not self._can_act():
            return
        
        if self.system == 'Darwin':
            for _ in range(steps):
                self._run_applescript('''
                    set curVolume to output volume of (get volume settings)
                    set volume output volume (curVolume + 6.25)
                ''')
            self.volume_level = min(100, self.volume_level + steps * 6)
        
        print(f"🔊 Volume Up (+{steps})")
    
    def volume_down(self, steps=1):
        """Decrease volume."""
        if not self._can_act():
            return
        
        if self.system == 'Darwin':
            for _ in range(steps):
                self._run_applescript('''
                    set curVolume to output volume of (get volume settings)
                    set volume output volume (curVolume - 6.25)
                ''')
            self.volume_level = max(0, self.volume_level - steps * 6)
        
        print(f"🔉 Volume Down (-{steps})")
    
    def mute(self):
        """Toggle mute."""
        if not self._can_act():
            return
        
        if self.system == 'Darwin':
            if self.is_muted:
                self._run_applescript('set volume without output muted')
            else:
                self._run_applescript('set volume with output muted')
        
        self.is_muted = not self.is_muted
        status = "🔇 Muted" if self.is_muted else "🔈 Unmuted"
        print(status)
    
    def get_status(self):
        """Get current playback status string."""
        play_status = "▶ Playing" if self.is_playing else "⏸ Paused"
        mute_status = " (Muted)" if self.is_muted else ""
        return f"{play_status}{mute_status}"
