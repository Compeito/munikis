import Tooltip from 'tooltip.js'

import { doc, docAll, ready, activateTweetButton, Notify } from '../utils'
import './styles.scss'


ready(() => {
  /**
   * 2重サブミット対策
   *
   */
  const $submitForm = docAll('form.submit-form')
  $submitForm.forEach($form => {
    const $button = $form.querySelector('button[type=submit]')
    $form.addEventListener('submit', e => {
      $button.classList.add('is-loading')
      $button.disabled = true
    })
  })

  /**
   * モーダル展開
   */
  const $modalButton = docAll('.modal-opener')
  $modalButton.forEach($button => {
    const modalId = $button.dataset.target
    $button.addEventListener('click', e => {
      doc('#' + modalId).classList.add('is-active')
    })
  })
  const $modalBg = docAll('.modal-closer')
  $modalBg.forEach($bg => {
    $bg.addEventListener('click', e => {
      $bg.parentNode.classList.remove('is-active')
    })
  })

  /**
   * ツイートボタン
   */
  docAll('.tweet-button').forEach(activateTweetButton)

  /**
   * 通知用
   */
  docAll('.notify-data').forEach(notification => {
    Notify.activate(notification.dataset.tag, notification.dataset.message)
  })

  /**
   * トロフィーポップアップ用
   */
  docAll('.tooltipRef').forEach($tooltip => {
    new Tooltip($tooltip, {
      title: $tooltip.dataset.tooltip,
      placement: 'bottom',
    })
  })

  /**
   * サムネイルgif
   */
  docAll('.video-thumbnail').forEach($wrapper => {
    const $thumb = $wrapper.querySelector('.video-thumbnail-image')
    const gif = $thumb.dataset.gif
    const jpg = $thumb.dataset.thumbnail
    if (!gif) return
    const isMobile = window.innerWidth < 769
    if (isMobile) {
      window.addEventListener('scroll', e => {
        const centerOfView = window.innerHeight / 2
        const wrapperRect = $wrapper.getBoundingClientRect()
        if (wrapperRect.top < centerOfView && centerOfView < wrapperRect.bottom) {
          if ($thumb.src !== gif) {
            $thumb.src = gif
          }
        } else {
          if ($thumb.src !== jpg) {
            $thumb.src = jpg
          }
        }
      })
    } else {
      $wrapper.addEventListener('mouseover', e => {
        if ($thumb.src !== gif) {
          $thumb.src = gif
        }
      })
      $wrapper.addEventListener('mouseout', e => {
        if ($thumb.src !== jpg) {
          $thumb.src = jpg
        }
      })
    }
  })
})
