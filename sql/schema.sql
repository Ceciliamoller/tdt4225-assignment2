-- create database 
CREATE DATABASE IF NOT EXISTS assignment_2
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;
USE assignment_2;

-- Taxis
CREATE TABLE IF NOT EXISTS taxis (
  taxi_id INT UNSIGNED PRIMARY KEY
) ENGINE=InnoDB;

-- Taxi stands
CREATE TABLE IF NOT EXISTS stands (
  stand_id INT UNSIGNED PRIMARY KEY
) ENGINE=InnoDB;

-- Trips
CREATE TABLE IF NOT EXISTS trips (
  trip_id       VARCHAR(32) PRIMARY KEY,              -- TRIP_ID
  taxi_id       INT UNSIGNED NOT NULL,                -- TAXI_ID
  call_type     ENUM('A','B','C') NOT NULL,           -- CALL_TYPE
  origin_call   BIGINT NULL,                          -- ORIGIN_CALL
  origin_stand  INT UNSIGNED NULL,                    -- ORIGIN_STAND
  start_ts      DATETIME NOT NULL,                    -- CSV TIMESTAMP -> DATETIME (UTC)
  day_type      ENUM('A','B','C') NOT NULL,           -- DAYTYPE
  missing_data  BOOLEAN NOT NULL,                     -- MISSING_DATA
  points_count  INT UNSIGNED NOT NULL,                -- len(POLYLINE)
  duration_s    INT UNSIGNED NOT NULL,                -- max(0,(points_count-1)*15)
  distance_m    DOUBLE NULL,                          -- Haversine sum (meters)

  start_point   POINT SRID 4326 NOT NULL,
  end_point     POINT SRID 4326 NOT NULL,
  polyline      LINESTRING SRID 4326 NULL,

  INDEX ix_trips_taxi_start (taxi_id, start_ts),
  INDEX ix_trips_calltype (call_type),
  INDEX ix_trips_daytype  (day_type),
  SPATIAL INDEX sp_trips_start (start_point),
  SPATIAL INDEX sp_trips_end   (end_point),

  CONSTRAINT fk_trips_taxi   FOREIGN KEY (taxi_id)      REFERENCES taxis(taxi_id),
  CONSTRAINT fk_trips_stand  FOREIGN KEY (origin_stand) REFERENCES stands(stand_id),

  CHECK (points_count >= 0),
  CHECK (duration_s >= 0)
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS trip_points (
  trip_id   VARCHAR(32) NOT NULL,
  seq_idx   INT UNSIGNED NOT NULL,                    -- 0..N-1
  ts        DATETIME NOT NULL,                        -- start_ts + 15*seq_idx
  lon       DOUBLE  NOT NULL,
  lat       DOUBLE  NOT NULL,
  pt        POINT SRID 4326 NOT NULL,

  PRIMARY KEY (trip_id, seq_idx),
  INDEX ix_points_ts (ts),
  SPATIAL INDEX sp_points (pt),

  CONSTRAINT fk_points_trip FOREIGN KEY (trip_id) REFERENCES trips(trip_id)
) ENGINE=InnoDB;
