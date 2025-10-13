package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/base64"
	"encoding/hex"
	"fmt"
	"hash/crc32"
	"io"
	"net/url"
	"reflect"
	"strings"
)

// 自定义结构体，字段顺序必须严格和浏览器一样
type Metrics struct {
	FP2          int `json:"fp2"`
	Browser      int `json:"browser"`
	Capabilities int `json:"capabilities"`
	GPU          int `json:"gpu"`
	DNT          int `json:"dnt"`
	Math         int `json:"math"`
	Screen       int `json:"screen"`
	Navigator    int `json:"navigator"`
	Auto         int `json:"auto"`
	Stealth      int `json:"stealth"`
	Subtle       int `json:"subtle"`
	Canvas       int `json:"canvas"`
	FormDetector int `json:"formdetector"`
	BE           int `json:"be"`
}

//// 生成 checksum
//func generateChecksum(jsonStr string) string {
//	// 计算 CRC32
//	crcTable := crc32.MakeTable(crc32.IEEE)
//	crc := crc32.Checksum([]byte(jsonStr), crcTable)
//
//	// CRC32 转大写 Hex
//	crcHex := strings.ToUpper(fmt.Sprintf("%08x", crc))
//
//	// 拼接最终结果
//	return crcHex + "#" + jsonStr
//}

// 模拟浏览器收集的 metrics 数据结构
type MetricsData struct {
	Metrics struct {
		FP2          int `json:"fp2"`
		Browser      int `json:"browser"`
		Capabilities int `json:"capabilities"`
		GPU          int `json:"gpu"`
		DNT          int `json:"dnt"`
		Math         int `json:"math"`
		Screen       int `json:"screen"`
		Navigator    int `json:"navigator"`
		Auto         int `json:"auto"`
		Stealth      int `json:"stealth"`
		Subtle       int `json:"subtle"`
		Canvas       int `json:"canvas"`
		FormDetector int `json:"formdetector"`
		BE           int `json:"be"`
	} `json:"metrics"`
	Start        int64       `json:"start"`
	FlashVersion interface{} `json:"flashVersion"` // null
	Plugins      []struct {
		Name string `json:"name"`
		Str  string `json:"str"`
	} `json:"plugins"`
	DupedPlugins string      `json:"dupedPlugins"`
	ScreenInfo   string      `json:"screenInfo"`
	Referrer     string      `json:"referrer"`
	UserAgent    string      `json:"userAgent"`
	Location     string      `json:"location"`
	WebDriver    bool        `json:"webDriver"`
	Capabilities interface{} `json:"capabilities"`
	GPUInfo      interface{} `json:"gpu"`
	DNTInfo      interface{} `json:"dnt"`
	MathInfo     interface{} `json:"math"`
	Automation   interface{} `json:"automation"`
	StealthInfo  interface{} `json:"stealth"`
	CryptoInfo   interface{} `json:"crypto"`
	CanvasInfo   interface{} `json:"canvas"`
	FormDetected bool        `json:"formDetected"`
	NumForms     int         `json:"numForms"`
	NumFormElem  int         `json:"numFormElements"`
	BEInfo       interface{} `json:"be"`
	End          int64       `json:"end"`
	Errors       []string    `json:"errors"`
	Version      string      `json:"version"`
	ID           string      `json:"id"`
}

