import './globals.css'
import Script from 'next/script'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: '慧感行 - 让我做你的眼',
  description: '智能导航应用',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body>
        <main style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center',
          minHeight: '100vh'
        }}>
          {children}
        </main>
        
        {/* 加载GSAP动画库 */}
        <Script 
          src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.0/gsap.min.js"
          strategy="beforeInteractive"
        />
      </body>
    </html>
  )
}