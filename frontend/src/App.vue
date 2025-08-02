<template>
  <v-app>
    <v-app-bar color="primary" density="comfortable">
      <v-app-bar-title>
        <v-icon icon="mdi-delete" class="mr-2"></v-icon>
        Smart Trash Collection System
      </v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn icon @click="fetchStats">
        <v-icon>mdi-refresh</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <!-- Statistics Cards -->
        <v-row class="mb-4">
          <v-col cols="12" sm="6" md="3">
            <v-card color="primary" variant="tonal">
              <v-card-text class="pa-4">
                <div class="text-h4 font-weight-bold">{{ stats.total_bins }}</div>
                <div class="text-subtitle-1">Total Bins</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card color="error" variant="tonal">
              <v-card-text class="pa-4">
                <div class="text-h4 font-weight-bold">{{ stats.full_bins }}</div>
                <div class="text-subtitle-1">Full Bins</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card color="warning" variant="tonal">
              <v-card-text class="pa-4">
                <div class="text-h4 font-weight-bold">{{ stats.needs_maintenance }}</div>
                <div class="text-subtitle-1">Need Maintenance</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card color="info" variant="tonal">
              <v-card-text class="pa-4">
                <div class="text-h4 font-weight-bold">{{ stats.avg_fill_percentage }}%</div>
                <div class="text-subtitle-1">Average Fill</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Filters -->
        <v-row class="mb-4">
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.district"
              :items="districts"
              label="District"
              clearable
              density="compact"
              variant="outlined"
            ></v-select>
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.binType"
              :items="binTypes"
              label="Bin Type"
              clearable
              density="compact"
              variant="outlined"
            ></v-select>
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.status"
              :items="statuses"
              label="Status"
              clearable
              density="compact"
              variant="outlined"
            ></v-select>
          </v-col>
          <v-col cols="12" md="3">
            <v-slider
              v-model="filters.minFill"
              :max="100"
              :step="10"
              label="Min Fill %"
              thumb-label
              density="compact"
            ></v-slider>
          </v-col>
        </v-row>

        <!-- Bins List -->
        <v-row>
          <v-col cols="12">
            <v-card>
              <v-card-title class="d-flex align-center">
                <v-icon icon="mdi-trash-can" class="mr-2"></v-icon>
                Trash Bins
                <v-spacer></v-spacer>
                <v-btn color="primary" @click="showAddDialog = true">
                  <v-icon icon="mdi-plus" class="mr-2"></v-icon>
                  Add Bin
                </v-btn>
              </v-card-title>
              <v-card-text class="pa-0">
                <v-data-table
                  :headers="headers"
                  :items="filteredBins"
                  :loading="loading"
                  density="comfortable"
                  :items-per-page="10"
                >
                  <template v-slot:item.location="{ item }">
                    <div>
                      <div class="font-weight-medium">{{ item.location }}</div>
                      <div class="text-caption text-grey">{{ item.district }}</div>
                    </div>
                  </template>
                  
                  <template v-slot:item.bin_type="{ item }">
                    <v-chip size="small" :color="getTypeColor(item.bin_type)">
                      {{ item.bin_type }}
                    </v-chip>
                  </template>
                  
                  <template v-slot:item.current_fill_percentage="{ item }">
                    <v-progress-linear
                      :model-value="item.current_fill_percentage"
                      :color="getFillColor(item.current_fill_percentage)"
                      height="25"
                      rounded
                    >
                      <template v-slot:default>
                        <strong>{{ item.current_fill_percentage }}%</strong>
                      </template>
                    </v-progress-linear>
                  </template>
                  
                  <template v-slot:item.status="{ item }">
                    <v-chip 
                      size="small" 
                      :color="getStatusColor(item.status)"
                      :prepend-icon="getStatusIcon(item.status)"
                    >
                      {{ formatStatus(item.status) }}
                    </v-chip>
                  </template>
                  
                  <template v-slot:item.last_emptied="{ item }">
                    <div class="text-caption">
                      {{ formatDate(item.last_emptied) }}
                    </div>
                  </template>
                  
                  <template v-slot:item.actions="{ item }">
                      <v-btn
                        icon="mdi-calendar-plus"
                        size="small"
                        variant="text"
                        @click="scheduleCollection(item)"
                        :disabled="item.current_fill_percentage < 20"
                      ></v-btn>
                      <v-btn
                        icon="mdi-delete-empty"
                        size="small"
                        variant="text"
                        color="primary"
                        @click="emptyBin(item.id)"
                        :disabled="item.current_fill_percentage === 0"
                      ></v-btn>
                      <v-btn
                        icon="mdi-wrench"
                        size="small"
                        variant="text"
                        color="warning"
                        @click="toggleMaintenance(item)"
                      ></v-btn>
                  </template>
                </v-data-table>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Upcoming Collections -->
        <v-row class="mt-4">
          <v-col cols="12">
            <v-card>
              <v-card-title>
                <v-icon icon="mdi-truck" class="mr-2"></v-icon>
                Upcoming Collections
              </v-card-title>
              <v-card-text>
                <v-list density="compact">
                  <v-list-item
                    v-for="schedule in upcomingSchedules"
                    :key="schedule.id"
                    :title="getBinLocation(schedule.bin_id)"
                    :subtitle="formatScheduleDate(schedule.scheduled_at)"
                  >
                    <template v-slot:prepend>
                      <v-icon icon="mdi-clock-outline"></v-icon>
                    </template>
                    <template v-slot:append>
                      <v-btn
                        size="small"
                        color="success"
                        @click="completeSchedule(schedule.id)"
                      >
                        Complete
                      </v-btn>
                    </template>
                  </v-list-item>
                  <v-list-item v-if="upcomingSchedules.length === 0">
                    <v-list-item-title class="text-grey">
                      No upcoming collections scheduled
                    </v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>

    <!-- Add Bin Dialog -->
    <v-dialog v-model="showAddDialog" max-width="500">
      <v-card>
        <v-card-title>Add New Bin</v-card-title>
        <v-card-text>
          <v-form ref="addForm">
            <v-text-field
              v-model="newBin.location"
              label="Location"
              required
              :rules="[v => !!v || 'Location is required']"
            ></v-text-field>
            <v-select
              v-model="newBin.district"
              :items="['Downtown', 'Commercial', 'Residential', 'Industrial']"
              label="District"
              required
              :rules="[v => !!v || 'District is required']"
            ></v-select>
            <v-select
              v-model="newBin.bin_type"
              :items="binTypes"
              label="Bin Type"
            ></v-select>
            <v-select
              v-model="newBin.capacity_liters"
              :items="[120, 240, 360]"
              label="Capacity (Liters)"
            ></v-select>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="showAddDialog = false">Done</v-btn>
          <v-btn color="primary" @click="addBin">Add</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Schedule Dialog -->
    <v-dialog v-model="showScheduleDialog" max-width="400">
      <v-card>
        <v-card-title>Schedule Collection</v-card-title>
        <v-card-text>
          <v-date-picker
            v-model="scheduleDate"
            :min="new Date().toISOString().substr(0, 10)"
          ></v-date-picker>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="showScheduleDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="confirmSchedule">Schedule</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color">
      {{ snackbar.text }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false">Close</v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script>
import { createApp } from 'vue'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
  },
})

