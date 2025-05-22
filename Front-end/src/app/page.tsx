'use client';

import React, { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import styles from './MainMenu.module.css';

interface GridItem {
  id: string;
  title: string;
  icon: string;
  color: string;
}

interface StatusButton {
  id: string;
  message: string;
  icon: string;
  label: string;
}

const gridItems: GridItem[] = [
  { id: 'location', title: '定位', icon: 'ri-map-pin-line', color: '#0ea5e9' },
  { id: 'footprint', title: '足迹', icon: 'ri-footprint-line', color: '#f97316' },
  { id: 'phone', title: '电话', icon: 'ri-phone-line', color: '#1d4ed8' },
  { id: 'weather', title: '天气', icon: 'ri-cloudy-line', color: '#10b981' },
  { id: 'message', title: '消息', icon: 'ri-message-3-line', color: '#6366f1' },
  { id: 'history', title: '历史', icon: 'ri-time-line', color: '#6b7280' },
  { id: 'status', title: '状态', icon: 'ri-bar-chart-2-line', color: '#16a34a' },
  { id: 'monitor', title: '监测', icon: 'ri-navigation-line', color: '#8b5cf6' },
  { id: 'version', title: '版本', icon: 'ri-information-line', color: '#f43f5e' },
];

const statusButtons: StatusButton[] = [
  { id: 'settings', message: '打开设置面板', icon: 'ri-settings-3-line', label: '设置' },
  { id: 'battery', message: '电量: 85%', icon: 'ri-battery-2-charge-line', label: '电量' },
  { id: 'user', message: '用户: 张三', icon: 'ri-user-3-line', label: '用户' },
];

const HomePage: React.FC = () => {
  const router = useRouter();
  const gridRef = useRef<HTMLDivElement>(null);
  const notificationRef = useRef<HTMLDivElement>(null);
  const touchStartX = useRef<number>(0);
  const touchEndX = useRef<number>(0);

  const showNotification = (message: string) => {
    if (notificationRef.current) {
      notificationRef.current.textContent = message;
      notificationRef.current.style.top = '20px';
      
      setTimeout(() => {
        if (notificationRef.current) {
          notificationRef.current.style.top = '-100px';
        }
      }, 2000);
    }
  };

  const handleGridItemClick = (item: GridItem, element: HTMLElement) => {
    showNotification(`正在进入: ${item.title}`);
    
    // 点击动画
    gsap.to(element, {
      scale: 0.95,
      duration: 0.1,
      onComplete: () => {
        gsap.to(element, {
          scale: 1,
          duration: 0.3,
          ease: 'back.out(1.5)',
          onComplete: () => {
            // 动画完成后导航到对应页面
            router.push(`/${item.id}`);
          }
        });
      }
    });
  };

  const handleStatusButtonClick = (button: StatusButton) => {
    showNotification(button.message);
  };

  const handleTouchStart = (e: TouchEvent) => {
    touchStartX.current = e.changedTouches[0].screenX;
  };

  const handleTouchEnd = (e: TouchEvent) => {
    touchEndX.current = e.changedTouches[0].screenX;
    handleSwipe();
  };

  const handleSwipe = () => {
    const swipeDistance = touchEndX.current - touchStartX.current;
    
    if (swipeDistance > 100) {
      showNotification('向右滑动：返回上一页');
    } else if (swipeDistance < -100) {
      showNotification('向左滑动：前往下一页');
    }
  };

  useEffect(() => {
    // 页面加载动画
    if (gridRef.current) {
      const gridItems = gridRef.current.querySelectorAll(`.${styles.gridItem}`);
      gsap.from(gridItems, {
        duration: 0.5,
        y: 50,
        opacity: 0,
        stagger: 0.05,
        ease: 'back.out(1.7)',
        delay: 0.8
      });
    }

    // 动态背景效果
    const colors = [
      'rgba(147, 51, 234, 0.05)',
      'rgba(59, 130, 246, 0.05)',
      'rgba(16, 185, 129, 0.05)',
      'rgba(249, 115, 22, 0.05)'
    ];
    
    let colorIndex = 0;
    
    const changeBackground = () => {
      document.body.style.backgroundColor = colors[colorIndex];
      colorIndex = (colorIndex + 1) % colors.length;
    };
    
    const backgroundInterval = setInterval(changeBackground, 10000);

    // 添加触摸事件监听器
    document.addEventListener('touchstart', handleTouchStart);
    document.addEventListener('touchend', handleTouchEnd);

    // 清理函数
    return () => {
      clearInterval(backgroundInterval);
      document.removeEventListener('touchstart', handleTouchStart);
      document.removeEventListener('touchend', handleTouchEnd);
    };
  }, []);

  return (
    <div className={styles.container}>
      {/* 顶部标题 */}
      <div className={`${styles.header} animate__animated animate__fadeIn`}>
        <div className={`${styles.logo} animate__animated animate__bounceIn animate__delay-1s`}>
          <i className="ri-eye-line"></i>
        </div>
        <h1 className={styles.title}>慧感行</h1>
        <p className={styles.subtitle}>让我做你的眼</p>
      </div>

      {/* 顶部状态按钮 */}
      <div className={`${styles.topButtons} animate__animated animate__fadeInUp animate__delay-1s`}>
        {statusButtons.map((button) => (
          <button
            key={button.id}
            className={`${styles.topBtn} hover-float`}
            onClick={() => handleStatusButtonClick(button)}
          >
            <i className={button.icon}></i> {button.label}
          </button>
        ))}
      </div>

      {/* 九宫格导航 - 使用Link组件实现页面导航 */}
      <div className={`${styles.grid} animate__animated animate__fadeIn animate__delay-1s`} ref={gridRef}>
        {gridItems.map((item) => (
          <Link
            href={`/${item.id}`}
            key={item.id}
            className={styles.gridItem}
            style={{ color: item.color, textDecoration: 'none', display: 'block' }}
            onClick={(e) => {
              e.preventDefault(); // 阻止默认跳转，先执行动画
              handleGridItemClick(item, e.currentTarget as HTMLElement);
            }}
          >
            <i className={item.icon}></i>
            <div className={styles.label}>{item.title}</div>
          </Link>
        ))}
      </div>

      <div className={styles.footer}>
        慧感行 &copy; 2025 版权所有
      </div>

      {/* 通知组件 */}
      <div className="notification" ref={notificationRef}></div>
    </div>
  );
};

export default HomePage;