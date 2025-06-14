import { useState } from 'react';
import { Play, RotateCcw, ChevronRight } from 'lucide-react';

interface Node {
  id: number;
  type: string;
  label: string;
  color: string;
  position: { x: number; y: number };
}

interface Edge {
  from: number;
  to: number;
}

interface NetworkData {
  nodes: Node[];
  edges: Edge[];
}

const DijkstraVisualization = () => {
  const networkData: NetworkData = {
    "nodes": [
      {"id": 1, "type": "departure", "label": "Vị trí xe 1 xuất phát", "color": "orange", "position": {"x": 1, "y": 1}},
      {"id": 2, "type": "departure", "label": "Vị trí xe 2 xuất phát", "color": "orange", "position": {"x": 1, "y": 2}},
      {"id": 3, "type": "intermediate", "label": "Nút trung gian", "color": "white", "position": {"x": 1, "y": 3}},
      {"id": 4, "type": "intermediate", "label": "Nút trung gian", "color": "white", "position": {"x": 1, "y": 4}},
      {"id": 5, "type": "intermediate", "label": "Nút trung gian", "color": "white", "position": {"x": 2, "y": 1}},
      {"id": 6, "type": "intermediate", "label": "Nút trung gian", "color": "white", "position": {"x": 2, "y": 2}},
      {"id": 7, "type": "intermediate", "label": "Nút trung gian", "color": "white", "position": {"x": 2, "y": 3}},
      {"id": 8, "type": "intermediate", "label": "Nút trung gian", "color": "white", "position": {"x": 2, "y": 4}},
      {"id": 9, "type": "intermediate", "label": "Nút trung gian", "color": "white", "position": {"x": 3, "y": 4}},
      {"id": 10, "type": "intermediate", "label": "Nút trung gian", "color": "white", "position": {"x": 3, "y": 3}},
      {"id": 11, "type": "intermediate", "label": "Nút trung gian", "color": "white", "position": {"x": 3, "y": 2}},
      {"id": 12, "type": "destination", "label": "Vị trí đích đến 1", "color": "green", "position": {"x": 4, "y": 2}},
      {"id": 13, "type": "destination", "label": "Vị trí đích đến 2", "color": "green", "position": {"x": 4, "y": 3}}
    ],
    "edges": [
      {"from": 1, "to": 5}, {"from": 1, "to": 2}, {"from": 2, "to": 6}, {"from": 2, "to": 3},
      {"from": 3, "to": 7}, {"from": 3, "to": 4}, {"from": 5, "to": 6}, {"from": 6, "to": 11},
      {"from": 7, "to": 8}, {"from": 7, "to": 10}, {"from": 10, "to": 9}, {"from": 10, "to": 11},
      {"from": 11, "to": 12}, {"from": 10, "to": 13}
    ]
  };

  const [selectedStart, setSelectedStart] = useState(1);
  const [selectedEnd, setSelectedEnd] = useState(12);
  const [isRunning, setIsRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [distances, setDistances] = useState<Record<number, number>>({});
  const [visited, setVisited] = useState(new Set<number>());
  const [path, setPath] = useState<number[]>([]);
  const [currentNode, setCurrentNode] = useState<number | null>(null);

  // Tính khoảng cách Euclidean giữa 2 nút
  const calculateDistance = (node1: Node, node2: Node) => {
    const dx = node1.position.x - node2.position.x;
    const dy = node1.position.y - node2.position.y;
    return Math.sqrt(dx * dx + dy * dy);
  };

  // Tạo adjacency list với trọng số
  const createAdjacencyList = () => {
    const adj: Record<number, Array<{ node: number; weight: number }>> = {};
    networkData.nodes.forEach(node => {
      adj[node.id] = [];
    });

    networkData.edges.forEach(edge => {
      const fromNode = networkData.nodes.find(n => n.id === edge.from);
      const toNode = networkData.nodes.find(n => n.id === edge.to);
      const weight = calculateDistance(fromNode, toNode);
      
      adj[edge.from].push({ node: edge.to, weight });
      adj[edge.to].push({ node: edge.from, weight }); // Vì là đồ thị không có hướng
    });

    return adj;
  };

  // Thuật toán Dijkstra
  const dijkstra = (start: number, end: number) => {
    const adj = createAdjacencyList();
    const dist: Record<number, number> = {};
    const prev: Record<number, number | null> = {};
    const pq: Array<{ node: number; distance: number }> = [];
    const steps: Array<{ currentNode: number; distances: Record<number, number>; visited: Set<number>; message: string }> = [];

    // Khởi tạo
    networkData.nodes.forEach(node => {
      dist[node.id] = node.id === start ? 0 : Infinity;
      prev[node.id] = null;
      pq.push({ node: node.id, distance: dist[node.id] });
    });

    const visitedNodes = new Set();

    while (pq.length > 0) {
      // Sắp xếp theo khoảng cách
      pq.sort((a, b) => a.distance - b.distance);
      const current = pq.shift();

      if (visitedNodes.has(current.node) || current.distance === Infinity) continue;

      visitedNodes.add(current.node);
      
      steps.push({
        currentNode: current.node,
        distances: { ...dist },
        visited: new Set(visitedNodes),
        message: `Đang xử lý nút ${current.node} với khoảng cách ${current.distance.toFixed(2)}`
      });

      if (current.node === end) break;

      // Cập nhật khoảng cách đến các nút kề
      adj[current.node].forEach((neighbor: { node: number; weight: number }) => {
        if (!visitedNodes.has(neighbor.node)) {
          const newDist = dist[current.node] + neighbor.weight;
          if (newDist < dist[neighbor.node]) {
            dist[neighbor.node] = newDist;
            prev[neighbor.node] = current.node;
            pq.push({ node: neighbor.node, distance: newDist });
          }
        }
      });
    }

    // Tái tạo đường đi
    const path = [];
    let current = end;
    while (current !== null) {
      path.unshift(current);
      current = prev[current];
    }

    return { steps, path, finalDistance: dist[end] };
  };

  const runAlgorithm = () => {
    const result = dijkstra(selectedStart, selectedEnd);
    setIsRunning(true);
    setCurrentStep(0);
    
    let step = 0;
    const interval = setInterval(() => {
      if (step < result.steps.length) {
        const currentStepData = result.steps[step];
        setDistances(currentStepData.distances);
        setVisited(currentStepData.visited);
        setCurrentNode(currentStepData.currentNode);
        setCurrentStep(step);
        step++;
      } else {
        setPath(result.path);
        setIsRunning(false);
        clearInterval(interval);
      }
    }, 1000);
  };

  const reset = () => {
    setIsRunning(false);
    setDistances({});
    setVisited(new Set());
    setPath([]);
    setCurrentNode(null);
    setCurrentStep(0);
  };

  const getNodeColor = (node: Node) => {
    if (path.includes(node.id) && !isRunning) return '#22c55e'; // Đường đi cuối cùng
    if (currentNode === node.id) return '#f59e0b'; // Nút đang xử lý
    if (visited.has(node.id)) return '#6b7280'; // Đã thăm
    if (node.type === 'departure') return '#f97316';
    if (node.type === 'destination') return '#10b981';
    return '#ffffff';
  };

  const getEdgeColor = (from: number, to: number) => {
    if (path.length > 0 && !isRunning) {
      const fromIndex = path.indexOf(from);
      const toIndex = path.indexOf(to);
      if (fromIndex !== -1 && toIndex !== -1 && Math.abs(fromIndex - toIndex) === 1) {
        return '#22c55e';
      }
    }
    return '#e5e7eb';
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-3xl font-bold text-center mb-6 text-gray-800">
          Thuật toán Dijkstra - Tìm đường đi ngắn nhất
        </h1>

        {/* Controls */}
        <div className="flex flex-wrap gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2">
            <label className="font-medium">Điểm xuất phát:</label>
            <select 
              value={selectedStart} 
              onChange={(e) => setSelectedStart(parseInt(e.target.value))}
              className="border rounded px-2 py-1"
              disabled={isRunning}
            >
              {networkData.nodes.filter(n => n.type === 'departure').map(node => (
                <option key={node.id} value={node.id}>Nút {node.id}</option>
              ))}
            </select>
          </div>
          
          <div className="flex items-center gap-2">
            <label className="font-medium">Điểm đích:</label>
            <select 
              value={selectedEnd} 
              onChange={(e) => setSelectedEnd(parseInt(e.target.value))}
              className="border rounded px-2 py-1"
              disabled={isRunning}
            >
              {networkData.nodes.filter(n => n.type === 'destination').map(node => (
                <option key={node.id} value={node.id}>Nút {node.id}</option>
              ))}
            </select>
          </div>

          <button
            onClick={runAlgorithm}
            disabled={isRunning}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            <Play size={16} />
            Chạy thuật toán
          </button>

          <button
            onClick={reset}
            className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
          >
            <RotateCcw size={16} />
            Reset
          </button>
        </div>

        {/* Visualization */}
        <div className="bg-gray-100 rounded-lg p-4 mb-6">
          <svg viewBox="0 0 500 400" className="w-full h-96">
            {/* Edges */}
            {networkData.edges.map((edge, index) => {
              const fromNode = networkData.nodes.find(n => n.id === edge.from);
              const toNode = networkData.nodes.find(n => n.id === edge.to);
              if (!fromNode || !toNode) return null;
              const x1 = fromNode.position.x * 100;
              const y1 = fromNode.position.y * 80;
              const x2 = toNode.position.x * 100;
              const y2 = toNode.position.y * 80;
              
              return (
                <line
                  key={index}
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke={getEdgeColor(edge.from, edge.to)}
                  strokeWidth="3"
                />
              );
            })}

            {/* Nodes */}
            {networkData.nodes.map(node => (
              <g key={node.id}>
                <circle
                  cx={node.position.x * 100}
                  cy={node.position.y * 80}
                  r="20"
                  fill={getNodeColor(node)}
                  stroke="#374151"
                  strokeWidth="2"
                />
                <text
                  x={node.position.x * 100}
                  y={node.position.y * 80 + 5}
                  textAnchor="middle"
                  className="text-sm font-bold"
                  fill="#374151"
                >
                  {node.id}
                </text>
                {distances[node.id] !== undefined && distances[node.id] !== Infinity && (
                  <text
                    x={node.position.x * 100}
                    y={node.position.y * 80 - 30}
                    textAnchor="middle"
                    className="text-xs font-medium"
                    fill="#dc2626"
                  >
                    {distances[node.id].toFixed(1)}
                  </text>
                )}
              </g>
            ))}
          </svg>
        </div>

        {/* Algorithm Explanation */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-3 text-blue-800">Thuật toán Dijkstra</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-start gap-2">
                <ChevronRight size={16} className="mt-0.5 text-blue-600" />
                <span><strong>Bước 1:</strong> Khởi tạo khoảng cách từ nút xuất phát = 0, các nút khác = ∞</span>
              </div>
              <div className="flex items-start gap-2">
                <ChevronRight size={16} className="mt-0.5 text-blue-600" />
                <span><strong>Bước 2:</strong> Chọn nút chưa thăm có khoảng cách nhỏ nhất</span>
              </div>
              <div className="flex items-start gap-2">
                <ChevronRight size={16} className="mt-0.5 text-blue-600" />
                <span><strong>Bước 3:</strong> Cập nhật khoảng cách đến các nút kề</span>
              </div>
              <div className="flex items-start gap-2">
                <ChevronRight size={16} className="mt-0.5 text-blue-600" />
                <span><strong>Bước 4:</strong> Đánh dấu nút hiện tại là đã thăm</span>
              </div>
              <div className="flex items-start gap-2">
                <ChevronRight size={16} className="mt-0.5 text-blue-600" />
                <span><strong>Bước 5:</strong> Lặp lại cho đến khi tìm được đích</span>
              </div>
            </div>
          </div>

          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-3 text-green-800">Đặc điểm & Ứng dụng</h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-start gap-2">
                <ChevronRight size={16} className="mt-0.5 text-green-600" />
                <span><strong>Độ phức tạp:</strong> O((V + E) log V) với heap</span>
              </div>
              <div className="flex items-start gap-2">
                <ChevronRight size={16} className="mt-0.5 text-green-600" />
                <span><strong>Điều kiện:</strong> Trọng số cạnh không âm</span>
              </div>
              <div className="flex items-start gap-2">
                <ChevronRight size={16} className="mt-0.5 text-green-600" />
                <span><strong>Ứng dụng:</strong> GPS, mạng máy tính, logistics</span>
              </div>
              <div className="flex items-start gap-2">
                <ChevronRight size={16} className="mt-0.5 text-green-600" />
                <span><strong>Ưu điểm:</strong> Tối ưu, dễ hiểu và cài đặt</span>
              </div>
            </div>
          </div>
        </div>

        {/* Status */}
        {path.length > 0 && !isRunning && (
          <div className="mt-4 p-4 bg-green-100 rounded-lg">
            <h4 className="font-semibold text-green-800 mb-2">Kết quả:</h4>
            <p className="text-green-700">
              Đường đi ngắn nhất từ nút {selectedStart} đến nút {selectedEnd}: {path.join(' → ')}
            </p>
            <p className="text-green-700">
              Tổng khoảng cách: {distances[selectedEnd]?.toFixed(2) || 'N/A'}
            </p>
          </div>
        )}

        {/* Legend */}
        <div className="mt-4 flex flex-wrap gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-orange-500 rounded-full"></div>
            <span>Xuất phát</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-green-500 rounded-full"></div>
            <span>Đích đến</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-yellow-500 rounded-full"></div>
            <span>Đang xử lý</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-gray-500 rounded-full"></div>
            <span>Đã thăm</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-white border-2 border-gray-400 rounded-full"></div>
            <span>Chưa thăm</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DijkstraVisualization;