import os

file_path = r"d:\MENG20251006\allgmtools\gmtools_python\frontend\src\views\admin\SuperAdmin.vue"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Target string to find
target = """            <!-- 活动管理 -->
            <ActivityManagementPanel v-else-if="currentModule === 'events'" ref="activityPanelRef" />"""

# Replacement string
replacement = """            <!-- 活动管理 -->
            <ActivityManagementPanel v-else-if="currentModule === 'events'" ref="activityPanelRef" />

            <!-- 道具限制管理 -->
            <ItemGiftManagementPanel v-else-if="currentModule === 'itemGift'" />"""

if "ItemGiftManagementPanel" in content:
    if '<ItemGiftManagementPanel v-else-if="currentModule === \'itemGift\'"' not in content:
        if target in content:
            content = content.replace(target, replacement)
            print("Template updated successfully")
        else:
            print("Target string not found in content")
            # Debug: print surrounding lines
            idx = content.find("ActivityManagementPanel")
            if idx != -1:
                print("Found ActivityManagementPanel at index", idx)
                print("Surrounding content:")
                print(content[idx-50:idx+150])
            else:
                print("ActivityManagementPanel not found")
    else:
        print("ItemGiftManagementPanel already in template")
else:
    print("ItemGiftManagementPanel not imported or defined?")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
