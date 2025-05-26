package main

import (
	"sync"
	"time"
)

// CacheManager defines the interface for cache management
type CacheManager interface {
	Get(key string) (interface{}, bool)
	Set(key string, value interface{})
	Delete(key string)
	Clear()
}

// InMemoryCache implements an in-memory cache
type InMemoryCache struct {
	items      map[string]*cacheItem
	mu         sync.RWMutex
	ttl        time.Duration
	cleanupInterval time.Duration
	quit       chan struct{}
}

// cacheItem represents an item in the cache
type cacheItem struct {
	value      interface{}
	expiration time.Time
}

// NewInMemoryCache creates a new in-memory cache
func NewInMemoryCache(ttlMinutes int) *InMemoryCache {
	ttl := time.Duration(ttlMinutes) * time.Minute
	cache := &InMemoryCache{
		items:      make(map[string]*cacheItem),
		ttl:        ttl,
		cleanupInterval: ttl / 2,
		quit:       make(chan struct{}),
	}
	
	// Start the cleanup goroutine
	go cache.cleanup()
	
	return cache
}

// Get retrieves a value from the cache
func (c *InMemoryCache) Get(key string) (interface{}, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()
	
	item, found := c.items[key]
	if !found {
		return nil, false
	}
	
	// Check if the item has expired
	if time.Now().After(item.expiration) {
		return nil, false
	}
	
	return item.value, true
}

// Set adds a value to the cache
func (c *InMemoryCache) Set(key string, value interface{}) {
	c.mu.Lock()
	defer c.mu.Unlock()
	
	c.items[key] = &cacheItem{
		value:      value,
		expiration: time.Now().Add(c.ttl),
	}
}

// Delete removes a value from the cache
func (c *InMemoryCache) Delete(key string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	
	delete(c.items, key)
}

// Clear removes all values from the cache
func (c *InMemoryCache) Clear() {
	c.mu.Lock()
	defer c.mu.Unlock()
	
	c.items = make(map[string]*cacheItem)
}

// cleanup periodically removes expired items from the cache
func (c *InMemoryCache) cleanup() {
	ticker := time.NewTicker(c.cleanupInterval)
	defer ticker.Stop()
	
	for {
		select {
		case <-ticker.C:
			c.removeExpired()
		case <-c.quit:
			return
		}
	}
}

// removeExpired removes expired items from the cache
func (c *InMemoryCache) removeExpired() {
	now := time.Now()
	
	c.mu.Lock()
	defer c.mu.Unlock()
	
	for key, item := range c.items {
		if now.After(item.expiration) {
			delete(c.items, key)
		}
	}
}

// Stop stops the cleanup goroutine
func (c *InMemoryCache) Stop() {
	close(c.quit)
}

// NoOpCache implements a no-op cache that doesn't actually cache anything
type NoOpCache struct{}

// NewNoOpCache creates a new no-op cache
func NewNoOpCache() *NoOpCache {
	return &NoOpCache{}
}

// Get always returns not found
func (c *NoOpCache) Get(key string) (interface{}, bool) {
	return nil, false
}

// Set does nothing
func (c *NoOpCache) Set(key string, value interface{}) {}

// Delete does nothing
func (c *NoOpCache) Delete(key string) {}

// Clear does nothing
func (c *NoOpCache) Clear() {}
