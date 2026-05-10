<template>
  <div class="starred-page">
    <h2>⭐ 星标论文</h2>
    <div v-if="papers.length === 0" class="empty">暂无星标论文</div>
    <div v-else class="paper-cards">
      <div v-for="p in papers" :key="p.id" class="paper-card">
        <h3 class="paper-title">
          <a :href="p.url" target="_blank" rel="noopener">{{ p.title }}</a>
        </h3>
        <div class="paper-meta">
          <span class="journal-tag">{{ p.journal_name }}</span>
          <span v-if="p.publication_date">{{ p.publication_date }}</span>
        </div>
        <div v-if="p.authors" class="paper-authors">{{ p.authors }}</div>
        <button @click="removeStar(p)" class="btn-unstar">取消星标</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getStarredPapers, updatePaperStatus } from '../api'

const papers = ref([])

async function load() {
  try {
    const res = await getStarredPapers()
    papers.value = res.data
  } catch (e) { console.error(e) }
}

async function removeStar(p) {
  await updatePaperStatus(p.id, { is_starred: false })
  papers.value = papers.value.filter(x => x.id !== p.id)
}

onMounted(load)
</script>

<style scoped>
h2 { margin-bottom: 16px; color: #333; }
.paper-cards { display: flex; flex-direction: column; gap: 12px; }
.paper-card { background: #fff; border-radius: 10px; padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
.paper-title { font-size: 14px; margin: 0 0 8px 0; }
.paper-title a { color: #1a73e8; text-decoration: none; }
.paper-title a:hover { text-decoration: underline; }
.paper-meta { font-size: 12px; color: #888; display: flex; gap: 10px; margin-bottom: 6px; }
.journal-tag { background: #fef7e0; color: #e8a800; padding: 2px 8px; border-radius: 4px; font-size: 11px; }
.paper-authors { font-size: 12px; color: #555; margin-bottom: 8px; }
.btn-unstar { padding: 4px 12px; border: 1px solid #ddd; border-radius: 4px; background: #fff; cursor: pointer; font-size: 12px; }
.btn-unstar:hover { background: #f5f5f5; }
.empty { text-align: center; color: #aaa; padding: 40px; }
</style>
