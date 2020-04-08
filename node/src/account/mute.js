import Vue from 'vue/dist/vue.esm'

import { ready, csrf, Notify } from '../utils'
import axios from 'axios'


ready(() => {
  new Vue({
    el: '#v-mute-button',
    delimiters: ['[[', ']]'],
    data() {
      return {
        isMuted: false,
        isLoading: false
      }
    },
    mounted() {
      this.existMute()
    },
    computed: {
      username() {
        return this.$refs.muteButton.dataset.targetUsername
      },
      label() {
        if (this.isLoading) return '...'
        if (this.isMuted) return 'を解除'
        return 'する'
      },
    },
    methods: {
      existMute() {
        this.isLoading = true
        axios.get(`/ajax/mutes/exist/${this.username}`)
          .then(response => {
            this.isMuted = response.data.results.isMuted
          })
          .finally(() => {
            this.isLoading = false
          })
      },
      toggleMute() {
        this.isLoading = true
        axios.post(`/ajax/mutes/toggle/${this.username}`, csrf())
          .then(response => {
            Notify.activate('success', response.data.results.message)
            this.isMuted = response.data.results.isMuted
          })
          .finally(() => {
            this.isLoading = false
          })
      }
    }
  })
})
