<template>
  <div class="paper-list-page">
    <!-- 搜索和筛选栏 -->
    <div class="toolbar">
      <input v-model="search" @input="loadPapers" placeholder="搜索标题/作者/摘要..." class="search-input" />
      <select v-model="filterCategory" @change="loadPapers" class="filter-select">
        <option value="">全部分类</option>
        <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
      </select>
      <select v-model="filterRead" @change="loadPapers" class="filter-select">
        <option value="">全部状态</option>
        <option value="unread">未读</option>
        <option value="read">已读</option>
        <option value="starred">已星标</option>
      </select>
      <select v-model="sortBy" @change="loadPapers" class="filter-select">
        <option value="fetched_at">按获取时间</option>
        <option value="publication_date">按发表日期</option>
        <option value="title">按标题</option>
      </select>
      <button @click="toggleOrder" class="btn-order">{{ order==='desc' ? '↓ 降序' : '↑ 升序' }}</button>
    </div>

    <!-- 论文列表 -->
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="papers.length === 0" class="empty">暂无论文，请先在「期刊管理」中添加期刊并抓取论文。</div>
    <div v-else class="paper-cards">
      <div v-for="p in papers" :key="p.id" class="paper-card" :class="{ 'is-read': p.is_read }">
        <div class="card-header">
          <span class="star" @click="toggleStar(p)">{{ p.is_starred ? '⭐' : '☆' }}</span>
          <span class="read-toggle" @click="toggleRead(p)">{{ p.is_read ? '✅ 已读' : '📄 未读' }}</span>
        </div>
        <h3 class="paper-title">
          <a :href="p.url" target="_blank" rel="noopener">{{ p.title }}</a>
        </h3>
        <div class="paper-meta">
          <span class="journal-tag">{{ p.journal_name }}</span>
          <span v-if="p.publication_date">{{ p.publication_date }}</span>
          <span v-if="p.volume">Vol.{{ p.volume }}</span>
        </div>
        <div v-if="p.authors" class="paper-authors">{{ p.authors }}</div>
        <p v-if="p.abstract" class="paper-abstract">{{ truncate(p.abstract, 200) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getPapers, getCategories, updatePaperStatus } from '../api'

const papers = ref([])
const categories = ref([])
const search = ref('')
const filterCategory = ref('')
const filterRead = ref('')
const sortBy = ref('fetched_at')
const order = ref('desc')
const loading = ref(false)
let skip = 0
const LIMIT = 50

async function loadPapers() {
  loading.value = true
  const params = {
    skip: 0,
    limit: LIMIT,
    sort_by: sortBy.value,
    order: order.value,
  }
  if (filterCategory.value) params.category = filterCategory.value
  if (filterRead.value === 'unread') params.is_read = false
  if (filterRead.value === 'read') params.is_read = true
  if (filterRead.value === 'starred') params.is_starred = true
  if (search.value) params.search = search.value

  try {
    const res = await getPapers(params)
    papers.value = res.data
  } catch (e) {
    console.error('加载论文失败', e)
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  try {
    const res = await getCategories()
    categories.value = res.data.categories || []
  } catch (e) { console.error(e) }
}

function toggleOrder() {
  order.value = order.value === 'desc' ? 'asc' : 'desc'
  loadPapers()
}

async function toggleStar(p) {
  const newVal = !p.is_starred
  await updatePaperStatus(p.id, { is_starred: newVal })
  p.is_starred = newVal
}

async function toggleRead(p) {
  const newVal = !p.is_read
  await updatePaperStatus(p.id, { is_read: newVal })
  p.is_read = newVal
}

function truncate(str, len) {
  if (!str) return ''
  return str.length > len ? str.slice(0, len) + '...' : str
}

onMounted(() => {
  loadCategories()
  loadPapers()
})
</script>

<style scoped>
.toolbar { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
.search-input { flex:1; min-width: 200px; padding: 8px 12px; border:1px solid #ddd; border-radius:6px; }
.filter-select { padding: 8px 12px; border:1px solid #ddd; border-radius:6px; background:#fff; }
.btn-order { padding: 8px 14px; border:1px solid #ddd; border-radius:6px; background:#fff; cursor:pointer; }
.paper-cards { display: flex; flex-direction: column; gap: 14px; }
.paper-card { background:#fff; border-radius:10px; padding:18px; box-shadow:0 1px 4px rgba(0,0,0,.08); }
.paper-card.is-read { opacity: 0.65; }
.card-header { display:flex; gap:12px; margin-bottom:8px; }
.star { cursor:pointer; font-size:18px; }
.read-toggle { cursor:pointer; font-size:12px; color:#888; }
.paper-title { font-size:15px; margin:0 0 8px 0; }
.paper-title a { color:#1a73e8; text-decoration:none; }
.paper-title a:hover { text-decoration:underline; }
.paper-meta { font-size:12px; color:#888; display:flex; gap:10px; margin-bottom:6px; }
.journal-tag { background:#e8f0fe; color:#1a73e8; padding:2px 8px; border-radius:4px; font-size:11px; }
.paper-authors { font-size:13px; color:#555; margin-bottom:6px; }
.paper-abstract { font-size:13px; color:#666; line-height:1.5; }
.loading, .empty { text-align:center; color:#888; padding:40px; }
</style>