var obfuscated = []string{
	"y29UC3rYDwn0B3i", "BgvUz3rO", "AgfZt3DUuhjVCgvYDhK", "y2fSBa", "B2jQzwn0", "zNvUy3rPB24", "DMfSDwu", "BgfIzwW", "Cg9W", "AxrLCMf0B3i", "zxjYB3i", "C2XPy2u", "DgHYB3C", "yxn5BMnjDgvYyxrVCG", "CMvZB2X2zq", "CMv0DxjU", "CMf3", "y3jLyxrL", "zgvMyxvSDa", "yxr0ywnOrxzLBNq", "yNvPBgrdCMnuywjSzq", "suvfrv9qt0XztK9nsufm", "y3jJvgfIBgu", "D2HPy2G", "zwXLBwvUDa", "yNvMzMvY", "v0Hjq0HFufjpuevsveLfuW", "zxzLBNrdEwnSzxm", "ChjVDg90ExbL", "y3jLyxrLrwXLBwvUDa", "C3r5Bgu", "CgfYzw50tM9Kzq", "ihT4lxfZytPLEhbYzxnZAw9UkgrVy3vTzw50lL9XC2eGjIyGzg9JDw1LBNqUx3fZys5WDxnOkhrOAxmPkx0", "ChvZAa", "y3LJBgvcDwzMzxi", "A2v5uhjLC3nLCW", "zgf0yq", "Dg91y2HLCW", "y2HHCKnVzgvbDa", "z2v0", "DxrMoevUy29Kzxi", "AgfZAa", "yxv0B2nVBxbSzxrL", "x19LC01VzhvSzq", "y29SBgvJDerHDge", "x19Nzw5LCMf0B3i", "yxzHAwXizwLNAhq", "BMfTzq", "Bwf0y2G", "A2v5", "y2fWDgnOyunHChrJAge", "x19LEhrLBMrZ", "yxGTCgX1z2LU", "y2HLy2Tby3rPDMvyugX1z2LU", "idOG", "EZG5qJrdmuneluiWmtGTnduXms1cmeeXltu0nZzeqKy3mdGYmh0", "EZq0qKjbodq4lundnteTmtfdrI1bquzbltaWqueWmei2mde1q30", "EZq0qKjbodqWlundnteTmtfdrI1bquzbltaWqueWmei2mde1q30", "yMvOyxzPB3i", "q09nue9oru5uuW", "z2v0q29TCg9Uzw50vMvYC2LVBG", "AxndB21WB25LBNrjBNn0ywXSzwq", "qxjYB3DsAwDODa", "uMLNAhq", "tu9vu0vFtu9wrv9fvKvova", "yMLUzeTLEwjVyxjKsgfUzgXLCG", "DgHYB3r0BgvY", "BgLZDgvUzxi", "ywrKrxzLBNrmAxn0zw5LCG", "C2nYB2XSwq", "zgvSDgfy", "Aw5KzxHpzG", "CgfNzvG", "C3rHCNrfDMvUDa", "C3rHCNq", "z2v0vgLTzq", "zxzLBNrZ", "yw16BJPMD2nPBtPLDMvUDhm", "C3rYAw5N", "yM9KEufcBg9I", "BwfW", "qLvgrKvsx0Tfwq", "CMvTB3zLsxrLBq", "AxrLBq", "zgvYAxzLqML0CW", "zw5JCNLWDa", "C3vWCg9YDhnxzwjdCNLWDg9tDwj0Bgu", "D2vIq3j5ChrVq2fWywjPBgL0AwvZ", "zgv0zwn0twvKAwfuExbLrgLZy3jLCgfUy3K", "zgv0zwn0vgLTzxjfDMfZAw9UCW", "CgvYzM9YBwfUy2u", "BMf2AwDHDgLVBLn0yxj0", "suzsqu1f", "x19HD2fPDgvY", "C2nYAxb0", "B2jMDxnJyxrLrw5JCNLWDa", "y29SBgvJDg9YtMfTzq", "CgvYzG", "q09ou1rbtLq", "C2LU", "y29SBgvJDa", "BgfZDenVBgXLy3rPB24", "z2v0ugfYyw1LDgvY", "zxHWzxjPBwvUDgfSlxDLyMDS", "zM9YBu1LDgHVza", "su5qvvrFu0vmrunut1jt", "Aw5WDxrBDhLWzt0IBNvTzxjPyYjD", "CxvLCNLtzwXLy3rVCKfSBa", "y29Uy2f0", "qxjPywWGr3jLzwS", "vhH0", "qwDLBMn5iezc", "svnpq1qY", "txLYAwfKiefYywjPyW", "rg90Dw0", "vgfOB21H", "v1aGtxvSDgLUyxrPB25HBeeGuM9Tyw4", "rxvYB3n0AwXL", "u3LSzMfLBG", "rMfUz1nVBMC", "qxjUBYbqCM8Gu21IzcbtDwjOzwfK", "sMfZBwLUzvvqqW", "u3DPCZCYmsbcBgTdBIbcva", "r2LKzhL1CcbtDgq", "rg90Dw1dAgu", "q29YyMvS", "sw1WCMLUDcbnvcbtAgfKB3C", "twLJCM9ZB2z0ifvPz2H1CG", "qMvSBcbhB3rOAwmGu3rKieXPz2H0", "vgLTzxmGtMv3ifjVBwfUiejHBhrPyW", "v1aGtxvSDgLUyxrPB25HBeiGuM9Tyw4", "r0ru", "qwXLEgfUzhjHifnJCMLWDa", "uhjVEhKGnq", "u2HVD2nHCMqGr290AgLJ", "u21HBgWGrM9UDhm", "v2LUz2rPBMDZidm", "qwrVyMuGq2fZBg9UifbYBW", "u2vNB2uGvuKGtgLNAhq", "s296DwTHieDVDgHPyYbqCM8GruW", "qxjPywWGqMXHy2S", "twLJCM9ZB2z0ifLPiejHAxrP", "qu1hrfq", "tgfVifvj", "q2XHCMvUzg9UiejSAYbcva", "u3rLBMnPBcbtDgq", "tw9VBejVCMfU", "wLDbzg9Izuy", "vgvRDg9UifbYBW", "uhjVEhKGmW", "u2LTsgvP", "qxjUBYbqCM8Gu21Iza", "Bw1TBw1TBw1TBwXSAq", "tw9UB3nWywm4mJeGqLq", "q1jdx0nbtenvtefut1i", "thvJAwrHiezHEa", "u2nYAxb0uW", "B2zMC2v0v2LKDgG", "Aw5Uzxjive1m", "qKftrv9gt05uuW", "zgv0zwn0", "C3rY", "C2nYzwvUsw5MBW", "Dgv4DfnOywrVDW", "y2fUDMfZ", "zMLSBfrLEhq", "Dg9vChbLCKnHC2u", "Aw5WDxrBDhLWzt1LBwfPBf0", "Aw5SAw5L", "AxnqB2LUDeLUugf0Aa", "mtbWDcbKzMDZDgC", "zxzLBM9Kza", "tM90ief2ywLSywjSzq", "CMvK", "iIK6ia", "Ahr0Chm6lY93D3CUyw1HEM9UlMnVBs8", "CMvMzxjYzxi", "v0vcrfjjvKvsx0rpq1vnru5ux1bst1bfuLrjrvm", "x19Syxn0v2f0AxjbBgvYDa", "v0vcrfjjvKvsx05bvKLhqvrpuL9quK9qrvjusuvt", "zNjLCxvLBMn5", "qxvKAw9dB250zxH0", "z2v0rMXVyxrgCMvXDwvUy3LeyxrH", "zNjLCxvLBMn5qMLUq291BNq", "x19LEhbVCNrtDgfY", "sw5WDxruzwXLBwv0CNK", "rwXLBwvUDfrLBgvTzxrYEq", "DgHPCW", "zxHWB3j0CW", "y2HHCKf0", "re9dvu1ftLrFrvzftLrFteLtvevorvi", "AwrSzunHBgXIywnRq2fSBgvK", "y2fSBgjHy2S", "DgLTzw91Da", "y2XLyxi", "AwrSzvrPBwvVDxq", "re9dvu1ftLrFsu5urvjbq1rjt05FrvzftLrt", "yNvPBgrvuKW", "AgfZugfYyw1LDgvY", "CgfNzuLK", "z2v0ugf0Ag5HBwu", "zNjHz2vTzw50v2L0AeHHC2G", "C2nOzw1Hv2L0AenVBg9U", "CgfYyw1LDgvYCW", "AM9PBG", "ugvYzM9YBwfUy2vdB2XSzwn0B3i", "qxvKAw9gAw5NzxjWCMLUDenVBgXLy3rVCG", "rg9oB3ruCMfJA0nVBgXLy3rVCG", "rwXLBwvUDfrLBgvTzxrYEunVBgXLy3rVCG", "rM9UDenVBgXLy3rVCG", "sgLZDg9YEunVBgXLy3rVCG", "ywvZ", "AxnbCNjHEq", "quvtlu9gqG", "zgvJCNLWDa", "y2LWAgvY", "y3jLyxrLrgvJAxbOzxi", "y2XPzw50", "CMvHza", "quvtluncqW", "y3jLyxrLq2LWAgvY", "A2v5CW", "veXtxZfFma", "BwLUB3i", "CMfUzg9T", "vMvYC2LVBNm", "B3v0Chv0", "BgfZDa", "Aw5PDa", "q2LWAgvYu3vPDgvZ", "BwfJx2fSz29YAxrOBq", "y2LWAgvYx3r5Cgu", "Ag1Hy19ZAgeX", "uhjPDMf0zuTLEuLUzM8", "q2XHC3m", "u3vIAMvJDfb1yMXPy0TLEuLUzM8", "vhLWzq", "u0vrvuvoq0u", "yxzHAwXHyMXL", "DhLWzq", "y29TCg9Zzwq", "DgfNq2XHC3m", "zxf1ywXZ", "vu5jvKvsu0fm", "qKLuu1rssu5h", "zNjVBunOyxjdB2rL", "zNjVBurLCG", "C3rYAwn0", "y3jLyxrLqNvMzMvY", "yML0u3rYAw5Nq29UDgvUDhm", "Chv0qNL0zxm", "Chv0qNL0zq", "C3vIC3rY", "C2v0vgLTzq", "zgf0zvrVvxrJvgLTzq", "z2v0vvrdtwLUDxrLCW", "Chv0u2LNBMvKsw50", "sw50zwDLCIb0B28GBgfYz2u7ig1HEcbPCYaZmI1IAxrZlG", "iIWGz290ici", "qxbWBgLJyxrPB246", "tK9orq", "sue1u3rYAw5N", "CgTP", "B2LKCW", "DxrPBa", "yNL0zxnuB0HLEa", "iMLUChv0iIbTDxn0igjLigeGC3rYAw5NlG", "Bw9Kzq", "Aw5PDgLHBgL6zq", "x2LUChv0", "x2rLy3j5Chq", "Dw5Wywq", "igj5DgvZigfUzcbLEhbLy3rLzca", "x2LUqMXVy2S", "x291DejSB2nR", "Dhj1BMnHDgu", "yMXVy2TtAxPL", "x3bHCNrPywXcBg9JAW", "x3bHCNrPywXcExrLCW", "z2vUzxjHDgviyxnOvgfIBgu", "z2v0sw50mZi", "Chv0sw50mZi", "x2LUDhm", "x2nPCgHLCKXLBMD0Aa", "B3zLCMzSB3C", "x2feyxrHtgvUz3rO", "Cg93", "z2nT", "BxvSDgLWBhK", "y3jLyxrLrgvJCNLWDgLVBKnPCgHLCG", "x2TLExm", "zwnI", "revtlungqG", "revtlunuuG", "m0rfuY1dvfi", "y3rY", "Dw5KzwzPBMvK", "BwvZC2fNzq", "ufjjvKfurv9lrvLFqLLurv9mru5hveG", "y29UC3rHBNrZ", "u0vfrf9cwvrfx0XftKDusa", "sw52ywXPzcblzxKU", "zgvYvg9pAwq", "yMLUyxj5", "u0LhtL9cwvrfx0XftKDusa", "C2HHnteY", "zNjVBq", "zMXVB3i", "Ag1HyW", "yxbWtMfTzq", "mdeYmZq1nJC4owfIy2rLzMDOAwPRBg1UB3bXCNn0Dxz3EhL6", "zgL2AwrL", "y29TCgfYzvrV", "C3fYvg8", "y29WEvrV", "CLnOAwz0vg8", "ywjZ", "C3f1yxjLvg8", "zgXtAgLMDfrV", "zhjtAgLMDfrV", "zxHW", "y29UDMvYDa", "BMvNyxrL", "CMv2zxj0", "CMvKDwnL", "C3vIvg8", "Dg9sywrPEa", "zNjVBuLUDa", "zNjVBu51BwjLCG", "BwLU", "t05f", "yML0D2LZzvrV", "y2XHBxa", "C3vIDhjHy3q", "C2v0qML0", "zMXPCejPDa", "AxnfDMvU", "y2XVBMu", "z2nK", "Bw9Ksw50", "ANnIBG", "qMLNsw50zwDLCG", "qNL0zuj1zMzLCG", "z2v0qNL0zxm", "Dg9tDhjPBMC", "z2vUzxjHDgu", "zgLNzxn0tgvUz3rO", "Bg9N", "su5urvjqt0Xbveu", "Bgv2zwXZ", "Aw5KzxG", "y2f0zwDVCNK", "C3rHBMrHCMrgDwXS", "Aw5MBW", "zMXHz3m", "yxbWBhK", "Bg9JyxrPB24", "Bg9JAW", "BwvZC2fNzuXLBMD0AfnPEMu", "yNL0zxm", "BwDMmq", "C2HHmJu2v2L0AfjtquvUy3j5ChrPB24", "ms4ZlJeWms4Xmti", "ms4YlJG0mc4Xmtm1ndKUms43lJe", "ms4YlJG0mc4Xmtm1ndKUms45lJq", "ms4YlJG0mc4Xmtm1ndKUms45lJy", "Bg9JywXlzxLjza", "y2vYDejHzW", "ms4YlJG0mc4Xmtm1ndKUms4XmI4Xmc4XlJu", "ms4YlJG0mc4Xmtm1ndKUmI43", "ms4YlJG0mc4Xmtm1ndKUmI4Xma", "mI4XnI44ndaUms4XmdeUmY40lJeUmG", "z2L2zw5oyw1L", "ANvYAxnKAwn0Aw9Ut2zjBMnVCNbVCMf0Aw9Uq291BNrYEu5HBwu", "A2v5vxnHz2vszxn0CMLJDgLVBG", "mI41lJi5lJy", "mI41lJi5lJe3", "yMfZAwndB25ZDhjHAw50CW", "zxHWAxjHDgLVBKrHDgu", "Aw5ZDhj1y3rPB25dB2rL", "mI41lJi5lJmZ", "mI41lJi5lJm0", "mI41lJi5lJm2", "DgLTzxn0yw1WtgLZDa", "yxv0Ag9YAxr5sw5MB0fJy2vZCW", "CgjL", "uejfuZjbBgDVCML0Ag1ZlNbHCMfTCW", "uejfuZjbBgDVCML0Ag1ZlNbHCMfTCY5ZywX0", "Ag1Hy1DPDgHtseeX", "Ag1Hy1DPDgHtseeZodq", "C2fSDfnPEMu", "ywXNB3jPDgHT", "C2HHmq", "y3jLyxrLrw5JCNLWDgLVBKnPCgHLCG", "DxbKyxrL", "t0Le", "B2LKvg9ezxi", "zw5JB2rL", "quvtlteYoc1dqKm", "ywvZmtKY", "revtluvertmTq0jd", "zgvRsw5MBW", "Chv0qNvMzMvY", "ywvZmJu2luncqW", "zgvZq0jd", "z2v0sw50", "Bwq1", "rgvYAxzLzcbRzxKGAxmGDg9VigXVBMCU", "zgLNzxn0", "y29UDgvUDerVBwfPBG", "DMfSDwvZ", "ChjVy1r5Cgu", "uhjVyY1uExbL", "sw52ywXPzcbqru0GzM9YBwf0DgvKig1LC3nHz2uUifrOzsaIuhjVyY1uExbLiIbOzwfKzxiGBxvZDcbOyxzLihr3BYbZDwjMAwvSzhmU", "sw52ywXPzcbqru0GzM9YBwf0DgvKig1LC3nHz2uU", "y2vPBa", "Eg9YqNL0zxm", "uLnbrvmTt0ffucbLBMnVzgvKig1LC3nHz2uGBgvUz3rOigLZigLUDMfSAwqU", "q29UDgvUDeLUzM8", "y29UDgvUDfr5Cgu", "su5uruDfuG", "u2fMzujHzY5IywDwywX1zq", "qxr0CMLIDxrLlMf0Dhjjza", "y29UC3rYDwn0zwq", "zw5JugfYyw1LDgvY", "yxnUmq", "q2fUBM90ihjLywqGueTduYmXmIa", "DMfSAwrHDgu", "yMfNvhLWzq", "C2fMzunVBNrLBNrZ", "zNjPzw5KBhLoyw1L", "ueTduYmXmIbqrLGGB2yGDMvYC2LVBIbVDgHLCIb0AgfUidmGBM90ihn1ChbVCNrLzc4", "DMvYC2LVBG", "ueTduYmXmIbbDxrOzw50AwnHDgvKu2fMzsbLEhbLy3rLzcb0BYbIzsbHifnfuvvftKnfie9gienVBNrLBNrjBMzV", "zw5JCNLWDgvK", "C2fMzujHz3m", "Dg9qA2nZmtjbC24X", "y291BNq", "u0vu", "t0nurvrtvfjjtKC", "q09ovevyvf9tuevdsuzjqW", "Dg9ezxi", "z2v0twfJ", "CgTJCZC", "zw5JCNLWDgvKq29UDgvUDa", "zgLNzxn0qwXNB3jPDgHT", "mtK1mc0Wms0WmvqWmdOWmdOWmfO", "vvrdveLnrq", "twfSzM9YBwvKifblq1mJnYbTzxnZywDLlcbLEhbLy3rPBMCGzw5JCNLWDgvKignVBNrLBNqGy29UC3rYDwn0zwqGB2yGB25SEsbpq1rfvcbtvfjjtKCGB2jQzwn0CY4", "y29UDgvUDeLUzM9wywXPzgf0B3i", "y3jLyxrLu2LNBMvKrgf0yq", "CMf3q2fWDhvYzq", "y29UDgvUDa", "yxv0AgvUDgLJyxrLzef0DhjPyNv0zxnbC24X", "BwvZC2fNzurPz2vZDa", "C2LNBG", "CgfYyw1LDgvY", "C2vYAwfStNvTyMvY", "CMvJAxbPzw50CW", "rw5JCNLWDgvKq29UDgvUDeLUzM8Uy29UDgvUDfr5Cgu", "rw5JCNLWDgvKq29UDgvUDeLUzM8Uy29UDgvUDevUy3j5ChrPB25bBgDVCML0Ag0UCgfYyw1LDgvY", "zw52zwXVCgvKrgf0yvzHBgLKyxrVCG", "u2LNBMvYsw5MBY5PC3n1zxjbBMrtzxjPywXoDw1Izxi", "u2LNBMvKrgf0ys5eAwDLC3rbBgDVCML0Ag1Z", "u2LNBMvKrgf0ys5dzxj0AwzPy2f0zxm", "ru5duLLqveve", "yML0tgvUz3rO", "C2HPzNrmzwz0", "yNL0zvzHBhvL", "C2vLzezPBgvtEw5J", "C2v0sw1TzwrPyxrL", "C2vLza", "C2vLzezPBgu", "ChjUzW", "BMvLzgvK", "C2fSDeXLBMD0Aa", "zMLSBfDPDgHcExrL", "B3b0Aw9UCW", "y2XPzw50wq", "zxHWyw5Ks2v5", "Chv0sw50mtzmzq", "AxnoB2rLANm", "uLnbuhjPDMf0zuTLEq", "ChjPDMf0zuTLEvb1yMXPy0v4Cg9Uzw50", "ChjPDMf0zuTLEvbYAw1Lmq", "uLnbuhvIBgLJs2v5lMv4Cg9Uzw50", "rgLNzxn0sw5MBY5eAwDLC3rbBgDVCML0Ag0UywXNB3jPDgHTswrLBNrPzMLLCG", "Bw9K", "rw5JCNLWDgLVBIbIBg9JAYbPCYbPBNzHBgLKlG", "Bw9Ksw52zxjZzq", "C3vIDgXL", "CNnH", "CejPDhm", "BNvT", "zefKze9MzNnLDa", "C3rHDgu", "yML0CW", "z2vUzxjHDgvlzxLqywLY", "BNvTyMvY", "z2vUzxjHDgvlzxK", "y3j5ChrV", "uLnbu1nblvblq1mXlxyXxZu", "z2vUzxjHDgvlzxLqywLYu3LUyW", "CgvT", "ChvIBgLJs2v5", "CgTJCZe", "qvnolJeGB2jQzwn0igrVzxmGBM90ignVBNrHAw4Gysb2ywXPzcbsu0ftu0eTueTduZeTDJfFnsbeAwDLC3rjBMzVihzHBhvLlG", "C2HHmJu2", "Dg9izxG", "CNnHuhvIBgLJs2v5", "ChvIBgLJs2v5tw9KDwX1CW", "ChvIBgLJs2v5rxHWB25LBNq", "DxrMoa", "zNvSBe1LC3nHz2vmzw5NDgG", "yMXVy2Tmzw5NDgG", "C2HHmZG0", "u0HbltuXmI8YmJq", "y29TCgfJDa", "Chv0u3rYAw5N", "C3nOlxjZysa", "ChjPDMf0zuTLEvrVugvT", "q29UBMvJDgLVBKvUza", "z2v0q2LWAgvYu3vPDgu", "B3bLBG", "tgv2zwW", "CxvLDwu", "y2LWAgvYx3n1AxrL", "q29TChjLC3nPB25nzxrOB2q", "rgvZy3jPChrPB24", "ChjVDg9JB2XFDMvYC2LVBG", "BwfQB3i", "u3vWCg9YDgvKvMvYC2LVBNm", "CMvZDw1PBMC", "y3jLyxrLu2vYDMvYsgvSBg8", "q29UDgvUDfr5Cgu", "zMfPBa", "AgfUzhnOywTL", "DMvYAwz5q2vYDgLMAwnHDgvdAgfPBG", "zMf0ywW", "ChjVy2vZCW", "AgfUzgXLu2vYDMvYs2v5rxHJAgfUz2u", "ChjLx21HC3rLCL9ZzwnYzxq", "zxHWzwn0", "qwXLCNq", "Aw5ZDwzMAwnPzw50x3nLy3vYAxr5", "C2vZC2LVBG", "AxndB25Uzwn0zwq", "zgvZy3jPChrPB24", "rgvJB21WCMvZC2LVBIbMywLSzwqU", "vw5ZDxbWB3j0zwqGy2vYDgLMAwnHDguU", "zgvJCNLWDf9LCNjVCG", "C2vYDMvY", "zNjHz21LBNq", "z2v0qNL0zq", "AgfUzgXLq2HHBMDLq2LWAgvYu3bLyW", "AgfUzgXLq2XPzw50s2v5rxHJAgfUz2u", "C2vYDMvYx3jHBMrVBq", "BwfJx2TLEv9Szw5NDgG", "y29TChjLC3ngDw5JDgLVBG", "z2vUzxjHDgvlzxLZ", "y29TChjLC3nPB25FywXNB3jPDgHT", "z2v0vgLTzxPVBMvpzMzZzxq", "y29TChjLC3nPB25nzxrOB2q", "C2vYDMvYtMfTzuXPC3q", "C2vYDMvYq2vYDgLMAwnHDgu", "Chv0sw50mJq", "z2v0u2LNBMf0DxjL", "DgXZrgf0yq", "yMfKx2nLCNrPzMLJyxrL", "ywXLCNq", "y2vYDgLMAwnHDgvfCNjVCG", "y3jLyxrLu2vZC2LVBKnHy2HL", "C2v0u2vZC2LVBG", "B3jKzxi", "y2fJAgu", "y3jLyxrLq29UBMvJDgLVBG", "y2LWAgvYu3vPDgvZ", "vMvYC2LVBG", "y29UBMvJDgvK", "DMvYAwz5q2XPzw50", "DgXZrgf0yvjLywr5", "zw50Axr5", "CMvJB3jK", "y3jLyxrLq29UBMvJDgLVBLn0yxrL", "sgfUzhnOywTLigfSCMvHzhKGAw4GChjVz3jLC3mU", "y3jLyxrLuMfUzg9T", "AxnfBxb0Eq", "zNjHz21LBNrLza", "CMvHzhK", "zMX1C2G", "y2XVC2vK", "DgXZ", "t25SEsa4lcaXnIWGmJqSig9YidmYigjPDhmGC3vWCg9YDgvKoIa", "BMv4DfrPy2S", "Cg9ZDe1LC3nHz2u", "zM9YrwfJAa", "DMvYC2LVBNm", "yNL0zuXLBMD0Aa", "qNL0zvn0CMLUz0j1zMzLCG", "AxnbCNjHEuj1zMzLCG", "D3jPDgu", "D3jPDgvpzMzZzxq", "z3jVD1nPEMu", "ywnJB21TB2rHDgu", "DxrMmty", "C2v0sw50mZi", "Chv0sw50", "y29WEq", "yMfZzty0", "Dgv4Da", "zw5JB2rLnJq", "zgvJB2rL", "C3vIyxjYyxK", "yMfZztu4", "zgvMBgf0zq", "D2vI", "ieTPqG", "yNL0zxnuB0Lq", "y29Yzxm", "y29TBw9UtMfTzq", "B3jNyw5PEMf0Aw9UtMfTzq", "q2vYDgLMAwnHDguUvejtq2vYDgLMAwnHDgu", "y2vYDfzLCNnPB24", "y2vYDgLUzM9tAwDUyxr1CMvpAwq", "q2vYDgLMAwnHDguUvejtq2vYDgLMAwnHDguUC2LNBMf0DxjLlNbHCMfTzxrLCNm", "y2vYDfzHBgLKAxr5mKDLBMvYywXPEMvKvgLTzq", "CNnHChnZlMHHC2HbBgDVCML0Ag0UqwXNB3jPDgHTswrLBNrPzMLLCI5HBgDVCML0Ag0", "CNnHChnZlM1HC2Thzw5bBgDVCML0Ag0UqwXNB3jPDgHTswrLBNrPzMLLCI5HBgDVCML0Ag0", "q2vYDgLMAwnHDgLVBLjLCxvLC3rjBMzVlMf0DhjPyNv0zxmUDhLWzq", "q2vYDgLMAwnHDgLVBLjLCxvLC3q", "y3nY", "q2vYDgLMAwnHDgLVBLjLCxvLC3qUC2LNBMf0DxjL", "C2HVCNroyw1L", "BwDM", "BwfZA0DLBKHHC2HpAwq", "C2LNBMf0DxjLt2LK", "zw5JB2rLvxrMoa", "zw5JAxbOzxjpBMX5", "yNL0zxngCM9Tsva", "y29TBwvUDa", "sue1u1rssu5h", "y2vYDa", "z2vUzxjHDgvtDwjQzwn0s2v5swrLBNrPzMLLCG", "Agv4vg9cExrLCW", "tLvmta", "y2vYDgLMAwnHDgvgCM9TugvT", "AgvHzgvYvhLWzq", "yM9KEq", "ChvIBgLJs2v5vg9su0fqDwjSAwnlzxK", "vw5RBM93BIbMAw5NzxjWCMLUDcb0ExbLici", "q0vsveLgsunbveuGuKvrvuvtva", "ywXNB3jPDgHTt2LK", "DMfSAwrPDhK", "ywrKrMLLBgq", "C3vIAMvJDa", "vgHLihbHCMvUDcbJzxj0AwzPy2f0zsbKAwqGBM90igLZC3vLihrOzsbNAxzLBIbJAgLSzcbJzxj0AwzPy2f0ztSGDgHLignOAwXKignLCNrPzMLJyxrLj3mGAxnZDwvYigrVzxmGBM90ig1HDgnOihrOzsbWyxjLBNqNCYbZDwjQzwn0lG", "y2vYDgLMAwnHDgu", "AxnZDwvK", "C2LNBMf0DxjL", "y2vYDfzHBgLKAxr5m1vuq1rPBwu", "AxnZDwvY", "y2vYDfn1yMPLy3q", "y2vYDev4DgvUC2LVBNm", "qK9ptevbtG", "y3jPDgLJywW", "BM9UuMvWDwrPyxrPB24", "y3nYu2LNBMf0DxjLt2LK", "yxr0CMLIDxrLCW", "y2vYDgLMAwnHDgLVBLjLCxvLC3rjBMzV", "C2LNAw5MBW", "zxH0zw5ZAw9UCW", "y2vYDgLMAwnHDgvfEhrLBNnPB25Zvg9bC24X", "y2vYDgLMAwnHDgvfEhrLBNnPB25uB0fZBJe", "ywrKq2vYDgLMAwnHDgu", "AgfZq2vYDgLMAwnHDgu", "y2vYDgLMAwnHDgvuB0fZBJe", "BgLZDefSBenLCNrPzMLJyxrLCW", "y2vYDhm", "BM90qwz0zxi", "q2vYDgLMAwnHDguGyMfZAwndB25ZDhjHAw50CYbWyxrOtgvUq29UC3rYywLUDcb2Aw9SyxrLzc4", "AxnjCa", "zxH0CMfJDeHVC3rUyw1L", "AxnqCML2yxrL", "ChvIBgLJu3vMzML4", "Axnjy2fUBG", "C3vIzg9TywLU", "CwvQtfa", "y1zdsuq", "C3bSAxq", "BMv4Da", "zg9Uzq", "Dhj5CW", "ruH5sxa", "B25SB2fK", "CMvZDwX0", "CMLVt2i", "v3vhAgK", "yNvvA2C", "wwXvD1G", "C3rYAw5NAwz5", "qZnYwuf3nu5PAeriq1C", "q2DMwumYDq", "BxrUvxnNthPXmfm", "CuS5BxjmBq", "DNzQBq", "BxrHwM9KBtnTzur5re0Xuurh", "ExHIv0jNteP5EhjqqLC", "qMC5tG", "q2DQzenNAq", "qJjymurNtfzcswu2Awe", "DdnYuerlzq", "y3rquwq", "EhrqD0m", "qK9mrLm", "C0XIC21g", "mdaWmq", "mteXmq", "qND2veiZAJu", "BKXmm3LlBNj2Cq", "Bu1yExn1ENn2Cq", "D3buAgG", "C3jJ", "tMv0D29YAYbYzq", "y21fqM0", "BLLYvgm", "D0DJuha", "ue9tva", "tMv0D29YAYbYzxnWB25Zzsb3yxmGBM90ig9R", "v0Tdug4", "Au9ytLO", "CwL0wKO", "C2vUDa", "Agv4", "ALzZqMK", "zgLMzMLJDwX0Eq", "svnOq1G", "zNHor2S", "y2HLy2TZDw0", "y2f0y2G", "DLn0EM4", "txzIvgK", "DvDzt2m", "nMe2n2y", "BgLZ", "B2rHm29Kr1LTm0WWC3vYnNPx", "BdnYtejNDLr6Ehjzrxe", "DMD6tuj4Dq", "CJbQwheZqW", "qxHYtennzJbcm2K", "DwD6tevLBq", "rgHQnxf3nuT2EgjlExe", "CxzqnhD3Eq", "AwDmvwLNmvbcz1Hqq1C", "BMrPnw1nnvvZAeqZqwe", "C3HMD3iXtW", "q00Xy0f2qW", "Ctj6CefNEq", "EuTizenozq", "rwziuNKYvW", "qMC5sNL4CLbcmJq", "EK1usND4zq", "BNDXnhKYDvL6DeHkBLC", "qNDmvxnntdbez3zzDhe", "ExvYv3DluW", "EtjMmhKYrW", "rgD2wKrLCLzcD2zqqKC", "qZnIu0f4Cq", "EKPXng5NEtjVzguZEMe", "EJj2mhzNtfr6Cq", "quTinNzLBq", "qJa1uhzmBq", "rhHUuejnq0DdmKHwq0C", "CxzYC3j4Dq", "qNvisxiWrW", "qLPvDxC", "vMzwyLC", "BLPdAue", "mtbWEa", "y29SB3i6ihbPBMS7igjHy2TNCM91BMqTy29SB3i6", "DvLAEuu", "te1AzhC", "Aw5WDxu", "C3rHy2S", "EgjPrfy", "sfjKANG", "ANnVBG", "B1rqs3a", "ww9tAw4", "BgvMDa", "yMXHy2S", "uePYCwW", "zw5Nzs1LCNjVCG", "rhf3ENK", "yxLrwNe", "AKXfChK", "t2XMzeG", "sKTTz2e", "tvHTz0u", "C3rHDhvZ", "AhuSidaXiePHBG", "tgf4", "ANzYBLG", "Dg9vventDhjPBMC", "BgfZDfjLzNjLC2G", "vg9OtM4", "uevruxm", "v3f5yxO", "vgzMBxu", "z2v0sxrLBq", "zw5FCMvMCMvZAf90Aw1LC3rHBxa", "DurxALe", "vgjKyva", "sLjrreK", "u2HVDwXKuMvMCG", "yurrExq", "CwfYCxe", "veDtDMy", "yuDTquq", "z29Vz2XLyM90", "DNPjAfy", "y2fUvxnLtg9JywXtDg9YywDL", "wM9LEq", "wxvtENu", "CwPSELq", "AMvxBxa", "rwHNzxq", "tNvHvvy", "DgHLBG", "v0fiAMm", "ChjVzMLSzq", "zwXLBwv0CNLeyxrH", "z2v0q2HLy2TZDw0", "yMLiAu8", "Dw1dzwy", "qwnJzxnZrgvUAwvK", "yxrH", "DuTMwxPmrW", "q0XUCxnLCq", "rgDiwuiZqW", "q056zxPorW", "rxHMEev4Aq", "re1Mu0r3Dq", "DhDmsKnnovP6D25wqKC", "DtnUsKf3rW", "qtbinxeXyq", "rgC5DKnOyKXds25iq1C", "CMDqCemWma", "D2zYDKjnma", "v3rYvKjN", "tM9Uzq", "u2vJB25KCW", "A0H5q1a", "q2HHBgXLBMDLrq", "q29VA2LLrMv0y2HuAw1L", "B09rzey", "vgvSzw1LDhj5rM9YBun5y2XLqNvMzMvYq2XLyxjLzenVDw50", "Exjhr1u", "vxjtq2y", "re9lB1O", "r2vZ", "qNjVD3nLCG", "rxfhAw0", "y3j5ChrVlMDLDfjHBMrVBvzHBhvLCYGPig5VDcbZDxbWB3j0zwqUifnLzsbODhrWCZOVl2DPDgH1yI5JB20VDxvPzgPZl3v1AwqJz2v0CMfUzg9TDMfSDwvZlw5VDc1ZDxbWB3j0zwq", "x19WCM90B19F", "uLH3Cgm", "rwvNyw4", "D1Purhu", "tfPjr0i", "vNnIvNq", "EMHpuxy", "EfPPD2W", "wMHQBfK", "CgXjyNO", "BNvTrM9YBxm", "vfLozLPM", "q012mer4ALu", "Dxz6vKfNtW", "D2u1AKrnCq", "BLPhng50AvPTz3i2reS1Dunx", "BLP1v21KrZrUD3zxD05iAunH", "BuPTmM5Ar1HVDuXXD3vYshvh", "q2XHC3mGzxH0zw5KCYb2ywX1zsa", "C0vRzhG", "DuHpzwW", "DvvpsNi", "uLDfqMG", "BwHOzfa", "A01NENa", "zKLxCKm", "ENHqmxrODq", "qJnIwG", "CM9TChqUANm", "ENb3zMi", "Bw96lwv4DgvUC2LVBJOVlW", "B1L6svi", "EtnQthL4CKXXtNznEKC", "CJjqC3j4zq", "B2ziy0qZsfneCq", "DgH2zxj4Cq", "q3zbr2K", "zuLnAhm", "AvnIDNy", "qMHlvee", "Ce5szg0", "Ae9Twfq", "DgrWyxa", "nMy3mwe1mtjImwuWmZvLywfIntnKogjLnZmXmJbKm2zInJHHmgnHmZq2yJK1nJbHywiZztvJzgy3ntnKnwu5oa", "Cxjut2S", "zw5lvuP1", "qZjyuhKYDq", "B2u5DurLovrfyq", "svDxrw0", "yKPZC1G", "rMnAsuu", "v0HLqvy", "xZb4mJjJmtK0", "q2XXzem", "BuXLy0i", "CuP4tgq", "sMvxEue", "Bg1AsevJ", "AxPLza", "C2TmBgS", "t0f2t28", "rgXKwwO", "rw5JCNLWDa", "DvjkALG", "Aw5PDgLHBgL6zunVBxbVDw5Kq29SBgvJDg9Y", "tKrAALi", "q2fWywjPBgL0EunVBgXLy3rVCG", "qxv0B21HDgLVBKrLDgvJDgLVBKnVBgXLy3rVCG", "r3vZD3y", "BM93", "u2LNBMfSrw5JCNLWDgLVBLrPBwu", "rg5YCg8", "u2rRq2i", "ENC1sW", "C3zIyNn3rW", "qZj2vurH", "rgDyD3Lnzq", "DtjmtKjnzLnYDZvkq0C", "BNPzCM4", "tK5YrMu", "sKvzs3u", "uwjzuxe", "CKTVAum", "Bufns24", "rM1hCMm", "ChDXt28", "zuDiC1i", "wKPqy00", "ugDgu28", "wev0zxe", "EgPVthK", "AePxr1u", "q2HQvKrNotbfEgjm", "EtfIm3OWrW", "B2rdnw50DMH5DvbKDwu4", "ywjJzgvMz2HPAMTSBw5VChfYC3r1DND4ExPbqKneruzhseLks0XntK9quvjtvfvwv1HzwJaXmJm0nty3odKRlZ0", "BuPXnw5ADvL6tMP1qNzYnG", "DMzmnun3zq", "ENHQmevX", "C2HPzNq", "tefMyNm", "qMPmr2S", "zw5KrxzLBNq", "zxH0CMfJDfDOAwnO", "vu5jrevoveLgsuve", "y2XLyxjpBKz1BgXcDwzMzxi", "zwzNDef2", "uLH6rgy", "Bw91C2vdEwnSzxm", "yMLUzevSzw1LBNq", "A1DbC3e", "sffcv3C", "Bw91C2vdBgLJA1bVC2L0Aw9UCW", "u0PuzwK", "zKHdyvC", "CLDeDMS", "z2v0qM91BMrPBG", "z2v0qM91BMrPBMDdBgLLBNrszwn0", "Bxrhww10EtnTAgi2EMD6CxvH", "ExDYs3j4EKXctNjTqxe", "DMDmvhPX", "qMvQmxPnEKXdrW", "ENDytej3DLveyq", "B2rdv25KEvHTz2yYEMCXuNPx", "shvbChPv", "sgfhseLT", "ugPWBgq", "qvfwC3y", "v09suKy", "y3jJq2fSy3vSyxrVCG", "Bwvbr2W", "AKfIv2C", "xZb4mtu3nwm5", "DgfTCa", "rxD2v0vnqW", "De1izxzluW", "qwDMwNqZrfv1AgPwq2e", "qK1mB3LoqW", "A2v5v2fZuhjLC3nLza", "vvrgoevUy29Kzxi", "zM9YBq", "rwrrB28", "C3rLBMvY", "zM9JDxnuAw1LCW", "Dg90ywXgB2n1C1rPBwu", "zM9JDxnuAw1LC3rHBxa", "EJjUsKmZAq", "AvzuBe8", "DgvSzw1LDhj5", "r1juvuy", "r2PQr1O", "AMvyque", "vgLTzq", "r2vUzxjHDg9YigLZigfSCMvHzhKGzxHLy3v0Aw5NlG", "Dg91y2HdEwnSzxm", "BejIy3m", "s2DQre4", "rLvnu2K", "C1H6wfa", "B3bZ", "CM9ys1m", "EwnSzxm", "veXJy1q", "zw5KrxzLBNruAw1L", "C3rHCNrfDMvUDfrPBwu", "DwvMDhuXrhb1s3jgC3e", "EJiXsxrNuW", "BvPLm0fnou1cs0rT", "AvbiBeC", "qu9TrKe", "z2TTrMG", "Agnmy0m", "v2zjzxa", "wvbVDLi", "qu5kwfC", "u1buB0S", "t1fZrgy", "t2vTu1G", "y29SBgvJDg9Y", "EKjRv0LK", "qtaXExzloa", "rhC1Dxzlma", "rwu5s3r3qW", "qZnYwuf3nu5bD3O1", "De16tKflma", "B2rlww9KCtr1AgztD2zQEq", "qMDythKZCLzdswjnqLC", "wuTqzLO", "BeHPEgG", "Aw5PDgLHBgL6zunVBxbVDw5Kq28", "yvP0BMe", "vwzqvfG", "zwDsDNy", "q3DUwum", "uK9Vv2K", "vgvSzw1LDhj5rw5JB2rPBMDuAw1L", "tLnKqu0", "vKHqEvi", "q29TCg91BMrdB2XSzwn0B3i", "zhLkEfy", "qwLlqwO", "q2C5vW", "rwDiANvnvW", "Bxr6Aun2thvbmNe", "ug14twS", "rMTKz3a", "uNfituS", "vNPXy2q", "qwfgAwK", "sKjLA3q", "xZb4mMvKmMyY", "zMHZEge", "uxPQChq", "EKryzw0", "uKv6zfO", "yxjY", "CMvQzwn0", "CLrIvhi", "B1HqALC", "twLSBgLZzwnVBMrZ", "rg1XtgC", "D3vRDNu", "Bwv0CMLJCW", "C2nOzwr1Bgu", "CMvX", "vxDVChi", "q0fKr1y", "wKLcCKu", "tNnQB3C", "tuPOBKC", "zgzsy2S", "yNjJEge", "rxHPC3rPBMDuB2TLBKzVDw5K", "DwnOzxi", "zgHJvuK", "CNDPDNu", "r0XVq0C", "yMLXzfy", "sNjPvfy", "u0fhrK8", "swvbzNG", "xZb4mtCXyJvM", "yMfJA29MzK1PBgXPCW", "vgr2v08", "qLnnrNy", "Ehn0rhC", "DgrmwgK", "ENLhqu0", "y2HHBgXLBMDLx3r5Cgu", "Aw5WDxq", "vLbbrvy", "D3HouNi", "C2LNBMfSCW", "CMfJzq", "wvf1u2y", "shv6wwm", "qMDJCvm", "r1nLDvO", "CxHQBKiWAq", "EJjUmNjmCq", "rgz2quv4Eq", "D2z6ENflDq", "ExHewNyYzK1YtxyWEvC", "D01My3z1Dq", "CxHewNyYzK1ZDZuWENe", "Cti5vKeYteXYtxyWEvC", "DKTezuvlBq", "DNC1wKr4yLDcm2OWENe", "ENy5serOCKXcEgiWq1C", "qtj2vxGYBK95D1HtENe", "De1qEhnoBq", "EK16theZzq", "BxrImxznCNLetvC", "DMD2u3P3muXeAgO1DeC", "qtj2vq", "rxHYzNjNtW", "rxvyzxrnuW", "D05qnefLuW", "EK1MsKrNovK", "DgCXm3r2tW", "CZbQm0j3sW", "BMrImuf3DNvZmK8", "qwz6ENiYAq", "BNr1wM10ztnUDNz6CMC5m0vH", "EK1Ut0jmtW", "q012mennteXdvW", "EK5MvueWEq", "EJfesKflCq", "zMD1A3e", "vwjfvuG", "vLjAqMi", "AgvHzgvYCW", "q0vPA1y", "DK5Nuhy", "yw1iD2y", "wgXUtuC", "y2HHBgXLBMDL", "tuvpA2O", "rwX6rxy", "zgHowK0", "zMvYCMvY", "z2v0vg9Rzw4", "yvPYBey", "rw1iA20", "Ag9ZDa", "C2v0", "s0TrswG", "wwX3Bfy", "y29SB3i6ihLLBgXVDW", "zLvSzLa", "Egf5thC", "y29TCgXLDgu", "Cvjcuxu", "xZb4mtDMy2y4", "wenksMi", "v3P4BNm", "thbwuNy", "zvLbzxa", "DwHJAe0", "z3zeyuC", "AhP0DMq", "s21gq3C", "v3vruNG", "uePjAue", "xZb4m2rLyMu2", "xZb4nwiXmtm2", "AK9cwuu", "r0jYtKG", "B1ryuw4", "v2Pxvwe",
}

