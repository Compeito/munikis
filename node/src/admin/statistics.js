import Chart from 'chart.js'
import 'chartjs-plugin-zoom'

document.addEventListener('DOMContentLoaded', () => {
  const ctx = document.getElementById('chart').getContext('2d')

  const chartDataJSON = document.getElementById('chartData')
  const chartData = JSON.parse(chartDataJSON.innerText)

  const chart = new Chart(ctx, {
    type: 'bar',
    data: {
      datasets: [
        {
          label: '動画投稿数',
          data: chartData.video.map((d) => {
            d.x = new Date(d.date)
            return d
          }),
          backgroundColor: 'red',
        },
        {
          label: '新規登録者数',
          data: chartData.user.map((d) => {
            d.x = new Date(d.date)
            return d
          }),
          backgroundColor: 'blue',
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
              round: 'day',
              displayFormats: {
                day: 'MMM D',
              },
            },
          },
        ],
        yAxes: [
          {
            ticks: {
              suggestedMax: 20,
              beginAtZero: true,
            },
          },
        ],
      },
      plugins: {
        zoom: {
          pan: {
            enabled: true,
            mode: 'x',
            rangeMax: {
              x: 7,
            },
          },
        }
      }
    },
  })
})
