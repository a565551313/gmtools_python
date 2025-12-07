<template>
  <div class="gm-equip">
    <!-- 一行三个大按钮切换 -->
    <div class="quick-tabs">
      <button @click="tab = 'equip'" :class="{ on: tab === 'equip' }">装备定制</button>
      <button @click="tab = 'ls'" :class="{ on: tab === 'ls' }">灵饰定制</button>
      <button @click="tab = 'blue'" :class="{ on: tab === 'blue' }">蓝字修改</button>
    </div>

    <!-- ==================== 装备定制 ==================== -->
    <div v-show="tab === 'equip'" class="section">
      <div class="row">
        <select v-model="equip.type">
          <option v-for="t in ['武器','衣服','头盔','项链','腰带','鞋子']" :value="t">{{ t }}</option>
        </select>
        <input v-model="equip.level" placeholder="等级（必填）" class="big" />
        <button class="go" @click="sendEquip">秒发装备</button>
      </div>

      <div class="grid">
        <input v-model="equip.attr.气血" placeholder="气血" />
        <input v-model="equip.attr.魔法" placeholder="魔法" />
        <input v-model="equip.attr.伤害" placeholder="伤害" />
        <input v-model="equip.attr.命中" placeholder="命中" />
        <input v-model="equip.attr.防御" placeholder="防御" />
        <input v-model="equip.attr.速度" placeholder="速度" />
        <input v-model="equip.attr.灵力" placeholder="灵力" />
        <input v-model="equip.attr.体质" placeholder="体质" />
        <input v-model="equip.attr.魔力" placeholder="魔力" />
        <input v-model="equip.attr.力量" placeholder="力量" />
        <input v-model="equip.attr.耐力" placeholder="耐力" />
        <input v-model="equip.attr.敏捷" placeholder="敏捷" />
      </div>

      <div class="row mt">
        <input v-model="equip.tx1" placeholder="特效（如：永不磨损）" class="long" />
        <input v-model="equip.tx2" placeholder="特效2（可选）" class="long" />
      </div>
      <div class="row">
        <input v-model="equip.tj" placeholder="特技（如：晶清诀）" class="long" />
        <input v-model="equip.zz" placeholder="制造/专用（如：简易、专用张三）" class="long" />
      </div>
    </div>

    <!-- ==================== 灵饰定制 ==================== -->
    <div v-show="tab === 'ls'" class="section">
      <div class="row">
        <select v-model="ls.part">
          <option v-for="p in ['戒指','手镯','佩饰','耳饰']" :value="p">{{ p }}</option>
        </select>
        <input v-model="ls.level" placeholder="等级" class="big" />
        <button class="go" @click="sendLs">秒发灵饰</button>
      </div>

      <div class="row mt">
        <input v-model="ls.mainName" :placeholder="lsMainHint" class="long" />
        <input v-model="ls.mainVal" placeholder="主属性数值（必填）" />
      </div>

      <div class="ls-grid">
        <template v-for="n in 4" :key="n">
          <input v-model="ls.c[n].name" :placeholder="`词条${n}`" />
          <input v-model="ls.c[n].val" placeholder="数值" class="s" />
        </template>
      </div>

      <div class="ls-grid mt">
        <template v-for="n in 2" :key="n">
          <input v-model="ls.e[n].name" :placeholder="`特效${n}`" />
          <input v-model="ls.e[n].val" placeholder="数值" class="s" />
        </template>
      </div>
    </div>

    <!-- ==================== 蓝字修改 ==================== -->
    <div v-show="tab === 'blue'" class="section">
      <div class="row">
        <select v-model="blue.part">
          <option v-for="p in ['武器','铠甲','项链','头盔','腰带','鞋子']" :value="p">{{ p }}</option>
        </select>
        <button class="go red" @click="sendBlue">强制改蓝字</button>
      </div>

      <div class="row mt">
        <input v-model="blue.mainName" placeholder="主属性（如：伤害）" class="long" />
        <input v-model="blue.mainVal" placeholder="数值" />
      </div>

      <div class="ls-grid">
        <template v-for="n in 3" :key="n">
          <input v-model="blue.c[n].name" :placeholder="`附加${n}`" />
          <input v-model="blue.c[n].val" placeholder="数值" class="s" />
        </template>
      </div>

      <div class="ls-grid mt">
        <template v-for="n in 3" :key="n">
          <input v-model="blue.e[n].name" :placeholder="`特效${n}`" />
          <input v-model="blue.e[n].val" placeholder="数值" class="s" />
        </template>
      </div>

      <div class="warning">
        注意：第2、3条附加属性数值会自动除2，三同词条请填3条相同属性
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, inject } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const playerId = inject('playerId')
const log = inject('logToConsole')

const tab = ref('equip')

// ==================== 装备定制 ====================
const equip = reactive({
  type: '武器',
  level: '160',
  attr: { 气血: '', 魔法: '', 伤害: '', 命中: '', 防御: '', 速度: '', 灵力: '', 体质: '', 魔力: '', 力量: '', 耐力: '', 敏捷: '' },
  tx1: '', tx2: '', tj: '', zz: ''
})

