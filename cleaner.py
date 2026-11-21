"""
cleanup_and_run.py
Remove cache, then user runs main manually.
"""
import os
import shutil

PROJECT_ROOT = "/storage/emulated/0/python/3phase_motor/kivy/0.1.3.2"

print("=" * 70)
print("CLEANUP")
print("=" * 70)

# حذف __pycache__
count = 0
for root, dirs, files in os.walk(PROJECT_ROOT):
    if "__pycache__" in dirs:
        p = os.path.join(root, "__pycache__")
        try:
            shutil.rmtree(p)
            count += 1
        except Exception:
            pass
print(f"  Removed {count} __pycache__ folders")

# حذف draft
draft = os.path.join(PROJECT_ROOT, "drafts", "project_draft.json")
if os.path.exists(draft):
    os.remove(draft)
    print(f"  Removed draft")

print()
print("Ready to run main0.1.3.2.py")