<template>
  <div class="activation-panel space-y-6">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon bg-teal-100 text-teal-600"><Ticket /></el-icon>
          <span>生成激活码</span>
        </div>
      </template>
      <div class="flex flex-wrap gap-4 items-end">
        <div class="w-40">
          <div class="label">类型</div>
          <el-select v-model="type" placeholder="选择类型">
            <el-option label="新手礼包" value="newbie" />
            <el-option label="进阶礼包" value="advanced" />
            <el-option label="至尊礼包" value="supreme" />
          </el-select>
        </div>
        <div class="w-32">
          <div class="label">数量</div>
          <el-input v-model="count" placeholder="1" />
        </div>
        <el-button type="primary" @click="generateCodes">生成</el-button>
      </div>
    </el-card>

    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon class="header-icon bg-gray-100 text-gray-600"><List /></el-icon>
          <span>激活码列表</span>
        </div>
      </template>
      <el-table :data="codes" style="width: 100%" v-loading="loading">
        <el-table-column prop="code" label="激活码" width="200" />
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'unused' ? 'success' : 'info'">
              {{ scope.row.status === 'unused' ? '未使用' : '已使用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, inject, onMounted } from 'vue'
import request from '@/api/request'
import { ElMessage } from 'element-plus'
import { Ticket, List } from '@element-plus/icons-vue'

const logToConsole = inject('logToConsole')

const type = ref('newbie')
const count = ref('1')
const codes = ref([])
const loading = ref(false)

async function generateCodes() {
  try {
    const res = await request.post('/api/activation', { 
      function: 'generate_codes', 
      args: { type: type.value, count: parseInt(count.value) || 1 } 
    })
    logToConsole('POST', '/api/activation', 200, res)
    ElMessage.success('生成成功')
    fetchCodes()
  } catch (e) {
    logToConsole('POST', '/api/activation', 0, { error: e.message })
  }
}

async function fetchCodes() {
  loading.value = true
  try {
    const res = await request.get('/api/activation/list')
    codes.value = res.data || []
    logToConsole('GET', '/api/activation/list', 200, res)
  } catch (e) {
    logToConsole('GET', '/api/activation/list', 0, { error: e.message })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCodes()
})
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: bold;
}

.header-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.label {
  font-size: 12px;
  font-weight: bold;
  color: #6b7280;
  text-transform: uppercase;
  margin-bottom: 4px;
}
</style>
