package main

import (
	"google.golang.org/grpc"
	"image_server/pb"
	"log"
	"net"
)

func main() {
	LoadEnv()

	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("❌ 無法監聽: %v", err)
	}

	grpcServer := grpc.NewServer()
	pb.RegisterImageServiceServer(grpcServer, &ImageHandler{})

	log.Println("🚀 gRPC server is running on :50051")
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("❌ gRPC 錯誤: %v", err)
	}
}
