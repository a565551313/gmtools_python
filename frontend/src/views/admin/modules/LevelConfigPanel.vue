<template>
  <div class="level-config-panel">
    <div class="panel-header">
      <div class="header-left">
        <el-icon class="header-icon"><Setting /></el-icon>
        <div class="header-text">
          <h2>等级配置管理</h2>
          <p>自定义等级名称、添加或删除等级配置</p>
        </div>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="showAddDialog">添加新等级</el-button>
        <el-button :icon="Refresh" @click="loadLevelConfigs">刷新</el-button>
      </div>
    </div>

    <!-- 等级配置表格 -->
    <el-table
      v-loading="loading"
      :data="levelConfigs"
      stripe
      style="width: 100%"
      class="level-table"
    >
      <el-table-column prop="level_value" label="等级值" width="100" sortable>
        <template #default="{ row }">
          <el-tag :type="getLevelTagType(row.level_value)" size="large">
            {{ row.level_value }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="display_name" label="显示名称" min-width="150">
        <template #default="{ row }">
          <span class="display-name">{{ row.display_name }}</span>
        </template>
      </el-table-column>

      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />

      <el-table-column prop="sort_order" label="排序" width="80" sortable />

      <el-table-column label="使用统计" width="280">
        <template #default="{ row }">
          <div class="stats-container">
            <el-tag size="small" type="success">
              <el-icon><User /></el-icon>
              {{ row.user_count || 0 }} 用户
            </el-tag>
            <el-tag size="small" type="warning">
              <el-icon><Ticket /></el-icon>
              {{ row.activation_code_unused || 0 }} / {{ row.activation_code_total || 0 }} 激活码
            </el-tag>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            :icon="Edit"
            @click="showEditDialog(row)"
          >
            编辑
          </el-button>
          <el-popconfirm
            title="确定删除此等级吗？"
            confirm-button-text="确定"
            cancel-button-text="取消"
            @confirm="deleteLevel(row.level_value)"
          >
            <template #reference>
              <el-button
                type="danger"
                size="small"
                :icon="Delete"
                :disabled="row.user_count > 0"
              >
                删除
              </el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'add' ? '添加新等级' : '编辑等级'"
      width="500px"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="等级值" prop="level_value" v-if="dialogMode === 'add'">
          <el-input-number
            v-model="formData.level_value"
            :min="1"
            :max="100"
            :step="1"
            style="width: 100%"
          />
          <span class="form-tip">1-100之间的整数，必须唯一</span>
        </el-form-item>

        <el-form-item label="显示名称" prop="display_name">
          <el-input
            v-model="formData.display_name"
            placeholder="如：青铜一、钻石"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="等级描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="对该等级的简要描述"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="排序顺序" prop="sort_order">
          <el-input-number
            v-model="formData.sort_order"
            :min="1"
            :max="1000"
            style="width: 100%"
          />
          <span class="form-tip">数字越小越靠前</span>
        </el-form-item>

        <el-form-item label="启用状态" prop="is_active" v-if="dialogMode === 'edit'">
          <el-switch v-model="formData.is_active" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          {{ dialogMode === 'add' ? '添加' : '保存' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '@/api/request'
import { ElMessage } from 'element-plus'
import {
  Setting, Plus, Refresh, Edit, Delete, User, Ticket
} from '@element-plus/icons-vue'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref('add') // 'add' or 'edit'
const formRef = ref(null)

const levelConfigs = ref([])

const formData = reactive({
  level_value: 1,
  display_name: '',
  description: '',
  sort_order: 1,
  is_active: true
})

const formRules = {
  level_value: [
    { required: true, message: '请输入等级值', trigger: 'blur' },
    { type: 'number', min: 1, max: 100, message: '等级值必须在1-100之间', trigger: 'blur' }
  ],
  display_name: [
    { required: true, message: '请输入显示名称', trigger: 'blur' },
    { min: 1, max: 50, message: '名称长度在1-50个字符', trigger: 'blur' }
  ],
  sort_order: [
    { required: true, message: '请输入排序顺序', trigger: 'blur' }
  ]
}

// 获取等级标签类型
function getLevelTagType(level) {
  if (level <= 3) return ''
  if (level <= 6) return 'success'
  if (level <= 9) return 'warning'
  return 'danger'
}

// 加载等级配置列表
async function loadLevelConfigs() {
  loading.value = true
  try {
    const res = await request.get('/api/level-configs', {
      params: {
        include_inactive: true,
        include_stats: true
      }
    })
    levelConfigs.value = res.data || []
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '加载等级配置失败')
  } finally {
    loading.value = false
  }
}

// 显示添加对话框
function showAddDialog() {
  dialogMode.value = 'add'
  resetForm()
  dialogVisible.value = true
}

// 显示编辑对话框
function showEditDialog(row) {
  dialogMode.value = 'edit'
  formData.level_value = row.level_value
  formData.display_name = row.display_name
  formData.description = row.description
  formData.sort_order = row.sort_order
  formData.is_active = row.is_active
  dialogVisible.value = true
}

// 重置表单
function resetForm() {
  formData.level_value = levelConfigs.value.length > 0 
    ? Math.max(...levelConfigs.value.map(c => c.level_value)) + 1 
    : 1
  formData.display_name = ''
  formData.description = ''
  formData.sort_order = formData.level_value
  formData.is_active = true
}

// 提交表单
async function submitForm() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (dialogMode.value === 'add') {
        await request.post('/api/level-configs', {
          level_value: formData.level_value,
          display_name: formData.display_name,
          description: formData.description,
          sort_order: formData.sort_order
        })
        ElMessage.success(`等级 ${formData.level_value} 创建成功`)
      } else {
        await request.put(`/api/level-configs/${formData.level_value}`, {
          display_name: formData.display_name,
          description: formData.description,
          sort_order: formData.sort_order,
          is_active: formData.is_active
        })
        ElMessage.success(`等级 ${formData.level_value} 更新成功`)
      }
      
      dialogVisible.value = false
      await loadLevelConfigs()
    } catch (e) {
      ElMessage.error(e.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

// 删除等级
async function deleteLevel(levelValue) {
  loading.value = true
  try {
    await request.delete(`/api/level-configs/${levelValue}`)
    ElMessage.success(`等级 ${levelValue} 已删除`)
    await loadLevelConfigs()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '删除失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadLevelConfigs()
})
</script>

<style scoped>
.level-config-panel {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  font-size: 32px;
  color: #409eff;
}

.header-text h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.header-text p {
  margin: 4px 0 0 0;
  font-size: 14px;
  color: #909399;
}

.header-right {
  display: flex;
  gap: 12px;
}

.level-table {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.display-name {
  font-weight: 600;
  color: #303133;
}

.stats-container {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.stats-container .el-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.form-tip {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .header-right {
    width: 100%;
  }
  
  .header-right .el-button {
    flex: 1;
  }
}
</style>
