import Chart from 'chart.js'
import 'chartjs-plugin-zoom'

document.addEventListener('DOMContentLoaded', () => {
  const chartDataJSON = document.getElementById('chartData')
  const chartData = JSON.parse(chartDataJSON.innerText)
  const viewCount = chartData.video.length > 20 ? 20 : chartData.video.length

  const ctx = document.getElementById('chart').getContext('2d')
  new Chart(ctx, {
    type: 'line',
    data: {
      datasets: [
        {
          label: '動画投稿数',
          lineTension: 0,
          data: chartData.video.map(item => {
            item.x = new Date(item.date)
            return item
          }),
          borderColor: 'rgb(166,206,227)',
          backgroundColor: 'rgba(0, 0, 0, 0)',
        },
        {
          label: '新規登録者数',
          lineTension: 0,
          data: chartData.user.map(item => {
            item.x = new Date(item.date)
            return item
          }),
          borderColor: 'rgb(31, 120, 180)',
          backgroundColor: 'rgba(31, 120, 180, 0.1)',
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        xAxes: [
          {
            type: 'time',
            time: {
              unit: 'day',
              displayFormats: {
                day: 'MMM D',
              },
            },
            ticks: {
              min: chartData.video[chartData.video.length - viewCount].x,
              max: chartData.video[chartData.video.length - 1].x,
            }
          },
        ],
      },
      plugins: {
        zoom: {
          pan: {
            enabled: true,
            mode: 'x',
          },
          zoom: {
            enabled: true,
            mode: 'x'
          }
        }
      }
    },
  })
})
