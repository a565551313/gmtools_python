import os

file_path = r"d:\MENG20251006\allgmtools\gmtools_python\frontend\src\views\dashboard\modules\GiftPanel.vue"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
if "onMounted" not in content:
    content = content.replace("import { ref, reactive, inject } from 'vue'", "import { ref, reactive, inject, onMounted, computed } from 'vue'")

# 2. Update template (Input -> Select)
old_template = """              <div class="input-group">
                <label>物品名称 <em>*</em></label>
                <el-input v-model="itemForm.name" placeholder="请输入物品名称" />
              </div>"""

new_template = """              <div class="input-group">
                <label>物品名称 <em>*</em></label>
                <el-select 
                  v-model="itemForm.name" 
                  placeholder="请选择物品" 
                  filterable 
                  style="width: 100%"
                >
                  <el-option
                    v-for="item in availableItems"
                    :key="item.item_name"
                    :label="item.display_name"
                    :value="item.item_name"
                  >
                    <span style="float: left">{{ item.display_name }}</span>
                    <span style="float: right; color: #8492a6; font-size: 13px">{{ item.item_name }}</span>
                  </el-option>
                </el-select>
                <div class="limit-info" v-if="currentItemLimit" style="margin-top: 5px; font-size: 12px; color: #666;">
                  <span :style="{ color: currentItemLimit.remaining <= 0 ? '#f56c6c' : '#67c23a' }">
                    剩余配额: {{ currentItemLimit.remaining }}/{{ currentItemLimit.total_limit }} 
                  </span>
                  <span style="color: #909399; margin-left: 5px;">
                    (每{{ currentItemLimit.reset_period_hours }}小时重置)
                  </span>
                </div>
              </div>"""

if "availableItems" not in content:
    content = content.replace(old_template, new_template)

# 3. Update Script Logic
old_script = """// ========== 物品赠送 ==========
async function giveItem() {
  if (!playerId.value) return ElMessage.error('请输入角色ID')
  if (!itemForm.name) return ElMessage.error('请输入物品名称')

  try {
    const res = await request.post('/api/gift', {
      function: 'give_item',
      args: {
        player_id: playerId.value,
        item_name: itemForm.name,
        count: parseInt(itemForm.amount || '1'),
        item_category: itemForm.params || "default"
      }
    })
    logToConsole('POST', '/api/gift', 200, res)
    ElMessage.success('道具赠送成功')
  } catch (e) {
    logToConsole('POST', '/api/gift', 0, { error: e.message })
    ElMessage.error('赠送失败')
  }
}"""

new_script = """// 物品列表和限制
const availableItems = ref([])
const itemLimits = ref({})
const itemUsage = ref({})

// 加载物品数据
async function loadItemData() {
  try {
    const [itemsRes, usageRes] = await Promise.all([
      request.get('/api/items/available'),
      request.get('/api/items/my-usage')
    ])
    availableItems.value = itemsRes.data || []
    
    // 处理使用情况
    const usageMap = {}
    if (usageRes.data) {
      usageRes.data.forEach(u => {
        usageMap[u.item_name] = u
      })
    }
    itemUsage.value = usageMap
  } catch (e) {
    console.error('加载物品数据失败', e)
  }
}

// 计算当前选中物品的限制信息
const currentItemLimit = computed(() => {
  if (!itemForm.name) return null
  return itemUsage.value[itemForm.name]
})

// ========== 物品赠送 ==========
async function giveItem() {
  if (!playerId.value) return ElMessage.error('请输入角色ID')
  if (!itemForm.name) return ElMessage.error('请选择物品')

  try {
    const res = await request.post('/api/items/send-gift', {
      recipient_username: playerId.value,
      item_name: itemForm.name,
      quantity: parseInt(itemForm.amount || '1')
    })
    
    logToConsole('POST', '/api/items/send-gift', 200, res)
    ElMessage.success(res.message || '道具赠送成功')
    
    // 刷新使用情况
    loadItemData()
  } catch (e) {
    const errorMsg = e.response?.data?.detail || '赠送失败'
    logToConsole('POST', '/api/items/send-gift', 0, { error: errorMsg })
    ElMessage.error(errorMsg)
  }
}

onMounted(() => {
  loadItemData()
})"""

if "loadItemData" not in content:
    content = content.replace(old_script, new_script)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("GiftPanel.vue updated successfully")
