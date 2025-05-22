'use client';

import { useEffect, useRef, useState } from 'react';
import Head from 'next/head';

// 定义类型
declare global {
  interface Window {
    L: any;
  }
}

const LocationInfo = () => {
  const mapRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<any>(null);
  const [marker, setMarker] = useState<any>(null);
  const [circle, setCircle] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [currentTime, setCurrentTime] = useState('');
  const [headerTime, setHeaderTime] = useState('');
  const [updateTime, setUpdateTime] = useState('');

  // 固定坐标（虚拟北京位置）
  const lat = 39.9042;
  const lng = 116.4074;

  // 更新时间函数
  const updateTimeDisplay = () => {
    const now = new Date();
    const formattedTime = now.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
    
    const headerTimeFormat = now.toLocaleString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
    
    setUpdateTime(formattedTime);
    setHeaderTime(headerTimeFormat);
  };

  // 初始化地图
  useEffect(() => {
    const initMap = () => {
      if (typeof window !== 'undefined' && window.L && mapRef.current) {
        // 初始化地图
        const mapInstance = window.L.map(mapRef.current).setView([lat, lng], 14);

        // 添加地图瓦片
        window.L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
          maxZoom: 19,
          attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, © <a href="https://carto.com/attributions">CARTO</a>'
        }).addTo(mapInstance);

        // 自定义标记图标
        const locationIcon = window.L.divIcon({
          html: '<i class="fas fa-map-marker-alt" style="font-size: 36px; color: #0ea5e9;"></i>',
          className: 'location-marker',
          iconSize: [36, 36],
          iconAnchor: [18, 36]
        });

        // 添加标记
        const markerInstance = window.L.marker([lat, lng], {icon: locationIcon}).addTo(mapInstance);
        
        // 添加圆圈指示定位半径
        const circleInstance = window.L.circle([lat, lng], {
          color: '#0ea5e9',
          fillColor: '#0ea5e9',
          fillOpacity: 0.1,
          radius: 1000,
          weight: 1
        }).addTo(mapInstance);

        // 给标记添加弹窗
        markerInstance.bindPopup("<strong>当前位置</strong><br>北京市东城区（虚拟）").openPopup();

        setMap(mapInstance);
        setMarker(markerInstance);
        setCircle(circleInstance);
      }
    };

    // 动态加载 Leaflet
    if (typeof window !== 'undefined' && !window.L) {
      const script = document.createElement('script');
      script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
      script.integrity = 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';
      script.crossOrigin = '';
      script.onload = initMap;
      document.head.appendChild(script);
    } else {
      initMap();
    }

    // 清理函数
    return () => {
      if (map) {
        map.remove();
      }
    };
  }, []);

  // 时间更新定时器
  useEffect(() => {
    updateTimeDisplay();
    const timer = setInterval(updateTimeDisplay, 1000);
    return () => clearInterval(timer);
  }, []);

  // 居中地图
  const centerMap = () => {
    if (map && marker) {
      map.setView([lat, lng], 14);
      marker.openPopup();
    }
  };

  // 刷新位置
  const refreshLocation = () => {
    setIsLoading(true);
    
    // 模拟位置更新过程
    setTimeout(() => {
      const smallOffset = (Math.random() - 0.5) * 0.01; // 小偏移模拟位置变化
      if (marker && circle) {
        marker.setLatLng([lat + smallOffset, lng + smallOffset]);
        circle.setLatLng([lat + smallOffset, lng + smallOffset]);
      }
      updateTimeDisplay();
      setIsLoading(false);
    }, 1500);
  };

  return (
    <>
      <Head>
        <title>定位信息页面</title>
        <link 
          rel="stylesheet" 
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" 
        />
        <link 
          rel="stylesheet" 
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" 
          crossOrigin=""
        />
      </Head>

      <div className="container">
        <div className="map-card">
          <div className="card-header">
            <h2>
              <i className="fas fa-map-marker-alt"></i> 实时位置信息
            </h2>
            <div className="time-display">{headerTime}</div>
          </div>
          
          <div className="card-body">
            <div className="map-controls">
              <button className="btn" onClick={centerMap}>
                <i className="fas fa-crosshairs"></i> 居中地图
              </button>
              <button className="btn btn-secondary" onClick={refreshLocation}>
                {isLoading && (
                  <span className="loading-indicator"></span>
                )}
                <i className="fas fa-sync-alt"></i> 刷新位置
              </button>
            </div>
            
            <div ref={mapRef} id="map"></div>
            
            <div className="info-container">
              <div className="info-item">
                <h3>
                  <i className="fas fa-location-dot"></i> 当前位置
                </h3>
                <div className="info-value">北京市东城区（虚拟）</div>
              </div>
              
              <div className="info-item">
                <h3>
                  <i className="fas fa-globe"></i> 经纬度
                </h3>
                <div className="info-value">
                  <div className="coordinate-badge">
                    <i className="fas fa-map-pin"></i>&nbsp;
                    <span>纬度 39.9042°, 经度 116.4074°</span>
                  </div>
                </div>
              </div>
              
              <div className="info-item">
                <h3>
                  <i className="fas fa-history"></i> 定位更新时间
                </h3>
                <div className="info-value">{updateTime}</div>
              </div>
            </div>
          </div>
        </div>

        <style jsx>{`
          .container {
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
          }

          .map-card {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            width: 92%;
            max-width: 800px;
            color: #1e293b;
            overflow: hidden;
          }

          .card-header {
            background: #0ea5e9;
            color: white;
            padding: 16px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
          }

          .card-header h2 {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
          }

          .card-body {
            padding: 24px;
          }

          #map {
            height: 400px;
            width: 100%;
            border-radius: 12px;
            margin-bottom: 24px;
            border: 1px solid rgba(0, 0, 0, 0.1);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
          }

          .info-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
          }

          .info-item {
            background: rgba(255, 255, 255, 0.5);
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
          }

          .info-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
          }

          .info-item h3 {
            margin: 0 0 10px 0;
            font-size: 1rem;
            color: #0ea5e9;
            display: flex;
            align-items: center;
            gap: 8px;
          }

          .info-value {
            font-size: 1.1rem;
            font-weight: 500;
          }

          .map-controls {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-bottom: 16px;
          }

          .btn {
            background: #0ea5e9;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 0.9rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: background 0.3s ease;
          }

          .btn:hover {
            background: #0284c7;
          }

          .btn-secondary {
            background: #06b6d4;
          }

          .btn-secondary:hover {
            background: #ea580c;
          }

          .loading-indicator {
            display: inline-block;
            width: 15px;
            height: 15px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
            margin-right: 8px;
          }

          @keyframes spin {
            to { transform: rotate(360deg); }
          }

          .coordinate-badge {
            display: inline-flex;
            align-items: center;
            background: rgba(14, 165, 233, 0.1);
            padding: 6px 12px;
            border-radius: 50px;
            font-family: monospace;
            font-size: 0.95rem;
            color: #0284c7;
            margin-top: 5px;
          }

          /* 暗黑主题支持 */
          @media (prefers-color-scheme: dark) {
            .map-card {
              background: rgba(30, 41, 59, 0.85);
              color: #f1f5f9;
            }

            .info-item {
              background: rgba(30, 41, 59, 0.5);
            }

            .coordinate-badge {
              background: rgba(14, 165, 233, 0.2);
              color: #7dd3fc;
            }
          }

          /* 响应式调整 */
          @media (max-width: 768px) {
            .map-card {
              width: 95%;
            }
            
            .card-header h2 {
              font-size: 1.2rem;
            }
            
            #map {
              height: 300px;
            }
            
            .info-container {
              grid-template-columns: 1fr;
            }
          }
        `}</style>
      </div>
    </>
  );
};

export default LocationInfo;