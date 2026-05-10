<template>
  <div class="journal-manage-page">
    <h2>📂 期刊管理</h2>

    <!-- OpenAlex 期刊搜索 -->
    <JournalSearch @journal-selected="onJournalSelected" />
    
    <!-- 添加期刊表单 -->
    <div class="add-form">
      <input v-model="form.name" placeholder="期刊名称（必填）" class="input" />
      <input v-model="form.category" placeholder="分类（如：HRM、战略管理）" class="input" />
      <input v-model="form.openalex_issn" placeholder="ISSN（如：0022-3514）" class="input" />
      <input v-model="form.publisher" placeholder="出版社" class="input" />
      <input v-model="form.url" placeholder="期刊主页 URL" class="input" />
      <button @click="addJournal" :disabled="!form.name" class="btn-add">添加期刊</button>
    </div>

    <!-- 分类筛选 -->
    <div class="cat-tabs">
      <span class="tab" :class="{ active: !filterCat }" @click="filterCat=''">全部</span>
      <span v-for="c in categories" :key="c" class="tab" :class="{ active: filterCat===c }" @click="filterCat=c">{{ c }}</span>
    </div>

    <!-- 期刊列表 -->
    <div v-if="journals.length===0" class="empty">暂无期刊，请在上方添加。</div>
    <div v-else class="journal-table">
      <div class="th">
        <span class="td name">期刊名称</span>
        <span class="td cat">分类</span>
        <span class="td issn">ISSN</span>
        <span class="td action">操作</span>
      </div>
      <div v-for="j in filteredJournals" :key="j.id" class="tr">
        <span class="td name">{{ j.name }}</span>
        <span class="td cat">{{ j.category }}</span>
        <span class="td issn">{{ j.openalex_issn || '—' }}</span>
        <span class="td action">
          <button @click="editJournal(j)" class="btn-sm">编辑</button>
          <button @click="removeJournal(j.id)" class="btn-sm btn-danger">删除</button>
        </span>
      </div>
    </div>

    <!-- 抓取论文按钮 -->
    <div class="fetch-bar">
      <button @click="fetchPapers" :disabled="fetching" class="btn-fetch">
        {{ fetching ? '抓取中...' : '🚀 立即抓取最新论文' }}
      </button>
      <p v-if="fetchMsg" class="fetch-msg">{{ fetchMsg }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getJournals, getCategories, createJournal, updateJournal, deleteJournal } from '../api'
import JournalSearch from '../components/JournalSearch.vue'

const journals = ref([])
const categories = ref([])
const filterCat = ref('')
const fetchMsg = ref('')
const fetching = ref(false)

const form = ref({ name:'', category:'', openalex_issn:'', publisher:'', url:'' })
const editingId = ref(null)

// 处理从 OpenAlex 搜索选择的期刊
function onJournalSelected(journal) {
  form.value.name = journal.name || ''
  form.value.publisher = journal.publisher || ''
  form.value.url = journal.homepage_url || ''
  form.value.openalex_issn = (journal.issn && journal.issn.length > 0) ? journal.issn[0] : ''
}

const filteredJournals = computed(() => {
  if (!filterCat.value) return journals.value
  return journals.value.filter(j => j.category === filterCat.value)
})

async function load() {
  try {
    const [jRes, cRes] = await Promise.all([getJournals(), getCategories()])
    journals.value = jRes.data
    categories.value = cRes.data.categories || []
  } catch(e) { console.error(e) }
}

async function addJournal() {
  if (!form.value.name) return
  try {
    if (editingId.value) {
      await updateJournal(editingId.value, form.value)
    } else {
      await createJournal(form.value)
    }
    form.value = { name:'', category:'', openalex_issn:'', publisher:'', url:'' }
    editingId.value = null
    await load()
  } catch(e) { alert('操作失败：' + (e.response?.data?.detail || e.message)) }
}

function editJournal(j) {
  editingId.value = j.id
  form.value = { name:j.name, category:j.category, openalex_issn:j.openalex_issn||'', publisher:j.publisher||'', url:j.url||'' }
}

async function removeJournal(id) {
  if (!confirm('确认删除此期刊？')) return
  await deleteJournal(id)
  await load()
}

async function fetchPapers() {
  fetching.value = true
  fetchMsg.value = '正在抓取，请稍候（可在服务器后台查看进度）...'
  // 调用后端触发抓取（需要后端添加此接口，当前版本请到服务器手动运行 python fetch_papers.py）
  fetchMsg.value = '请到服务器终端运行：cd /root/academic-tracker/backend && python fetch_papers.py'
  fetching.value = false
}

onMounted(load)
</script>

<style scoped>
h2 { margin-bottom: 16px; }
.add-form { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:20px; padding:16px; background:#fff; border-radius:10px; }
.input { padding:8px 12px; border:1px solid #ddd; border-radius:6px; font-size:13px; }
.btn-add { padding:8px 18px; background:#1a73e8; color:#fff; border:none; border-radius:6px; cursor:pointer; }
.btn-add:disabled { opacity:.5; }
.cat-tabs { display:flex; gap:8px; margin-bottom:16px; flex-wrap:wrap; }
.tab { padding:4px 12px; border-radius:16px; font-size:12px; cursor:pointer; background:#eee; }
.tab.active { background:#1a73e8; color:#fff; }
.journal-table { background:#fff; border-radius:10px; overflow:hidden; }
.th { display:flex; background:#f5f6fa; font-weight:600; font-size:13px; padding:10px 16px; }
.tr { display:flex; padding:10px 16px; border-top:1px solid #f0f0f0; font-size:13px; }
.td { display:flex; align-items:center; }
.td.name { flex:3; }
.td.cat { flex:2; color:#888; }
.td.issn { flex:1; color:#aaa; font-size:12px; }
.td.action { flex:1; gap:6px; }
.btn-sm { padding:3px 10px; border:1px solid #ddd; border-radius:4px; background:#fff; cursor:pointer; font-size:12px; }
.btn-danger { color:#d93025; border-color:#f5c6c6; }
.fetch-bar { margin-top:20px; }
.btn-fetch { padding:10px 20px; background:#34a853; color:#fff; border:none; border-radius:6px; cursor:pointer; font-size:14px; }
.btn-fetch:disabled { opacity:.6; }
.fetch-msg { margin-top:8px; font-size:12px; color:#888; }
.empty { text-align:center; color:#aaa; padding:32px; }
</style>
