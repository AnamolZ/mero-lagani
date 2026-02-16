package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/gofiber/fiber/v2/middleware/limiter"
	"github.com/gofiber/storage/redis/v3"
)

var ctx = context.Background()

// main initializes and runs the Go Fiber API server for serving IPO data.
// Features:
// - CORS enabled
// - Redis-backed rate limiting
// - Redis data fetching from Django cache (DB 1)
func main() {
	redisAddr := getEnv("REDIS_ADDR", "localhost:6379")

	// Redis storage for rate limiter (DB 0 to avoid collision with Django cache)
	limiterStore := redis.New(redis.Config{
		Host:     redisAddr,
		Port:     6379,
		Password: "",
		Database: 0,
		Reset:    false,
	})

	// Initialize Fiber application
	app := fiber.New()

	// Enable CORS for cross-origin requests
	app.Use(cors.New())

	// Rate Limiter Middleware
	// Restricts each IP to 50 requests per minute
	app.Use(limiter.New(limiter.Config{
		Max:        50,
		Expiration: 1 * time.Minute,
		Storage:    limiterStore,
		KeyGenerator: func(c *fiber.Ctx) string {
			return c.IP() // Use client IP for limiting
		},
		LimitReached: func(c *fiber.Ctx) error {
			return c.Status(fiber.StatusTooManyRequests).JSON(fiber.Map{
				"error": "Too many requests. Please try again later.",
			})
		},
	}))

	// Redis client for reading IPO data from Django cache (DB 1)
	dataClient := redis.New(redis.Config{
		Host:     redisAddr,
		Port:     6379,
		Database: 1, // Matches Django cache DB
	})

	// Endpoint: GET /api/ipos/
	// Returns IPO data stored in Redis as JSON
	app.Get("/api/ipos/", func(c *fiber.Ctx) error {
		val, err := dataClient.Get("ipo_list")
		if err != nil {
			// Cache miss or connection issue
			return c.Status(fiber.StatusServiceUnavailable).JSON(fiber.Map{
				"message": "Data syncing or cache empty.",
			})
		}

		// Respond with JSON content
		c.Set("Content-Type", "application/json")
		return c.Send(val)
	})

	fmt.Println("Go API Server running on port 8080")
	log.Fatal(app.Listen(":8080"))
}

// getEnv retrieves environment variables or returns a fallback value if not set
func getEnv(key, fallback string) string {
	if val, exists := os.LookupEnv(key); exists {
		return val
	}
	return fallback
}
