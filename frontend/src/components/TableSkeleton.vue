<template>
  <div class="table-skeleton">
    <div class="skeleton-header">
      <div class="skeleton-title"></div>
      <div class="skeleton-button"></div>
    </div>
    <div class="skeleton-table">
      <div class="skeleton-thead">
        <div v-for="i in columns" :key="i" class="skeleton-th"></div>
      </div>
      <div v-for="row in rows" :key="row" class="skeleton-tbody">
        <div v-for="i in columns" :key="i" class="skeleton-td"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  columns?: number
  rows?: number
}>(), {
  columns: 6,
  rows: 5
})
</script>

<style scoped>
.table-skeleton {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.skeleton-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.skeleton-title {
  width: 120px;
  height: 24px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s ease-in-out infinite;
  border-radius: 4px;
}

.skeleton-button {
  width: 100px;
  height: 36px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s ease-in-out infinite;
  border-radius: 4px;
}

.skeleton-table {
  width: 100%;
}

.skeleton-thead {
  display: flex;
  margin-bottom: 12px;
  padding: 12px;
  background-color: #f8fafc;
  border-radius: 4px;
}

.skeleton-th {
  flex: 1;
  height: 16px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s ease-in-out infinite;
  border-radius: 4px;
  margin: 0 8px;
}

.skeleton-th:first-child {
  margin-left: 0;
}

.skeleton-th:last-child {
  margin-right: 0;
}

.skeleton-tbody {
  display: flex;
  padding: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.skeleton-tbody:last-child {
  border-bottom: none;
}

.skeleton-td {
  flex: 1;
  height: 14px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s ease-in-out infinite;
  border-radius: 4px;
  margin: 0 8px;
}

.skeleton-td:first-child {
  margin-left: 0;
}

.skeleton-td:last-child {
  margin-right: 0;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>