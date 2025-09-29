package main

import (
	"bufio"
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"github.com/chromedp/cdproto/network"
	"github.com/chromedp/chromedp"
	"io"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"
)

func estimateChangelly(from, to, amountFrom, deviceID, clientID string) {
	u := "https://web-bff.changelly.com/v1/f2c/estimate"

	payload := fmt.Sprintf(`{
		"from":"%s",
		"to":"%s",
		"amountFrom":"%s",
		"source":"web",
		"user":{"clientId":"%s"},
		"metadata":{
			"isSsr":false,
			"deviceId":"%s",
			"deviceInfo":{
				"userAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
				"language":"zh-CN",
				"platform":"Win32"
			}
		}
	}`, from, to, amountFrom, clientID, deviceID)

	client := &http.Client{}
	req, err := http.NewRequest("post", u, strings.NewReader(payload))

	if err != nil {
		fmt.Println(err)

	}
	req.Header.Add("accept", "*/*")
	req.Header.Add("accept-language", "zh-CN,zh;q=0.9")
	req.Header.Add("cache-control", "no-cache")
	req.Header.Add("content-type", "application/json")
	req.Header.Add("origin", "https://changelly.com")
	req.Header.Add("pragma", "no-cache")
	req.Header.Add("priority", "u=1, i")
	req.Header.Add("referer", "https://changelly.com/")
	req.Header.Add("sec-ch-ua", "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"")
	req.Header.Add("sec-ch-ua-mobile", "?0")
	req.Header.Add("sec-ch-ua-platform", "\"Windows\"")
	req.Header.Add("sec-fetch-dest", "empty")
	req.Header.Add("sec-fetch-mode", "cors")
	req.Header.Add("sec-fetch-site", "same-site")
	req.Header.Add("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
	req.Header.Add("x-analytics-id", "SIffqqkwjBLSfLkS")
	req.Header.Add("x-cache-id", "HIT =0=1w2U3r4x5k6Z7T8x9k0Q1q2d334a5x6F7n8Z9m0l102U3")
	req.Header.Add("x-device-id", "f6777e4a-0b0a-4ef3-b694-f9341519478c")
	req.Header.Add("x-source-id", "web")
	req.Header.Add("Cookie", "ipcountry=SG; device_id=f6777e4a-0b0a-4ef3-b694-f9341519478c; SmartRouting3_1_ABvariant=default; ExtraBonusWithApp_ABvariant=default; BuyTransactionWidget_ABvariant=default; landing_page_path=/buy-crypto; cf_clearance=lG.XBiaJPfPj21lINjl5UtcxnPusH1wR90jIOuGrM1E-1758780934-1.2.1.1-56YeZdWIPNShZv4i.5mCOp2IY976eG5uUdr.Bom4gp2lyvvwGd9sCOolPStEL2FnqSc_I.mty84qnGkSu_G_yaaqX_0kyrhV0TiNQFiBZXaNUyMTpOIn3XJXKS0Ve98jBhUi2ToIcq6rYR9CSHj_u4svoQrBcGOPV6CZclw.uPVioHz.KgeuUsPjHWnkHGmvc9uYMH5sokB9rfkErlRQRr0glZubrs7ZyN3f0tHYqXI; _ga=GA1.1.1758780934.8030201691356; _hjSessionUser_2540120=eyJpZCI6ImU4ZGM5MjMwLWJkMTEtNTMyNS05N2RlLWJmOTdjNmMxMWNhYSIsImNyZWF0ZWQiOjE3NTg3ODA5NDAwODMsImV4aXN0aW5nIjpmYWxzZX0=; _hjSession_2540120=eyJpZCI6ImUyMTUyZGE4LTg5MGQtNDJmZi1iZmQ0LWMyMGY5Mzc0NGYzYiIsImMiOjE3NTg3ODA5NDAwODQsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MX0=; banner-mobile-app=disable; last_transaction_params={%22c2c%22:{%22from%22:%22%22%2C%22to%22:%22%22%2C%22amount%22:%22%22}%2C%22f2c%22:{%22from%22:%22sgd%22%2C%22to%22:%22btc%22%2C%22amount%22:%22700%22}%2C%22c2f%22:{%22from%22:%22%22%2C%22to%22:%22%22%2C%22amount%22:%22%22}}; _ga_43VWC8E6KH=GS1.1.1758780935.1.1.1758780946.0.0.0; last_active_at=2025-09-25T06:15:49.419Z")

	res, err := client.Do(req)
	if err != nil {
		fmt.Println(err)

	}
	defer res.Body.Close()

	body, err := io.ReadAll(res.Body)
	if err != nil {
		fmt.Println(err)

	}
	fmt.Println(string(body))
}

var (
	clients    *http.Client
	clientOnce sync.Once
)

func main() {
	reader := bufio.NewReader(os.Stdin)

	// === 1. 输入 amountFrom ===
	fmt.Print("请输入兑换金额 (amountFrom): ")
	amountInput, _ := reader.ReadString('\n')
	amountInput = strings.TrimSpace(amountInput)

	amountFrom, err := strconv.Atoi(amountInput)
	if err != nil {
		fmt.Println("金额输入错误:", err)
		return
	}
	fmt.Print("请输入钱包地址: ")
	addr, _ := reader.ReadString('\n')
	addr = strings.TrimSpace(addr)
	fmt.Println(addr)
	client := getHttpClient()
	as, _ := fetchAnalytics("https://web-bff.changelly.com/v1/status")
	//addr := "T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb"
	u := "https://web-bff.changelly.com/v1/f2c/estimate"
	method := "POST"
	to := "usdtrx"

	data := map[string]interface{}{
		"from":       "sgd",
		"to":         to,
		"amountFrom": strconv.Itoa(amountFrom), // 👈 注意是字符串
		"source":     "web",
		"user": map[string]string{
			"clientId": "1758699511459.3546787310762",
		},
		"metadata": map[string]interface{}{
			"isSsr":      false,
			"refId":      "",
			"affiseData": nil,
			"deviceId":   "9335c575-fccc-417e-834f-baab00102262",
			"deviceInfo": map[string]interface{}{
				"userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
				"language":  "zh-CN",
				"languages": []string{"zh-CN", "zh"},
				"platform":  "Win32",
				"screenSize": map[string]int{
					"width":  879,
					"height": 1305,
				},
			},
		},
	}

	payloadBytes, _ := json.Marshal(data)
	payload := bytes.NewReader(payloadBytes)
	req, err := http.NewRequest(method, u, payload)

	if err != nil {
		fmt.Println(err)
		return
	}
	req.Header.Add("accept", "*/*")
	req.Header.Add("accept-language", "zh-CN,zh;q=0.9")
	req.Header.Add("cache-control", "no-cache")
	req.Header.Add("content-type", "application/json")
	req.Header.Add("origin", "https://changelly.com")
	req.Header.Add("pragma", "no-cache")
	req.Header.Add("priority", "u=1, i")
	req.Header.Add("referer", "https://changelly.com/")
	req.Header.Add("sec-ch-ua", "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"")
	req.Header.Add("sec-ch-ua-mobile", "?0")
	req.Header.Add("sec-ch-ua-platform", "\"Windows\"")
	req.Header.Add("sec-fetch-dest", "empty")
	req.Header.Add("sec-fetch-mode", "cors")
	req.Header.Add("sec-fetch-site", "same-site")
	req.Header.Add("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
	req.Header.Add("x-device-id", "9335c575-fccc-417e-834f-baab00102262")
	req.Header.Add("x-analytics-id", as["x-analytics-id"])

	req.Header.Add("x-cache-id", as["x-cache-id"])
	req.Header.Add("x-source-id", "web")
	req.Header.Add("Cookie", "ipcountry=SG; device_id=9335c575-fccc-417e-834f-baab00102262; SmartRouting3_1_ABvariant=new; ExtraBonusWithApp_ABvariant=new; BuyTransactionWidget_ABvariant=new; landing_page_path=/buy-crypto; _ga=GA1.1.1758699511459.3546787310762; banner-mobile-app=disable; _hjSession_2540120=eyJpZCI6IjkwZDVhZmM3LWUwZDEtNGJjNi1hZDE0LTMwOTAzOGEwYjUzMyIsImMiOjE3NTg3ODgxMzM5MDgsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MH0=; _hjSessionUser_2540120=eyJpZCI6IjQxYTRkOTZlLTg3OWYtNTMxMC04MjI5LWZkNmY3N2ViZDYzYyIsImNyZWF0ZWQiOjE3NTg3ODgxMzM5MDcsImV4aXN0aW5nIjp0cnVlfQ==; cf_clearance=nJERIhqdkSmaMHElgeNa0trLU_G_fGkvfYFLRAF2j2w-1758789129-1.2.1.1-1k5EtQ77xuM8KU6VPS3t3dJjJ_HqCvwSmKUEmFu4RrWL.CpinSxpQefxNzIMYYoNPjdDoJdoO.tkJc8lGdc2Vt2uyR29KKVGpfldwiNDGN_Tx5jokn0ywoB_aQGhSsGskf.fbnfe4MSUYXb2FX3KrR3kXhCWyvMN9w1JcSUoaDszLd8pf5Ym_ayrVFPpg6_NJc7.SiKq8kEGbIOU6t9wSDp81stEAcSuSHzL0II0qYk; last_active_at=2025-09-25T08:44:31.254Z; last_transaction_params={%22c2c%22:{%22from%22:%22%22%2C%22to%22:%22%22%2C%22amount%22:%22%22}%2C%22f2c%22:{%22from%22:%22sgd%22%2C%22to%22:%22btc%22%2C%22amount%22:%22700%22}%2C%22c2f%22:{%22from%22:%22%22%2C%22to%22:%22%22%2C%22amount%22:%22%22}}; _ga_43VWC8E6KH=GS1.1.1758788129.1.1.1758790104.0.0.0; _ga=GA1.1.1758699511459.3546787310762; _ga_43VWC8E6KH=GS1.1.1758786981.1.1.1758788384.0.0.0")
	res, err := client.Do(req)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer res.Body.Close()

	body, err := io.ReadAll(res.Body)
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Println(string(body))
	var d estimateResp
	err = json.Unmarshal(body, &d)
	if err != nil {
		fmt.Println(string(body))
		fmt.Println(err)
	}

	err = validateAddress(addr, to, as)
	if err != nil {
		fmt.Println(err)
	} else {
		for _, v := range d.Offers {
			if strings.Contains(v.Key, "unlimit") {
				exchange(amountFrom, to, addr, as, v)
			}
		}

	}
}

func a(input string) string {
	// 1. base64 编码
	encoded := base64.StdEncoding.EncodeToString([]byte(input))

	// 2. 反转字符串
	runes := []rune(encoded)
	for i, j := 0, len(runes)-1; i < j; i, j = i+1, j-1 {
		runes[i], runes[j] = runes[j], runes[i]
	}

	// 3. 每个字符拼接上索引个位数
	var builder strings.Builder
	for idx, ch := range runes {
		builder.WriteRune(ch)
		builder.WriteString(fmt.Sprintf("%d", idx%10))
	}
	return builder.String()
}

// 请求接口并处理逻辑
func fetchAnalytics(u string) (amap map[string]string, err error) {

	method := "GET"

	client := getHttpClient()
	req, err := http.NewRequest(method, u, nil)

	if err != nil {
		fmt.Println(err)
		return
	}
	req.Header.Add("accept", "*/*")
	req.Header.Add("accept-language", "zh-CN,zh;q=0.9")
	req.Header.Add("cache-control", "no-cache")
	req.Header.Add("origin", "https://changelly.com")
	req.Header.Add("pragma", "no-cache")
	req.Header.Add("priority", "u=1, i")
	req.Header.Add("referer", "https://changelly.com/")
	req.Header.Add("sec-ch-ua", "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"")
	req.Header.Add("sec-ch-ua-mobile", "?0")
	req.Header.Add("sec-ch-ua-platform", "\"Windows\"")
	req.Header.Add("sec-fetch-dest", "empty")
	req.Header.Add("sec-fetch-mode", "cors")
	req.Header.Add("sec-fetch-site", "same-site")
	req.Header.Add("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
	req.Header.Add("Cookie", "_ga=GA1.1.1758699511459.3546787310762; _ga_43VWC8E6KH=GS1.1.1758786981.1.1.1758788384.0.0.0")

	res, err := client.Do(req)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer res.Body.Close()

	body, err := io.ReadAll(res.Body)
	if err != nil {
		fmt.Println(err)
		return
	}
	var data fetchAnalyticsResp
	if err := json.Unmarshal(body, &data); err != nil {
		return nil, err
	}
	// 调用 a(n)
	r := a(data.AnalyticsId)

	// 拼接返回 map
	result := map[string]string{
		"x-analytics-id": data.AnalyticsId,
		"x-cache-id":     "HIT " + r,
	}

	return result, nil
}
func validateAddress(address, currency string, as map[string]string) (err error) {
	url := "https://web-bff.changelly.com/v1/wallets/validate-address?address=" + address + "&extraId=&currency=" + currency
	method := "GET"

	client := getHttpClient()
	req, err := http.NewRequest(method, url, nil)

	if err != nil {
		fmt.Println(err)
		return
	}
	req.Header.Add("accept", "*/*")
	req.Header.Add("accept-language", "zh-CN,zh;q=0.9")
	req.Header.Add("cache-control", "no-cache")
	req.Header.Add("origin", "https://changelly.com")
	req.Header.Add("pragma", "no-cache")
	req.Header.Add("priority", "u=1, i")
	req.Header.Add("referer", "https://changelly.com/")
	req.Header.Add("sec-ch-ua", "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"")
	req.Header.Add("sec-ch-ua-mobile", "?0")
	req.Header.Add("sec-ch-ua-platform", "\"Windows\"")
	req.Header.Add("sec-fetch-dest", "empty")
	req.Header.Add("sec-fetch-mode", "cors")
	req.Header.Add("sec-fetch-site", "same-site")
	req.Header.Add("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
	req.Header.Add("x-analytics-id", "SIfSfIBLBwjxILkS")
	req.Header.Add("x-analytics-id", as["x-analytics-id"])

	req.Header.Add("x-cache-id", as["x-cache-id"])
	req.Header.Add("x-source-id", "web")
	req.Header.Add("Cookie", "ipcountry=SG; device_id=9335c575-fccc-417e-834f-baab00102262; SmartRouting3_1_ABvariant=new; ExtraBonusWithApp_ABvariant=new; BuyTransactionWidget_ABvariant=new; landing_page_path=/buy-crypto; _ga=GA1.1.1758699511459.3546787310762; banner-mobile-app=disable; _hjSessionUser_2540120=eyJpZCI6IjQxYTRkOTZlLTg3OWYtNTMxMC04MjI5LWZkNmY3N2ViZDYzYyIsImNyZWF0ZWQiOjE3NTg3ODgxMzM5MDcsImV4aXN0aW5nIjp0cnVlfQ==; cf_clearance=8MMpBCxnz_Qr6ATe8BmHMDjWCLJXx0pgReQC8BK4Yww-1758868949-1.2.1.1-BrHW6ed_ChAEM0QWFPTNPwC1jbQzUMR2MceYn28RVQEjU_yrS.eowaPJCo6ATRUVwRKlqn2AWzIF4iAvcTrJHxNSTpHJB122EN7o5fNbpVhAV5bj1CxcXxAwd2n6kmLHtlRbRp6Ofp9vVwYuHl2JGOiBOp1rIo7C8S.DVGzwQeBYRnIH.GRFed2frrl6Jqwhc6kzqkaSLIPxNMIaCa2qlQVqYMxDM0ndfvMckOL.3Xs; _hjSession_2540120=eyJpZCI6IjllNTVmNWRkLTU1NGItNDhmMC1iYzViLWI4MTlkMDFiODk2NiIsImMiOjE3NTg4Njg5NTY1OTIsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MX0=; test_device_id=9335c575-fccc-417e-834f-baab00102262||SEP||1758869088408; last_active_at=2025-09-26T07:10:07.831Z; last_transaction_params={%22c2c%22:{%22from%22:%22%22%2C%22to%22:%22%22%2C%22amount%22:%22%22}%2C%22f2c%22:{%22from%22:%22sgd%22%2C%22to%22:%22usdtrx%22%2C%22amount%22:%22700%22}%2C%22c2f%22:{%22from%22:%22%22%2C%22to%22:%22%22%2C%22amount%22:%22%22}}; _ga_43VWC8E6KH=GS1.1.1758868951.3.1.1758870620.0.0.0; _ga=GA1.1.1758699511459.3546787310762; _ga_43VWC8E6KH=GS1.1.1758786981.1.1.1758788384.0.0.0")

	res, err := client.Do(req)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer res.Body.Close()

	body, err := io.ReadAll(res.Body)
	if err != nil {
		fmt.Println(err)
		return
	}
	var data validateResp
	err = json.Unmarshal(body, &data)
	if err != nil {
		return
	}
	return nil
}
func exchange(amount int, currency string, addr string, as map[string]string, offers Offers) {
	u := "https://web-bff.changelly.com/v1/f2c/exchange"
	method := "POST"

	payload := strings.NewReader(`{"from":"sgd","to":"` + currency + `","amount":"` + strconv.Itoa(amount) + `","outAmount":"` + offers.Amount + `","address":"` + addr + `","extraId":"","paymentMethod":"card","analyticsPayload":{"gaClientId":"1758699511459.3546787310762","refId":"","source":"web","deviceId":"9335c575-fccc-417e-834f-baab00102262","affiseData":null},"provider":"` + offers.Provider.Code + `","offerId":"` + offers.OfferId + `"}`)

	client := getHttpClient()
	req, err := http.NewRequest(method, u, payload)

	if err != nil {
		fmt.Println(err)
		return
	}
	req.Header.Add("accept", "*/*")
	req.Header.Add("accept-language", "zh-CN,zh;q=0.9")
	req.Header.Add("cache-control", "no-cache")
	req.Header.Add("content-type", "application/json")
	req.Header.Add("origin", "https://changelly.com")
	req.Header.Add("pragma", "no-cache")
	req.Header.Add("priority", "u=1, i")
	req.Header.Add("referer", "https://changelly.com/")
	req.Header.Add("sec-ch-ua", "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"")
	req.Header.Add("sec-ch-ua-mobile", "?0")
	req.Header.Add("sec-ch-ua-platform", "\"Windows\"")
	req.Header.Add("sec-fetch-dest", "empty")
	req.Header.Add("sec-fetch-mode", "cors")
	req.Header.Add("sec-fetch-site", "same-site")
	req.Header.Add("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
	req.Header.Add("x-analytics-id", as["x-analytics-id"])
	req.Header.Add("x-cache-id", as["x-cache-id"])
	req.Header.Add("x-device-id", "9335c575-fccc-417e-834f-baab00102262")
	req.Header.Add("x-source-id", "web")
	req.Header.Add("Cookie", "ipcountry=SG; device_id=9335c575-fccc-417e-834f-baab00102262; SmartRouting3_1_ABvariant=new; ExtraBonusWithApp_ABvariant=new; BuyTransactionWidget_ABvariant=new; landing_page_path=/buy-crypto; _ga=GA1.1.1758699511459.3546787310762; banner-mobile-app=disable; _hjSessionUser_2540120=eyJpZCI6IjQxYTRkOTZlLTg3OWYtNTMxMC04MjI5LWZkNmY3N2ViZDYzYyIsImNyZWF0ZWQiOjE3NTg3ODgxMzM5MDcsImV4aXN0aW5nIjp0cnVlfQ==; cf_clearance=8MMpBCxnz_Qr6ATe8BmHMDjWCLJXx0pgReQC8BK4Yww-1758868949-1.2.1.1-BrHW6ed_ChAEM0QWFPTNPwC1jbQzUMR2MceYn28RVQEjU_yrS.eowaPJCo6ATRUVwRKlqn2AWzIF4iAvcTrJHxNSTpHJB122EN7o5fNbpVhAV5bj1CxcXxAwd2n6kmLHtlRbRp6Ofp9vVwYuHl2JGOiBOp1rIo7C8S.DVGzwQeBYRnIH.GRFed2frrl6Jqwhc6kzqkaSLIPxNMIaCa2qlQVqYMxDM0ndfvMckOL.3Xs; _hjSession_2540120=eyJpZCI6IjllNTVmNWRkLTU1NGItNDhmMC1iYzViLWI4MTlkMDFiODk2NiIsImMiOjE3NTg4Njg5NTY1OTIsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MX0=; test_device_id=9335c575-fccc-417e-834f-baab00102262||SEP||1758869088408; last_transaction_params={%22c2c%22:{%22from%22:%22%22%2C%22to%22:%22%22%2C%22amount%22:%22%22}%2C%22f2c%22:{%22from%22:%22sgd%22%2C%22to%22:%22usdtrx%22%2C%22amount%22:%22700%22}%2C%22c2f%22:{%22from%22:%22%22%2C%22to%22:%22%22%2C%22amount%22:%22%22}}; _ga_43VWC8E6KH=GS1.1.1758868951.3.1.1758870622.0.0.0; last_active_at=2025-09-26T07:10:34.393Z; _ga=GA1.1.1758699511459.3546787310762; _ga_43VWC8E6KH=GS1.1.1758786981.1.1.1758788384.0.0.0")

	res, err := client.Do(req)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer res.Body.Close()

	body, err := io.ReadAll(res.Body)
	if err != nil {
		fmt.Println(err)
		return
	}
	fmt.Println(string(body))
	var d exchangeResp
	json.Unmarshal(body, &d)
	opts := append(chromedp.DefaultExecAllocatorOptions[:],
		chromedp.Flag("headless", false), // 可视化浏览器
	)
	allocCtx, cancel := chromedp.NewExecAllocator(context.Background(), opts...)
	defer cancel()
	ctx, cancel := chromedp.NewContext(allocCtx)
	defer cancel()
	_ = chromedp.Run(ctx, network.Enable())

	//Step7: 打开支付表单页面
	err = chromedp.Run(ctx,
		chromedp.Navigate(d.Url),
	)
	if err != nil {
		fmt.Println(err)
		return
	}

	fmt.Println("浏览器已打开，用户可以手动提交支付表单")
	time.Sleep(120 * time.Second) // 保留页面
}

type fetchAnalyticsResp struct {
	ServerMaintenance bool    `json:"serverMaintenance"`
	ServerUptime      float64 `json:"serverUptime"`
	RequestTimeout    int     `json:"requestTimeout"`
	DefaultLocale     string  `json:"defaultLocale"`
	CacheEnabled      bool    `json:"cacheEnabled"`
	MaxConnections    int     `json:"maxConnections"`
	AnalyticsId       string  `json:"analyticsId"`
}
type estimateResp struct {
	EstimationId   string `json:"estimationId"`
	PaymentMethods []struct {
		MethodName string `json:"methodName"`
		Method     string `json:"method"`
	} `json:"paymentMethods"`
	Offers     []Offers  `json:"offers"`
	LastUpdate time.Time `json:"lastUpdate"`
}

type Offers struct {
	Key        string `json:"key,omitempty"`
	Amount     string `json:"amount,omitempty"`
	OfferId    string `json:"offerId,omitempty"`
	Method     string `json:"method,omitempty"`
	MethodName string `json:"methodName,omitempty"`
	Provider   struct {
		Id   int    `json:"id"`
		Code string `json:"code"`
		Name string `json:"name"`
	} `json:"provider"`
	Rate           string `json:"rate,omitempty"`
	BaseRate       string `json:"baseRate,omitempty"`
	AdditionalData struct {
		Fields []interface{} `json:"fields"`
	} `json:"additionalData,omitempty"`
	TransactionDetails []struct {
		Field string `json:"field"`
		Value string `json:"value"`
		Type  string `json:"type"`
	} `json:"transactionDetails"`
	Labels []string `json:"labels"`
	Error  struct {
		Type    string `json:"type"`
		Message string `json:"message"`
		Details struct {
			IsInTickerPresent  bool   `json:"isInTickerPresent,omitempty"`
			IsOutTickerPresent bool   `json:"isOutTickerPresent,omitempty"`
			InTicker           string `json:"inTicker,omitempty"`
			OutTicker          string `json:"outTicker,omitempty"`
			Country            string `json:"country,omitempty"`
		} `json:"details"`
	} `json:"error,omitempty"`
}
type validateResp struct {
	Currency string `json:"currency"`
	Address  string `json:"address"`
	ExtraId  string `json:"extraId"`
}
type exchangeResp struct {
	FaTransactionId string `json:"faTransactionId"`
	TransactionId   string `json:"transactionId"`
	Url             string `json:"url"`
	Type            string `json:"type"`
}

func getHttpClient() *http.Client {
	clientOnce.Do(func() {
		reader := bufio.NewReader(os.Stdin)
		fmt.Print("是否使用代理？(y/n): ")
		useProxyInput, _ := reader.ReadString('\n')
		useProxyInput = strings.TrimSpace(useProxyInput)

		if strings.ToLower(useProxyInput) == "y" {
			fmt.Print("请输入代理地址 (例如 http://127.0.0.1:7890): ")
			proxyAddr, _ := reader.ReadString('\n')
			proxyAddr = strings.TrimSpace(proxyAddr)

			proxyURL, err := url.Parse(proxyAddr)
			if err != nil {
				fmt.Println("代理地址格式错误:", err)
				os.Exit(1)
			}

			transport := &http.Transport{
				Proxy: http.ProxyURL(proxyURL),
			}
			clients = &http.Client{Transport: transport, Timeout: 15 * time.Second}
		} else {
			clients = &http.Client{Timeout: 15 * time.Second}
		}
	})
	return clients
}
