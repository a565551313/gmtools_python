<template>
  <div class="gm-game">
    <!-- 广播公告 - 最顶上，最常用 -->
    <div class="section">
      <div class="row">
        <input v-model="broadcast" placeholder="输入广播/公告内容" class="flex1" />
        <button class="go" @click="send('广播')" :disabled="loading">📢 广播</button>
        <button class="go orange" @click="send('公告')" :disabled="loading">📣 公告</button>
      </div>
    </div>

    <!-- 全局设置 -->
    <div class="section">
      <div class="section-title">⚙️ 全局设置</div>
      <div class="row">
        <input v-model="rateVal" placeholder="输入数值" class="num" />
        <button @click="setRate('经验倍率')">经验倍率</button>
        <button @click="setRate('游戏难度')">游戏难度</button>
        <button @click="setRate('等级上限')">等级上限</button>
      </div>
    </div>

    <!-- 活动控制 -->
    <div class="section">
      <div class="section-title">🎮 活动控制</div>
      
      <!-- 快速切换分类 -->
      <div class="cat-row">
        <button v-for="(cat, key) in cats" :key="key" :class="{ on: curCat === key }" @click="curCat = key">
          {{ cat.icon }} {{ cat.name }}
        </button>
      </div>

      <!-- 活动按钮 -->
      <div class="act-grid">
        <button v-for="act in cats[curCat].items" :key="act" class="act-btn" @click="trigger(act)">
          {{ act }}
        </button>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="section">
      <div class="section-title">🚀 快捷操作</div>
      <div class="quick-grid">
        <button class="quick blue" @click="trigger('保存数据')">💾 保存数据</button>
        <button class="quick green" @click="trigger('假人走动')">🚶 假人走动</button>
        <button class="quick green" @click="trigger('假人摆摊')">🏪 假人摆摊</button>
        <button class="quick green" @click="trigger('假人聊天')">💬 假人聊天</button>
        <button class="quick red" @click="trigger('关闭游戏')">🔴 关闭游戏</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, inject } from 'vue'
import request from '@/api/request'
import { ElMessage } from 'element-plus'

const log = inject('logToConsole')

const broadcast = ref('')
const rateVal = ref('')
const curCat = ref('regular')
const loading = ref(false)

const cats = reactive({
  regular: {
    name: '常规',
    icon: '🎪',
    items: ['四墓灵鼠', '天降灵猴', '皇宫飞贼', '门派入侵', '长安保卫', '新春活动', '嘉年华', '天降辰星', '彩虹争霸', '糖果派对', '知了先锋', '小小盲僧']
  },
  boss: {
    name: 'BOSS',
    icon: '👹',
    items: ['刷出妖魔', '二八星宿', '天庭叛逆', '刷出星宿', '刷出星官', '刷出天罡', '刷出地煞', '圣兽残魂', '刷出知了', '世界挑战', '混世魔王', '刷出桐人', '魔化桐人', '创世佛屠', '善恶如来']
  },
  system: {
    name: '开关',
    icon: '🔘',
    items: ['开启异界', '开启经宝', '开启万象', '开启生肖', '门派开关', '宝藏开关', '镖王开关', '游泳开关', '开启病毒']
  },
  pvp: {
    name: 'PVP',
    icon: '⚔️',
    items: ['开启帮战', '结束帮战', '开启比武', '比武入场', '结束比武', '开启剑会', '结束剑会']
  }
})

// 发送广播/公告
async function send(type) {
  if (!broadcast.value) return ElMessage.error('内容不能为空')
  if (loading.value) return // 防止重复点击
  loading.value = true
  try {
    const res = await request.post('/api/game', {
      function: type === '广播' ? 'send_broadcast' : 'send_announcement',
      args: { content: broadcast.value }
    })
    log('POST', '/api/game', 200, res)
    ElMessage.success(`${type}已发送！`)
    broadcast.value = ''
  } catch (e) { 
    log('POST', '/api/game', 0, { error: e.message }); 
    ElMessage.error('发送失败') 
  } finally {
    loading.value = false
  }
}

// 设置倍率
async function setRate(type) {
  if (!rateVal.value) return ElMessage.error('请输入数值')
  if (loading.value) return // 防止重复点击
  loading.value = true
  const funcMap = { '经验倍率': 'set_exp_rate', '游戏难度': 'set_difficulty', '等级上限': 'set_level_cap' }
  try {
    const res = await request.post('/api/game', { function: funcMap[type], args: { rate: String(rateVal.value) } })
    log('POST', '/api/game', 200, res)
    ElMessage.success(`${type}已设置为 ${rateVal.value}`)
  } catch (e) { 
    log('POST', '/api/game', 0, { error: e.message }); 
    ElMessage.error('设置失败') 
  } finally {
    loading.value = false
  }
}

// 触发活动
async function trigger(name) {
  if (loading.value) return // 防止重复点击
  loading.value = true
  try {
    const res = await request.post('/api/game', { function: 'trigger_activity', args: { activity_name: name } })
    log('POST', '/api/game', 200, res)
    ElMessage.success(`已触发：${name}`)
  } catch (e) { 
    log('POST', '/api/game', 0, { error: e.message }); 
    ElMessage.error('触发失败') 
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.gm-game {
  font-family: system-ui, -apple-system, sans-serif;
  padding: 20px;
  background: #f7f9fc;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.section-title {
  font-size: 15px;
  font-weight: bold;
  color: #333;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

input, select {
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
}

input:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.15);
}

.flex1 { flex: 1; min-width: 200px; }
.num { width: 120px; }

button {
  padding: 12px 20px;
  border: none;
  background: #e2e8f0;
  color: #444;
  font-weight: 600;
  font-size: 13px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
}

button:hover {
  background: #cbd5e1;
}

button:active {
  transform: scale(0.97);
}

.go {
  background: #10b981;
  color: white;
}

.go:hover {
  background: #059669;
}

.go.orange {
  background: #f59e0b;
}

.go.orange:hover {
  background: #d97706;
}

/* 分类标签 */
.cat-row {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.cat-row button {
  padding: 10px 16px;
  background: #f1f5f9;
}

.cat-row button.on {
  background: #6366f1;
  color: white;
}

/* 活动网格 */
.act-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
}

.act-btn {
  padding: 12px 8px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  font-size: 13px;
}

.act-btn:hover {
  background: #6366f1;
  border-color: #6366f1;
  color: white;
}

/* 快捷操作 */
.quick-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 12px;
}

.quick {
  padding: 14px 16px;
  font-size: 14px;
}

.quick.blue {
  background: #3b82f6;
  color: white;
}

.quick.blue:hover {
  background: #2563eb;
}

.quick.green {
  background: #22c55e;
  color: white;
}

.quick.green:hover {
  background: #16a34a;
}

.quick.red {
  background: #ef4444;
  color: white;
}

.quick.red:hover {
  background: #dc2626;
}

/* 响应式 */
@media (max-width: 640px) {
  .gm-game {
    padding: 12px;
  }

  .section {
    padding: 16px;
  }

  .row {
    flex-direction: column;
    align-items: stretch;
  }

  .row input,
  .row button {
    width: 100%;
  }

  .num {
    width: 100%;
  }

  .cat-row {
    overflow-x: auto;
    flex-wrap: nowrap;
    padding-bottom: 8px;
  }

  .cat-row button {
    flex-shrink: 0;
  }

  .act-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .quick-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 400px) {
  .act-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .quick-grid {
    grid-template-columns: 1fr;
  }
}
</style>