const b64chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/="

// 将 JSON 字符串生成浏览器一致 checksum
func generateChecksum(jsonStr string) string {
	crcTable := crc32.MakeTable(crc32.IEEE)
	crc := crc32.Checksum([]byte(jsonStr), crcTable)
	crcHex := strings.ToUpper(fmt.Sprintf("%08x", crc))
	return crcHex + "#" + jsonStr
}

//	func main() {
//		// 这里填入浏览器收集的 metrics JSON（顺序、字段、数组严格一致）
//		jsonData := `{"metrics":{"fp2":0,"browser":1,"capabilities":1,"gpu":11,"dnt":0,"math":0,"screen":0,"navigator":1,"auto":0,"stealth":0,"subtle":0,"canvas":24,"formdetector":1,"be":0},"start":1759110997811,"flashVersion":null,"plugins":[{"name":"PDF Viewer","str":"PDF Viewer "},{"name":"Chrome PDF Viewer","str":"Chrome PDF Viewer "},{"name":"Chromium PDF Viewer","str":"Chromium PDF Viewer "},{"name":"Microsoft Edge PDF Viewer","str":"Microsoft Edge PDF Viewer "},{"name":"WebKit built-in PDF","str":"WebKit built-in PDF "}],"dupedPlugins":"PDF Viewer Chrome PDF Viewer Chromium PDF Viewer Microsoft Edge PDF Viewer WebKit built-in PDF ||2560-1440-1392-24-*-*-*","screenInfo":"2560-1440-1392-24-*-*-*","referrer":"https://tickets.interpark.com/","userAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36","location":"https://ticket.globalinterpark.com/Global/Play/Gate/CBTLoginGate.asp?k=aFjSgryV2%2BapMJPmZnwBcQ%3D%3D&r=https%3A%2F%2Ftickets.interpark.com%2Fwaiting%3Fkey%3DXTlsCeoGxuB4ynlKRtI5JjofWgSCMSGyqGiU8pJ8kDy%252BRIqKyTuCDRVhDhq67xbvC%252FtIE4ypSGUeret7H1gsfGbE97heEIwzXe7SvWjZQO%252FkcZuTrsYroM4fL5vDjXPNozKgbYodvVMSAOPc1QfNpyLRVWxLas%252FtSojLTaX8x%252BB07mYqUq0drEAu0vGqtcGpL9gpVvt%252F45DMqz%252FIxE9V0hkS98egKrlnl92%252F8sP2u8H98O9UhQZHYTD3qjkIPZYN7DoEuJhamdxUc4i5LNAvHETg1OyrFYz%252FZ5m9Q2vwcXAD2TpGHrUi37S0Hv86USYmwU0XNtxXlEjJ1zMpnJlzbBvteGASX2gECDekfjiBfKoylVls3aAoCR%252BD8TXk1Ets9oxg3nHMC%252FN9Wry%252Fu8U5WVQZ0OlLKvulfyqwGc4twjrsAnChHRnam4KOdyeZ%252BCT9XpzTzbogIU1FQGUrk%252FlCLuCLpAUmPc9UqCcFysuUCosQuJdsnxUZk2YqoDw0tnBkg19W5%252Be2eBR%252F3QYNBSUZ4w%253D%253D%26lang%3Dzh&lng=zh","webDriver":false,"capabilities":{},"gpu":{},"dnt":null,"math":{},"automation":{},"stealth":{},"crypto":{},"canvas":{},"formDetected":false,"numForms":0,"numFormElements":0,"be":{},"end":1759110997812,"errors":[],"version":"2.4.0","id":"ea81e92b-e1f3-429b-bce1-6dbf6e392bbe"}`
//
//		checksum := generateChecksum(jsonData)
//		fmt.Println(checksum) // 输出浏览器一致 checksum，例如 D340EB72#...
//	}

