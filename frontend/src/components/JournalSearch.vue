<template>
  <div class="journal-search">
    <div class="search-box">
      <span class="search-icon">🔍</span>
      <input
        v-model="query"
        @keyup.enter="handleSearch"
        placeholder="搜索期刊（输入英文名称，如：Journal of Applied Psychology）"
        class="search-input"
      />
      <button @click="handleSearch" :disabled="loading" class="btn btn-primary btn-sm">
        {{ loading ? '搜索中...' : '搜索' }}
      </button>
    </div>

    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="results.length > 0 && !selectedJournal" class="search-results">
      <h4>搜索结果（点击选择）：</h4>
      <div class="results-list">
        <div
          v-for="(journal, index) in results"
          :key="index"
          class="journal-item"
          @click="handleSelect(journal)"
        >
          <div class="journal-info">
            <div class="journal-name">
              ✅ {{ journal.name }}
            </div>
            <div class="journal-meta">
              <span v-if="journal.publisher" class="meta-item">📚 {{ journal.publisher }}</span>
              <span v-if="journal.issn && journal.issn.length > 0" class="meta-item">
                ISSN: {{ journal.issn.join(', ') }}
              </span>
              <span class="meta-item">📊 论文数: {{ journal.works_count }}</span>
              <span class="meta-item">📈 被引: {{ journal.cited_by_count }}</span>
            </div>
            <a
              v-if="journal.homepage_url"
              :href="journal.homepage_url"
              target="_blank"
              rel="noopener noreferrer"
              class="journal-url"
              @click.stop
            >
              🔗 访问期刊主页
            </a>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedJournal" class="selected-journal">
      <h4>✅ 已选择期刊：</h4>
      <div class="journal-card">
        <div class="journal-name">{{ selectedJournal.name }}</div>
        <div class="journal-details">
          <p><strong>出版社：</strong>{{ selectedJournal.publisher || '未知' }}</p>
          <p v-if="selectedJournal.issn && selectedJournal.issn.length > 0">
            <strong>ISSN：</strong>{{ selectedJournal.issn.join(', ') }}
          </p>
          <p><strong>论文数量：</strong>{{ selectedJournal.works_count }}</p>
          <p><strong>被引用次数：</strong>{{ selectedJournal.cited_by_count }}</p>
          <p v-if="selectedJournal.homepage_url">
            <strong>主页：</strong>
            <a :href="selectedJournal.homepage_url" target="_blank" rel="noopener noreferrer">
              {{ selectedJournal.homepage_url }}
            </a>
          </p>
          <p><strong>OpenAlex ID：</strong>{{ selectedJournal.openalex_id }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  onSelectJournal: Function
})

const query = ref('')
const results = ref([])
const loading = ref(false)
const error = ref('')
const selectedJournal = ref(null)

const emit = defineEmits(['journalSelected'])

const handleSearch = async () => {
  if (!query.value.trim()) {
    error.value = '请输入期刊名称'
    return
  }

  loading.value = true
  error.value = ''
  results.value = []

  try {
    const response = await fetch(
      `/api/openalex/search?query=${encodeURIComponent(query.value)}&limit=10`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      }
    )

    if (!response.ok) {
      throw new Error('搜索失败')
    }

    const data = await response.json()
    results.value = data.journals || []
    
    if (results.value.length === 0) {
      error.value = '未找到相关期刊，请尝试其他关键词'
    }
  } catch (err) {
    error.value = err.message || '搜索失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const handleSelect = (journal) => {
  selectedJournal.value = journal
  emit('journalSelected', journal)
  if (props.onSelectJournal) {
    props.onSelectJournal(journal)
  }
}
</script>

<style scoped>
.journal-search {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 2px dashed #dee2e6;
}

.search-box {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 1rem;
}

.search-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  padding: 0.5rem 1rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.9rem;
}

.search-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.error-message {
  padding: 0.75rem;
  background: #f8d7da;
  color: #721c24;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.search-results {
  margin-top: 1rem;
}

.search-results h4 {
  margin-bottom: 0.75rem;
  color: #495057;
  font-size: 0.95rem;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.journal-item {
  padding: 1rem;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.journal-item:hover {
  border-color: #007bff;
  box-shadow: 0 2px 4px rgba(0, 123, 255, 0.1);
  transform: translateY(-1px);
}

.journal-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.journal-name {
  font-weight: 600;
  color: #212529;
  font-size: 1rem;
}

.journal-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.85rem;
  color: #6c757d;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.journal-url {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #007bff;
  text-decoration: none;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.journal-url:hover {
  text-decoration: underline;
}

.selected-journal {
  margin-top: 1rem;
}

.selected-journal h4 {
  color: #28a745;
  margin-bottom: 0.75rem;
}

.journal-card {
  padding: 1rem;
  background: white;
  border: 2px solid #28a745;
  border-radius: 6px;
}

.journal-card .journal-name {
  font-size: 1.1rem;
  color: #212529;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #dee2e6;
}

.journal-details p {
  margin: 0.5rem 0;
  font-size: 0.9rem;
  color: #495057;
}

.journal-details strong {
  color: #212529;
  margin-right: 0.5rem;
}

.journal-details a {
  color: #007bff;
  text-decoration: none;
}

.journal-details a:hover {
  text-decoration: underline;
}
</style>
