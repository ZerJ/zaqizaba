package main

import (
	"context"
	"fmt"
	"github.com/chromedp/cdproto/network"
	"github.com/chromedp/chromedp"
	"log"
	"regexp"
	"strings"
	"time"
)

// 38T34157488755
func main() {
	fmt.Println("所有配送方式信息：")
	// 🔧 修改为你的代理地址（如 http://127.0.0.1:7890）
	proxy := "http://127.0.0.1:7890"

	// 启动参数
	opts := append(chromedp.DefaultExecAllocatorOptions[:],
		chromedp.Flag("headless", true),        // 可视化
		chromedp.Flag("start-maximized", true), // 启动最大化
		chromedp.Flag("disable-infobars", true),
		chromedp.ProxyServer(proxy),                 // ✅ 使用代理
		chromedp.Flag("disable-web-security", true), // 绕过 CORS
		chromedp.Flag("disable-site-isolation-trials", true),
		chromedp.Flag("auto-open-devtools-for-tabs", true), // ✅ 自动打开 DevTools
	)

	allocCtx, cancel := chromedp.NewExecAllocator(context.Background(), opts...)
	defer cancel()
	ctx, cancel := chromedp.NewContext(allocCtx)
	defer cancel()

	// 启用 network
	if err := chromedp.Run(ctx, network.Enable()); err != nil {
		log.Fatal(err)
	}

	// 用于传递捕获到的 Cookie
	mcChan := make(chan string, 1)

	// === 监听响应头 ===
	chromedp.ListenTarget(ctx, func(ev interface{}) {
		if info, ok := ev.(*network.EventResponseReceivedExtraInfo); ok {
			if sc, ok := info.Headers["set-cookie"]; ok {
				if strings.Contains(sc.(string), "mc=") {
					re := regexp.MustCompile(`mc=([^;]+)`)
					if match := re.FindStringSubmatch(sc.(string)); len(match) > 1 {
						value := match[1]
						fmt.Println("🎯 捕获到 mc =", value)
						mcChan <- value
					}
				}
			}
		}
	})

	url := `https://ticket.globalinterpark.com/Global/Play/Gate/CBTLoginGate.asp?k=hqp%2FGBg%2BJmZ3%2FcLfernFNw%3D%3D&r=https%3A%2F%2Ftickets.interpark.com%2Fwaiting%3Fkey%3D1LfF8KdMI0jqXlBoa8JKpFpwuprBHnOKJQ5R1o7gVXS%252BRIqKyTuCDRVhDhq67xbvC%252FtIE4ypSGUeret7H1gsfGbE97heEIwzXe7SvWjZQO%252FkcZuTrsYroM4fL5vDjXPNozKgbYodvVMSAOPc1QfNpyLRVWxLas%252FtSojLTaX8x%252BB07mYqUq0drEAu0vGqtcGpL9gpVvt%252F45DMqz%252FIxE9V0hkS98egKrlnl92%252F8sP2u8H98O9UhQZHYTD3qjkIPZYN7DoEuJhamdxUc4i5LNAvHETg1OyrFYz%252FZ5m9Q2vwcXAD2TpGHrUi37S0Hv86USYmwU0XNtxXlEjJ1zMpnJlzbBvteGASX2gECDekfjiBfKoylVls3aAoCR%252BD8TXk1Ets9oxg3nHMC%252FN9Wry%252Fu8U5WVQZ0OlLKvulfyqwGc4twjrsAnChHRnam4KOdyeZ%252BCT9e4YJ5DJKbtnrEQ6MMCxon%252BCLpAUmPc9UqCcFysuUCosQuJdsnxUZk2YqoDw0tnBkg19W5%252Be2eBR%252F3QYNBSUZ4w%253D%253D%26lang%3Dzh&lng=zh`

	// 在独立 goroutine 中打开网页
	go func() {
		err := chromedp.Run(ctx,
			chromedp.Navigate(url),
			chromedp.WaitReady("body", chromedp.ByQuery),
			chromedp.Sleep(30*time.Second), // 等页面加载完 cookie
		)
		if err != nil {
			log.Println("页面加载错误:", err)
		}
	}()

	select {
	case mc := <-mcChan:
		fmt.Println("✅ 成功捕获 mc:", mc)
		fmt.Println("⏹ 程序即将退出。")
	case <-time.After(90 * time.Second):
		fmt.Println("❌ 超时未获取到 mc Cookie")
	}

	cancel()
}