const sendEquip = async () => {
  if (!playerId.value) return ElMessage.error('请先输入角色ID')
  if (!equip.level) return ElMessage.error('等级必填')

  const data = { type: equip.type, 等级: equip.level }
  Object.entries(equip.attr).forEach(([k, v]) => v && (data[k] = Number(v) || v))
  equip.tx1 && (data.特效 = equip.tx1)
  equip.tx2 && (data.特效2 = equip.tx2)
  equip.tj && (data.特技 = equip.tj)
  equip.zz && (data.制造 = equip.zz)

  try {
    await request.post('/api/equipment', { function: 'send_equipment', args: { char_id: playerId.value, equip_data: data }})
    ElMessage.success('装备已秒发！')
  } catch { ElMessage.error('发送失败') }
}

// ==================== 灵饰定制 ====================
const ls = reactive({
  part: '戒指',
  level: '160',
  mainName: '',
  mainVal: '',
  c: Array(5).fill().map(() => ({ name: '', val: '' })),
  e: Array(3).fill().map(() => ({ name: '', val: '' }))
})

const lsMainHint = computed(() => {
  const map = { 戒指: '伤害/防御', 手镯: '封印命中/抵抗封印', 佩饰: '速度', 耳饰: '法术伤害/法术防御' }
  return map[ls.part] || ''
})

const sendLs = async () => {
  if (!playerId.value) return ElMessage.error('请先输入角色ID')
  if (!ls.mainVal) return ElMessage.error('主属性数值必填')

  const data = {
    部位: ls.part,
    等级: Number(ls.level),
    主属性: { 属性: ls.mainName || lsMainHint.value.split('/')[0], 数值: Number(ls.mainVal) },
    词条: {},
    特效: {}
  }

  ls.c.slice(1,5).forEach((c,i) => c.name && c.val && (data.词条[i+1] = { 词条: c.name, 数值: Number(c.val) }))
  ls.e.slice(1,3).forEach((e,i) => e.name && e.val && (data.特效[i+1] = { 特效: e.name, 数值: Number(e.val) }))

  try {
    await request.post('/api/equipment', { function: 'send_ornament', args: { char_id: playerId.value, ornament_data: data }})
    ElMessage.success('灵饰已秒发！')
  } catch { ElMessage.error('发送失败') }
}

// ==================== 蓝字修改 ====================
const blue = reactive({
  part: '武器',
  mainName: '',
  mainVal: '',
  c: Array(4).fill().map(() => ({ name: '', val: '' })),
  e: Array(4).fill().map(() => ({ name: '', val: '' }))
})

const sendBlue = async () => {
  if (!playerId.value) return ElMessage.error('请先输入角色ID')

  const data = { 部位: blue.part }
  if (blue.mainName && blue.mainVal) data.主属性 = { 属性: blue.mainName, 数值: Number(blue.mainVal) }
  data.词条 = {}
  data.特效 = {}

  blue.c.slice(1,4).forEach((c,i) => c.name && c.val && (data.词条[i+1] = { 词条: c.name, 数值: Number(c.val) }))
  blue.e.slice(1,4).forEach((e,i) => e.name && e.val && (data.特效[i+1] = { 特效: e.name, 数值: Number(e.val) }))

  try {
    await request.post('/api/equipment', { function: 'send_affix', args: { char_id: playerId.value, affix_data: data }})
    ElMessage.success('蓝字已强制修改！')
  } catch { ElMessage.error('修改失败') }
}
</script>

<style scoped>
.gm-equip { font-family: system-ui,-apple-system,sans-serif; padding: 20px; background: #f7f9fc; min-height: 100vh; }
.quick-tabs { display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
.quick-tabs button { padding: 12px 24px; border: none; background: #e2e8f0; color: #444; font-weight: bold; border-radius: 8px; cursor: pointer; }
.quick-tabs button.on { background: #6366f1; color: white; }

.section { background: white; padding: 24px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }

.row { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; margin-bottom: 16px; }
.mt { margin-top: 16px; }

input, select {
  padding: 12px 16px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px;
  outline: none; transition: all 0.2s;
}
input:focus, select:focus { border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.15); }

.big { width: 120px; font-weight: bold; }
.long { flex: 1; min-width: 200px; }
.s { width: 90px; }

.grid, .ls-grid {
  display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 16px;
}
.ls-grid { grid-template-columns: repeat(4, 1fr); }

.go {
  background: #10b981; color: white; border: none; padding: 12px 32px; border-radius: 8px; font-weight: bold; cursor: pointer;
}
.go.red { background: #ef4444; }

.warning {
  margin-top: 20px; padding: 12px 16px; background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; font-size: 13px; color: #92400e;
}

/* 超小屏也丝滑 */
@media (max-width: 640px) {
  .grid, .ls-grid { grid-template-columns: 1fr 1fr; }
  .row { flex-direction: column; align-items: stretch; }
  .go { width: 100%; }
}
</style>