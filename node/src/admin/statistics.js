import Chart from 'chart.js'
import 'chartjs-plugin-zoom'

const VIEW_COUNT = 10

document.addEventListener('DOMContentLoaded', () => {
  const chartDataJSON = document.getElementById('chartData')
  const chartData = JSON.parse(chartDataJSON.innerText)

  const createChart = chartOption => {
    const ctx = document.getElementById(chartOption.id).getContext('2d')
    new Chart(ctx, {
      type: 'bar',
      data: {
        datasets: [
          {
            label: chartOption.label,
            data: chartOption.data.map(item => {
              item.x = new Date(item.date)
              return item
            }),
            borderColor: chartOption.color,
            backgroundColor: chartOption.color,
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
                min: chartOption.data[chartOption.data.length - VIEW_COUNT].x,
                max: chartOption.data[chartOption.data.length - 1].x,
              }
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
              speed: 10,
              threshold: 10,
            },
            zoom: {
              enabled: true,
              mode: ''
            }
          }
        }
      },
    })
  }

  createChart({
    id: 'userChart',
    label: '新規登録者数',
    data: chartData.user,
    color: 'blue'
  })

  createChart({
    id: 'videoChart',
    label: '動画投稿数',
    data: chartData.video,
    color: 'red'
  })
})
