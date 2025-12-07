<template>
  <div class="activity-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>活动管理系统</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          创建活动
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon">🎯</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.totalActivities }}</div>
          <div class="stat-label">总活动数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.activeActivities }}</div>
          <div class="stat-label">进行中</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.totalParticipants }}</div>
          <div class="stat-label">参与人次</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🎁</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.totalRewards }}</div>
          <div class="stat-label">已发奖品</div>
        </div>
      </div>
    </div>

    <!-- 活动列表 -->
    <div class="activity-list">
      <el-table :data="activities" stripe style="width: 100%">
        <el-table-column prop="name" label="活动名称" min-width="150" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="scope">
            <el-tag :type="getTypeTagType(scope.row.type)">
              {{ getTypeLabel(scope.row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'info'">
              {{ scope.row.is_active ? '进行中' : '已暂停' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时间范围" min-width="200">
          <template #default="scope">
            <div class="time-range">
              <div v-if="scope.row.start_time">
                开始：{{ formatTime(scope.row.start_time) }}
              </div>
              <div v-if="scope.row.end_time">
                结束：{{ formatTime(scope.row.end_time) }}
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="参与限制" width="100">
          <template #default="scope">
            {{ scope.row.max_participations || '无限制' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-button size="small" @click="viewActivity(scope.row.id)">
                查看详情
              </el-button>
              <el-button size="small" type="primary" @click="editActivity(scope.row.id)">
                编辑
              </el-button>
              <el-button 
                size="small" 
                :type="scope.row.is_active ? 'warning' : 'success'"
                @click="toggleActivityStatus(scope.row.id)"
              >
                {{ scope.row.is_active ? '暂停' : '启用' }}
              </el-button>
              <el-button size="small" type="danger" @click="deleteActivity(scope.row.id)">
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 创建/编辑活动对话框 -->
    <el-dialog 
      v-model="showCreateDialog" 
      :title="editingActivity ? '编辑活动' : '创建活动'"
      width="800px"
      :before-close="resetForm"
    >
      <el-form :model="activityForm" :rules="activityRules" ref="activityFormRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="活动名称" prop="name">
              <el-input v-model="activityForm.name" placeholder="请输入活动名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="活动类型" prop="type">
              <el-select v-model="activityForm.type" placeholder="选择活动类型" style="width: 100%">
                <el-option label="大转盘" value="roulette" />
                <el-option label="抽奖券" value="lottery" />
                <el-option label="刮刮卡" value="scratch" />
                <el-option label="积分抽奖" value="points" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="活动描述">
          <el-input 
            v-model="activityForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入活动描述"
          />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始时间" prop="start_time">
              <el-date-picker 
                v-model="activityForm.start_time"
                type="datetime"
                placeholder="选择开始时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间" prop="end_time">
              <el-date-picker 
                v-model="activityForm.end_time"
                type="datetime"
                placeholder="选择结束时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="最大参与次数">
              <el-input-number 
                v-model="activityForm.max_participations" 
                :min="0" 
                :max="1000"
                placeholder="0表示无限制"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="需要游戏ID">
              <el-switch v-model="activityForm.game_id_required" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 活动配置 -->
        <el-divider content-position="left">活动配置</el-divider>
        <div v-if="activityForm.type === 'roulette' && activityForm.config" class="config-section">
          <h4>大转盘配置</h4>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="转盘尺寸">
                <el-input-number 
                  v-model="activityForm.config.size" 
                  :min="300" 
                  :max="800"
                  placeholder="转盘直径(px)"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="旋转时间">
                <el-input-number 
                  v-model="activityForm.config.rotate_duration" 
                  :min="1" 
                  :max="10"
                  placeholder="旋转时长(秒)"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="背景音乐">
                <el-switch v-model="activityForm.config.enable_sound" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="resetForm">取消</el-button>
          <el-button type="primary" @click="saveActivity">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 活动详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="活动详情" width="1000px">
      <div v-if="currentActivity" class="activity-detail">
        <el-tabs v-model="activeDetailTab">
          <el-tab-pane label="基本信息" name="basic">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="活动名称">{{ currentActivity.activity.name }}</el-descriptions-item>
              <el-descriptions-item label="活动类型">{{ getTypeLabel(currentActivity.activity.type) }}</el-descriptions-item>
              <el-descriptions-item label="活动状态">
                <el-tag :type="currentActivity.activity.is_active ? 'success' : 'info'">
                  {{ currentActivity.activity.is_active ? '进行中' : '已暂停' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="参与限制">{{ currentActivity.activity.max_participations || '无限制' }}</el-descriptions-item>
              <el-descriptions-item label="开始时间">{{ formatTime(currentActivity.activity.start_time) }}</el-descriptions-item>
              <el-descriptions-item label="结束时间">{{ formatTime(currentActivity.activity.end_time) }}</el-descriptions-item>
              <el-descriptions-item label="活动描述" :span="2">{{ currentActivity.activity.description }}</el-descriptions-item>
            </el-descriptions>
            
            <div v-if="currentActivity.activity.config_parsed" class="config-display">
              <h4>活动配置</h4>
              <el-descriptions :column="3" border>
                <el-descriptions-item v-for="(value, key) in currentActivity.activity.config_parsed" :key="key" :label="key">
                  {{ value }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="奖项设置" name="rewards">
            <div class="rewards-section">
              <div class="section-header">
                <h4>奖项列表</h4>
                <el-button size="small" type="primary" @click="showAddRewardDialog = true">
                  <el-icon><Plus /></el-icon>
                  添加奖项
                </el-button>
              </div>
              
              <el-table :data="currentActivity.rewards" stripe>
                <el-table-column label="顺序" width="80">
                  <template #default="scope">
                    {{ scope.$index + 1 }}
                  </template>
                </el-table-column>
                <el-table-column prop="name" label="奖项名称" />
                <el-table-column label="类型" width="100">
                  <template #default="scope">
                    <el-tag>{{ scope.row.type }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="probability" label="中奖率" width="100">
                  <template #default="scope">
                    {{ scope.row.probability }}%
                  </template>
                </el-table-column>
                <el-table-column prop="total_quantity" label="总数量" width="100" />
                <el-table-column prop="remaining_quantity" label="剩余数量" width="100" />
                <el-table-column label="操作" width="150">
                  <template #default="scope">
                    <el-button size="small" @click="editReward(scope.row)">编辑</el-button>
                    <el-button size="small" type="danger" @click="deleteReward(scope.row.id)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="参与统计" name="statistics">
            <div class="statistics-section">
              <el-row :gutter="20">
                <el-col :span="6">
                  <el-card class="stat-card">
                    <div class="stat-value">{{ currentActivity.statistics?.total_participations || 0 }}</div>
                    <div class="stat-label">总参与次数</div>
                  </el-card>
                </el-col>
                <el-col :span="6">
                  <el-card class="stat-card">
                    <div class="stat-value">{{ currentActivity.statistics?.unique_users || 0 }}</div>
                    <div class="stat-label">独立用户数</div>
                  </el-card>
                </el-col>
                <el-col :span="6">
                  <el-card class="stat-card">
                    <div class="stat-value">{{ currentActivity.statistics?.winning_count || 0 }}</div>
                    <div class="stat-label">中奖次数</div>
                  </el-card>
                </el-col>
                <el-col :span="6">
                  <el-card class="stat-card">
                    <div class="stat-value">{{ (currentActivity.statistics?.win_rate || 0).toFixed(2) }}%</div>
                    <div class="stat-label">中奖率</div>
                  </el-card>
                </el-col>
              </el-row>
              
              <!-- 奖项统计 -->
              <el-divider>奖项发放统计</el-divider>
              <el-table :data="currentActivity.statistics?.reward_stats || []" stripe>
                <el-table-column prop="name" label="奖项名称" />
                <el-table-column prop="total_quantity" label="总数量" width="100" />
                <el-table-column prop="remaining_quantity" label="剩余数量" width="100" />
                <el-table-column prop="won_count" label="已发放" width="100" />
                <el-table-column prop="win_rate" label="实际中奖率" width="120">
                  <template #default="scope">
                    {{ scope.row.win_rate.toFixed(2) }}%
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>


          <el-tab-pane label="中奖记录" name="records">
            <div class="records-section">
              <div class="section-header">
                <h4>中奖记录列表</h4>
                <el-button size="small" @click="loadParticipations">刷新</el-button>
              </div>
              
              <!-- 筛选栏 -->
              <div class="filter-bar" style="margin-bottom: 20px;">
                <el-row :gutter="20">
                  <el-col :span="6">
                    <el-input v-model="participationFilters.game_id" placeholder="玩家ID" clearable @clear="loadParticipations" />
                  </el-col>
                  <el-col :span="6">
                    <el-input v-model="participationFilters.reward_name" placeholder="奖品名称" clearable @clear="loadParticipations" />
                  </el-col>
                  <el-col :span="4">
                    <el-select v-model="participationFilters.status" placeholder="状态" clearable @clear="loadParticipations">
                      <el-option label="成功" :value="1" />
                      <el-option label="待补发" :value="2" />
                    </el-select>
                  </el-col>
                  <el-col :span="4">
                    <el-button type="primary" @click="loadParticipations">查询</el-button>
                  </el-col>
                </el-row>
              </div>
              
              <el-table :data="participations" stripe v-loading="loadingParticipations">
                <el-table-column prop="id" label="ID" width="80" />
                <el-table-column prop="game_id" label="玩家ID" width="150" />
                <el-table-column label="活动类型" width="120">
                  <template #default="scope">
                    <el-tag :type="getTypeTagType(scope.row.activity_type)">
                      {{ getTypeLabel(scope.row.activity_type) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="reward_name" label="奖品名称" />
                <el-table-column label="中奖时间" width="180">
                  <template #default="scope">
                    {{ formatTime(scope.row.created_at) }}
                  </template>
                </el-table-column>
                <el-table-column label="状态" width="100">
                  <template #default="scope">
                    <el-tag :type="scope.row.status === 1 ? 'success' : 'warning'">
                      {{ scope.row.status === 1 ? '成功' : '待补发' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="100">
                  <template #default="scope">
                    <el-button 
                      size="small" 
                      type="warning" 
                      @click="handleResend(scope.row)"
                      :loading="scope.row.resending"
                    >
                      补发
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              
              <!-- 分页 -->
              <div class="pagination-container" style="margin-top: 20px; text-align: right;">
                <el-pagination
                  v-model:current-page="participationPagination.page"
                  v-model:page-size="participationPagination.pageSize"
                  :total="participationPagination.total"
                  layout="total, prev, pager, next"
                  @current-change="loadParticipations"
                />
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDetailDialog = false">关闭</el-button>
          <el-button type="primary" @click="copyActivityUrl(currentActivity.activity.id)">
            复制活动链接
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 添加奖项对话框 -->
    <el-dialog v-model="showAddRewardDialog" title="添加奖项" width="600px">
      <el-form :model="rewardForm" :rules="rewardRules" ref="rewardFormRef" label-width="100px">
        <el-form-item label="奖项名称" prop="name">
          <el-input v-model="rewardForm.name" placeholder="请输入奖项名称" />
        </el-form-item>
        
        <el-form-item label="奖项描述">
          <el-input v-model="rewardForm.description" type="textarea" :rows="2" placeholder="请输入奖项描述" />
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="奖项类型" prop="type">
              <el-select v-model="rewardForm.type" placeholder="选择类型" style="width: 100%">
                <el-option label="道具" value="item" />
                <el-option label="货币" value="currency" />
                <el-option label="装备" value="equipment" />
                <el-option label="经验" value="exp" />
                <el-option label="特殊奖励" value="special" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="中奖率%" prop="probability">
              <el-input-number 
                v-model="rewardForm.probability" 
                :min="0" 
                :max="100" 
                :precision="2"
                placeholder="0-100"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="总数量" prop="total_quantity">
              <el-input-number 
                v-model="rewardForm.total_quantity" 
                :min="1" 
                placeholder="奖品总数量"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="显示顺序">
              <el-input-number 
                v-model="rewardForm.order_index" 
                :min="0" 
                placeholder="显示顺序"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="奖励值">
          <el-input 
            v-model="rewardForm.value_json" 
            type="textarea" 
            :rows="3"
            placeholder='道具: {"item_name": "屠龙刀", "quantity": 1}
宝石: {"gem_name": "红宝石", "min_level": 1, "max_level": 1}'
          />
        </el-form-item>
        
        <el-form-item label="奖项图标">
          <el-input v-model="rewardForm.icon" placeholder="图标URL或emoji" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="resetRewardForm">取消</el-button>
          <el-button type="primary" @click="saveReward">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/api/request'

// 响应式数据
const activities = ref([])
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const showAddRewardDialog = ref(false)
const activeDetailTab = ref('basic')
const editingActivity = ref(null)
const currentActivity = ref(null)
const activityFormRef = ref(null)
const rewardFormRef = ref(null)

// 统计数据
const stats = reactive({
  totalActivities: 0,
  activeActivities: 0,
  totalParticipants: 0,
  totalRewards: 0
})

// 活动表单
const activityForm = reactive({
  name: '',
  type: 'roulette',
  description: '',
  start_time: '',
  end_time: '',
  max_participations: 0,
  game_id_required: true,
  config: {
    size: 400,
    rotate_duration: 3,
    enable_sound: true
  }
})

// 奖项表单
const rewardForm = reactive({
  name: '',
  description: '',
  type: 'item',
  probability: 0,
  total_quantity: 1,
  value_json: '',
  icon: '',
  order_index: 0
})

// 表单验证规则
const activityRules = {
  name: [{ required: true, message: '请输入活动名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择活动类型', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }]
}

const rewardRules = {
  name: [{ required: true, message: '请输入奖项名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择奖项类型', trigger: 'change' }],
  probability: [{ required: true, message: '请输入中奖率', trigger: 'blur' }],
  total_quantity: [{ required: true, message: '请输入总数量', trigger: 'blur' }]
}

// 中奖记录相关
const participations = ref([])
const loadingParticipations = ref(false)
const participationFilters = reactive({
  game_id: '',
  reward_name: '',
  status: '',
  activity_type: ''
})
const participationPagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 监听标签页切换
watch(activeDetailTab, (newVal) => {
  if (newVal === 'records' && currentActivity.value) {
    loadParticipations()
  }
})

// 加载中奖记录
async function loadParticipations() {
  if (!currentActivity.value) return
  
  loadingParticipations.value = true
  try {
    const params = {
      limit: participationPagination.pageSize,
      offset: (participationPagination.page - 1) * participationPagination.pageSize,
      ...participationFilters
    }
    // 移除空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null) {
        delete params[key]
      }
    })
    
    // 构建查询字符串
    const queryString = new URLSearchParams(params).toString()
    
    const result = await request.get(`/api/activity/${currentActivity.value.activity.id}/participations?${queryString}`)
    if (result.status === 'success' || result.success) {
      participations.value = result.data || []
      participationPagination.total = result.total || 0
    } else {
      ElMessage.error(result.message || '加载记录失败')
    }
  } catch (error) {
    console.error('加载记录失败:', error)
    ElMessage.error('网络请求失败')
  } finally {
    loadingParticipations.value = false
  }
}

// 补发奖励
async function handleResend(record) {
  try {
    // 乐观更新 UI
    record.resending = true
    
    const result = await request.post(`/api/activity/${currentActivity.value.activity.id}/participations/${record.id}/resend`)
    
    if (result.status === 'success' || result.success) {
      ElMessage.success('补发成功')
      record.status = 1 // 更新状态为成功
    } else {
      ElMessage.error(result.message || '补发失败')
    }
  } catch (error) {
    console.error('补发失败:', error)
    ElMessage.error('网络请求失败')
  } finally {
    record.resending = false
  }
}

// 初始化
onMounted(async () => {
  await loadActivities()
  loadStats()
})

// 加载活动列表
async function loadActivities() {
  try {
    const result = await request.get('/api/activity/list')
    
    if (result.status === 'success' || result.success) {
      activities.value = result.data || []
    } else {
      ElMessage.error('加载活动列表失败')
    }
  } catch (error) {
    console.error('加载活动失败:', error)
    // 如果API不存在，显示模拟数据提示
    activities.value = []
  }
}

// 加载统计数据
async function loadStats() {
  // 简化统计，实际应该从API获取
  stats.totalActivities = activities.value.length
  stats.activeActivities = activities.value.filter(a => a.is_active).length
  stats.totalParticipants = activities.value.reduce((sum, a) => sum + (a.statistics?.total_participations || 0), 0)
  stats.totalRewards = activities.value.reduce((sum, a) => sum + (a.statistics?.winning_count || 0), 0)
}

// 获取类型标签样式
function getTypeTagType(type) {
  const typeMap = {
    'roulette': 'success',
    'lottery': 'primary',
    'scratch': 'warning',
    'points': 'info'
  }
  return typeMap[type] || 'default'
}

// 获取类型标签文本
function getTypeLabel(type) {
  const typeMap = {
    'roulette': '大转盘',
    'lottery': '抽奖券',
    'scratch': '刮刮卡',
    'points': '积分抽奖'
  }
  return typeMap[type] || type
}

// 格式化时间
function formatTime(timeStr) {
  if (!timeStr) return '-'
  return new Date(timeStr).toLocaleString('zh-CN')
}

// 保存活动
async function saveActivity() {
  if (!activityFormRef.value) return
  
  await activityFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      const formData = {
        ...activityForm,
        config: activityForm.config, // 后端期望字典，不要手动stringify
        start_time: activityForm.start_time || null, // 空字符串转为null
        end_time: activityForm.end_time || null
      }
    
    let result
    if (editingActivity.value) {
      result = await request.put(`/api/activity/${editingActivity.value}`, formData)
    } else {
      result = await request.post('/api/activity/create', formData)
    }
    
    if (result.status === 'success' || result.success) {
      ElMessage.success(editingActivity.value ? '活动更新成功' : '活动创建成功')
      showCreateDialog.value = false
      resetForm()
      await loadActivities()
      loadStats()
    } else {
      ElMessage.error(result.message || '操作失败')
    }
    } catch (error) {
      console.error('保存活动失败:', error)
      ElMessage.error('网络请求失败')
    }
  })
}

// 重置表单
function resetForm() {
  Object.assign(activityForm, {
    name: '',
    type: 'roulette',
    description: '',
    start_time: '',
    end_time: '',
    max_participations: 0,
    game_id_required: true,
    config: {
      size: 400,
      rotate_duration: 3,
      enable_sound: true
    }
  })
  editingActivity.value = null
  showCreateDialog.value = false
}

// 查看活动详情
async function viewActivity(activityId) {
  try {
    const result = await request.get(`/api/activity/${activityId}`)
    
    if (result.status === 'success' || result.success) {
      currentActivity.value = result.data
      showDetailDialog.value = true
    } else {
      ElMessage.error('加载活动详情失败')
    }
  } catch (error) {
    console.error('查看活动失败:', error)
    ElMessage.error('网络请求失败')
  }
}

// 编辑活动
async function editActivity(activityId) {
  try {
    const result = await request.get(`/api/activity/${activityId}`)
    
    if (result.status === 'success' || result.success) {
      const activity = result.data?.activity || result.data
      Object.assign(activityForm, {
        name: activity.name,
        type: activity.type,
        description: activity.description,
        start_time: activity.start_time,
        end_time: activity.end_time,
        max_participations: activity.max_participations,
        game_id_required: activity.game_id_required,
        config: activity.config_parsed || {
          size: 400,
          rotate_duration: 3,
          enable_sound: true
        }
      })
      editingActivity.value = activityId
      showCreateDialog.value = true
    } else {
      ElMessage.error('加载活动信息失败')
    }
  } catch (error) {
    console.error('编辑活动失败:', error)
    ElMessage.error('网络请求失败')
  }
}

// 切换活动状态
async function toggleActivityStatus(activityId) {
  try {
    const result = await request.put(`/api/activity/${activityId}/toggle-status`)
    
    if (result.status === 'success' || result.success) {
      ElMessage.success('活动状态更新成功')
      await loadActivities()
      loadStats()
    } else {
      ElMessage.error(result.message || '状态更新失败')
    }
  } catch (error) {
    console.error('切换活动状态失败:', error)
    ElMessage.error('网络请求失败')
  }
}

// 删除活动
async function deleteActivity(activityId) {
  try {
    await ElMessageBox.confirm('确定要删除这个活动吗？此操作不可恢复！', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const result = await request.delete(`/api/activity/${activityId}`)
    
    if (result.status === 'success' || result.success) {
      ElMessage.success('活动删除成功')
      await loadActivities()
      loadStats()
    } else {
      ElMessage.error(result.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除活动失败:', error)
      ElMessage.error('网络请求失败')
    }
  }
}

// 保存奖项
async function saveReward() {
  if (!rewardFormRef.value) return
  
  await rewardFormRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      if (!currentActivity.value) return
      
      const activityId = currentActivity.value.activity?.id || currentActivity.value.id
      const rewardData = {
        ...rewardForm,
        value: JSON.parse(rewardForm.value_json || '{}')
      }
    
    let result
    if (rewardForm.id) {
      // 更新奖项
      result = await request.put(`/api/activity/${activityId}/rewards/${rewardForm.id}`, rewardData)
    } else {
      // 创建奖项
      result = await request.post(`/api/activity/${activityId}/add-reward`, rewardData)
    }
    
    if (result.status === 'success' || result.success) {
      ElMessage.success(rewardForm.id ? '奖项更新成功' : '奖项添加成功')
      resetRewardForm()
      showAddRewardDialog.value = false
      viewActivity(activityId) // 刷新详情
    } else {
      ElMessage.error(result.message || '操作失败')
    }
    } catch (error) {
      console.error('保存奖项失败:', error)
      ElMessage.error('网络请求失败或参数错误')
    }
  })
}

// 重置奖项表单
function resetRewardForm() {
  Object.assign(rewardForm, {
    id: null, // 清除ID
    name: '',
    description: '',
    type: 'item',
    probability: 0,
    total_quantity: 1,
    value_json: '',
    icon: '',
    order_index: 0
  })
}

// 复制活动链接
function copyActivityUrl(activityId) {
  const url = `${window.location.origin}/activity/${activityId}`
  navigator.clipboard.writeText(url).then(() => {
    ElMessage.success('活动链接已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

// 编辑奖项
function editReward(reward) {
  Object.assign(rewardForm, {
    id: reward.id, // 保存ID用于更新
    name: reward.name,
    description: reward.description,
    type: reward.type,
    probability: reward.probability,
    total_quantity: reward.total_quantity,
    value_json: JSON.stringify(JSON.parse(reward.value || '{}'), null, 2),
    icon: reward.icon,
    order_index: reward.order_index
  })
  showAddRewardDialog.value = true
}

// 删除奖项
async function deleteReward(rewardId) {
  try {
    await ElMessageBox.confirm('确定要删除这个奖项吗？', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const activityId = currentActivity.value.activity?.id || currentActivity.value.id
    const result = await request.delete(`/api/activity/${activityId}/rewards/${rewardId}`)
    
    if (result.status === 'success' || result.success) {
      ElMessage.success('奖项删除成功')
      viewActivity(activityId) // 刷新详情
    } else {
      ElMessage.error(result.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除奖项失败:', error)
      ElMessage.error('网络请求失败')
    }
  }
}

</script>

<style scoped>
.activity-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  font-size: 2rem;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 1.8rem;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  color: #909399;
  margin-top: 5px;
}

.activity-list {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.time-range {
  font-size: 12px;
  color: #606266;
}

.activity-detail {
  padding: 10px 0;
}

.config-section {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
}

.config-section h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.rewards-section {
  padding: 10px 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h4 {
  margin: 0;
}

.statistics-section {
  padding: 10px 0;
}

.stat-card {
  text-align: center;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  color: #606266;
  font-size: 14px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 768px) {
  .activity-management {
    padding: 10px;
  }
  
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .time-range {
    font-size: 11px;
  }
  
  .el-button-group {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }
  
  .el-button-group .el-button {
    margin: 0;
  }
}

@media (max-width: 480px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .el-dialog {
    width: 95% !important;
  }
  
  .el-row {
    flex-direction: column;
  }
  
  .el-col {
    width: 100% !important;
    max-width: 100% !important;
  }
}
</style>