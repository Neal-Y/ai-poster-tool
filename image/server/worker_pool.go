package main

import (
	"log"
	"sync"
)

// Task represents a function to be executed by a worker
type Task func()

// WorkerPool manages a pool of workers for processing tasks
type WorkerPool struct {
	Tasks       chan Task
	workerCount int
	wg          sync.WaitGroup
	quit        chan struct{}
}

// NewWorkerPool creates a new worker pool
func NewWorkerPool(workerCount, queueSize int) *WorkerPool {
	return &WorkerPool{
		Tasks:       make(chan Task, queueSize),
		workerCount: workerCount,
		quit:        make(chan struct{}),
	}
}

// Start starts the worker pool
func (p *WorkerPool) Start() {
	log.Printf("Starting worker pool with %d workers", p.workerCount)
	
	// Start the workers
	for i := 0; i < p.workerCount; i++ {
		p.wg.Add(1)
		go p.worker(i)
	}
}

// Stop stops the worker pool
func (p *WorkerPool) Stop() {
	log.Println("Stopping worker pool")
	
	// Signal all workers to quit
	close(p.quit)
	
	// Wait for all workers to finish
	p.wg.Wait()
	
	// Close the tasks channel
	close(p.Tasks)
	
	log.Println("Worker pool stopped")
}

// worker is the main worker goroutine
func (p *WorkerPool) worker(id int) {
	defer p.wg.Done()
	
	log.Printf("Worker %d started", id)
	
	for {
		select {
		case task, ok := <-p.Tasks:
			if !ok {
				// Channel closed
				log.Printf("Worker %d shutting down: tasks channel closed", id)
				return
			}
			
			// Execute the task
			func() {
				defer func() {
					if r := recover(); r != nil {
						log.Printf("Worker %d recovered from panic: %v", id, r)
					}
				}()
				
				task()
			}()
			
		case <-p.quit:
			// Received quit signal
			log.Printf("Worker %d shutting down: quit signal received", id)
			return
		}
	}
}

// QueueSize returns the current number of tasks in the queue
func (p *WorkerPool) QueueSize() int {
	return len(p.Tasks)
}
