package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"github.com/chromedp/cdproto/network"
	"github.com/chromedp/chromedp"
	"github.com/google/uuid"
	"golang.org/x/net/html"
	"io"
	"net/http"
	"net/http/cookiejar"
	"net/url"
	"strings"
	"time"
)

// GetOrSetSXUID 会在 Cookie 中查找 sxuid，如果没有就生成一个新的 UUID 并写入
func GetOrSetSXUID(client *http.Client, url string) string {
	u, err := http.NewRequest("GET", url, nil)
	if err != nil {
		panic(err)
	}

	// 先检查 Cookie 里有没有 sxuid
	cookies := client.Jar.Cookies(u.URL)
	for _, c := range cookies {
		if c.Name == "sxuid" && c.Value != "" {
			return c.Value
		}
	}

	// 没有就生成一个新的 UUID
	newUUID := uuid.New().String()
	newCookie := &http.Cookie{
		Name:     "sxuid",
		Value:    newUUID,
		Path:     "/",
		MaxAge:   60 * 60 * 24 * 365 * 30, // 30 年
		Expires:  time.Now().AddDate(30, 0, 0),
		HttpOnly: false,
	}
	client.Jar.SetCookies(u.URL, []*http.Cookie{newCookie})

	return newUUID
}

func main() {

	u1 := "https://buy.simplex.com/"

	// 创建 Cookie Jar（自动管理 Cookie）
	jar, err := cookiejar.New(nil)
	if err != nil {
		panic(err)
	}
	client := &http.Client{Jar: jar,
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			// 阻止自动跳转，返回 http.ErrUseLastResponse 保持原始响应
			if len(via) >= 1 {
				return http.ErrUseLastResponse
			}
			return nil
		}}

	// 确保 sxuid 存在

	// 构造请求
	req, err := http.NewRequest("GET", u1, nil)
	if err != nil {
		panic(err)
	}

	// 设置请求头（模拟 curl）
	req.Header.Set("accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7")
	req.Header.Set("accept-language", "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6")
	req.Header.Set("cache-control", "max-age=0")
	req.Header.Set("priority", "u=0, i")
	req.Header.Set("sec-ch-ua", `"Chromium";v="140", "Not=A?Brand";v="24", "Microsoft Edge";v="140"`)
	req.Header.Set("sec-ch-ua-arch", `"x86"`)
	req.Header.Set("sec-ch-ua-bitness", `"64"`)
	req.Header.Set("sec-ch-ua-full-version", `"140.0.3485.81"`)
	req.Header.Set("sec-ch-ua-full-version-list", `"Chromium";v="140.0.7339.186", "Not=A?Brand";v="24.0.0.0", "Microsoft Edge";v="140.0.3485.81"`)
	req.Header.Set("sec-ch-ua-mobile", "?0")
	req.Header.Set("sec-ch-ua-model", `""`)
	req.Header.Set("sec-ch-ua-platform", `"Windows"`)
	req.Header.Set("sec-ch-ua-platform-version", `"15.0.0"`)
	req.Header.Set("sec-fetch-dest", "document")
	req.Header.Set("sec-fetch-mode", "navigate")
	req.Header.Set("sec-fetch-site", "none")
	req.Header.Set("sec-fetch-user", "?1")
	req.Header.Set("upgrade-insecure-requests", "1")
	req.Header.Set("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0")

	// 发送请求
	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	//body, _ := io.ReadAll(resp.Body)
	fmt.Println("Status:", resp.Status)
	fmt.Println("Cookies after request:", client.Jar.Cookies(req.URL))
	sxuid := GetOrSetSXUID(client, u1)
	fmt.Println("Current sxuid:", sxuid)
	u1 = "https://iframe.simplex-affiliates.com/form?uid=" + sxuid
	fmt.Println(u1)
	method := "GET"
	req2, err := http.NewRequest(method, u1, nil)
	req2.Header.Add("accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7")
	req2.Header.Add("accept-language", "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6")
	req2.Header.Add("priority", "u=0, i")
	req2.Header.Add("referer", "https://buy.simplex.com/")
	req2.Header.Add("sec-ch-ua", "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Microsoft Edge\";v=\"140\"")
	req2.Header.Add("sec-ch-ua-mobile", "?0")
	req2.Header.Add("sec-ch-ua-platform", "\"Windows\"")
	req2.Header.Add("sec-fetch-dest", "iframe")
	req2.Header.Add("sec-fetch-mode", "navigate")
	req2.Header.Add("sec-fetch-site", "cross-site")
	req2.Header.Add("sec-fetch-storage-access", "active")
	req2.Header.Add("upgrade-insecure-requests", "1")
	req2.Header.Add("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0")
	res, err := client.Do(req2)
	fmt.Println(res.Status)
	fmt.Println("Cookies after request:", client.Jar.Cookies(req2.URL))

	apiQuoteURL := "https://iframe.simplex-affiliates.com/api/quote"
	method = "POST"

	payload := strings.NewReader(`{"source_amount":300,"source_currency":"USD","target_currency":"USDT-TRC20","uid":"` + sxuid + `","abTests":{},"hostname":"https://buy.simplex.com/"}`)
	req3, err := http.NewRequest(method, apiQuoteURL, payload)
	req3.Header.Add("accept", "application/json, text/plain, */*")
	req3.Header.Add("accept-language", "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6")
	req3.Header.Add("content-type", "application/json")
	//req3.Header.Add("Cookie", "uaid=Yhje0BldrM9%2B6dSZCaflgc7W1gcVx8XC1bzg6wRgv1zYg6szrDvL0FWLw5ERnjvtV32QvN7RcEq4K3TU64QG%2BwYMTr2SP8EVk%2F2kMY59IUJfzXexWCEp7ccXd31AQbPu1LH8Qf%2FPYTmDRynkUAlGcUM5%2BD7UBUZIxDdGilUz9AI%3D; connect.sid=s%3AlVlL1rwcXW6J2rfvi4jQ7O85073MgwSq.koZJYxBdZler4ft3s7yOFJzMMJnfxmiXq%2FHzjtFwpMM; connect.sid=s%3AOEzZ_cfJhwP394MtzY2umIbFXisAUCKV.cO%2Bo4B3KNBDls7ZTU4jI8XJBkZ569oegAysZuDPsnr4; uaid=GhnukTEGjBYA5LpFRmz8a1bxl1pT0WzA026Sw6qNSvKsSDp6JZ7u8D%2BjQp64BZMTfKhPjTk%2BORaFEQwV%2FjlIRrpX7R9MWpHWUDJs1Bfw3ZwFxMcE%2BY6iqlYSdWnanx7pgLA%2FPsFtaFKsbH%2FU3684VTtRocWZFWE%2By9LlwIcMIhs%3D; uid=475371d2-5909-4e3f-b71e-1bd9f57f5376")
	uQuote, _ := url.Parse(apiQuoteURL)
	client.Jar.SetCookies(uQuote, append(client.Jar.Cookies(uQuote), &http.Cookie{
		Name:  "uid",
		Value: sxuid,
		Path:  "/",
	}))
	res1, err := client.Do(req3)
	if err != nil {
		fmt.Println(err)
	}
	fmt.Println("Cookies after request:", client.Jar.Cookies(req3.URL))
	fmt.Println(res1.Status)
	body, err := io.ReadAll(res1.Body)
	if err != nil {
		fmt.Println(err)
		return
	}
	var quoteResp QuoteResponse
	json.Unmarshal(body, &quoteResp)
	apiPaymentURL := "https://iframe.simplex-affiliates.com/api/payment"
	paymentPayload := PaymentPayload{
		WalletAddress:     "T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb",
		WalletAddressTag:  "",
		LastQuoteResponse: quoteResp,
		Recaptcha:         "",
		AbTests:           map[string]interface{}{},
		Hostname:          "https://buy.simplex.com/",
	}
	paymentBytes, _ := json.Marshal(paymentPayload)
	req4, _ := http.NewRequest("POST", apiPaymentURL, bytes.NewReader(paymentBytes))
	req4.Header.Set("content-type", "application/json")
	req4.Header.Set("user-agent", "Mozilla/5.0 ...")

	resp4, _ := client.Do(req4)
	defer resp4.Body.Close()
	body4, _ := io.ReadAll(resp4.Body)
	var payResp paymentResp
	json.Unmarshal(body4, &payResp)
	fmt.Println("Step 4 Status:", resp4.Status)
	fmt.Println("Step 4 Response:", string(body4))

	formData, formAction, err := parseFormHTML(string(body4))
	fmt.Println(formData)
	fmt.Println(formAction)
	req6, _ := http.NewRequest("POST", formAction, strings.NewReader(formData.Encode()))
	req6.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req6.Header.Set("User-Agent", "Mozilla/5.0 (Go-http-client)")

	resp3, err := client.Do(req6)
	if err != nil {
		panic(err)
	}
	defer resp3.Body.Close()
	if resp3.StatusCode == http.StatusSeeOther {
		redirectURL := resp3.Header.Get("Location")
		fmt.Println("Step3 redirect to:", redirectURL)
		fmt.Println(resp3.Header.Get("Set-Cookie"))
		//req4, _ := http.NewRequest("GET", redirectURL, nil)
		//resp4, err := client.Do(req4)
		//if err != nil {
		//	panic(err)
		//}
		//defer resp4.Body.Close()
		//
		//body4, _ := io.ReadAll(resp4.Body)
		fmt.Println("Final HTML:", string(body4))
	}

	redirectURL := resp3.Header.Get("Location")
	fmt.Println("Step3 /payments/new 状态:", resp3.Status)
	fmt.Println("Step3 redirect to:", redirectURL)
	fmt.Println(resp3.Header.Get("Set-Cookie"))
	opts := append(chromedp.DefaultExecAllocatorOptions[:],
		chromedp.Flag("headless", false), // 可视化浏览器
	)
	allocCtx, cancel := chromedp.NewExecAllocator(context.Background(), opts...)
	defer cancel()
	ctx, cancel := chromedp.NewContext(allocCtx)
	defer cancel()
	_ = chromedp.Run(ctx, network.Enable())

	for _, c := range client.Jar.Cookies(req6.URL) {
		_ = chromedp.Run(ctx, network.SetCookie(c.Name, c.Value).
			WithDomain("https://checkout.simplexcc.com").
			WithPath(c.Path))
	}
	redirectLocation := "https://checkout.simplexcc.com" + redirectURL
	fmt.Println(client.Jar.Cookies(req6.URL)[0].Domain)
	fmt.Println("Cookies after request:", client.Jar.Cookies(req6.URL))
	//Step7: 打开支付表单页面
	err = chromedp.Run(ctx,
		chromedp.Navigate(redirectLocation),
	)
	if err != nil {
		fmt.Println(err)
		return
	}

	fmt.Println("浏览器已打开，用户可以手动提交支付表单")
	time.Sleep(120 * time.Second) // 保留页面
	//body6, _ := io.ReadAll(resp3.Body)
	//fmt.Println("Step3 /payments/new body", string(body6))
	//fmt.Println("Step3 /payments/new 状态:", resp3.Status)
}

