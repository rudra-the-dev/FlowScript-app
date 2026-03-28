[app]
title = FlowScript
package.name = flowscript
package.domain = app.flowscript
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,java,xml
version = 0.4
requirements = python3,kivy==2.1.0,requests
android.permissions = INTERNET,BIND_ACCESSIBILITY_SERVICE,POST_NOTIFICATIONS
android.api = 31
android.minapi = 21
android.ndk = 25b
android.build_tools_version = 33.0.0
android.archs = arm64-v8a
android.allow_backup = True
android.add_res = res
android.add_manifests = manifest_patch.xml
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1