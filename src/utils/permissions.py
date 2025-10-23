"""
macOS Permissions Checker

Handles checking and requesting macOS permissions for:
- Microphone access
- Accessibility (for hotkey monitoring)
- Screen Recording (for context capture)
"""

import subprocess
import os
from typing import Dict, Tuple
from enum import Enum


class Permission(Enum):
    """Permission types"""
    MICROPHONE = "microphone"
    ACCESSIBILITY = "accessibility"
    SCREEN_RECORDING = "screen_recording"


class PermissionChecker:
    """Check and request macOS permissions"""

    @staticmethod
    def check_microphone() -> bool:
        """
        Check if microphone permission is granted

        Returns:
            True if microphone access is granted
        """
        try:
            # Try to import AVFoundation
            from Cocoa import AVCaptureDevice, AVMediaTypeAudio
            from Cocoa import AVAuthorizationStatusAuthorized

            # Check authorization status
            status = AVCaptureDevice.authorizationStatusForMediaType_(AVMediaTypeAudio)
            return status == AVAuthorizationStatusAuthorized
        except ImportError:
            # PyObjC not properly installed, skip check
            # macOS will prompt when app tries to use microphone
            print("Note: Cannot check microphone permission (PyObjC issue)")
            print("macOS will prompt for permission when needed")
            return True  # Assume granted, let macOS handle it
        except Exception as e:
            print(f"Error checking microphone permission: {e}")
            # If we can't check, assume granted and let macOS handle it
            return True

    @staticmethod
    def request_microphone() -> None:
        """
        Request microphone permission
        This will trigger the system permission dialog
        """
        try:
            from Cocoa import AVCaptureDevice, AVMediaTypeAudio

            # This triggers the permission dialog
            AVCaptureDevice.requestAccessForMediaType_completionHandler_(
                AVMediaTypeAudio,
                lambda granted: print(f"Microphone access: {'granted' if granted else 'denied'}")
            )
        except Exception as e:
            print(f"Error requesting microphone permission: {e}")

    @staticmethod
    def check_accessibility() -> bool:
        """
        Check if Accessibility permission is granted

        Returns:
            True if accessibility access is granted
        """
        try:
            # Use AppleScript to check accessibility
            script = """
            tell application "System Events"
                return true
            end tell
            """
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Note: Cannot check accessibility permission")
            print("macOS will prompt when needed")
            # Assume granted, let macOS handle it
            return True

    @staticmethod
    def request_accessibility() -> None:
        """
        Request Accessibility permission
        Opens System Settings to the correct pane
        """
        try:
            # Open System Settings to Accessibility pane
            subprocess.run([
                'open',
                'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'
            ])
            print("Please grant Accessibility permission in System Settings")
        except Exception as e:
            print(f"Error opening accessibility settings: {e}")

    @staticmethod
    def check_screen_recording() -> bool:
        """
        Check if Screen Recording permission is granted

        Returns:
            True if screen recording access is granted
        """
        try:
            # Try to capture a tiny screenshot to check permission
            from Quartz import CGWindowListCreateImage, CGRectNull, kCGWindowListOptionOnScreenOnly, kCGNullWindowID

            # Attempt to capture screen
            image = CGWindowListCreateImage(
                CGRectNull,
                kCGWindowListOptionOnScreenOnly,
                kCGNullWindowID,
                0
            )

            return image is not None
        except ImportError:
            # Quartz not properly installed, skip check
            print("Note: Cannot check screen recording permission (Quartz not available)")
            print("This is OK - screen recording is only needed for context awareness")
            return True  # Assume granted, not critical for basic functionality
        except Exception as e:
            print(f"Note: Cannot check screen recording permission")
            # Not critical, assume granted
            return True

    @staticmethod
    def request_screen_recording() -> None:
        """
        Request Screen Recording permission
        Opens System Settings to the correct pane
        """
        try:
            # Open System Settings to Screen Recording pane
            subprocess.run([
                'open',
                'x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture'
            ])
            print("Please grant Screen Recording permission in System Settings")
        except Exception as e:
            print(f"Error opening screen recording settings: {e}")

    @staticmethod
    def check_all_permissions() -> Dict[Permission, bool]:
        """
        Check all required permissions

        Returns:
            Dictionary mapping permission types to their status
        """
        return {
            Permission.MICROPHONE: PermissionChecker.check_microphone(),
            Permission.ACCESSIBILITY: PermissionChecker.check_accessibility(),
            Permission.SCREEN_RECORDING: PermissionChecker.check_screen_recording(),
        }

    @staticmethod
    def get_missing_permissions() -> list[Permission]:
        """
        Get list of missing permissions

        Returns:
            List of permissions that are not granted
        """
        all_perms = PermissionChecker.check_all_permissions()
        return [perm for perm, granted in all_perms.items() if not granted]

    @staticmethod
    def request_permission(permission: Permission) -> None:
        """
        Request a specific permission

        Args:
            permission: The permission to request
        """
        if permission == Permission.MICROPHONE:
            PermissionChecker.request_microphone()
        elif permission == Permission.ACCESSIBILITY:
            PermissionChecker.request_accessibility()
        elif permission == Permission.SCREEN_RECORDING:
            PermissionChecker.request_screen_recording()

    @staticmethod
    def request_all_missing() -> list[Permission]:
        """
        Request all missing permissions

        Returns:
            List of permissions that were requested
        """
        missing = PermissionChecker.get_missing_permissions()
        for perm in missing:
            PermissionChecker.request_permission(perm)
        return missing

    @staticmethod
    def get_permission_status_message() -> str:
        """
        Get a human-readable status message about permissions

        Returns:
            Status message string
        """
        perms = PermissionChecker.check_all_permissions()
        missing = [p for p, granted in perms.items() if not granted]

        if not missing:
            return "✓ All permissions granted"

        messages = []
        for perm in missing:
            if perm == Permission.MICROPHONE:
                messages.append("✗ Microphone access required")
            elif perm == Permission.ACCESSIBILITY:
                messages.append("✗ Accessibility access required (for hotkey detection)")
            elif perm == Permission.SCREEN_RECORDING:
                messages.append("✗ Screen Recording access required (for context capture)")

        return "\n".join(messages)

    @staticmethod
    def wait_for_permissions(required: list[Permission] = None, timeout: int = 60) -> bool:
        """
        Wait for permissions to be granted (polling)

        Args:
            required: List of required permissions (default: all)
            timeout: Maximum time to wait in seconds

        Returns:
            True if all required permissions are granted within timeout
        """
        import time

        if required is None:
            required = [Permission.MICROPHONE, Permission.ACCESSIBILITY, Permission.SCREEN_RECORDING]

        start_time = time.time()
        while time.time() - start_time < timeout:
            all_perms = PermissionChecker.check_all_permissions()
            if all(all_perms.get(p, False) for p in required):
                return True
            time.sleep(1)

        return False


