package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	_ "github.com/go-sql-driver/mysql"
)

var (
	db *sql.DB
)

func initDB() *sql.DB {
	sqlUser := os.Getenv("SQL_USER")
	sqlPass := os.Getenv("SQL_PASS")
	dbName := "garmin"
	db, err := sql.Open("mysql", fmt.Sprintf("%s:%s@/%s", sqlUser, sqlPass, dbName))
	if err != nil {
		log.Fatalf("Error connecting to the database: %v", err)
	}
	return db
}

func main() {
	db = initDB()
	defer db.Close()

	r := gin.Default()

	// Heart Rate endpoint
	r.GET("/heart_rate", func(c *gin.Context) {
		rows, err := db.Query("SELECT calendar_date, min_avg_hr, resting_hr, max_avg_hr FROM heart_rate")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		defer rows.Close()

		var heartRates []gin.H
		for rows.Next() {
			var calendarDate string
			var minAvgHR, restingHR, maxAvgHR int
			err := rows.Scan(&calendarDate, &minAvgHR, &restingHR, &maxAvgHR)
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
			heartRates = append(heartRates, gin.H{
				"calendar_date": calendarDate,
				"min_avg_hr":    minAvgHR,
				"resting_hr":    restingHR,
				"max_avg_hr":    maxAvgHR,
			})
		}
		c.JSON(http.StatusOK, heartRates)
	})

	// Sleep endpoint
	r.GET("/sleep", func(c *gin.Context) {
		rows, err := db.Query("SELECT * FROM sleep")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		defer rows.Close()

		var sleeps []gin.H
		for rows.Next() {
			var calendarDate string
			var remTime, restingHeartRate, totalSleepTimeInSeconds, deepTime, awakeTime int
			var respiration, localSleepEndTimeInMillis, localSleepStartTimeInMillis float64
			var sleepScoreQuality, hrvStatus string
			var bodyBatteryChange, gmtSleepStartTimeInMillis, gmtSleepEndTimeInMillis, sleepNeed, sleepScore int
			var skinTempF, skinTempC, lightTime, hrv7dAverage sql.NullFloat64
			var spO2 sql.NullFloat64

			err := rows.Scan(&calendarDate, &remTime, &restingHeartRate, &totalSleepTimeInSeconds,
				&respiration, &localSleepEndTimeInMillis, &deepTime, &awakeTime, &sleepScoreQuality,
				&spO2, &localSleepStartTimeInMillis, &sleepNeed, &bodyBatteryChange, &gmtSleepStartTimeInMillis,
				&gmtSleepEndTimeInMillis, &hrvStatus, &skinTempF, &sleepScore, &skinTempC, &lightTime, &hrv7dAverage)
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
			var spO2Value interface{}
			if spO2.Valid {
				spO2Value = spO2.Float64
			} else {
				spO2Value = nil
			}
			sleeps = append(sleeps, gin.H{
				"calendar_date":               calendarDate,
				"remTime":                     remTime,
				"restingHeartRate":            restingHeartRate,
				"totalSleepTimeInSeconds":     totalSleepTimeInSeconds,
				"respiration":                 respiration,
				"localSleepEndTimeInMillis":   localSleepEndTimeInMillis,
				"deepTime":                    deepTime,
				"awakeTime":                   awakeTime,
				"sleepScoreQuality":           sleepScoreQuality,
				"spO2":                        spO2Value,
				"localSleepStartTimeInMillis": localSleepStartTimeInMillis,
				"sleepNeed":                   sleepNeed,
				"bodyBatteryChange":           bodyBatteryChange,
				"gmtSleepStartTimeInMillis":   gmtSleepStartTimeInMillis,
				"gmtSleepEndTimeInMillis":     gmtSleepEndTimeInMillis,
				"hrvStatus":                   hrvStatus,
				"skinTempF":                   skinTempF,
				"sleepScore":                  sleepScore,
				"skinTempC":                   skinTempC,
				"lightTime":                   lightTime,
				"hrv7dAverage":                hrv7dAverage,
			})
		}
		c.JSON(http.StatusOK, sleeps)
	})

	// Respiration endpoint
	r.GET("/respiration", func(c *gin.Context) {
		rows, err := db.Query("SELECT * FROM respiration")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		defer rows.Close()

		var respirations []gin.H
		for rows.Next() {
			var calendarDate string
			var lowestRespirationValue, highestRespirationValue, avgWakingRespirationValue, avgSleepRespirationValue int

			err := rows.Scan(&calendarDate, &lowestRespirationValue, &highestRespirationValue,
				&avgWakingRespirationValue, &avgSleepRespirationValue)
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
			respirations = append(respirations, gin.H{
				"calendar_date":                calendarDate,
				"lowest_respiration_value":     lowestRespirationValue,
				"highest_respiration_value":    highestRespirationValue,
				"avg_waking_respiration_value": avgWakingRespirationValue,
				"avg_sleep_respiration_value":  avgSleepRespirationValue,
			})
		}
		c.JSON(http.StatusOK, respirations)
	})

	// Steps endpoint
	r.GET("/steps", func(c *gin.Context) {
		rows, err := db.Query("SELECT * FROM steps")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		defer rows.Close()

		var steps []gin.H
		for rows.Next() {
			var calendarDate string
			var stepGoal, totalSteps int
			var totalDistance float64

			err := rows.Scan(&calendarDate, &stepGoal, &totalSteps, &totalDistance)
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
			steps = append(steps, gin.H{
				"calendar_date":  calendarDate,
				"step_goal":      stepGoal,
				"total_steps":    totalSteps,
				"total_distance": totalDistance,
			})
		}
		c.JSON(http.StatusOK, steps)
	})

	// Stress endpoint
	r.GET("/stress", func(c *gin.Context) {
		rows, err := db.Query("SELECT * FROM stress")
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		defer rows.Close()

		var stresses []gin.H
		for rows.Next() {
			var calendarDate string
			var highStressDuration, lowStressDuration, overallStressLevel, restStressDuration, mediumStressDuration int

			err := rows.Scan(&calendarDate, &highStressDuration, &lowStressDuration, &overallStressLevel,
				&restStressDuration, &mediumStressDuration)
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
			stresses = append(stresses, gin.H{
				"calendar_date":          calendarDate,
				"high_stress_duration":   highStressDuration,
				"low_stress_duration":    lowStressDuration,
				"overall_stress_level":   overallStressLevel,
				"rest_stress_duration":   restStressDuration,
				"medium_stress_duration": mediumStressDuration,
			})
		}
		c.JSON(http.StatusOK, stresses)
	})

	// Run server
	if err := r.Run(":8080"); err != nil {
		log.Fatalf("Failed to run server: %v", err)
	}
}
