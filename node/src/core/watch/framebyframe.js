import { doc, range, ready } from '../../utils'


class Video {
  constructor(video) {
    this.$el = doc(video)
    this.frames = this.getFrames()
    const $fpsInput = doc('#fps-input')
    if ($fpsInput) {
      $fpsInput.addEventListener('change', () => {
        this.frames = this.getFrames()
      })
    }
  }

  getFrames() {
    const fps = parseInt(this.$el.dataset.fps) || parseInt(doc('#fps-input').value)
    const duration = parseFloat(this.$el.dataset.duration) || this.$el.duration
    const frameLength = 1 / fps
    const framesCount = Math.floor(fps * duration)
    return range(framesCount).map(i => i * frameLength)
  }

  getCurrentFrame() {
    let minDiffFrame = 0
    let diff = []
    this.frames.forEach((frameVal, frame) => {
      diff[frame] = Math.abs(this.$el.currentTime - frameVal)
      minDiffFrame = (diff[minDiffFrame] < diff[frame]) ? minDiffFrame : frame
    })
    return minDiffFrame
  }

  ready() {
    if (this.$el.currentTime === 0) this.$el.play()
    if (!this.$el.paused) this.$el.pause()
    return this
  }

  push_frame() {
    const currentFrame = this.getCurrentFrame()
    if (currentFrame >= this.frames.length - 1) {
      this.$el.currentTime = this.$el.duration
    } else {
      this.$el.currentTime = parseFloat(this.frames[currentFrame + 1])
    }
  }

  back_frame() {
    const currentFrame = this.getCurrentFrame()
    if (currentFrame <= 0) {
      this.$el.currentTime = 0
    } else {
      this.$el.currentTime = parseFloat(this.frames[currentFrame - 1])
    }
  }
}

ready(() => {
  const video = new Video('video')

  const push_frame = () => video.ready().push_frame()
  const back_frame = () => video.ready().back_frame()

  doc('#next-frame').addEventListener('click', push_frame)
  doc('#prev-frame').addEventListener('click', back_frame)

  document.addEventListener('keydown', e => {
    if (
      ['TEXTAREA', 'INPUT'].indexOf(document.activeElement.tagName) > -1
      || e.shiftKey || e.altKey || e.ctrlKey || e.metaKey
    ) return

    switch (e.code) {
      case 'ArrowRight':
        push_frame()
        e.preventDefault()
        break
      case 'ArrowLeft':
        back_frame()
        e.preventDefault()
        break
      case 'Space':
        if (video.$el.paused) {
          video.$el.play()
        } else {
          video.$el.pause()
        }
        e.preventDefault()
        break
    }
  })
})
