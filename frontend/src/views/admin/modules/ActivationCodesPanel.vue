<template>
  <div class="panel-container">
    <!-- 筛选器 -->
    <div class="filter-bar">
      <div class="filter-grid">
        <div class="filter-item">
          <label>等级筛选</label>
          <el-select v-model="filters.level" placeholder="全部等级" clearable @change="loadCodes(1)">
            <el-option v-for="level in 10" :key="level" :label="'Level ' + level" :value="level" />
          </el-select>
        </div>
        <div class="filter-item">
          <label>使用状态</label>
          <el-select v-model="filters.is_used" placeholder="全部状态" clearable @change="loadCodes(1)">
            <el-option label="未使用" value="false" />
            <el-option label="已使用" value="true" />
          </el-select>
        </div>
        <div class="filter-item">
          <label>每页数量</label>
          <el-select v-model="filters.limit" @change="loadCodes(1)">
            <el-option :label="'10 条/页'" :value="10" />
            <el-option :label="'20 条/页'" :value="20" />
            <el-option :label="'50 条/页'" :value="50" />
          </el-select>
        </div>
      </div>
      <div class="filter-actions">
        <el-button @click="loadCodes(1)" plain>
          <el-icon><Refresh /></el-icon> 刷新
        </el-button>
        <el-button type="primary" @click="showGenerateModal = true">
          <el-icon><Plus /></el-icon> 生成激活码
        </el-button>
      </div>
    </div>

    <!-- 桌面端表格视图 (> 768px) -->
    <div class="desktop-view">
      <div class="table-container">
        <el-table :data="codes" v-loading="loading" style="width: 100%">
          <el-table-column label="激活码" min-width="180">
            <template #default="{ row }">
              <code class="code-cell">{{ row.code }}</code>
            </template>
          </el-table-column>
          <el-table-column label="等级" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="primary" size="small" effect="dark">Lv.{{ row.level }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_used ? 'danger' : 'success'" size="small">
                {{ row.is_used ? '已使用' : '未使用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="used_username" label="使用用户" width="120" align="center">
            <template #default="{ row }">{{ row.used_username || row.used_by || '-' }}</template>
          </el-table-column>
          <el-table-column prop="expires_at" label="过期时间" width="160" align="center" />
          <el-table-column prop="created_at" label="创建时间" width="160" align="center" />
          <el-table-column label="操作" width="80" align="center" fixed="right">
            <template #default="{ row }">
              <el-button link type="danger" @click="deleteCode(row.code)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 移动端卡片视图 (<= 768px) -->
    <div class="mobile-view">
      <div v-if="codes.length === 0 && !loading" class="empty-state">
        <el-icon :size="48"><Ticket /></el-icon>
        <h3>暂无激活码</h3>
        <p>点击上方按钮生成新的激活码</p>
      </div>

      <div v-else class="cards-container" v-loading="loading">
        <div v-for="code in codes" :key="code.code" class="code-card">
          <div class="card-header">
            <code class="code-text">{{ code.code }}</code>
            <el-tag :type="code.is_used ? 'danger' : 'success'" size="small">
              {{ code.is_used ? '已使用' : '未使用' }}
            </el-tag>
          </div>
          
          <div class="card-body">
            <div class="info-row">
              <span class="label">等级权限</span>
              <el-tag type="primary" size="small" effect="dark">Level {{ code.level }}</el-tag>
            </div>
            <div class="info-row" v-if="code.is_used">
              <span class="label">使用者</span>
              <span class="value">{{ code.used_username || code.used_by }}</span>
            </div>
            <div class="info-row">
              <span class="label">过期时间</span>
              <span class="value">{{ code.expires_at }}</span>
            </div>
          </div>

          <div class="card-footer">
            <el-button type="danger" plain size="small" style="width: 100%" @click="deleteCode(code.code)">
              <el-icon><Delete /></el-icon> 删除激活码
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 (通用) -->
    <div v-if="totalPages > 1" class="pagination">
      <span class="page-info">
        共 <strong>{{ totalCodes }}</strong> 条，第 <strong>{{ currentPage }}</strong> / <strong>{{ totalPages }}</strong> 页
      </span>
      <div class="page-btns">
        <el-button :disabled="currentPage === 1" @click="loadCodes(currentPage - 1)" size="small">上一页</el-button>
        <el-button :disabled="currentPage === totalPages" @click="loadCodes(currentPage + 1)" size="small">下一页</el-button>
      </div>
    </div>

    <!-- 生成激活码对话框 -->
    <el-dialog 
      v-model="showGenerateModal" 
      title="生成激活码" 
      width="90%"
      style="max-width: 400px;"
      custom-class="responsive-dialog"
      append-to-body
    >
      <el-form :model="generateForm" label-width="80px">
        <el-form-item label="设置等级">
          <el-select v-model="generateForm.level" style="width: 100%">
            <el-option v-for="level in 10" :key="level" :label="'Level ' + level" :value="level" />
          </el-select>
        </el-form-item>
        <el-form-item label="生成数量">
          <el-input-number v-model="generateForm.count" :min="1" :max="100" style="width: 100%" />
        </el-form-item>
        <el-form-item label="有效期">
          <el-input-number v-model="generateForm.expires_days" :min="1" :max="365" style="width: 100%">
            <template #suffix>天</template>
          </el-input-number>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showGenerateModal = false">取消</el-button>
          <el-button type="primary" @click="generateCodes" :loading="generating">立即生成</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '@/api/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Plus, Delete, Ticket } from '@element-plus/icons-vue'

const loading = ref(false)
const generating = ref(false)
const showGenerateModal = ref(false)
const codes = ref([])
const currentPage = ref(1)
const totalPages = ref(1)
const totalCodes = ref(0)

const filters = reactive({ level: '', is_used: '', limit: 20 })
const generateForm = reactive({ level: 1, count: 1, expires_days: 30 })

async function loadCodes(page = 1) {
  loading.value = true
  currentPage.value = page
  try {
    let url = `/api/activation/list?page=${page}&limit=${filters.limit}`
    if (filters.level) url += `&level=${filters.level}`
    if (filters.is_used !== '') url += `&is_used=${filters.is_used}`
    
    const res = await request.get(url)
    codes.value = res.data?.codes || []
    totalCodes.value = res.data?.total || 0
    totalPages.value = Math.ceil(totalCodes.value / filters.limit)
  } catch (e) {} finally { loading.value = false }
}

async function generateCodes() {
  generating.value = true
  try {
    const res = await request.post('/api/activation/generate', generateForm)
    ElMessage.success(res.message || '生成成功')
    showGenerateModal.value = false
    Object.assign(generateForm, { level: 1, count: 1, expires_days: 30 })
    loadCodes(1)
  } catch (e) {} finally { generating.value = false }
}

async function deleteCode(code) {
  try {
    await ElMessageBox.confirm(`确定要删除激活码 ${code} 吗？`, '提示', { type: 'warning' })
    const res = await request.delete(`/api/activation/${code}`)
    ElMessage.success(res.message || '删除成功')
    loadCodes(currentPage.value)
  } catch (e) {}
}

onMounted(() => loadCodes())
</script>

<style scoped>
.panel-container { width: 100%; }

/* 筛选栏 */
.filter-bar {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: flex-end;
  gap: 20px;
  flex-wrap: wrap;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  margin-bottom: 20px;
}

.filter-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 16px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-item label {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
}

.filter-actions {
  display: flex;
  gap: 8px;
}

/* 桌面端表格 */
.desktop-view {
  display: block;
}

.mobile-view {
  display: none;
}

.table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}

:deep(.el-table__header th) {
  background: #f9fafb !important;
  color: #374151;
  font-weight: 600;
}

.code-cell {
  font-family: 'Courier New', monospace;
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 4px;
  color: #374151;
  font-weight: 600;
  font-size: 13px;
}

/* 移动端卡片 */
.code-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border: 1px solid #f3f4f6;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f3f4f6;
}

.code-text {
  font-family: 'Courier New', monospace;
  font-weight: 700;
  font-size: 15px;
  color: #1f2937;
}

.card-body {
  margin-bottom: 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
}

.info-row .label {
  color: #6b7280;
}

.info-row .value {
  color: #374151;
  font-weight: 500;
}

/* 分页 */
.pagination {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-top: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}

.page-info {
  font-size: 13px;
  color: #6b7280;
}

.page-btns {
  display: flex;
  gap: 8px;
}

/* 响应式 */
@media (max-width: 768px) {
  .desktop-view { display: none; }
  .mobile-view { display: block; }
  
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
    padding: 16px;
    gap: 16px;
  }
  
  .filter-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .filter-actions {
    justify-content: space-between;
  }
  
  .filter-actions .el-button {
    flex: 1;
  }
  
  .pagination {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
  
  .page-btns {
    width: 100%;
  }
  
  .page-btns .el-button {
    flex: 1;
  }
}

@media (max-width: 480px) {
  .filter-grid {
    grid-template-columns: 1fr;
  }
}

/* 对话框底部 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