func main() {
	// 这里直接用你从浏览器收集的完整 JSON（确保顺序和类型不变）
	//jsonData := `{"metrics":{"fp2":0,"browser":1,"capabilities":1,"gpu":11,"dnt":0,"math":0,"screen":0,"navigator":1,"auto":0,"stealth":0,"subtle":0,"canvas":24,"formdetector":1,"be":0},"start":1759110997811,"flashVersion":null,"plugins":[{"name":"PDF Viewer","str":"PDF Viewer "},{"name":"Chrome PDF Viewer","str":"Chrome PDF Viewer "},{"name":"Chromium PDF Viewer","str":"Chromium PDF Viewer "},{"name":"Microsoft Edge PDF Viewer","str":"Microsoft Edge PDF Viewer "},{"name":"WebKit built-in PDF","str":"WebKit built-in PDF "}],"dupedPlugins":"PDF Viewer Chrome PDF Viewer Chromium PDF Viewer Microsoft Edge PDF Viewer WebKit built-in PDF ||2560-1440-1392-24-*-*-*","screenInfo":"2560-1440-1392-24-*-*-*","referrer":"https://tickets.interpark.com/","userAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36","location":"https://ticket.globalinterpark.com/Global/Play/Gate/CBTLoginGate.asp?k=aFjSgryV2%2BapMJPmZnwBcQ%3D%3D&r=https%3A%2F%2Ftickets.interpark.com%2Fwaiting%3Fkey%3DXTlsCeoGxuB4ynlKRtI5JjofWgSCMSGyqGiU8pJ8kDy%252BRIqKyTuCDRVhDhq67xbvC%252FtIE4ypSGUeret7H1gsfGbE97heEIwzXe7SvWjZQO%252FkcZuTrsYroM4fL5vDjXPNozKgbYodvVMSAOPc1QfNpyLRVWxLas%252FtSojLTaX8x%252BB07mYqUq0drEAu0vGqtcGpL9gpVvt%252F45DMqz%252FIxE9V0hkS98egKrlnl92%252F8sP2u8H98O9UhQZHYTD3qjkIPZYN7DoEuJhamdxUc4i5LNAvHETg1OyrFYz%252FZ5m9Q2vwcXAD2TpGHrUi37S0Hv86USYmwU0XNtxXlEjJ1zMpnJlzbBvteGASX2gECDekfjiBfKoylVls3aAoCR%252BD8TXk1Ets9oxg3nHMC%252FN9Wry%252Fu8U5WVQZ0OlLKvulfyqwGc4twjrsAnChHRnam4KOdyeZ%252BCT9XpzTzbogIU1FQGUrk%252FlCLuCLpAUmPc9UqCcFysuUCosQuJdsnxUZk2YqoDw0tnBkg19W5%252Be2eBR%252F3QYNBSUZ4w%253D%253D%26lang%3Dzh&lng=zh","webDriver":false,"capabilities":{"css":{"textShadow":1,"WebkitTextStroke":1,"boxShadow":1,"borderRadius":1,"borderImage":1,"opacity":1,"transform":1,"transition":1},"js":{"audio":true,"geolocation":true,"localStorage":"supported","touch":false,"video":true,"webWorker":true},"elapsed":1},"gpu":{"vendor":"Google Inc. (NVIDIA)","model":"ANGLE (NVIDIA, NVIDIA GeForce GTX 1050 Ti (0x00001C82) Direct3D11 vs_5_0 ps_5_0, D3D11)","extensions":["ANGLE_instanced_arrays","EXT_blend_minmax","EXT_clip_control","EXT_color_buffer_half_float","EXT_depth_clamp","EXT_disjoint_timer_query","EXT_float_blend","EXT_frag_depth","EXT_polygon_offset_clamp","EXT_shader_texture_lod","EXT_texture_compression_bptc","EXT_texture_compression_rgtc","EXT_texture_filter_anisotropic","EXT_texture_mirror_clamp_to_edge","EXT_sRGB","KHR_parallel_shader_compile","OES_element_index_uint","OES_fbo_render_mipmap","OES_standard_derivatives","OES_texture_float","OES_texture_float_linear","OES_texture_half_float","OES_texture_half_float_linear","OES_vertex_array_object","WEBGL_blend_func_extended","WEBGL_color_buffer_float","WEBGL_compressed_texture_s3tc","WEBGL_compressed_texture_s3tc_srgb","WEBGL_debug_renderer_info","WEBGL_debug_shaders","WEBGL_depth_texture","WEBGL_draw_buffers","WEBGL_lose_context","WEBGL_multi_draw","WEBGL_polygon_mode"]},"dnt":null,"math":{"tan":"-1.4214488238747245","sin":"0.8178819121159085","cos":"-0.5753861119575491"},"automation":{"wd":{"properties":{"document":[],"window":[],"navigator":[]}},"phantom":{"properties":{"window":[]}}},"stealth":{"t1":0,"t2":0,"i":1,"mte":0,"mtd":false},"crypto":{"crypto":1,"subtle":1,"encrypt":true,"decrypt":true,"wrapKey":true,"unwrapKey":true,"sign":true,"verify":true,"digest":true,"deriveBits":true,"deriveKey":true,"getRandomValues":true,"randomUUID":true},"canvas":{"hash":-2120415875,"emailHash":null,"histogramBins":[13756,74,66,60,47,75,31,42,36,29,40,47,35,41,26,82,58,33,59,31,30,31,33,52,33,28,38,25,33,30,37,50,44,53,22,24,34,27,24,45,30,41,24,26,32,27,17,37,32,35,39,34,26,21,11,33,26,27,12,14,52,42,14,12,22,18,34,15,18,43,9,19,26,16,39,20,16,12,49,49,41,14,14,22,28,20,16,25,25,61,25,25,21,25,17,18,34,7,30,89,68,25,517,34,13,43,24,21,11,16,17,43,24,12,18,17,20,25,25,22,31,36,19,14,47,35,26,16,32,50,26,55,25,15,23,27,22,42,74,18,26,15,17,18,17,17,32,21,8,14,58,20,22,87,21,53,30,19,15,27,14,20,11,9,26,35,8,18,18,25,20,29,27,43,18,37,58,82,15,22,15,56,15,28,13,8,20,11,15,54,17,31,16,6,36,17,20,28,62,11,30,40,37,41,54,75,100,12,38,20,24,14,20,42,43,26,27,21,29,37,35,26,69,87,24,61,31,46,64,41,25,38,22,42,27,52,43,36,32,76,63,41,65,34,84,60,40,81,52,34,91,68,55,57,93,13309]},"formDetected":false,"numForms":0,"numFormElements":0,"be":{"si":false},"end":1759110997812,"errors":[],"version":"2.4.0","id":"ea81e92b-e1f3-429b-bce1-6dbf6e392bbe"}`
	jsonData := `{"metrics":{"fp2":0,"browser":0,"capabilities":0,"gpu":19,"dnt":0,"math":0,"screen":0,"navigator":0,"auto":0,"stealth":1,"subtle":0,"canvas":7,"formdetector":0,"be":0},"start":1759912981211,"flashVersion":null,"plugins":[{"name":"PDF Viewer","str":"PDF Viewer "},{"name":"Chrome PDF Viewer","str":"Chrome PDF Viewer "},{"name":"Chromium PDF Viewer","str":"Chromium PDF Viewer "},{"name":"Microsoft Edge PDF Viewer","str":"Microsoft Edge PDF Viewer "},{"name":"WebKit built-in PDF","str":"WebKit built-in PDF "}],"dupedPlugins":"PDF Viewer Chrome PDF Viewer Chromium PDF Viewer Microsoft Edge PDF Viewer WebKit built-in PDF ||2560-1440-1392-24-*-*-*","screenInfo":"2560-1440-1392-24-*-*-*","referrer":"https://tickets.interpark.com/","userAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36","location":"https://ticket.globalinterpark.com/Global/Play/Gate/CBTLoginGate.asp?k=PQ5VTFmFcZVuq77HIXRERA%3D%3D&r=https%3A%2F%2Ftickets.interpark.com%2Fwaiting%3Fkey%3D1LfF8KdMI0jqXlBoa8JKpFpwuprBHnOKJQ5R1o7gVXS%252BRIqKyTuCDRVhDhq67xbvC%252FtIE4ypSGUeret7H1gsfGbE97heEIwzXe7SvWjZQO%252FkcZuTrsYroM4fL5vDjXPNozKgbYodvVMSAOPc1QfNpyLRVWxLas%252FtSojLTaX8x%252BB07mYqUq0drEAu0vGqtcGpL9gpVvt%252F45DMqz%252FIxE9V0hkS98egKrlnl92%252F8sP2u8H98O9UhQZHYTD3qjkIPZYN7DoEuJhamdxUc4i5LNAvHETg1OyrFYz%252FZ5m9Q2vwcXAD2TpGHrUi37S0Hv86USYmwU0XNtxXlEjJ1zMpnJlzbBvteGASX2gECDekfjiBfKoylVls3aAoCR%252BD8TXk1Ets9oxg3nHMC%252FN9Wry%252Fu8U5WVQZ0OlLKvulfyqwGc4twjrsAnChHRnam4KOdyeZ%252BCT9c301g%252B3EE4wt%252FnqU%252FJwVO%252BCLpAUmPc9UqCcFysuUCosQuJdsnxUZk2YqoDw0tnBkg19W5%252Be2eBR%252F3QYNBSUZ4w%253D%253D%26lang%3Dzh&lng=zh","webDriver":false,"capabilities":{"css":{"textShadow":1,"WebkitTextStroke":1,"boxShadow":1,"borderRadius":1,"borderImage":1,"opacity":1,"transform":1,"transition":1},"js":{"audio":true,"geolocation":true,"localStorage":"supported","touch":false,"video":true,"webWorker":true},"elapsed":0},"gpu":{"vendor":"Google Inc. (NVIDIA)","model":"ANGLE (NVIDIA, NVIDIA GeForce GTX 1050 Ti (0x00001C82) Direct3D11 vs_5_0 ps_5_0, D3D11)","extensions":["ANGLE_instanced_arrays","EXT_blend_minmax","EXT_clip_control","EXT_color_buffer_half_float","EXT_depth_clamp","EXT_disjoint_timer_query","EXT_float_blend","EXT_frag_depth","EXT_polygon_offset_clamp","EXT_shader_texture_lod","EXT_texture_compression_bptc","EXT_texture_compression_rgtc","EXT_texture_filter_anisotropic","EXT_texture_mirror_clamp_to_edge","EXT_sRGB","KHR_parallel_shader_compile","OES_element_index_uint","OES_fbo_render_mipmap","OES_standard_derivatives","OES_texture_float","OES_texture_float_linear","OES_texture_half_float","OES_texture_half_float_linear","OES_vertex_array_object","WEBGL_blend_func_extended","WEBGL_color_buffer_float","WEBGL_compressed_texture_s3tc","WEBGL_compressed_texture_s3tc_srgb","WEBGL_debug_renderer_info","WEBGL_debug_shaders","WEBGL_depth_texture","WEBGL_draw_buffers","WEBGL_lose_context","WEBGL_multi_draw","WEBGL_polygon_mode"]},"dnt":null,"math":{"tan":"-1.4214488238747245","sin":"0.8178819121159085","cos":"-0.5753861119575491"},"automation":{"wd":{"properties":{"document":[],"window":[],"navigator":[]}},"phantom":{"properties":{"window":[]}}},"stealth":{"t1":0,"t2":0,"i":1,"mte":0,"mtd":false},"crypto":{"crypto":1,"subtle":1,"encrypt":true,"decrypt":true,"wrapKey":true,"unwrapKey":true,"sign":true,"verify":true,"digest":true,"deriveBits":true,"deriveKey":true,"getRandomValues":true,"randomUUID":true},"canvas":{"hash":-2120415875,"emailHash":null,"histogramBins":[13756,74,66,60,47,75,31,42,36,29,40,47,35,41,26,82,58,33,59,31,30,31,33,52,33,28,38,25,33,30,37,50,44,53,22,24,34,27,24,45,30,41,24,26,32,27,17,37,32,35,39,34,26,21,11,33,26,27,12,14,52,42,14,12,22,18,34,15,18,43,9,19,26,16,39,20,16,12,49,49,41,14,14,22,28,20,16,25,25,61,25,25,21,25,17,18,34,7,30,89,68,25,517,34,13,43,24,21,11,16,17,43,24,12,18,17,20,25,25,22,31,36,19,14,47,35,26,16,32,50,26,55,25,15,23,27,22,42,74,18,26,15,17,18,17,17,32,21,8,14,58,20,22,87,21,53,30,19,15,27,14,20,11,9,26,35,8,18,18,25,20,29,27,43,18,37,58,82,15,22,15,56,15,28,13,8,20,11,15,54,17,31,16,6,36,17,20,28,62,11,30,40,37,41,54,75,100,12,38,20,24,14,20,42,43,26,27,21,29,37,35,26,69,87,24,61,31,46,64,41,25,38,22,42,27,52,43,36,32,76,63,41,65,34,84,60,40,81,52,34,91,68,55,57,93,13309]},"formDetected":false,"numForms":0,"numFormElements":0,"be":{"si":false},"end":1759912981212,"errors":[],"version":"2.4.0","id":"82f37aca-f4e8-49f2-bb77-8b17465c6e6f"}`
	checksum := generateChecksum(jsonData)
	fmt.Println(checksum) // 这里应该输出 D340EB72#...

	index := 906
	encoded := obfuscated[index]

	decoded, err := decodeJSString(encoded)
	if err != nil {
		fmt.Printf("Error decoding string at index %d: %v\n", index, err)
		return
	}
	iv1 := generateIV(12) // _0x23e776(0xc)浏览器示例里是 12 bytes
	ivBase64 := base64.StdEncoding.EncodeToString(iv1)
	fmt.Printf("ivBase64: %s\n", ivBase64)
	fmt.Printf("Original Encoded: %s\n", encoded)
	fmt.Printf("Decoded String: %s\n", decoded)
	bytes, err := hexToBytes(decoded)
	if err != nil {
		fmt.Println("Error:", err)
		return
	}

	fmt.Println("Bytes:", bytes)                   // 字节数组
	fmt.Println("String:", bytesToJSString(bytes)) // JS 中的 "\x..." 字符串效果
	//iv, err := randomBytesToString(12)                                //随机生成12自己
	cipherHex, tag, err := EncryptAESGCM([]byte(checksum), bytes, iv1) // _0x3d5057['toHex']()
	fmt.Println(tag)
	token := fmt.Sprintf("Zoey::%s::%s::%s", ivBase64, tag, cipherHex)
	fmt.Println(token)
}
func generateIV(n int) []byte {
	iv := make([]byte, n)
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		panic(err)
	}
	return iv
}

