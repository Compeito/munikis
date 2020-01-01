import Chart from 'chart.js'
import 'chartjs-plugin-zoom'

const VIEW_COUNT = 20

document.addEventListener('DOMContentLoaded', () => {
  const chartDataJSON = document.getElementById('chartData')
  const chartData = JSON.parse(chartDataJSON.innerText)

  const createChart = chartOption => {
    const ctx = document.getElementById(chartOption.id).getContext('2d')
    new Chart(ctx, {
      type: 'line',
      data: {
        datasets: [
          {
            label: chartOption.label,
            lineTension: 0,
            data: chartOption.data.map(item => {
              item.x = new Date(item.date)
              return item
            }),
            borderColor: `rgba(${chartOption.color}, 1)`,
            backgroundColor: `rgba(${chartOption.color}, 0.5)`,
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
        },
        plugins: {
          zoom: {
            pan: {
              enabled: true,
              mode: 'x',
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
    color: '0, 0, 255'
  })

  createChart({
    id: 'videoChart',
    label: '動画投稿数',
    data: chartData.video,
    color: '255, 0, 0'
  })
})
