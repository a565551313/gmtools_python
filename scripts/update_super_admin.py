import os

file_path = r"d:\MENG20251006\allgmtools\gmtools_python\frontend\src\views\admin\SuperAdmin.vue"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Goods icon
if "Goods" not in content:
    content = content.replace("DArrowRight\n} from '@element-plus/icons-vue'", "DArrowRight, Goods\n} from '@element-plus/icons-vue'")

# 2. Add itemGift module
item_gift_module = """  levelConfig: {
    name: '等级管理',
    description: '管理等级配置，自定义等级名称',
    icon: markRaw(Star),
    badge: null
  },
  itemGift: {
    name: '道具限制',
    description: '管理道具白名单及等级发送限制',
    icon: markRaw(Goods),
    badge: null
  }"""

if "itemGift: {" not in content:
    content = content.replace("""  levelConfig: {
    name: '等级管理',
    description: '管理等级配置，自定义等级名称',
    icon: markRaw(Star),
    badge: null
  }""", item_gift_module)

# 3. Add template
template_part = """            <!-- 活动管理 -->
            <ActivityManagementPanel v-else-if="currentModule === 'events'" ref="activityPanelRef" />

            <!-- 道具限制管理 -->
            <ItemGiftManagementPanel v-else-if="currentModule === 'itemGift'" />"""

if "ItemGiftManagementPanel" not in content:
    # Note: checking if already added in template
    if '<ItemGiftManagementPanel v-else-if="currentModule === \'itemGift\'"' not in content:
        content = content.replace("""            <!-- 活动管理 -->
            <ActivityManagementPanel v-else-if="currentModule === 'events'" ref="activityPanelRef" />""", template_part)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SuperAdmin.vue updated successfully")
