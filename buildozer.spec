[app]
title = FlowScript
package.name = flowscript
package.domain = app.flowscript
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,java,xml
version = 0.3

# ✅ STABLE COMBO
requirements = python3==3.9.18,kivy==2.1.0,requests,certifi,pyjnius==1.5.0

# ✅ MINIMAL SAFE PERMISSIONS (add later if needed)
android.permissions = INTERNET,BIND_ACCESSIBILITY_SERVICE,POST_NOTIFICATIONS

# ✅ STABLE ANDROID LEVELS
android.api = 31
android.minapi = 21

# ✅ MATCH BUILD TOOLS
android.build_tools_version = 33.0.0
android.ndk = 25.1.8937393

# ✅ SINGLE ARCH (LESS CHAOS)
android.archs = arm64-v8a

# ✅ IMPORTANT (prevents toolchain mismatch)


# ✅ KEEP THIS
android.release_artifact = apk
android.allow_backup = True

# Keep your custom stuff
android.add_res = res
android.add_manifests = manifest_patch.xml

# SDK paths
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.1.8937393

orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1