// decodeJSString 模仿 JavaScript 中的 _0x386f87 函数
// 核心逻辑：非标准 Base64 解码 -> 转换为 URL 百分号编码 -> URL 解码
func decodeJSString(encoded string) (string, error) {
	var decodedBytes []byte
	var char1, char2, char3, char4 int = 0, 0, 0, 0
	var byte1, byte2, byte3 int = 0, 0, 0

	// 1. 非标准 Base64 解码
	for i := 0; i < len(encoded); i++ {
		char := encoded[i]
		charValue := strings.IndexByte(b64chars, char)

		// ~charValue 在 JavaScript 中用于检查 charValue 是否为 -1 (即不在 b64chars 中)
		// 如果不在，则忽略该字符（相当于 Base64 中的填充 '='）
		if charValue == -1 {
			continue
		}

		// Base64 核心逻辑：每 4 个 Base64 字符生成 3 个字节
		switch i % 4 {
		case 0:
			char1 = charValue
		case 1:
			char2 = charValue
			byte1 = (char1 << 2) | ((char2 & 0x30) >> 4)
			decodedBytes = append(decodedBytes, byte(byte1))
		case 2:
			char3 = charValue
			byte2 = ((char2 & 0xf) << 4) | ((char3 & 0x3c) >> 2)
			decodedBytes = append(decodedBytes, byte(byte2))
		case 3:
			char4 = charValue
			byte3 = ((char3 & 0x3) << 6) | char4
			decodedBytes = append(decodedBytes, byte(byte3))
		}
	}

	// 2. 转换为 URL 百分号编码 (Percent-Encoding)
	var percentEncoded string
	for _, b := range decodedBytes {
		// Javascript 代码: '%' + ('00' + byte.toString(16)).slice(-2)
		// 模仿 JavaScript 的 '00' + hex 字符串截取，确保两位十六进制
		percentEncoded += fmt.Sprintf("%%%02x", b)
	}

	// 3. URL 解码 (decodeURIComponent)
	// Go 语言的 net/url 包中的 QueryUnescape 函数实现了类似 decodeURIComponent 的功能
	decodedString, err := url.QueryUnescape(percentEncoded)
	if err != nil {
		return "", fmt.Errorf("URL decoding error: %w", err)
	}

	return decodedString, nil
}
func hexToBytes(hexStr string) ([]byte, error) {
	if strings.HasPrefix(hexStr, "0x") || strings.HasPrefix(hexStr, "0X") {
		hexStr = hexStr[2:]
	}
	return hex.DecodeString(hexStr)
}
func bytesToJSString(b []byte) string {
	var sb strings.Builder
	for _, v := range b {
		if v >= 32 && v <= 126 { // 可打印 ASCII
			sb.WriteByte(v)
		} else {
			sb.WriteString(fmt.Sprintf("\\x%02X", v))
		}
	}
	return sb.String()
}

