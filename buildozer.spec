[app]
title = FlowScript
package.name = flowscript
package.domain = app.flowscript
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,java,xml
version = 0.3

# 🔥 FIXED REQUIREMENTS
requirements = python3==3.10.12,kivy==2.1.0,requests,certifi,pyjnius

# 🔥 CLEAN PERMISSIONS (removed risky ones for now)
android.permissions = INTERNET,BIND_ACCESSIBILITY_SERVICE,POST_NOTIFICATIONS

# 🔥 STABLE ANDROID API
android.api = 31
android.minapi = 21

# 🔥 SAFE TOOLCHAIN
android.ndk = 25.1.8937393
android.build_tools_version = 33.0.0

# 🔥 SINGLE ARCH (reduces crashes)
android.archs = arm64-v8a

android.allow_backup = True

# Keep these (they're fine now)
android.add_res = res
android.add_manifests = manifest_patch.xml

# SDK paths (unchanged)
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.1.8937393

orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1