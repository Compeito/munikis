import Plyr from 'plyr'
import 'plyr/dist/plyr.css'

import { ready } from '../../utils'

ready(() => {
  const player = new Plyr('#video-player', {
    ratio: '16:9',
    keyboard: {focused: false, global: false},
  })
})
