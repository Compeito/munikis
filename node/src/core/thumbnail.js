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
    // SafariではSubmitと同時の処理が動作しない？
    // https://stackoverflow.com/questions/9934803/show-div-upon-form-submit-works-in-chrome-ff-ie-but-not-safari
    setTimeout(() => {
      $form.submit()
    }, 100)
  })
})
