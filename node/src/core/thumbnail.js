import { doc, ready } from '../utils'

ready(() => {
  const $video = doc('video')
  const $timeInput = doc('#id_time')
  const $form = doc('#thumbnail-form')
  const $button = $form.querySelector('button[type=button]')
  $button.addEventListener('click', e => {
    $timeInput.value = $video.currentTime
    $button.classList.add('is-loading')
    $button.disabled = true
    $form.submit()
  })
})
