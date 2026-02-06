
package main

import (
	"context"
	"fmt"
	"log"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/redis/go-redis/v9"
)

var ctx = context.Background()

// Redis Key used by Django
const RedisKey = ":1:ipo_list"

func main() {
	// Connect to Redis
	rdb := redis.NewClient(&redis.Options{
		Addr:     "localhost:6379",
		Password: "", // no password set
		DB:       1,  // Django settings uses "redis://.../1".
	})

	if err := rdb.Ping(ctx).Err(); err != nil {
		log.Fatalf("Failed to connect to Redis: %v", err)
	}

	// Setup Fiber
	app := fiber.New()

	// Enable CORS
	app.Use(cors.New())

	// Endpoint Defination
	app.Get("/api/ipos", func(c *fiber.Ctx) error {
		
		// Read raw JSON string stored by Python's get_redis_connection()
		val, err := rdb.Get(ctx, "ipo_list").Result()
		if err == redis.Nil {
			return c.Status(503).JSON(fiber.Map{
				"message": "Data syncing, please try again in a moment.",
			})
		} else if err != nil {
			return c.Status(500).JSON(fiber.Map{
				"error": "Redis error",
			})
		}

		// Python must store JSON (not pickled) so Go can read or unmarshal it safely.
		c.Set("Content-Type", "application/json")
		return c.SendString(val)
	})

	fmt.Println("Go API Server running on port 8080")
	log.Fatal(app.Listen(":8080"))
}