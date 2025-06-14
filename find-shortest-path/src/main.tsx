import React from 'react'
import ReactDOM from 'react-dom/client'
import DijkstraVisualization from './DijkstraVisualization'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <DijkstraVisualization />
  </React.StrictMode>,
)