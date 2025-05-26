package main

import (
	"sync"
	"time"
)

// RateLimiter defines the interface for rate limiting
type RateLimiter interface {
	Allow() bool
}

// TokenBucketLimiter implements a token bucket rate limiter
type TokenBucketLimiter struct {
	rate       float64     // tokens per second
	capacity   float64     // bucket capacity
	tokens     float64     // current token count
	lastRefill time.Time   // last time tokens were added
	mu         sync.Mutex  // mutex for thread safety
}

// NewRateLimiter creates a new rate limiter
func NewRateLimiter(ratePerMinute int) RateLimiter {
	return NewTokenBucketLimiter(float64(ratePerMinute) / 60.0, float64(ratePerMinute) / 6.0)
}

// NewTokenBucketLimiter creates a new token bucket rate limiter
func NewTokenBucketLimiter(rate, capacity float64) *TokenBucketLimiter {
	return &TokenBucketLimiter{
		rate:       rate,
		capacity:   capacity,
		tokens:     capacity,
		lastRefill: time.Now(),
	}
}

// Allow checks if a request is allowed under the rate limit
func (l *TokenBucketLimiter) Allow() bool {
	l.mu.Lock()
	defer l.mu.Unlock()
	
	// Refill tokens based on time elapsed
	now := time.Now()
	elapsed := now.Sub(l.lastRefill).Seconds()
	l.tokens = min(l.capacity, l.tokens + elapsed * l.rate)
	l.lastRefill = now
	
	// Check if we have enough tokens
	if l.tokens < 1.0 {
		return false
	}
	
	// Consume a token
	l.tokens -= 1.0
	return true
}

// min returns the minimum of two float64 values
func min(a, b float64) float64 {
	if a < b {
		return a
	}
	return b
}

// SemaphoreLimiter implements a semaphore-based concurrency limiter
type SemaphoreLimiter struct {
	sem chan struct{}
}

// NewSemaphoreLimiter creates a new semaphore-based concurrency limiter
func NewSemaphoreLimiter(maxConcurrent int) *SemaphoreLimiter {
	return &SemaphoreLimiter{
		sem: make(chan struct{}, maxConcurrent),
	}
}

// Acquire acquires a semaphore
func (l *SemaphoreLimiter) Acquire() bool {
	select {
	case l.sem <- struct{}{}:
		return true
	default:
		return false
	}
}

// Release releases a semaphore
func (l *SemaphoreLimiter) Release() {
	select {
	case <-l.sem:
	default:
		// This should never happen if used correctly
	}
}
