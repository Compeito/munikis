import Tooltip from 'tooltip.js'

import { doc, docAll, ready, activateTweetButton, Notify } from '../utils'
import './styles.scss'


ready(() => {
  /**
   * 2重サブミット対策
   *
   */
  const $submitButtons = docAll('button[type=submit]')
  $submitButtons.forEach($button => {
    $button.addEventListener('click', e => {
      $button.classList.add('is-loading')
    })
  })
  const $submitForm = docAll('form.submit-form')
  $submitForm.forEach($form => {
    $form.addEventListener('submit', e => {
      $submitButtons.forEach($submitButton => {
        $submitButton.disabled = true
      })
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

    const isInWindow = ($dom) => {
      const rect = $dom.getBoundingClientRect()
      return 0 < rect.top && rect.bottom < window.innerHeight
    }

    const scrollCallBack = e => {
      if (!isInWindow($wrapper)) {
        if ($thumb.src !== jpg) {
          $thumb.src = jpg
        }
        return
      }
      setTimeout(() => {
        if (isInWindow($wrapper) && $thumb.src !== gif) {
          $thumb.src = gif
        }
      }, 500)
    }

    scrollCallBack()
    window.addEventListener('scroll', scrollCallBack)
  })
})