export default {
  name: 'SmartTrashApp',
  data() {
    return {
      bins: [],
      schedules: [],
      stats: {
        total_bins: 0,
        full_bins: 0,
        needs_maintenance: 0,
        avg_fill_percentage: 0,
        bins_by_type: {},
        bins_by_district: {}
      },
      loading: false,
      showAddDialog: false,
      showScheduleDialog: false,
      selectedBin: null,
      scheduleDate: new Date().toISOString().substr(0, 10),
      filters: {
        district: null,
        binType: null,
        status: null,
        minFill: 0
      },
      newBin: {
        location: '',
        district: '',
        bin_type: 'General',
        capacity_liters: 120
      },
      snackbar: {
        show: false,
        text: '',
        color: 'success'
      },
      headers: [
        { title: 'Location', key: 'location', width: '20%' },
        { title: 'Type', key: 'bin_type', width: '10%' },
        { title: 'Fill Level', key: 'current_fill_percentage', width: '15%' },
        { title: 'Status', key: 'status', width: '12%' },
        { title: 'Last Emptied', key: 'last_emptied', width: '13%' },
        { title: 'Actions', key: 'actions', width: '20%', sortable: false }
      ],
      binTypes: ['General', 'Recycling', 'Organic', 'Hazardous'],
      statuses: ['empty', 'low', 'medium', 'high', 'full', 'needs_maintenance']
    }
  },
  computed: {
    filteredBins() {
      return this.bins.filter(bin => {
        if (this.filters.district && bin.district !== this.filters.district) return false
        if (this.filters.binType && bin.bin_type !== this.filters.binType) return false
        if (this.filters.status && bin.status !== this.filters.status) return false
        if (bin.current_fill_percentage < this.filters.minFill) return false
        return true
      })
    },
    districts() {
      return [...new Set(this.bins.map(b => b.district))]
    },
    upcomingSchedules() {
      return this.schedules.filter(s => !s.completed).slice(0, 5)
    }
  },
  mounted() {
    this.fetchBins()
    this.fetchStats()
    this.fetchSchedules()
    // Auto-refresh every 30 seconds
    setInterval(() => {
      this.fetchBins()
      this.fetchStats()
    }, 30000)
  },
  methods: {
    async fetchBins() {
      this.loading = true
      try {
        const params = new URLSearchParams()
        if (this.filters.district) params.append('district', this.filters.district)
        if (this.filters.binType) params.append('bin_type', this.filters.binType)
        if (this.filters.status) params.append('status', this.filters.status)
        if (this.filters.minFill > 0) params.append('min_fill', this.filters.minFill)
        
        const response = await fetch(`http://localhost:8000/api/bins?${params}`)
        this.bins = await response.json()
      } catch (error) {
        this.showSnackbar('Error fetching bins', 'error')
      } finally {
        this.loading = false
      }
    },
    
    async fetchStats() {
      try {
        const response = await fetch('http://localhost:8000/api/stats')
        this.stats = await response.json()
      } catch (error) {
        this.showSnackbar('Error fetching stats', 'error')
      }
    },
    
    async fetchSchedules() {
      try {
        const response = await fetch('http://localhost:8000/api/schedules')
        this.schedules = await response.json()
      } catch (error) {
        this.showSnackbar('Error fetching schedules', 'error')
      }
    },
    
    async addBin() {
      // Vuetify 3 validate() returns { valid: boolean }
      const form = this.$refs.addForm
      if (form) {
        const result = await form.validate();
        if (!result.valid) return;
      }
      try {
        const payload = { ...this.newBin, bin_type: this.newBin.bin_type.toLowerCase() }
        const response = await fetch('http://localhost:8000/api/bins', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        if (response.ok) {
          this.showSnackbar('Bin added successfully', 'success')
          this.showAddDialog = false
          this.resetNewBin()
          this.fetchBins()
          this.fetchStats()
        }
      } catch (error) {
        this.showSnackbar('Error adding bin', 'error')
      }
    },
    
    async emptyBin(binId) {
      try {
        const response = await fetch(`http://localhost:8000/api/bins/${binId}/empty`, {
          method: 'POST'
        })
        
        if (response.ok) {
          this.showSnackbar('Bin emptied successfully', 'success')
          this.fetchBins()
          this.fetchStats()
        }
      } catch (error) {
        this.showSnackbar('Error emptying bin', 'error')
      }
    },
    
    async toggleMaintenance(bin) {
      try {
        const response = await fetch(`http://localhost:8000/api/bins/${bin.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            maintenance_required: !bin.maintenance_required,
            status: !bin.maintenance_required ? 'needs_maintenance' : 'empty'
          })
        })
        
        if (response.ok) {
          this.showSnackbar('Maintenance status updated', 'success')
          this.fetchBins()
          this.fetchStats()
        }
      } catch (error) {
        this.showSnackbar('Error updating maintenance status', 'error')
      }
    },
    
    scheduleCollection(bin) {
      this.selectedBin = bin
      this.showScheduleDialog = true
    },
    
    async confirmSchedule() {
      if (!this.selectedBin) return
      
      try {
        const scheduledAt = new Date(this.scheduleDate)
        scheduledAt.setHours(9, 0, 0, 0) // Default to 9 AM
        
        const response = await fetch('http://localhost:8000/api/schedules', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            bin_id: this.selectedBin.id,
            scheduled_at: scheduledAt.toISOString()
          })
        })
        
        if (response.ok) {
          this.showSnackbar('Collection scheduled successfully', 'success')
          this.showScheduleDialog = false
          this.fetchSchedules()
        }
      } catch (error) {
        this.showSnackbar('Error scheduling collection', 'error')
      }
    },
    
    async completeSchedule(scheduleId) {
      try {
        const response = await fetch(`http://localhost:8000/api/schedules/${scheduleId}/complete`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            truck_id: `TRUCK-${Math.floor(Math.random() * 100)}`
          })
        })
        
        if (response.ok) {
          this.showSnackbar('Collection completed', 'success')
          this.fetchSchedules()
          this.fetchBins()
          this.fetchStats()
        }
      } catch (error) {
        this.showSnackbar('Error completing collection', 'error')
      }
    },
    
    getBinLocation(binId) {
      const bin = this.bins.find(b => b.id === binId)
      return bin ? bin.location : 'Unknown'
    },
    
    getTypeColor(type) {
      const colors = {
        General: 'grey',
        Recycling: 'blue',
        Organic: 'green',
        Hazardous: 'red'
      }
      return colors[type] || 'grey'
    },
    
    getFillColor(percentage) {
      if (percentage >= 90) return 'red'
      if (percentage >= 70) return 'orange'
      if (percentage >= 40) return 'yellow'
      return 'green'
    },
    
    getStatusColor(status) {
      const colors = {
        empty: 'green',
        low: 'light-green',
        medium: 'yellow',
        high: 'orange',
        full: 'red',
        needs_maintenance: 'purple'
      }
      return colors[status] || 'grey'
    },
    
    getStatusIcon(status) {
      const icons = {
        empty: 'mdi-check-circle',
        low: 'mdi-circle-slice-2',
        medium: 'mdi-circle-slice-4',
        high: 'mdi-circle-slice-6',
        full: 'mdi-circle-slice-8',
        needs_maintenance: 'mdi-wrench'
      }
      return icons[status] || 'mdi-help-circle'
    },
    
    formatStatus(status) {
      return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      const now = new Date()
      const diffHours = Math.floor((now - date) / (1000 * 60 * 60))
      
      if (diffHours < 1) return 'Just now'
      if (diffHours < 24) return `${diffHours}h ago`
      if (diffHours < 48) return 'Yesterday'
      return `${Math.floor(diffHours / 24)}d ago`
    },
    
    formatScheduleDate(dateString) {
      const date = new Date(dateString)
      const options = { 
        weekday: 'short', 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
      }
      return date.toLocaleDateString('en-US', options)
    },
    
    resetNewBin() {
      this.newBin = {
        location: '',
        district: '',
        bin_type: 'General',
        capacity_liters: 120
      }
    },
    
    showSnackbar(text, color = 'success') {
      this.snackbar.text = text
      this.snackbar.color = color
      this.snackbar.show = true
    }
  }
}

// Create and mount the app with Vuetify
const app = createApp(this)
app.use(vuetify)
app.mount('#app')
</script>

<style scoped>
.v-application {
  font-family: 'Roboto', sans-serif;
}
</style>