func EncryptAESGCM(plaintext, key, iv []byte) (cipherHex, tagHex string, err error) {
	block, err := aes.NewCipher(key)
	if err != nil {
		return "", "", err
	}
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return "", "", err
	}
	if iv == nil {
		iv = make([]byte, gcm.NonceSize())
		if _, err := io.ReadFull(rand.Reader, iv); err != nil {
			return "", "", err
		}
	} else if len(iv) != gcm.NonceSize() {
		return "", "", fmt.Errorf("invalid IV length: %d, required: %d", len(iv), gcm.NonceSize())
	}

	ciphertextWithTag := gcm.Seal(nil, iv, plaintext, nil)
	tagSize := gcm.Overhead()
	ciphertext := ciphertextWithTag[:len(ciphertextWithTag)-tagSize]
	tag := ciphertextWithTag[len(ciphertextWithTag)-tagSize:]

	return hex.EncodeToString(ciphertext), hex.EncodeToString(tag), nil
}
func ParseQueryToStruct(query url.Values, out interface{}) {
	v := reflect.ValueOf(out).Elem()
	t := v.Type()

	for i := 0; i < v.NumField(); i++ {
		field := t.Field(i)
		tag := field.Tag.Get("json")
		if tag == "" {
			continue
		}
		if val := query.Get(tag); val != "" {
			v.Field(i).SetString(val)
		}
	}
}
