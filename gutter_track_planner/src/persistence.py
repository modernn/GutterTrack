import json
import os
import shutil
import datetime
import asyncio
from pathlib import Path

# For PWA local storage compatibility
try:
    from js import localStorage
    IS_WEB = True
except ImportError:
    IS_WEB = False

class TrackStorage:
    """Handles track storage for both local and web environments"""
    
    def __init__(self, app_name="GutterTrack"):
        self.app_name = app_name
        
        if IS_WEB:
            # For web/PWA environment, use localStorage
            self.storage_type = "web"
        else:
            # For local environment, use file system
            self.storage_type = "local"
            
            # Create app data directory if it doesn't exist
            if os.name == 'nt':  # Windows
                app_data = os.getenv('APPDATA') or os.path.expanduser('~\\AppData\\Roaming')
                self.data_dir = os.path.join(app_data, app_name)
            else:  # macOS/Linux
                self.data_dir = os.path.expanduser(f'~/.{app_name.lower()}')
            
            os.makedirs(self.data_dir, exist_ok=True)
    
    def save_track(self, track, filename=None):
        """Save track to storage"""
        try:
            # Convert track to JSON
            track_data = track.to_dict()
            track_json = json.dumps(track_data)
            
            if filename is None:
                # Generate a default filename if none provided
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"track_{timestamp}.json"
            elif not filename.endswith('.json'):
                filename += '.json'
            
            if self.storage_type == "web":
                # Save to localStorage
                key = f"{self.app_name}_track_{filename}"
                try:
                    localStorage.setItem(key, track_json)
                except Exception as e:
                    print(f"Error saving to localStorage: {e}")
                    return False, str(e)
            else:
                # Save to file
                file_path = os.path.join(self.data_dir, filename)
                with open(file_path, 'w') as f:
                    f.write(track_json)
            
            return True, filename
        except Exception as e:
            return False, str(e)
    
    def load_track(self, filename):
        """Load track from storage"""
        try:
            from models import Track
            
            if self.storage_type == "web":
                # Load from localStorage
                key = f"{self.app_name}_track_{filename}"
                track_json = localStorage.getItem(key)
                if not track_json:
                    return False, f"Track '{filename}' not found"
            else:
                # Load from file
                file_path = os.path.join(self.data_dir, filename)
                if not os.path.exists(file_path):
                    return False, f"File not found: {file_path}"
                
                with open(file_path, 'r') as f:
                    track_json = f.read()
            
            # Convert JSON to Track object
            track_data = json.loads(track_json)
            track = Track.from_dict(track_data)
            
            return True, track
        except Exception as e:
            return False, str(e)
    
    def list_tracks(self):
        """List all saved tracks"""
        tracks = []
        
        try:
            if self.storage_type == "web":
                # List tracks from localStorage
                for i in range(localStorage.length):
                    key = localStorage.key(i)
                    if key and key.startswith(f"{self.app_name}_track_"):
                        filename = key.replace(f"{self.app_name}_track_", "")
                        # Extract timestamp from filename if possible
                        try:
                            if "_" in filename:
                                date_part = filename.split("_")[1].split(".")[0]
                                date = datetime.datetime.strptime(date_part, "%Y%m%d%H%M%S")
                            else:
                                date = datetime.datetime.now()
                        except:
                            date = datetime.datetime.now()
                        
                        tracks.append({
                            'name': filename,
                            'path': key,
                            'date': date.timestamp()
                        })
            else:
                # List tracks from file system
                for filename in os.listdir(self.data_dir):
                    if filename.endswith('.json'):
                        file_path = os.path.join(self.data_dir, filename)
                        tracks.append({
                            'name': filename,
                            'path': file_path,
                            'date': os.path.getmtime(file_path)
                        })
            
            # Sort by date (newest first)
            tracks.sort(key=lambda x: x['date'], reverse=True)
        except Exception as e:
            print(f"Error listing tracks: {e}")
        
        return tracks
    
    def delete_track(self, filename):
        """Delete a track from storage"""
        try:
            if self.storage_type == "web":
                # Delete from localStorage
                key = f"{self.app_name}_track_{filename}"
                localStorage.removeItem(key)
            else:
                # Delete from file system
                file_path = os.path.join(self.data_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                else:
                    return False, f"File not found: {file_path}"
            
            return True, f"Deleted track: {filename}"
        except Exception as e:
            return False, str(e)
    
    def export_track(self, track, export_path):
        """Export track to a specific location"""
        try:
            # Convert track to JSON
            track_data = track.to_dict()
            track_json = json.dumps(track_data, indent=2)
            
            # Ensure path has .json extension
            if not export_path.endswith('.json'):
                export_path += '.json'
            
            # Write to file
            with open(export_path, 'w') as f:
                f.write(track_json)
            
            return True, export_path
        except Exception as e:
            return False, str(e)
    
    def import_track(self, import_path):
        """Import track from a specific location"""
        try:
            from models import Track
            
            # Read file
            with open(import_path, 'r') as f:
                track_json = f.read()
            
            # Convert JSON to Track object
            track_data = json.loads(track_json)
            track = Track.from_dict(track_data)
            
            # Also save to default storage
            filename = os.path.basename(import_path)
            self.save_track(track, filename)
            
            return True, track
        except Exception as e:
            return False, str(e)
    
    def backup_all_tracks(self, backup_dir):
        """Backup all tracks to a directory"""
        try:
            if self.storage_type == "web":
                # For web storage, export each track to the backup directory
                success_count = 0
                for track_info in self.list_tracks():
                    success, track = self.load_track(track_info['name'])
                    if success:
                        backup_path = os.path.join(backup_dir, track_info['name'])
                        success, _ = self.export_track(track, backup_path)
                        if success:
                            success_count += 1
                
                return True, f"Backed up {success_count} tracks"
            else:
                # For file storage, just copy all files
                os.makedirs(backup_dir, exist_ok=True)
                
                copied = 0
                for filename in os.listdir(self.data_dir):
                    if filename.endswith('.json'):
                        src = os.path.join(self.data_dir, filename)
                        dst = os.path.join(backup_dir, filename)
                        shutil.copy2(src, dst)
                        copied += 1
                
                return True, f"Backed up {copied} tracks"
        except Exception as e:
            return False, str(e)

# For web environments, create a wrapper for localStorage to use in cache
class LocalStorageCache:
    """Cache wrapper for localStorage"""
    def __init__(self, prefix="GutterTrack_cache_"):
        self.prefix = prefix
    
    def get(self, key):
        """Get item from cache"""
        if not IS_WEB:
            return None
        
        try:
            full_key = f"{self.prefix}{key}"
            value = localStorage.getItem(full_key)
            if value:
                # Check if it's JSON
                try:
                    return json.loads(value)
                except:
                    return value
            return None
        except:
            return None
    
    def set(self, key, value, expiry_seconds=None):
        """Set item in cache with optional expiry"""
        if not IS_WEB:
            return False
        
        try:
            full_key = f"{self.prefix}{key}"
            
            # If value is not a string, convert to JSON
            if not isinstance(value, str):
                value = json.dumps(value)
            
            # If expiry is set, create a wrapper object with expiry timestamp
            if expiry_seconds:
                expiry = datetime.datetime.now() + datetime.timedelta(seconds=expiry_seconds)
                wrapper = {
                    "value": value,
                    "expiry": expiry.timestamp()
                }
                localStorage.setItem(full_key, json.dumps(wrapper))
            else:
                localStorage.setItem(full_key, value)
            
            return True
        except:
            return False
    
    def delete(self, key):
        """Delete item from cache"""
        if not IS_WEB:
            return False
        
        try:
            full_key = f"{self.prefix}{key}"
            localStorage.removeItem(full_key)
            return True
        except:
            return False
    
    def clear(self):
        """Clear all items from cache with this prefix"""
        if not IS_WEB:
            return False
        
        try:
            keys_to_remove = []
            
            # Find all keys with our prefix
            for i in range(localStorage.length):
                key = localStorage.key(i)
                if key and key.startswith(self.prefix):
                    keys_to_remove.append(key)
            
            # Remove all found keys
            for key in keys_to_remove:
                localStorage.removeItem(key)
            
            return True
        except:
            return False