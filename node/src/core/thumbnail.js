import { doc, ready } from '../utils'

ready(() => {
  const $form = doc('form')
  const $submitButton = $form.querySelector('button[type=button]')
  $submitButton.addEventListener('click', e => {
    doc('#id_time').value = doc('video').currentTime
    $submitButton.classList.add('is-loading')
    $submitButton.disabled = true
    $form.submit()
  })
})
