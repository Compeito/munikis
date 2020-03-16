import Vue from 'vue/dist/vue.esm'

import { ready, csrf, Notify } from '../utils'
import axios from 'axios'


ready(() => {
  new Vue({
    el: '#v-follow-button',
    delimiters: ['[[', ']]'],
    data() {
      return {
        isFollowing: false,
        isLoading: false
      }
    },
    mounted() {
      this.existFriendship()
    },
    computed: {
      username() {
        return this.$refs.followButton.dataset.followeeUsername
      },
      label() {
        return this.isFollowing ? '中' : 'する'
      },
      className() {
        return (this.isFollowing ? ' is-primary' : '') +
          (this.isLoading ? ' is-loading' : '')
      }
    },
    methods: {
      existFriendship() {
        this.isLoading = true
        axios.get(`/ajax/friendships/exist/${this.username}`)
          .then(response => {
            this.isFollowing = response.data.results.isFollowing
          })
          .finally(() => {
            this.isLoading = false
          })
      },
      toggleFavorite() {
        this.isLoading = true
        axios.post(`/ajax/friendships/toggle/${this.username}`, csrf())
          .then(response => {
            Notify.activate('success', response.data.results.message)
            this.existFriendship()
          })
          .finally(() => {
            this.isLoading = false
          })
      }
    }
  })
})