type QuoteResponse struct {
	UserId       string `json:"user_id"`
	QuoteId      string `json:"quote_id"`
	DigitalMoney struct {
		Currency string  `json:"currency"`
		Amount   float64 `json:"amount"`
	} `json:"digital_money"`
	FiatMoney struct {
		Currency    string  `json:"currency"`
		BaseAmount  float64 `json:"base_amount"`
		TotalAmount int     `json:"total_amount"`
		Amount      int     `json:"amount"`
	} `json:"fiat_money"`
	SupportedDigitalCurrencies []string `json:"supported_digital_currencies"`
	SupportedFiatCurrencies    []string `json:"supported_fiat_currencies"`
	Fees                       struct {
		PartnerFee struct {
			Currency string `json:"currency"`
			Amount   string `json:"amount"`
		} `json:"partner_fee"`
		PaymentFee struct {
			Currency string `json:"currency"`
			Amount   string `json:"amount"`
		} `json:"payment_fee"`
		BlockchainFee struct {
			Currency string `json:"currency"`
			Amount   string `json:"amount"`
		} `json:"blockchain_fee"`
	} `json:"fees"`
	TxnAmountLimits struct {
		Fiat struct {
			Currency      string `json:"currency"`
			MinimumAmount string `json:"minimumAmount"`
			MaximumAmount string `json:"maximumAmount"`
		} `json:"fiat"`
		Crypto struct {
			Currency      string `json:"currency"`
			MinimumAmount string `json:"minimumAmount"`
			MaximumAmount string `json:"maximumAmount"`
		} `json:"crypto"`
	} `json:"txn_amount_limits"`
}
type PaymentPayload struct {
	WalletAddress     string        `json:"walletaddress"`
	WalletAddressTag  string        `json:"walletaddresstag"`
	LastQuoteResponse QuoteResponse `json:"last_quote_response"`
	Recaptcha         string        `json:"g-recaptcha-response"`
	AbTests           interface{}   `json:"abTests"`
	Hostname          string        `json:"hostname"`
}

func parseFormHTML(htmlStr string) (url.Values, string, error) {
	doc, err := html.Parse(strings.NewReader(htmlStr))
	if err != nil {
		return nil, "", err
	}
	formData := url.Values{}
	var formAction string

	var f func(*html.Node)
	f = func(n *html.Node) {
		if n.Type == html.ElementNode && n.Data == "form" {
			for _, attr := range n.Attr {
				if attr.Key == "action" {
					formAction = attr.Val
				}
			}
		}
		if n.Type == html.ElementNode && n.Data == "input" {
			var name, value string
			for _, attr := range n.Attr {
				if attr.Key == "name" {
					name = attr.Val
				}
				if attr.Key == "value" {
					value = attr.Val
				}
			}
			if name != "" {
				formData.Set(name, value)
			}
		}
		for c := n.FirstChild; c != nil; c = c.NextSibling {
			f(c)
		}
	}
	f(doc)
	return formData, formAction, nil
}

type paymentResp struct {
	IsAddressValid bool   `json:"isAddressValid"`
	IsTagValid     bool   `json:"isTagValid"`
	Form           string `json:"form"`
	PaymentId      string `json:"paymentId"`
}
