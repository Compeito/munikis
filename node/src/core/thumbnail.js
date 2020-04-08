import { doc, ready } from '../utils'

ready(() => {
  const $video = doc('video')
  setInterval(() => {
    doc('#id_time').value = $video.currentTime
  }, 100)
})