def check_and_request_permissions(interactive: bool = True) -> Tuple[bool, list[Permission]]:
    """
    Convenience function to check and optionally request permissions

    Args:
        interactive: If True, request missing permissions

    Returns:
        Tuple of (all_granted, missing_permissions)
    """
    checker = PermissionChecker()
    missing = checker.get_missing_permissions()

    if missing and interactive:
        print("\nVoice Mode requires the following permissions:")
        print(checker.get_permission_status_message())
        print("\nOpening System Settings to grant permissions...")

        for perm in missing:
            checker.request_permission(perm)

        print("\nWaiting for permissions to be granted...")
        print("(Grant permissions in System Settings, then this will continue)")

        # Wait for permissions
        if checker.wait_for_permissions(missing, timeout=120):
            print("\n✓ All permissions granted!")
            return True, []
        else:
            print("\n✗ Timeout waiting for permissions")
            return False, missing

    return len(missing) == 0, missing


if __name__ == "__main__":
    # Test permissions
    print("Checking macOS permissions...\n")
    checker = PermissionChecker()

    all_perms = checker.check_all_permissions()
    for perm, granted in all_perms.items():
        status = "✓" if granted else "✗"
        print(f"{status} {perm.value}: {'granted' if granted else 'NOT granted'}")

    missing = checker.get_missing_permissions()
    if missing:
        print(f"\nMissing permissions: {[p.value for p in missing]}")
        print("\nRun check_and_request_permissions() to request them.")
    else:
        print("\n✓ All permissions granted!")
