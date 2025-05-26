package main

import (
	"context"
	"crypto/sha1"
	"fmt"
	"image_server/pb"
	"log"
	"sync"
)

type ImageHandler struct {
	pb.UnimplementedImageServiceServer
}

func (h *ImageHandler) GenerateImage(ctx context.Context, req *pb.ImageRequest) (*pb.ImageResponse, error) {
	prompt := req.GetPrompt()
	hash := fmt.Sprintf("%x", sha1.Sum([]byte(prompt)))

	imgData, err := GetImageFromOpenAI(prompt)
	if err != nil {
		log.Printf("❌ 單圖產圖失敗：%v", err)
		return nil, err
	}

	return &pb.ImageResponse{
		ImageData:  imgData,
		PromptHash: hash,
		FileType:   "png",
	}, nil
}

func (h *ImageHandler) GenerateBatch(ctx context.Context, req *pb.BatchRequest) (*pb.BatchResponse, error) {
	prompts := req.GetPrompts()
	var wg sync.WaitGroup

	numWorker := 3
	type result struct {
		item *pb.BatchItem
		err  error
	}

	jobs := make(chan string, len(prompts))
	resultChan := make(chan result, len(prompts))

	for i := 0; i < numWorker; i++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()
			for prompt := range jobs {
				hash := fmt.Sprintf("%x", sha1.Sum([]byte(prompt)))
				imgData, err := GetImageFromOpenAI(prompt)
				if err != nil {
					log.Printf("❌ Worker %d 處理失敗：%v", workerID, err)
					continue
				}

				resultChan <- result{item: &pb.BatchItem{
					Prompt:     prompt,
					PromptHash: hash,
					ImageData:  imgData,
					FileType:   "png",
				}, err: nil}
			}
		}(i)
	}

	for _, prompt := range prompts {
		jobs <- prompt
	}
	close(jobs)

	wg.Wait()
	close(resultChan)

	var items []*pb.BatchItem
	for r := range resultChan {
		if r.item != nil {
			items = append(items, r.item)
		}
	}

	return &pb.BatchResponse{Items: items}, nil
}
