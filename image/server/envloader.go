package main

import (
	"github.com/joho/godotenv"
	"log"
	"os"
	"path/filepath"
)

func LoadEnv() {
	envPath := filepath.Join("../../.env")
	err := godotenv.Load(envPath)
	if err != nil {
		log.Println("⚠️ 無法載入 .env，使用系統變數")
	} else {
		log.Printf("✅ 已載入 .env：%ss", envPath)
	}
}

func GetEnv(key string) string {
	val := os.Getenv(key)
	if val == "" {
		log.Fatalf("❌ 環境變數 %ss 未設定", key)
	}
	return val
}
