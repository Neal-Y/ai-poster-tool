package main

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"
)

type openAIImageRequest struct {
	Prompt         string `json:"prompt"`
	N              int    `json:"n"`
	Size           string `json:"size"`
	ResponseFormat string `json:"response_format"`
}

type openAIImageResponse struct {
	Created int64 `json:"created"`
	Data    []struct {
		B64JSON string `json:"b64_json"`
	} `json:"data"`
}

func GetImageFromOpenAI(prompt string) ([]byte, error) {
	apiKey := os.Getenv("OPENAI_API_KEY")
	if apiKey == "" {
		return nil, errors.New("OPENAI_API_KEY 未設定")
	}

	payload := openAIImageRequest{
		Prompt:         prompt,
		N:              1,
		Size:           "512x512",
		ResponseFormat: "b64_json",
	}

	body, _ := json.Marshal(payload)
	req, _ := http.NewRequest("POST", "https://api.openai.com/v1/images/generations", bytes.NewReader(body))
	req.Header.Set("Authorization", "Bearer "+apiKey)
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("OpenAI API 請求失敗：%w", err)
	}
	defer resp.Body.Close()

	respBody, _ := io.ReadAll(resp.Body)
	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("OpenAI API 錯誤（%d）：%s", resp.StatusCode, string(respBody))
	}

	var result openAIImageResponse
	if err := json.Unmarshal(respBody, &result); err != nil {
		return nil, fmt.Errorf("解析回傳失敗：%w", err)
	}

	if len(result.Data) == 0 || result.Data[0].B64JSON == "" {
		return nil, errors.New("OpenAI 未回傳圖片 base64")
	}

	return base64.StdEncoding.DecodeString(result.Data[0].B64JSON)
}
