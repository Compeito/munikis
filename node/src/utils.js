import Vue from 'vue/dist/vue.esm'
import axios from 'axios'

export const ready = callback => window.addEventListener('DOMContentLoaded', callback)

export const doc = q => document.querySelector(q)

export const docAll = q => Array.from(document.querySelectorAll(q))

export const range = n => [...Array(n).keys()]

export const getTweetHref = (text = document.title, url = location.href, hashtags = 'tsukuriga') => {
  return encodeURI(
    decodeURI(
      `https://twitter.com/intent/tweet?text=${text}&url=${url}&hashtags=${hashtags}`
    )
  )
}

export const getTweetOnClick = href => {
  return e => {
    window.open(href, 'ツイート',
      'width=650, height=270, personalbar=0, toolbar=0, scrollbars=1, sizable=1'
    )
    e.preventDefault()
  }
}

export const activateTweetButton = $button => {
  const url = $button.dataset.href ? (location.origin + $button.dataset.href) : undefined
  $button.href = getTweetHref($button.dataset.text, url, $button.dataset.hashtags)
  $button.onclick = getTweetOnClick($button.href)
}

export const user = () => {
  const jsonString = doc('#userJson').textContent
  return jsonString ? JSON.parse(jsonString) : {}
}

export const csrf = () => {
  const form = new FormData()
  const csrf = document.querySelector('body').dataset.csrf
  form.append('csrfmiddlewaretoken', csrf)
  return form
}

export const ajaxForm = (form, callback) => {
  const $form = doc(form)
  const $submitButton = $form.querySelector('button[type=submit]')
  $form.addEventListener('submit', e => {
    e.preventDefault()

    $submitButton.disabled = true
    $submitButton.classList.add('is-loading')

    const formData = new FormData($form)
    $form.reset()

    axios.post($form.action, formData)
      .then(response => {
        if (response.data.isSuccess) {
          response.data.results.forEach(result => {
            Notify.activate('success', result.message)
          })
        }
      })
      .catch(err => {
        err.response.data.errors.forEach(error => {
          Notify.activate('danger', error.message)
        })
      })
      .finally(() => {
        callback()
        $submitButton.classList.remove('is-loading')
        $submitButton.disabled = false
      })
  })
}

export const deleteModal = el => {
  return new Vue({
    el: el,
    data() {
      return {
        deleteInput: '',
        correctInput: ''
      }
    },
    mounted() {
      const $modal = this.$refs.deleteModal
      this.correctInput = $modal.dataset.correct
    },
    computed: {
      isDeletable() {
        return this.deleteInput === this.correctInput
      }
    },
    methods: {
      hideModal() {
        this.$refs.deleteModal.classList.remove('is-active')
      }
    }
  })
}

export const fadeIn = el => {
  /**
   * http://youmightnotneedjquery.com/
   */
  el.style.opacity = 0

  let last = +new Date()
  const tick = () => {
    el.style.opacity = +el.style.opacity + (new Date() - last) / 400
    last = +new Date()

    if (+el.style.opacity < 1) {
      (window.requestAnimationFrame && requestAnimationFrame(tick)) || setTimeout(tick, 16)
    }
  }

  tick()
}

export const Notify = {
  instance: null,
  getInstance() {
    if (this.instance) return this.instance
    return new Vue({
      el: '#notify-container',
      delimiters: ['[[', ']]'],
      computed: {
        hasNotify() {
          return this.tag.length > 0 && this.message.length > 0
        },
        className() {
          if (this.hasNotify) {
            if (this.tag === 'error') {
              this.tag = 'danger'
            }
            return 'notification is-' + this.tag
          }
        }
      },
      data() {
        return {
          tag: '',
          message: ''
        }
      },
      methods: {
        activate(tag, message) {
          fadeIn(this.$refs.notifyItem)
          this.tag = tag
          this.message = message
          setTimeout(() => {
            this.deactivate()
          }, 5000)
        },
        deactivate() {
          this.tag = ''
          this.message = ''
        }
      }
    })
  },
  activate(tag, message) {
    this.instance = this.getInstance()
    this.instance.activate(tag, message)
  }
}
